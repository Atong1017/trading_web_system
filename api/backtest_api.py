#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回測相關API模組
包含回測執行、結果匯出等功能
"""

import os
import concurrent.futures
import copy
from functools import partial
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import polars as pl
from fastapi import HTTPException, Request, Form, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.utils import Utils
from config.trading_config import TradingConfig
from strategies.dynamic_strategy import DynamicStrategy
from api.cache_api import CacheAPI
from api.excel_api import ExcelAPI

def print_log(message: str):
    """日誌輸出"""
    print(f"********** backtest_api.py - {message}")

def create_strategy(strategy_id: str, parameters: Dict[str, Any], strategy_manager=None):
    """建立策略實例"""
    # 處理自定義策略ID格式
    if strategy_id.startswith('custom_'):
        strategy_id = strategy_id.replace('custom_', '')
    
    # 從策略管理器取得自定義策略
    if strategy_manager is None:
        raise ValueError("需要傳入 strategy_manager 參數來建立策略")
    
    strategy_data = strategy_manager.get_strategy(strategy_id)
    if not strategy_data:
        raise ValueError(f"策略不存在: {strategy_id}")
    
    # 建立動態策略實例
    return DynamicStrategy(
        parameters=copy.deepcopy(parameters),
        strategy_code=strategy_data['code'],
        strategy_name=strategy_data['name']
    )

def combine_backtest_results(results: List, initial_capital: float) -> Dict[str, Any]:
    """合併多個回測結果"""
    if not results:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_profit_loss": 0.0,
            "total_profit_loss_rate": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_rate": 0.0,
            "sharpe_ratio": 0.0,
            "trade_records": [],
            "equity_curve": [initial_capital],
            "dates": [datetime.now()],
            "charts": []
        }
    
    # 合併交易記錄
    all_trades = []
    for result in results:
        all_trades.extend(result['trade_records'])
        
    # 計算總體統計
    total_trades = len(all_trades)
    # 檢查交易記錄是物件還是字典
    if all_trades and hasattr(all_trades[0], 'net_profit_loss'):
        # 如果是物件，使用屬性存取
        winning_trades = len([t for t in all_trades if t.net_profit_loss > 0])
        losing_trades = len([t for t in all_trades if t.net_profit_loss < 0])
        total_profit_loss = sum(t.net_profit_loss for t in all_trades)
    else:
        # 如果是字典，使用鍵值存取
        winning_trades = len([t for t in all_trades if t.get('net_profit_loss', 0) > 0])
        losing_trades = len([t for t in all_trades if t.get('net_profit_loss', 0) < 0])
        total_profit_loss = sum(t.get('net_profit_loss', 0) for t in all_trades)
    
    win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
    total_profit_loss_rate = total_profit_loss / initial_capital if initial_capital > 0 else 0.0

    # 合併權益曲線（簡化版，實際應按日期合併）
    try:
        all_equity_curves = [result.equity_curve for result in results]
        all_dates = [result.dates for result in results]
    except Exception as e:
        all_equity_curves = [result['equity_curve'] for result in results]
        all_dates = [result['dates'] for result in results]
       
    # 計算最大回撤
    max_drawdown = 0.0
    max_drawdown_rate = 0.0
    
    for equity_curve in all_equity_curves:
        if equity_curve:
            drawdown_info = Utils.calculate_drawdown(equity_curve)
            max_drawdown = max(max_drawdown, drawdown_info.get('max_drawdown', 0.0))
            max_drawdown_rate = max(max_drawdown_rate, drawdown_info.get('max_drawdown_pct', 0.0))
            
    # 計算夏普比率
    all_returns = []
    for equity_curve in all_equity_curves:
        for i in range(1, len(equity_curve)):
            if equity_curve[i-1] > 0:
                all_returns.append((equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1])
    
    sharpe_ratio = Utils.calculate_sharpe_ratio(all_returns)

    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "total_profit_loss": total_profit_loss,
        "total_profit_loss_rate": total_profit_loss_rate,
        "max_drawdown": max_drawdown,
        "max_drawdown_rate": max_drawdown_rate,
        "sharpe_ratio": sharpe_ratio,
        "trade_records": all_trades,
        "equity_curve": all_equity_curves[0] if all_equity_curves else [initial_capital],
        "dates": all_dates[0] if all_dates else [datetime.now()],
        "charts": results[0]['charts'] if results else []
    }

class BacktestAPI:
    """回測API類別"""    
    @staticmethod
    async def execute_backtest(
        excel_file: Optional[UploadFile],
        strategy_id: str,
        stock_source: str,
        price_source: str,
        initial_capital: float,
        manual_stock_ids: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
        start_year: Optional[str],
        end_year: Optional[str],
        request: Request
    ):
        """執行回測"""
        try:            
            # 從表單資料中收集策略參數
            form_data = await request.form()
            strategy_params = {}
            
            # 收集策略參數
            for key, value in form_data.items():
                if key.startswith('param-'):
                    param_name = key[6:]  # 移除 'param-' 前綴                    
                    # 根據參數類型轉換值                    
                    if TradingConfig.is_boolean_parameter(param_name):
                        strategy_params[param_name] = value.lower() == 'true' if value else TradingConfig.get_boolean_parameter_default(param_name)             
                    elif TradingConfig.is_float_parameter(param_name):
                        strategy_params[param_name] = float(value) if value else TradingConfig.get_float_parameter_default(param_name)
                    elif TradingConfig.is_int_parameter(param_name):
                        strategy_params[param_name] = int(value) if value else TradingConfig.get_int_parameter_default(param_name)
                    elif TradingConfig.is_string_parameter(param_name):
                        strategy_params[param_name] = str(value) if value else TradingConfig.get_string_parameter_default(param_name)
                    elif TradingConfig.is_special_parameter(param_name):
                        # 處理特殊參數
                        if param_name == 'record_holdings':
                            if isinstance(value, str):
                                strategy_params[param_name] = 1 if value.lower() in ['true', '1', 'on'] else 0
                            else:
                                strategy_params[param_name] = 1 if value else 0
                        else:
                            strategy_params[param_name] = TradingConfig.get_special_parameter_default(param_name)
                    elif any(param_name.endswith(suffix) for suffix in ['rate', 'percentage', 'percent']):
                        # 處理包含 'rate' 'percentage' 'percent' 的參數，預設為浮點數
                        strategy_params[param_name] = float(value) if value else 0.0
                    else:
                        # 嘗試轉換為適當的類型                        
                        try:
                            if value.lower() in ['true', 'false']:
                                strategy_params[param_name] = value.lower() == 'true'
                            elif '.' in str(value):
                                strategy_params[param_name] = float(value)
                            else:
                                strategy_params[param_name] = int(value)
                        except (ValueError, AttributeError):
                            strategy_params[param_name] = value
                elif key == 'initial_capital':
                    strategy_params[key] = float(value)
                    
            # 建立策略實例
            # 從請求的應用狀態取得策略管理器
            strategy_manager = request.app.state.strategy_manager if hasattr(request.app.state, 'strategy_manager') else None
            
            if strategy_manager is None:
                raise HTTPException(status_code=500, detail="策略管理器未初始化")
            
            strategy_instance = create_strategy(strategy_id, strategy_params, strategy_manager)
            
            # 準備參數
            parameters = {
                "strategy_params": strategy_params
            }
            
            # 初始化 stock_ids 變數
            stock_ids = None
            
            # 處理股票來源
            if stock_source == "excel":
                if not excel_file:
                    raise HTTPException(status_code=400, detail="請選擇Excel檔案")
                
                # 使用 ExcelAPI 處理股票來源Excel檔案
                excel_result = await ExcelAPI.process_stock_source_excel(excel_file)
                
                parameters["excel_data"] = excel_result["excel_data"]
                parameters["stock_ids"] = excel_result["stock_ids"]
                stock_ids = excel_result["stock_ids"]
                
            elif stock_source == "manual":
                if not manual_stock_ids:
                    raise HTTPException(status_code=400, detail="請輸入股票代碼")
                
                # 解析手動輸入的股票代碼
                stock_ids = [line.strip() for line in manual_stock_ids.split('\n') if line.strip()]
                if not stock_ids:
                    raise HTTPException(status_code=400, detail="沒有有效的股票代碼")
                
                parameters["stock_ids"] = stock_ids
                
                # 處理日期範圍
                if start_date and end_date:
                    parameters["start_date"] = datetime.fromisoformat(start_date)
                    parameters["end_date"] = datetime.fromisoformat(end_date)
            
            # 處理股價資料來源
            price_data = None
            
            if price_source == "excel":
                # Excel模式：從上傳的檔案取得資料
                price_excel_file = form_data.get('price_excel_file')
                if not price_excel_file and not excel_file:
                    raise HTTPException(status_code=400, detail="請選擇包含股價資料的Excel檔案")
                
                # 如果有專門的股價資料檔案，使用它；否則使用股票來源的檔案
                target_excel_file = price_excel_file if price_excel_file else excel_file
                
                # 使用 ExcelAPI 處理股價資料Excel檔案
                price_data = await ExcelAPI.process_price_excel(
                    target_excel_file, 
                    stock_ids, 
                    start_date, 
                    end_date
                )
                
                if price_data is None or price_data.is_empty():
                    raise HTTPException(status_code=400, detail="股價資料Excel檔案為空或格式錯誤")
                    
            elif price_source == "cache":
                # 快取模式：從快取系統取得資料
                cache_file = form_data.get('cache_file')
                if not cache_file:
                    raise HTTPException(status_code=400, detail="請選擇快取檔案")
                
                # 從快取API取得資料                    
                price_data = await CacheAPI.get_cache_data(cache_file)             
                if price_data is None or price_data.is_empty():
                    raise HTTPException(status_code=400, detail="快取檔案為空或格式錯誤")
                
                # 使用 Utils.standardize_columns 進行欄位標準化
                required_columns = ["stock_id", "date", "open", "high", "low", "close"]
                try:
                    price_data = Utils.standardize_columns(price_data, required_columns)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"快取資料欄位標準化失敗: {str(e)}")
                
                # 轉換日期欄位為 datetime 類型
                if "date" in price_data.columns and price_data["date"].dtype != pl.Date:
                    price_data = Utils.standardize_date_column(price_data, "date")
                
                # 過濾指定股票和日期範圍的資料
                if stock_ids is not None:
                    price_data = price_data.filter(pl.col("stock_id").is_in(stock_ids))
                
                if start_date and end_date:
                    price_data = price_data.filter(
                        (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                    )
                    
            # 統一驗證和標準化資料（Excel 和快取共用）
            if price_data is not None:
                # 驗證資料包含完整的K線資料並標準化欄位名稱
                required_columns = ["stock_id", "date", "open", "high", "low", "close"]
                column_mapping = Utils.validate_stock_data(price_data, required_columns)
                
                # 標準化欄位名稱
                standardized_data = price_data.clone()
                rename_dict = {}
                for standard_col, actual_col in column_mapping.items():
                    if actual_col != standard_col:
                        rename_dict[actual_col] = standard_col
                
                if rename_dict:
                    standardized_data = standardized_data.rename(rename_dict)
                
                parameters["price_data"] = standardized_data
                
            # 使用策略驗證特殊參數
            try:
                strategy_instance.validate_special_parameters(parameters)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            
            if "Jupyter" not in strategy_instance.strategy_name:
                # 使用策略處理參數
                processed_params = strategy_instance.process_parameters(parameters, parameters.get("excel_data"))
                # 提取處理後的資料
                stock_ids = processed_params["stock_ids"]
                start_date = processed_params.get("start_date")
                end_date = processed_params.get("end_date")
                price_data = processed_params.get("price_data")
            else:
                stock_ids = parameters.get("stock_ids")
                start_date = parameters.get("start_date", "")
                end_date = parameters.get("end_date", "")
                price_data = parameters.get("price_data", "")
                
            if "Jupyter" not in strategy_instance.strategy_name and 'use_vectorized' in processed_params:
                parameters['strategy_params']["use_vectorized"] = processed_params["use_vectorized"]
            
            if not stock_ids:
                raise HTTPException(status_code=400, detail="沒有有效的股票代碼")
            
            # 根據資料來源處理
            if price_source == "api":
                # API模式：使用策略處理後的資料請求API
                from api.stock_api import StockAPI
                async with StockAPI() as stock_api:
                    # 取得股價資料
                    stock_data = await stock_api.get_stock_price(stock_ids, start_date, end_date)
                    # 使用策略處理所需的API資料
                    stock_data = await strategy_instance.process_api_data(stock_data, stock_api)
            else:
                # Excel/快取模式：使用已處理的股價資料
                stock_data = price_data
                
            # 執行回測
            if stock_data is None or stock_data.is_empty():
                raise HTTPException(status_code=400, detail="沒有有效的股票資料")
            
            # 按股票分組執行回測
            results = []
            stock_groups = stock_data.group_by("stock_id")
            def process_single_stock(stock_id, group_data, strategy_id, strategy_params, initial_capital):
                """處理單一股票的回測"""
                try:
                    # 建立策略實例（每個股票獨立），確保參數獨立
                    strategy_instance = create_strategy(strategy_id, copy.deepcopy(strategy_params), strategy_manager)
                    try:
                        # 取得股票名稱
                        stock_name = group_data['stock_name'][0]
                    except Exception as e:
                        # 如果沒有股票名稱，使用股票代碼
                        stock_name = stock_id
                        
                    # 執行回測
                    strategy_instance.run_backtest(
                        group_data, 
                        parameters.get("excel_data"),
                        initial_capital, 
                        stock_id,  # 使用實際的股票代碼
                        f"{stock_name}"  # 使用實際的股票名稱
                    )
                    
                    # 取得結果
                    result = strategy_instance.get_strategy_result(initial_capital)

                    return result
                    
                except Exception as e:
                    print_log(f"execute_backtest:股票 {stock_id} 回測失敗: {e}")
                    return None
                    
            # 準備並行處理的任務
            tasks = []
            for stock_id, group_data in stock_groups:
                task = partial(
                    process_single_stock,
                    stock_id=stock_id,
                    group_data=group_data,
                    strategy_id=strategy_id,
                    strategy_params=strategy_params,
                    initial_capital=initial_capital
                )
                tasks.append(task)
            
            # 使用線程池執行並行處理
            max_workers = min(len(tasks), 10)  # 最多10個線程，避免過度並行
            
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任務
                future_to_stock = {executor.submit(task): task for task in tasks}
                
                # 收集結果
                for future in concurrent.futures.as_completed(future_to_stock):
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                    except Exception as e:
                        print_log(f"execute_backtest:任務執行失敗: {e}")
            
            # 合併結果
            combined_result = combine_backtest_results(results, initial_capital)
            # 轉換為前端需要的格式
            trades = []
            for trade_record in combined_result.get("trade_records", []):
                # 檢查 trade_record 是物件還是字典
                if hasattr(trade_record, 'entry_date'):
                    # 如果是物件，使用屬性存取
                    trades.append({
                        "position_id": trade_record.position_id,
                        "entry_date": trade_record.entry_date.strftime("%Y-%m-%d") if hasattr(trade_record.entry_date, 'strftime') else str(trade_record.entry_date),
                        "exit_date": trade_record.exit_date.strftime("%Y-%m-%d") if hasattr(trade_record.exit_date, 'strftime') else str(trade_record.exit_date),
                        "stock_id": trade_record.stock_id,
                        "stock_name": trade_record.stock_name,
                        "trade_direction": trade_record.trade_direction,
                        "entry_price": trade_record.entry_price,
                        "exit_price": trade_record.exit_price,
                        "shares": trade_record.shares,
                        "profit_loss": trade_record.profit_loss,
                        "profit_loss_rate": trade_record.profit_loss_rate,
                        "commission": trade_record.commission,
                        "securities_tax": trade_record.securities_tax,
                        "net_profit_loss": trade_record.net_profit_loss,
                        "holding_days": trade_record.holding_days,
                        "exit_reason": trade_record.exit_reason,
                        "current_price": trade_record.current_price,
                        "unrealized_profit_loss": trade_record.unrealized_profit_loss,
                        "unrealized_profit_loss_rate": trade_record.unrealized_profit_loss_rate,
                        "current_date": trade_record.current_date.strftime("%Y-%m-%d") if hasattr(trade_record.current_date, 'strftime') else str(trade_record.current_date),
                        "exit_price_type": trade_record.exit_price_type,
                        "current_entry_price": trade_record.current_entry_price,
                        "current_exit_price": trade_record.current_exit_price,
                        "current_profit_loss": trade_record.current_profit_loss,
                        "current_profit_loss_rate": trade_record.current_profit_loss_rate,
                        "take_profit_price": trade_record.take_profit_price,
                        "stop_loss_price": trade_record.stop_loss_price,
                        "open_price": trade_record.open_price,
                        "high_price": trade_record.high_price,
                        "low_price": trade_record.low_price,
                        "close_price": trade_record.close_price
                    })
                else:
                    # 如果是字典，使用鍵值存取
                    trades.append({
                        "position_id": trade_record.get("position_id", ""),
                        "entry_date": trade_record.get("entry_date", ""),
                        "exit_date": trade_record.get("exit_date", ""),
                        "stock_id": trade_record.get("stock_id", ""),
                        "stock_name": trade_record.get("stock_name", ""),
                        "trade_direction": trade_record.get("trade_direction", 1),
                        "entry_price": trade_record.get("entry_price", 0),
                        "exit_price": trade_record.get("exit_price", 0),
                        "shares": trade_record.get("shares", 0),
                        "profit_loss": trade_record.get("profit_loss", 0),
                        "profit_loss_rate": trade_record.get("profit_loss_rate", 0),
                        "commission": trade_record.get("commission", 0),
                        "securities_tax": trade_record.get("securities_tax", 0),
                        "net_profit_loss": trade_record.get("net_profit_loss", 0),
                        "holding_days": trade_record.get("holding_days", 0),
                        "exit_reason": trade_record.get("exit_reason", ""),
                        "current_price": trade_record.get("current_price", 0),
                        "unrealized_profit_loss": trade_record.get("unrealized_profit_loss", 0),
                        "unrealized_profit_loss_rate": trade_record.get("unrealized_profit_loss_rate", 0),
                        "current_date": trade_record.get("current_date", ""),
                        "exit_price_type": trade_record.get("exit_price_type", ""),
                        "current_entry_price": trade_record.get("current_entry_price", 0),
                        "current_exit_price": trade_record.get("current_exit_price", 0),
                        "current_profit_loss": trade_record.get("current_profit_loss", 0),
                        "current_profit_loss_rate": trade_record.get("current_profit_loss_rate", 0),
                        "take_profit_price": trade_record.get("take_profit_price", 0),
                        "stop_loss_price": trade_record.get("stop_loss_price", 0),
                        "open_price": trade_record.get("open_price", 0),
                        "high_price": trade_record.get("high_price", 0),
                        "low_price": trade_record.get("low_price", 0),
                        "close_price": trade_record.get("close_price", 0)
                    })
            
            # 處理持有部位資料
            holding_positions = []
            for result in results:
                # 檢查 result 是字典還是物件
                if isinstance(result, dict):
                    # 如果是字典（自定義策略），從字典中取得 holding_positions
                    if "holding_positions" in result and result["holding_positions"]:
                        for position in result["holding_positions"]:
                            # 檢查 position 是物件還是字典
                            if hasattr(position, 'entry_date'):
                                # 如果是物件，使用屬性存取
                                holding_positions.append({
                                    "entry_date": position.entry_date.strftime("%Y-%m-%d"),
                                    "stock_id": position.stock_id,
                                    "stock_name": position.stock_name,
                                    "trade_direction": position.trade_direction,
                                    "entry_price": position.entry_price,
                                    "current_price": position.current_price,
                                    "shares": position.shares,
                                    "unrealized_profit_loss": position.unrealized_profit_loss,
                                    "unrealized_profit_loss_rate": position.unrealized_profit_loss_rate,
                                    "holding_days": position.holding_days,
                                    "current_date": position.current_date.strftime("%Y-%m-%d"),
                                    "exit_price_type": position.exit_price_type,
                                    "current_exit_price": position.current_exit_price,
                                    "current_profit_loss": position.current_profit_loss,
                                    "current_profit_loss_rate": position.current_profit_loss_rate,
                                    "take_profit_price": position.take_profit_price,
                                    "stop_loss_price": position.stop_loss_price,
                                    "open_price": position.open_price,
                                    "high_price": position.high_price,
                                    "low_price": position.low_price,
                                    "close_price": position.close_price
                                })
                            else:
                                # 如果是字典，使用鍵值存取
                                holding_positions.append({
                                    "entry_date": position.get("entry_date", ""),
                                    "stock_id": position.get("stock_id", ""),
                                    "stock_name": position.get("stock_name", ""),
                                    "trade_direction": position.get("trade_direction", ""),
                                    "entry_price": position.get("entry_price", 0),
                                    "current_price": position.get("current_price", 0),
                                    "shares": position.get("shares", 0),
                                    "unrealized_profit_loss": position.get("unrealized_profit_loss", 0),
                                    "unrealized_profit_loss_rate": position.get("unrealized_profit_loss_rate", 0),
                                    "holding_days": position.get("holding_days", 0),
                                    "current_date": position.get("current_date", ""),
                                    "exit_price_type": position.get("exit_price_type", ""),
                                    "current_exit_price": position.get("current_exit_price", 0),
                                    "current_profit_loss": position.get("current_profit_loss", 0),
                                    "current_profit_loss_rate": position.get("current_profit_loss_rate", 0),
                                    "take_profit_price": position.get("take_profit_price", 0),
                                    "stop_loss_price": position.get("stop_loss_price", 0),
                                    "open_price": position.get("open_price", 0),
                                    "high_price": position.get("high_price", 0),
                                    "low_price": position.get("low_price", 0),
                                    "close_price": position.get("close_price", 0)
                                })
                else:
                    # 如果是物件（內建策略），從物件屬性中取得 holding_positions
                    if hasattr(result, 'holding_positions') and result.holding_positions:
                        for position in result.holding_positions:
                            # 檢查 position 是物件還是字典
                            if hasattr(position, 'entry_date'):
                                # 如果是物件，使用屬性存取
                                holding_positions.append({
                                    "entry_date": position.entry_date.strftime("%Y-%m-%d"),
                                    "stock_id": position.stock_id,
                                    "stock_name": position.stock_name,
                                    "trade_direction": position.trade_direction,
                                    "entry_price": position.entry_price,
                                    "current_price": position.current_price,
                                    "shares": position.shares,
                                    "unrealized_profit_loss": position.unrealized_profit_loss,
                                    "unrealized_profit_loss_rate": position.unrealized_profit_loss_rate,
                                    "holding_days": position.holding_days,
                                    "current_date": position.current_date.strftime("%Y-%m-%d"),
                                    "exit_price_type": position.exit_price_type,
                                    "current_exit_price": position.current_exit_price,
                                    "current_profit_loss": position.current_profit_loss,
                                    "current_profit_loss_rate": position.current_profit_loss_rate,
                                    "take_profit_price": position.take_profit_price,
                                    "stop_loss_price": position.stop_loss_price,
                                    "open_price": position.open_price,
                                    "high_price": position.high_price,
                                    "low_price": position.low_price,
                                    "close_price": position.close_price
                                })
                            else:
                                # 如果是字典，使用鍵值存取
                                holding_positions.append({
                                    "entry_date": position.get("entry_date", ""),
                                    "stock_id": position.get("stock_id", ""),
                                    "stock_name": position.get("stock_name", ""),
                                    "trade_direction": position.get("trade_direction", ""),
                                    "entry_price": position.get("entry_price", 0),
                                    "current_price": position.get("current_price", 0),
                                    "shares": position.get("shares", 0),
                                    "unrealized_profit_loss": position.get("unrealized_profit_loss", 0),
                                    "unrealized_profit_loss_rate": position.get("unrealized_profit_loss_rate", 0),
                                    "holding_days": position.get("holding_days", 0),
                                    "current_date": position.get("current_date", ""),
                                    "exit_price_type": position.get("exit_price_type", ""),
                                    "current_exit_price": position.get("current_exit_price", 0),
                                    "current_profit_loss": position.get("current_profit_loss", 0),
                                    "current_profit_loss_rate": position.get("current_profit_loss_rate", 0),
                                    "take_profit_price": position.get("take_profit_price", 0),
                                    "stop_loss_price": position.get("stop_loss_price", 0),
                                    "open_price": position.get("open_price", 0),
                                    "high_price": position.get("high_price", 0),
                                    "low_price": position.get("low_price", 0),
                                    "close_price": position.get("close_price", 0)
                                })
            
            return {
                "success": True,
                "summary": {
                    "total_trades": combined_result.get("total_trades", 0),
                    "winning_trades": combined_result.get("winning_trades", 0),
                    "losing_trades": combined_result.get("losing_trades", 0),
                    "win_rate": combined_result.get("win_rate", 0.0),
                    "total_profit": combined_result.get("total_profit_loss", 0.0),
                    "total_profit_rate": combined_result.get("total_profit_loss_rate", 0.0)
                },
                "trades": trades,
                "holding_positions": holding_positions
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def export_backtest_excel(request: Request):
        """匯出回測結果為Excel"""
        try:
            data = await request.json()
            trade_records = data.get("trade_records", [])
            
            if not trade_records:
                raise HTTPException(status_code=400, detail="沒有交易記錄可匯出")
            
            # 使用 ExcelAPI 匯出
            return await ExcelAPI.export_backtest_excel(trade_records)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_detailed_records(
        excel_file: UploadFile,
        strategy_name: str,
        dataSource: str,
        config: str
    ):
        """取得詳細交易記錄"""
        try:
            # 這裡應該實作詳細記錄的邏輯
            # 目前返回空記錄
            return {
                "success": True,
                "records": []
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_excel_format():
        """取得Excel檔案格式說明"""
        try:
            return await ExcelAPI.get_excel_format()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def export_detailed_records(request: Request):
        """匯出詳細回測記錄為Excel"""
        try:
            data = await request.json()
            strategy_name = data.get("strategy_name", "未知策略")
            
            # 使用完整的交易記錄資料
            complete_trade_records = data.get("complete_trade_records", [])
            complete_holding_positions = data.get("complete_holding_positions", [])
            
            # 如果沒有完整資料，嘗試使用原始資料
            if not complete_trade_records and not complete_holding_positions:
                trade_records = data.get("trade_records", [])
                holding_positions = data.get("holding_positions", [])
                
                if not trade_records and not holding_positions:
                    raise HTTPException(status_code=400, detail="沒有記錄可匯出")
                
                # 使用 ExcelAPI 取得完整資料
                complete_data = await ExcelAPI.get_complete_trade_data(trade_records, holding_positions)
                complete_trade_records = complete_data["complete_trade_records"]
                complete_holding_positions = complete_data["complete_holding_positions"]
            
            # 使用 ExcelAPI 匯出詳細記錄
            return await ExcelAPI.export_detailed_records(
                strategy_name,
                complete_trade_records,
                complete_holding_positions
            )
            
        except Exception as e:
            print_log(f"export_detailed_records error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_data_structure():
        """取得 TradeRecord 和 HoldingPosition 的欄位定義"""
        try:
            from strategies.base_strategy import TradeRecord, HoldingPosition
            from dataclasses import fields
            
            # 取得 TradeRecord 欄位定義
            trade_record_fields = []
            for field in fields(TradeRecord):
                trade_record_fields.append({
                    "name": field.name,
                    "type": str(field.type),
                    "default": field.default if field.default is not None else None,
                    "description": field.metadata.get("description", "") if hasattr(field, "metadata") else ""
                })
            
            # 取得 HoldingPosition 欄位定義
            holding_position_fields = []
            for field in fields(HoldingPosition):
                holding_position_fields.append({
                    "name": field.name,
                    "type": str(field.type),
                    "default": field.default if field.default is not None else None,
                    "description": field.metadata.get("description", "") if hasattr(field, "metadata") else ""
                })
            
            return {
                "success": True,
                "trade_record_fields": trade_record_fields,
                "holding_position_fields": holding_position_fields
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_complete_trade_data(request: Request):
        """取得完整的交易記錄資料，包含所有欄位"""
        try:
            data = await request.json()
            trade_records = data.get("trade_records", [])
            holding_positions = data.get("holding_positions", [])
            
            # 使用 ExcelAPI 取得完整資料
            return await ExcelAPI.get_complete_trade_data(trade_records, holding_positions)
            
        except Exception as e:
            print_log(f"get_complete_trade_data error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

 