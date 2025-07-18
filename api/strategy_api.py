#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略相關API模組
包含自定義策略的CRUD操作和測試功能
"""

import ast
import re
import pickle
import os
import tempfile
import shutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from io import BytesIO
import numpy as np

import polars as pl
import pandas as pd
from fastapi import HTTPException, Request, Form, File, UploadFile
from fastapi.responses import Response, FileResponse

from core.utils import Utils
from strategies.dynamic_strategy import DynamicStrategy
from strategies.base_strategy import HoldingPosition, TradeRecord
from core.price_utils import PriceUtils

# 程式碼格式化相關
try:
    import black
    BLACK_AVAILABLE = True
except ImportError:
    BLACK_AVAILABLE = False

def print_log(message: str):
    """日誌輸出"""
    print(f"********** strategy_api.py - {message}")

def _generate_mock_data() -> pl.DataFrame:
    """生成模擬股價資料"""
    
    dates = []
    base_price = 100.0
    current_date = datetime(2024, 1, 1)
    
    for i in range(30):
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    # 生成模擬股價資料
    prices = []
    for i, date in enumerate(dates):
        # 模擬價格變化
        change = np.random.normal(0, 0.02)  # 2% 標準差
        base_price *= (1 + change)
        
        open_price = base_price * (1 + np.random.normal(0, 0.01))
        high_price = max(open_price, base_price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, base_price) * (1 - abs(np.random.normal(0, 0.01)))
        close_price = base_price
        volume = int(np.random.normal(1000000, 200000))
        
        prices.append({
            'date': date,
            'stock_id': 'TEST',
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
    
    return pl.DataFrame(prices)

class StrategyAPI:
    """策略API類別"""
    @staticmethod
    async def get_custom_strategies(request: Request, is_confirmed: bool = None):
        """取得自定義策略列表"""        
        try:
            strategy_manager = request.app.state.strategy_manager
            
            if is_confirmed is not None:
                # 根據確認狀態篩選
                if is_confirmed:
                    strategies = strategy_manager.get_confirmed_strategies()
                else:
                    strategies = strategy_manager.get_editing_strategies()
            else:
                # 取得所有策略
                strategies = strategy_manager.get_all_strategies()
            # print_log(f"------ get_custom_strategies strategies: {strategies}")
            return {"status": "success", "strategies": strategies}
        except Exception as e:
            print_log(f"get_custom_strategies error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_strategy_template(request: Request):
        """取得策略模板"""
        try:            
            if not hasattr(request.app, 'state'):
                print_log("request.app.state 不存在")
                raise HTTPException(status_code=500, detail="應用程式狀態未初始化")
            
            if not hasattr(request.app.state, 'strategy_manager'):
                print_log("request.app.state.strategy_manager 不存在")
                raise HTTPException(status_code=500, detail="策略管理器未初始化")
            
            strategy_manager = request.app.state.strategy_manager
            if strategy_manager is None:
                print_log("strategy_manager 為 None")
                raise HTTPException(status_code=500, detail="策略管理器為空")
            
            # 取得模板類型參數
            template_type = request.query_params.get('type', 'mixed')
            print_log(f"請求的模板類型: {template_type}")
            
            # 根據類型取得對應的模板
            if template_type == 'vectorized':
                template = strategy_manager.get_vectorized_template()
                print_log("使用向量化模板")
            elif template_type == 'state_machine':
                template = strategy_manager.get_state_machine_template()
                print_log("使用狀態機模板")
            else:
                template = strategy_manager.get_strategy_template()  # 預設混合模式
                print_log("使用混合模式模板")
            
            print_log(f"成功取得策略模板，長度: {len(template)}")
            
            return {"status": "success", "template": template}
            
        except HTTPException:
            raise
        except Exception as e:
            print_log(f"get_strategy_template error: {e}")
            raise HTTPException(status_code=500, detail=f"取得策略模板失敗: {str(e)}")
    
    @staticmethod
    async def get_custom_strategy(strategy_id: str, request: Request):
        """取得特定自定義策略"""
        try:
            strategy_manager = request.app.state.strategy_manager
            
            strategy = strategy_manager.get_strategy(strategy_id)
            if strategy:
                return {"status": "success", "strategy": strategy}
            else:
                raise HTTPException(status_code=404, detail="策略不存在")
        except Exception as e:
            print_log(f"get_custom_strategy error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def create_custom_strategy(request: Request):
        """建立自定義策略"""
        try:
            data = await request.json()
            name = data.get("name")                     
            description = data.get("description", "")
            strategy_type = data.get("type", "mixed")
            editor_mode = data.get("editor_mode", "jupyter")
            jupyter_strategy_type = data.get("jupyter_strategy_type", "analysis")

            if not name:
                raise HTTPException(status_code=400, detail="策略名稱不能為空")
            
            strategy_manager = request.app.state.strategy_manager  # 取得策略管理器
            
            # 根據編輯模式和策略類型決定程式碼模板
            if editor_mode == "jupyter":
                # Jupyter 模式：根據 Jupyter 策略類型設定
                if jupyter_strategy_type == "vectorized":
                    code = "# Jupyter 向量化策略\n# 使用向量化計算處理所有資料\n# 請在 Jupyter 編輯器中實作您的策略"
                elif jupyter_strategy_type == "state_machine":
                    code = "# Jupyter 狀態機策略\n# 使用狀態機逐筆處理資料\n# 請在 Jupyter 編輯器中實作您的策略"
                elif jupyter_strategy_type == "hybrid":
                    code = "# Jupyter 混合策略\n# 結合向量化和狀態機優勢\n# 請在 Jupyter 編輯器中實作您的策略"
                elif jupyter_strategy_type == "analysis":
                    code = "# Jupyter 分析模式\n# 純資料分析，無交易邏輯\n# 請在 Jupyter 編輯器中實作您的分析"
                else:
                    code = "# Jupyter 策略\n# 請在 Jupyter 編輯器中實作您的策略"
            else:
                # 傳統模式：根據策略類型載入模板
                if strategy_type == "vectorized":
                    code = strategy_manager.get_vectorized_template()
                elif strategy_type == "state_machine":
                    code = strategy_manager.get_state_machine_template()
                elif strategy_type == "mixed":
                    code = strategy_manager.get_strategy_template()
                elif strategy_type == "empty":
                    code = "# 空白策略\n# 請在此處實作您的策略邏輯\n"
                else:
                    code = strategy_manager.get_strategy_template()
            
            try:
                # 建立策略時包含編輯模式資訊
                strategy_id = strategy_manager.create_strategy(
                    name, 
                    description, 
                    code,
                    editor_mode=editor_mode,
                    jupyter_strategy_type=jupyter_strategy_type
                )
            except Exception as e:
                print_log(f"------- ********** create_custom_strategy error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            print_log(f"------ create_custom_strategy: strategy_id {strategy_id}")
            return {"status": "success", "strategy_id": strategy_id}
        except Exception as e:
            print_log(f"create_custom_strategy error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def update_custom_strategy(strategy_id: str, request: Request):
        """更新自定義策略"""
        try:
            data = await request.json()
            name = data.get("name")
            description = data.get("description")
            code = data.get("code")
            parameters = data.get("parameters")  # 新增參數支援
            
            strategy_manager = request.app.state.strategy_manager
            success = strategy_manager.update_strategy(
                strategy_id, name, description, code, parameters
            )
            
            if success:
                return {"status": "success", "message": "策略更新成功"}
            else:
                raise HTTPException(status_code=500, detail="策略更新失敗")
        except Exception as e:
            print_log(f"update_custom_strategy error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def delete_custom_strategy(strategy_id: str, request: Request):
        """刪除自定義策略"""
        try:
            strategy_manager = request.app.state.strategy_manager
            success = strategy_manager.delete_strategy(strategy_id)
            
            if success:
                return {"status": "success", "message": "策略刪除成功"}
            else:
                raise HTTPException(status_code=500, detail="策略刪除失敗")
        except Exception as e:
            print_log(f"delete_custom_strategy error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def validate_strategy_code(request: Request):
        """驗證策略程式碼"""
        try:
            data = await request.json()
            code = data.get("code", "")
            
            strategy_manager = request.app.state.strategy_manager
            is_valid = strategy_manager.validate_strategy_code(code)
            
            if is_valid:
                return {"status": "success", "message": "程式碼驗證通過"}
            else:
                return {"status": "error", "message": "程式碼驗證失敗"}
        except Exception as e:
            print_log(f"validate_strategy_code error: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def format_strategy_code(request: Request):
        """格式化策略程式碼"""
        try:
            if not BLACK_AVAILABLE:
                return {"status": "error", "message": "程式碼格式化功能不可用，請安裝 black 模組"}
            
            data = await request.json()
            code = data.get("code", "")
            
            if not code.strip():
                return {"status": "error", "message": "程式碼不能為空"}
            
            # 自動修復 stock_data.row() 調用，確保加上 named=True 參數，且不重複
            def fix_named_true(m):
                args = m.group(1).rstrip()
                # 如果已經有 named=True 就不加
                if 'named=True' in args:
                    return f'stock_data.row({args})'
                else:
                    return f'stock_data.row({args}, named=True)'
            code = re.sub(r'stock_data\.row\(([^)]*)\)', fix_named_true, code)
            
            # 使用 black 格式化程式碼
            try:
                # 設定 black 格式化選項
                mode = black.FileMode(
                    target_versions={black.TargetVersion.PY37},
                    line_length=88,
                    string_normalization=True,
                    is_pyi=False,
                )
                
                # 格式化程式碼
                formatted_code = black.format_str(code, mode=mode)
                
                return {
                    "status": "success", 
                    "message": "程式碼格式化成功",
                    "formatted_code": formatted_code
                }
                
            except Exception as e:
                return {"status": "error", "message": f"格式化失敗: {str(e)}"}
                
        except Exception as e:
            print_log(f"format_strategy_code error: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def test_custom_strategy(
        strategy_id: str,
        code: str,
        strategy_table: str,
        excel_file: Optional[UploadFile],
        request: Request
    ):
        """測試自定義策略"""
        try:
            # 自動修復 stock_data.row() 調用，確保加上 named=True 參數，且不重複
            def fix_named_true(m):
                args = m.group(1).rstrip()
                # 如果已經有 named=True 就不加
                if 'named=True' in args:
                    return f'stock_data.row({args})'
                else:
                    return f'stock_data.row({args}, named=True)'
            code = re.sub(r'stock_data\.row\(([^)]*)\)', fix_named_true, code)
            
            # 簡單的語法檢查        
            try:
                ast.parse(code)
                validation = True
                errors = []
            except SyntaxError as e:
                validation = False
                errors = [f"語法錯誤: {str(e)}"]
            fixed_code = code
            # 檢查函數定義
            functions = []
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
            except:
                pass
            
            # 如果語法驗證通過，嘗試執行策略回測
            backtest_results = None
            if validation:
                try:
                    # 建立策略實例，使用修復後的程式碼
                    strategy_manager = request.app.state.strategy_manager
                    original_strategy = strategy_manager.get_strategy(strategy_id)  # 取得原始策略
                    
                    if original_strategy:
                        # 從 trading_config 取得基礎參數
                        from config.trading_config import TradingConfig
                        
                        # 確保有預設參數
                        default_parameters = {
                            "commission_rate": TradingConfig.COMMISSION_RATE,  # 手續費
                            "commission_discount": 0.3,  # 手續費折扣 0.3%
                            "securities_tax_rate": TradingConfig.SECURITIES_TAX_RATE,  # 當沖證交稅
                            "sstt_rate": TradingConfig.SECURITIES_TAX_RATE,  # 波段證交稅
                            "slippage_rate": TradingConfig.DEFAULT_SLIPPAGE,  # 滑價
                            "shares_per_trade": 1000,
                            "share_type": "mixed",
                            "initial_capital": 1_000_000.0
                        }
                        
                        # 合併原始策略參數和預設參數
                        strategy_parameters = original_strategy.get("parameters", {})
                        merged_parameters = {**default_parameters, **strategy_parameters}
                        
                        # 建立策略實例，傳入合併後的參數
                        strategy_instance = DynamicStrategy(
                            parameters=merged_parameters,
                            strategy_code=code,
                            strategy_name=original_strategy.get("name", "自定義策略")
                        )
                        
                        # 手動設定 custom_parameters，確保網頁編輯器新增的參數能被使用
                        if strategy_parameters:
                            strategy_instance.custom_parameters = strategy_parameters
                    else:
                        strategy_instance = None
                    
                    if strategy_instance:
                        # 優先使用快取中的資料進行回測
                        cache_manager = request.app.state.cache_manager
                        # 預設參數
                        data_type = "daily_price_adjusted"
                        stock_id = ""
                        excel_pl_df = None
                        
                        # 處理 Excel 檔案（如果有的話）
                        if excel_file:
                            try:
                                # 讀取 Excel 檔案，只取得股票代碼和日期
                                excel_content = await excel_file.read()
                                excel_df = pd.read_excel(BytesIO(excel_content))                            
                                # 將 pandas DataFrame 轉換為 polars DataFrame
                                excel_pl_df = pl.from_pandas(excel_df)
                                # 檢查必要欄位並標準化欄位名稱
                                required_columns = ['stock_id', 'date']

                                try:
                                    # 標準化欄位名稱，日期轉換為 date 物件
                                    standardized_excel_df = Utils.standardize_columns(excel_pl_df, required_columns)                                    
                                except ValueError as e:
                                    backtest_results = {
                                        "message": f"Excel 檔案格式錯誤: {str(e)}。需要包含 stock_id 和 date 欄位。"
                                    }
                                    results = {
                                        "validation": validation,
                                        "functions": functions,
                                        "errors": errors,
                                        "backtest_results": backtest_results
                                    }
                                    return {"status": "success", "results": results}
                                
                                # 使用標準化後的資料
                                excel_pl_df = standardized_excel_df
                                # 取得股票代碼
                                stock_ids = excel_pl_df['stock_id'].unique().to_list()
                                stock_ids = [s.split(' ') for s in stock_ids if s and s.strip()]  # 股票代碼 list :去除可能包含股票名稱和不必要的空格
                                # 取得日期範圍
                                dates = excel_pl_df['date'].to_list() 

                                # 使用第一個股票代碼作為主要股票
                                stock_id = stock_ids[0] if stock_ids else ""
                                # 從策略使用表格取得實際資料
                                data_provider = request.app.state.data_provider
                                # 嘗試從快取取得資料
                                test_stock_data = None
                                cache_source = "快取"

                                # 檢查是否選擇了特定的快取檔案
                                if strategy_table and strategy_table != "auto" and not strategy_table.startswith("daily_price") and not strategy_table.startswith("minute_price") and not strategy_table.startswith("technical_indicators"):
                                    # 使用指定的快取檔案
                                    cache_key = strategy_table
                                    cache_file = cache_manager._get_cache_file_path(cache_key)
                                    if os.path.exists(cache_file):
                                        try:                    
                                            # 使用 pickle 載入快取檔案
                                            with open(cache_file, 'rb') as f:
                                                cached_data = pickle.load(f)
                                            # 確保快取資料的日期欄位格式正確
                                            if cached_data['date'].dtype != pl.Date:
                                                cached_data = Utils.standardize_date_column(cached_data, 'date')
                                                
                                            # 如果是 Polars DataFrame，使用更安全的過濾方式
                                            try:
                                                stock_ids = [stock_id[0] for stock_id in stock_ids]                                        
                                                filtered_data = cached_data.filter(
                                                    (pl.col('stock_id').is_in(stock_ids))
                                                    # & (pl.col('date').is_in(dates))
                                                )
                                            except Exception as filter_error:
                                                print_log(f"使用 is_in 過濾失敗: {filter_error}")
                                                # 使用更安全的過濾方式
                                                filtered_data = cached_data.filter(
                                                    pl.col('stock_id').is_in(stock_ids)
                                                )
                                                # 然後再過濾日期
                                                if len(filtered_data) > 0:
                                                    # 將日期轉換為字串進行比較
                                                    date_strings = [str(d) for d in dates]
                                                    filtered_data = filtered_data.filter(
                                                        pl.col('date').cast(pl.Utf8).is_in(date_strings)
                                                    )

                                            if len(filtered_data) > 0:
                                                test_stock_data = filtered_data
                                                cache_source = f"快取檔案: {cache_key}"
                                                
                                        except Exception as e:
                                            print_log(f"載入快取檔案失敗: {e}")
                                    else:
                                        print_log(f"快取檔案不存在: {cache_file}")
                                # 如果快取中沒有資料，嘗試從資料提供者載入
                                if test_stock_data is None:
                                    cache_source = "API"
                                    try:
                                        # 為每個股票載入資料
                                        all_data = []
                                        for stock_id in stock_ids:
                                            # 使用預設的資料類型載入資料
                                            sample_parameters = {
                                                'stock_id': stock_id,
                                                'start_date': min(dates),
                                                'end_date': max(dates)
                                            }
                                            # 載入預設類型的資料
                                            sample_data = await data_provider.load_data("daily_price_adjusted", sample_parameters)
                                            if sample_data and len(sample_data) > 0:
                                                # 轉換為 polars DataFrame
                                                stock_df = pl.DataFrame(sample_data)
                                                # 確保日期欄位格式正確
                                                if 'date' in stock_df.columns and stock_df['date'].dtype != pl.Datetime:
                                                    stock_df = Utils.standardize_date_column(stock_df, 'date')
                                                
                                                # 篩選指定的日期，使用更安全的過濾方式
                                                try:
                                                    filtered_df = stock_df.filter(pl.col('date').is_in(dates))
                                                except Exception as filter_error:
                                                    print_log(f"使用 is_in 過濾日期失敗: {filter_error}")
                                                    # 使用更安全的過濾方式
                                                    date_strings = [str(d) for d in dates]
                                                    filtered_df = stock_df.filter(
                                                        pl.col('date').cast(pl.Utf8).is_in(date_strings)
                                                    )
                                                
                                                if len(filtered_df) > 0:
                                                    all_data.append(filtered_df)
                                                    print_log(f"載入股票 {stock_id} 資料: {len(filtered_df)} 筆")
                                        if all_data:
                                            # 合併所有股票資料
                                            test_stock_data = pl.concat(all_data)
                                            print_log(f"合併所有股票資料: {len(test_stock_data)} 筆")
                                        else:
                                            print_log(f"無法取得任何股票資料")
                                    except Exception as e:
                                        print_log(f"載入API資料失敗: {e}")
                                # 如果仍然沒有資料，使用模擬資料
                                if test_stock_data is None:
                                    cache_source = "模擬"
                                    print_log(f"無法取得資料，使用模擬資料")
                                    test_stock_data = _generate_mock_data()
                                # 確保資料格式正確
                                if test_stock_data is not None and len(test_stock_data) > 0:                                                                               
                                    # 確保價格欄位是數值格式
                                    price_columns = ['open', 'high', 'low', 'close']
                                    for col in price_columns:
                                        if col in test_stock_data.columns:
                                            if test_stock_data[col].dtype != pl.Float64:
                                                test_stock_data = test_stock_data.with_columns([
                                                    pl.col(col).cast(pl.Float64, strict=False)
                                                ])
                                                                                                
                                if len(test_stock_data) > 0:
                                    # 執行策略回測
                                    initial_capital = 1000000  # 100萬初始資金
                                    if hasattr(strategy_instance, 'run_backtest'):
                                        # 使用多執行緒處理多股票，就像回測一樣
                                        if len(stock_ids) == 1:
                                            # 單股票直接執行
                                            stock_id = stock_ids[0]
                                            # 過濾該股票的資料
                                            stock_excel_data = test_stock_data.filter(pl.col("stock_id") == stock_id)
                                            
                                            if len(stock_excel_data) == 0:
                                                backtest_results = {
                                                    "message": f"股票 {stock_id} 沒有資料"
                                                }
                                            else:
                                                strategy_instance.run_backtest(
                                                    stock_excel_data,  # 修正：使用該股票的資料
                                                    excel_pl_df,  # excel_pl_df 參數
                                                    initial_capital, 
                                                    stock_id,
                                                    f"{stock_id}股票"
                                                )
                                        else:
                                            # 多股票使用多執行緒處理
                                            print_log(f"使用多執行緒處理 {len(stock_ids)} 個股票")
                                            # 為每個股票創建獨立的策略實例
                                            strategy_instances = {}
                                            # print_log(f"-------test_custom_strategy fixed_code: {fixed_code}")
                                            for stock_id in stock_ids:
                                                strategy_instances[stock_id] = DynamicStrategy(
                                                    parameters=merged_parameters.copy(),
                                                    strategy_code=fixed_code,
                                                    strategy_name=original_strategy.get("name", "自定義策略")
                                                )
                                                
                                            # 使用線程池執行多股票回測
                                            from concurrent.futures import ThreadPoolExecutor, as_completed
                                            
                                            with ThreadPoolExecutor(max_workers=min(len(stock_ids), 4)) as executor:
                                                # 提交所有任務
                                                future_to_stock = {}
                                                
                                                for stock_id in stock_ids:
                                                    # 過濾該股票的資料
                                                    stock_excel_data = test_stock_data.filter(pl.col("stock_id") == stock_id)
                                                    
                                                    if len(stock_excel_data) == 0:
                                                        print_log(f"股票 {stock_id} 沒有資料，跳過")
                                                        continue

                                                    # 提交任務 - 修正：傳遞該股票的資料而不是全部資料
                                                    future = executor.submit(
                                                        strategy_instances[stock_id].run_backtest,
                                                        stock_excel_data,  # 修正：使用該股票的資料
                                                        excel_pl_df,  # excel_pl_df 參數
                                                        initial_capital,
                                                        stock_id,
                                                        f"股票{stock_id}"
                                                    )

                                                    future_to_stock[future] = stock_id
                                                
                                                # 收集結果
                                                for future in as_completed(future_to_stock):
                                                    stock_id = future_to_stock[future]
                                                    try:
                                                        result = future.result()
                                                    except Exception as e:
                                                        print_log(f"股票 {stock_id} 回測失敗: {e}")
                                            
                                            # 合併所有策略實例的交易記錄
                                            for stock_id, instance in strategy_instances.items():
                                                strategy_instance.trade_records.extend(instance.trade_records)
                                                
                                        # 取得回測結果
                                        backtest_result = strategy_instance.get_strategy_result(initial_capital)
                                        # print_log(f"------ 111111111111 ------ backtest_result : {backtest_result}")
                                        if backtest_result:
                                            # 準備交易記錄資料
                                            trade_records = []
                                            if hasattr(strategy_instance, 'trade_records') and strategy_instance.trade_records:
                                                for trade in strategy_instance.trade_records:
                                                    trade_records.append({
                                                        "entry_date": trade.entry_date.isoformat() if hasattr(trade.entry_date, 'isoformat') else str(trade.entry_date),
                                                        "exit_date": trade.exit_date.isoformat() if hasattr(trade.exit_date, 'isoformat') else str(trade.exit_date),
                                                        "stock_id": trade.stock_id,
                                                        "stock_name": trade.stock_name,
                                                        "entry_price": trade.entry_price,
                                                        "exit_price": trade.exit_price,
                                                        "shares": trade.shares,
                                                        "profit_loss": trade.profit_loss,
                                                        "profit_loss_rate": trade.profit_loss_rate,
                                                        "net_profit_loss": trade.net_profit_loss,
                                                        "holding_days": trade.holding_days,
                                                        "exit_reason": trade.exit_reason
                                                    })
                                            
                                            # 準備持有部位資料
                                            holding_positions = []
                                            if hasattr(strategy_instance, 'holding_positions') and strategy_instance.holding_positions:
                                                for position in strategy_instance.holding_positions:
                                                    holding_positions.append({
                                                        "entry_date": position.entry_date.isoformat() if hasattr(position.entry_date, 'isoformat') else str(position.entry_date),
                                                        "stock_id": position.stock_id,
                                                        "stock_name": position.stock_name,
                                                        "trade_direction": "買入" if position.trade_direction == 1 else "賣出",
                                                        "entry_price": position.entry_price,
                                                        "current_price": position.current_price,
                                                        "shares": position.shares,
                                                        "unrealized_profit_loss": position.unrealized_profit_loss,
                                                        "unrealized_profit_loss_rate": position.unrealized_profit_loss_rate,
                                                        "holding_days": position.holding_days,
                                                        "take_profit_price": position.take_profit_price,
                                                        "stop_loss_price": position.stop_loss_price
                                                    })
                                            
                                            # 生成圖表
                                            charts = []
                                            if trade_records and len(trade_records) > 0:
                                                try:
                                                    # 強制轉換 trade_records 為 list of dict
                                                    if isinstance(trade_records, pl.DataFrame):
                                                        trade_records = trade_records.to_dicts()
                                                    elif isinstance(trade_records, list) and len(trade_records) > 0 and hasattr(trade_records[0], 'to_dict'):
                                                        trade_records = [row.to_dict() for row in trade_records]
                                                    elif isinstance(trade_records, list) and len(trade_records) > 0 and isinstance(trade_records[0], dict):
                                                        pass  # already correct
                                                    else:
                                                        print_log(f"trade_records 型態異常: {type(trade_records)}")

                                                    from api.chart_api import ChartAPI
                                                    from fastapi import Request as FastAPIRequest
                                                    
                                                    # 生成主要圖表類型
                                                    chart_types = [
                                                        "drawdown_merge",
                                                        "heatmap", 
                                                        "monthly_return_heatmap",
                                                        "win_rate_heatmap"
                                                    ]
                                                    
                                                    for chart_type in chart_types:
                                                        try:
                                                            # 創建模擬請求
                                                            class MockChartRequest:
                                                                async def json(self):
                                                                    return {
                                                                        "chart_type": chart_type,
                                                                        "trade_records": trade_records
                                                                    }
                                                            
                                                            chart_result = await ChartAPI.generate_charts(MockChartRequest())
                                                            
                                                            if chart_result.get("success"):
                                                                chart_title = {
                                                                    "drawdown_merge": "回撤分析圖",
                                                                    "heatmap": "月損益熱力圖",
                                                                    "monthly_return_heatmap": "月收益率熱力圖",
                                                                    "win_rate_heatmap": "月勝率熱力圖"
                                                                }.get(chart_type, f"圖表 {chart_type}")
                                                                
                                                                charts.append({
                                                                    "id": chart_type,
                                                                    "title": chart_title,
                                                                    "html": chart_result.get("chart_html", ""),
                                                                    "type": chart_type
                                                                })
                                                        except Exception as chart_error:
                                                            print_log(f"生成圖表 {chart_type} 失敗: {chart_error}")
                                                except Exception as e:
                                                    print_log(f"圖表生成失敗: {e}")
                                                    
                                            backtest_results = {
                                                "total_trades": backtest_result.get("total_trades", 0),
                                                "final_capital": initial_capital + backtest_result.get("total_profit_loss", 0),
                                                "total_return": backtest_result.get("total_profit_loss_rate", 0),
                                                "win_rate": backtest_result.get("win_rate", 0),
                                                "max_drawdown": backtest_result.get("max_drawdown_rate", 0),
                                                "sharpe_ratio": backtest_result.get("sharpe_ratio", 0),
                                                "data_source": f"Excel檔案: {excel_file.filename} -> {cache_source}",
                                                "data_count": len(test_stock_data),
                                                "strategy_table": strategy_table,
                                                "stock_id": f"{len(stock_ids)}個股票: {', '.join(stock_ids[:3])}{'...' if len(stock_ids) > 3 else ''}",
                                                "data_type": "excel_upload",
                                                "date_range": f"{min(dates)} 到 {max(dates)}",
                                                "trade_records": trade_records,
                                                "holding_positions": holding_positions,
                                                "charts": charts
                                            }
                                        else:
                                            backtest_results = {
                                                "message": "無法取得回測結果"
                                            }
                            except Exception as e:
                                print_log(f"Excel 檔案處理錯誤: {e}")
                                backtest_results = {
                                    "message": f"Excel 檔案處理錯誤: {str(e)}"
                                }
                        else:
                            # 沒有 Excel 檔案，使用原來的邏輯
                            # 如果策略表格是自動選擇，使用測試資料類型
                            if strategy_table == "auto":
                                strategy_table = data_type
                            # 嘗試從快取取得指定類型的資料
                            test_stock_data = None
                            cache_source = "模擬資料"
                            # 檢查是否選擇了特定的快取檔案
                            if strategy_table and strategy_table != "auto" and not strategy_table.startswith("daily_price") and not strategy_table.startswith("minute_price") and not strategy_table.startswith("technical_indicators"):
                                # 使用指定的快取檔案
                                cache_key = strategy_table
                                cache_file = cache_manager._get_cache_file_path(cache_key)
                                if os.path.exists(cache_file):
                                    try:                    
                                        # 使用 pickle 載入快取檔案
                                        with open(cache_file, 'rb') as f:
                                            test_stock_data = pickle.load(f)
                                        cache_source = f"快取檔案: {cache_key}"
                                        print_log(f"使用快取檔案: {cache_key} ({len(test_stock_data)} 筆)")
                                    except Exception as e:
                                        print_log(f"載入快取檔案失敗: {e}")
                                else:
                                    print_log(f"快取檔案不存在: {cache_file}")
                            # 如果快取中沒有指定類型的資料，嘗試從資料提供者載入
                            if test_stock_data is None:
                                cache_source = "API"
                                data_provider = request.app.state.data_provider
                                try:
                                    # 使用指定的資料類型載入資料
                                    sample_parameters = {
                                        'stock_id': stock_id,
                                        'start_date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
                                        'end_date': datetime.now().strftime('%Y-%m-%d')
                                    }
                                    # 載入指定類型的資料
                                    sample_data = await data_provider.load_data(data_type, sample_parameters)
                                    if sample_data and len(sample_data) > 0:
                                        # 轉換為 polars DataFrame
                                        stock_df = pl.DataFrame(sample_data)
                                        # 確保日期欄位格式正確
                                        if 'date' in stock_df.columns and stock_df['date'].dtype != pl.Datetime:
                                            stock_df = Utils.standardize_date_column(stock_df, 'date')
                                        
                                        # 篩選指定的日期，使用更安全的過濾方式
                                        try:
                                            filtered_df = stock_df.filter(pl.col('date').is_in(dates))
                                        except Exception as filter_error:
                                            print_log(f"使用 is_in 過濾日期失敗: {filter_error}")
                                            # 使用更安全的過濾方式
                                            date_strings = [str(d) for d in dates]
                                            filtered_df = stock_df.filter(
                                                pl.col('date').cast(pl.Utf8).is_in(date_strings)
                                            )
                                        
                                        if len(filtered_df) > 0:
                                            all_data.append(filtered_df)
                                            print_log(f"載入股票 {stock_id} 資料: {len(filtered_df)} 筆")
                                    else:
                                        print_log(f"無法取得API資料 ({data_type})，使用模擬資料")
                                        cache_source = "模擬"
                                        # 生成模擬資料
                                        test_stock_data = _generate_mock_data()
                                except Exception as e:
                                    print_log(f"載入API資料失敗 ({data_type}): {e}")
                                    cache_source = "模擬"
                                    # 使用簡單的模擬資料作為最後備案
                                    test_stock_data = _generate_mock_data()
                            # 確保資料格式正確
                            if test_stock_data is not None and len(test_stock_data) > 0:
                                # 確保日期欄位是 datetime 格式
                                if 'date' in test_stock_data.columns:
                                    if test_stock_data['date'].dtype != pl.Datetime:
                                        test_stock_data = Utils.standardize_date_column(test_stock_data, 'date')
                                # 確保價格欄位是數值格式
                                price_columns = ['open', 'high', 'low', 'close']
                                for col in price_columns:
                                    if col in test_stock_data.columns:
                                        if test_stock_data[col].dtype != pl.Float64:
                                            test_stock_data = test_stock_data.with_columns([
                                                pl.col(col).cast(pl.Float64, strict=False)
                                            ])
                            if len(test_stock_data) > 0:
                                # 執行策略回測
                                initial_capital = 1000000  # 100萬初始資金
                                if hasattr(strategy_instance, 'run_backtest'):
                                    # 使用多執行緒處理多股票，就像回測一樣
                                    if len(stock_ids) == 1:
                                        # 單股票直接執行
                                        stock_id = stock_ids[0]
                                        # 過濾該股票的資料
                                        stock_excel_data = test_stock_data.filter(pl.col("stock_id") == stock_id)
                                        
                                        if len(stock_excel_data) == 0:
                                            backtest_results = {
                                                "message": f"股票 {stock_id} 沒有資料"
                                            }
                                        else:
                                            strategy_instance.run_backtest(
                                                stock_excel_data,  # 修正：使用該股票的資料
                                                excel_pl_df,  # excel_pl_df 參數
                                                initial_capital, 
                                                stock_id,
                                                f"{stock_id}股票"
                                            )
                                    else:
                                        # 多股票使用多執行緒處理
                                        print_log(f"使用多執行緒處理 {len(stock_ids)} 個股票")
                                        
                                        # 為每個股票創建獨立的策略實例
                                        strategy_instances = {}
                                        for stock_id in stock_ids:
                                            strategy_instances[stock_id] = DynamicStrategy(
                                                parameters=merged_parameters.copy(),
                                                strategy_code=fixed_code,
                                                strategy_name=original_strategy.get("name", "自定義策略")
                                            )
                                        
                                        # 使用線程池執行多股票回測
                                        import concurrent.futures
                                        from concurrent.futures import ThreadPoolExecutor, as_completed
                                        
                                        with ThreadPoolExecutor(max_workers=min(len(stock_ids), 4)) as executor:
                                            # 提交所有任務
                                            future_to_stock = {}
                                            for stock_id in stock_ids:
                                                # 過濾該股票的資料
                                                stock_excel_data = test_stock_data.filter(pl.col("stock_id") == stock_id)
                                                
                                                if len(stock_excel_data) == 0:
                                                    print_log(f"股票 {stock_id} 沒有資料，跳過")
                                                    continue
                                                
                                                # 提交任務 - 修正：傳遞該股票的資料而不是全部資料
                                                future = executor.submit(
                                                    strategy_instances[stock_id].run_backtest,
                                                    stock_excel_data,  # 修正：使用該股票的資料
                                                    excel_pl_df,  # excel_pl_df 參數
                                                    initial_capital,
                                                    stock_id,
                                                    f"股票{stock_id}"
                                                )
                                                future_to_stock[future] = stock_id
                                            
                                            # 收集結果
                                            for future in as_completed(future_to_stock):
                                                stock_id = future_to_stock[future]
                                                try:
                                                    result = future.result()
                                                except Exception as e:
                                                    print_log(f"股票 {stock_id} 回測失敗: {e}")
                                            
                                            # 合併所有策略實例的交易記錄
                                            for stock_id, instance in strategy_instances.items():
                                                strategy_instance.trade_records.extend(instance.trade_records)
                                        
                                        # 取得回測結果
                                        backtest_result = strategy_instance.get_strategy_result(initial_capital)
                                        
                                        if backtest_result:
                                            # 準備交易記錄資料
                                            trade_records = []
                                            if hasattr(strategy_instance, 'trade_records') and strategy_instance.trade_records:
                                                for trade in strategy_instance.trade_records:
                                                    trade_records.append({
                                                        "entry_date": trade.entry_date.isoformat() if hasattr(trade.entry_date, 'isoformat') else str(trade.entry_date),
                                                        "exit_date": trade.exit_date.isoformat() if hasattr(trade.exit_date, 'isoformat') else str(trade.exit_date),
                                                        "stock_id": trade.stock_id,
                                                        "stock_name": trade.stock_name,
                                                        "entry_price": trade.entry_price,
                                                        "exit_price": trade.exit_price,
                                                        "shares": trade.shares,
                                                        "profit_loss": trade.profit_loss,
                                                        "profit_loss_rate": trade.profit_loss_rate,
                                                        "net_profit_loss": trade.net_profit_loss,
                                                        "holding_days": trade.holding_days,
                                                        "exit_reason": trade.exit_reason
                                                    })
                                            
                                            # 準備持有部位資料
                                            holding_positions = []
                                            if hasattr(strategy_instance, 'holding_positions') and strategy_instance.holding_positions:
                                                for position in strategy_instance.holding_positions:
                                                    holding_positions.append({
                                                        "entry_date": position.entry_date.isoformat() if hasattr(position.entry_date, 'isoformat') else str(position.entry_date),
                                                        "stock_id": position.stock_id,
                                                        "stock_name": position.stock_name,
                                                        "trade_direction": "買入" if position.trade_direction == 1 else "賣出",
                                                        "entry_price": position.entry_price,
                                                        "current_price": position.current_price,
                                                        "shares": position.shares,
                                                        "unrealized_profit_loss": position.unrealized_profit_loss,
                                                        "unrealized_profit_loss_rate": position.unrealized_profit_loss_rate,
                                                        "holding_days": position.holding_days,
                                                        "take_profit_price": position.take_profit_price,
                                                        "stop_loss_price": position.stop_loss_price
                                                    })
                                            
                                            backtest_results = {
                                                "total_trades": backtest_result.get("total_trades", 0),
                                                "final_capital": initial_capital + backtest_result.get("total_profit_loss", 0),
                                                "total_return": backtest_result.get("total_profit_loss_rate", 0),
                                                "win_rate": backtest_result.get("win_rate", 0),
                                                "max_drawdown": backtest_result.get("max_drawdown_rate", 0),
                                                "sharpe_ratio": backtest_result.get("sharpe_ratio", 0),
                                                "data_source": cache_source,
                                                "data_count": len(test_stock_data) if test_stock_data is not None else 0,
                                                "strategy_table": strategy_table,
                                                "stock_id": f"{len(stock_ids)}個股票: {', '.join(stock_ids[:3])}{'...' if len(stock_ids) > 3 else ''}",
                                                "data_type": data_type,
                                                "trade_records": trade_records,
                                                "holding_positions": holding_positions
                                            }
                                        else:
                                            backtest_results = {
                                                "message": "無法建立策略實例"
                                            }
                                else:
                                    backtest_results = {
                                        "message": "無法建立策略實例"
                                    }
                    else:
                        backtest_results = {
                            "message": "無法建立策略實例"
                        }
                except Exception as e:
                    backtest_results = {
                        "message": f"策略執行錯誤: {str(e)}"
                    }
            
            results = {
                "validation": validation,
                "functions": functions,
                "errors": errors,
                "backtest_results": backtest_results
            }
            
            return {"status": "success", "results": results}
        except Exception as e:
            print_log(f"test_custom_strategy error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def test_custom_strategy_with_excel(
        strategy_id: str,
        code: str,
        strategy_table: str,
        excel_file: UploadFile,
        request: Request
    ):
        """使用 Excel 檔案指定股票代碼和日期進行策略測試"""
        try:
            print_log(f"test_custom_strategy_with_excel: strategy_id={strategy_id}")
            
            # 驗證策略程式碼
            validation = True
            functions = []
            errors = []
            
            try:
                # 自動修正 stock_data.row() 調用
                def fix_named_true(m):
                    return m.group(0) + ', named=True'
                
                # 修正 stock_data.row() 調用
                fixed_code = re.sub(
                    r'stock_data\.row\([^)]*\)(?!\s*,\s*named\s*=\s*True)',
                    fix_named_true,
                    code
                )
                
                # 編譯程式碼檢查語法
                compiled_code = {
                    'pl': pl,
                    'datetime': datetime,
                    'TradeRecord': TradeRecord,
                    'HoldingPosition': HoldingPosition,
                    'PriceUtils': PriceUtils,
                    'Utils': Utils
                }
                exec(fixed_code, compiled_code, compiled_code)
                
                # 檢測策略函數
                required_functions = ['should_entry', 'should_exit', 'calculate_entry_price', 'calculate_shares']
                for func_name in required_functions:
                    if func_name in compiled_code:
                        functions.append(func_name)
                    else:
                        errors.append(f"缺少必要函數: {func_name}")
                        
            except Exception as e:
                validation = False
                errors.append(f"語法錯誤: {str(e)}")
            
            # 處理 Excel 檔案
            backtest_results = {}
            
            if validation:
                try:
                    # 讀取 Excel 檔案，只取得股票代碼和日期
                    
                    # 讀取 Excel 檔案內容
                    excel_content = await excel_file.read()
                    excel_df = pd.read_excel(BytesIO(excel_content))
                    
                    print_log(f"Excel 檔案載入成功: {len(excel_df)} 筆資料")
                    
                    # 檢查必要欄位
                    required_columns = ['stock_id', 'date']
                    missing_columns = [col for col in required_columns if col not in excel_df.columns]
                    
                    if missing_columns:
                        backtest_results = {
                            "message": f"Excel 檔案缺少必要欄位: {', '.join(missing_columns)}。需要包含 stock_id 和 date 欄位。"
                        }
                    else:
                        # 取得股票代碼和日期範圍
                        stock_ids = excel_df['stock_id'].unique().tolist()
                        dates = excel_df['date'].tolist()
                        
                        print_log(f"從 Excel 檔案取得 {len(stock_ids)} 個股票代碼: {stock_ids}")
                        print_log(f"日期範圍: {min(dates)} 到 {max(dates)}")
                        
                        # 從策略使用表格取得實際資料
                        cache_manager = request.app.state.cache_manager
                        data_provider = request.app.state.data_provider
                        
                        # 嘗試從快取取得資料
                        test_stock_data = None
                        cache_source = "快取"
                        
                        # 檢查是否選擇了特定的快取檔案
                        if strategy_table and strategy_table != "auto" and not strategy_table.startswith("daily_price") and not strategy_table.startswith("minute_price") and not strategy_table.startswith("technical_indicators"):
                            # 使用指定的快取檔案
                            cache_key = strategy_table
                            cache_file = cache_manager._get_cache_file_path(cache_key)
                            
                            if os.path.exists(cache_file):
                                try:                    
                                    # 使用 pickle 載入快取檔案
                                    with open(cache_file, 'rb') as f:
                                        cached_data = pickle.load(f)
                                    
                                    # 篩選指定的股票和日期
                                    if isinstance(cached_data, pl.DataFrame):
                                        # 如果是 Polars DataFrame
                                        filtered_data = cached_data.filter(
                                            (pl.col('stock_id').is_in(stock_ids)) &
                                            (pl.col('date').is_in(dates))
                                        )
                                        if len(filtered_data) > 0:
                                            test_stock_data = filtered_data
                                            cache_source = f"快取檔案: {cache_key}"
                                            
                                    else:
                                        # 如果是其他格式，轉換為 Polars DataFrame
                                        df = pl.DataFrame(cached_data)
                                        filtered_data = df.filter(
                                            (pl.col('stock_id').is_in(stock_ids)) &
                                            (pl.col('date').is_in(dates))
                                        )
                                        if len(filtered_data) > 0:
                                            test_stock_data = filtered_data
                                            cache_source = f"快取檔案: {cache_key}"
                                    
                                except Exception as e:
                                    print_log(f"載入快取檔案失敗: {e}")
                            else:
                                print_log(f"快取檔案不存在: {cache_file}")
                        
                        # 如果快取中沒有資料，嘗試從資料提供者載入
                        if test_stock_data is None:
                            cache_source = "API"
                            
                            try:
                                # 為每個股票載入資料
                                all_data = []
                                for stock_id in stock_ids:
                                    # 使用預設的資料類型載入資料
                                    sample_parameters = {
                                        'stock_id': stock_id,
                                        'start_date': min(dates),
                                        'end_date': max(dates)
                                    }
                                    
                                    # 載入預設類型的資料
                                    sample_data = await data_provider.load_data("daily_price_adjusted", sample_parameters)
                                    
                                    if sample_data and len(sample_data) > 0:
                                        # 轉換為 polars DataFrame
                                        stock_df = pl.DataFrame(sample_data)
                                        # 確保日期欄位格式正確
                                        if 'date' in stock_df.columns and stock_df['date'].dtype != pl.Datetime:
                                            stock_df = Utils.standardize_date_column(stock_df, 'date')
                                        
                                        # 篩選指定的日期，使用更安全的過濾方式
                                        try:
                                            filtered_df = stock_df.filter(pl.col('date').is_in(dates))
                                        except Exception as filter_error:
                                            print_log(f"使用 is_in 過濾日期失敗: {filter_error}")
                                            # 使用更安全的過濾方式
                                            date_strings = [str(d) for d in dates]
                                            filtered_df = stock_df.filter(
                                                pl.col('date').cast(pl.Utf8).is_in(date_strings)
                                            )
                                        
                                        if len(filtered_df) > 0:
                                            all_data.append(filtered_df)
                                            print_log(f"載入股票 {stock_id} 資料: {len(filtered_df)} 筆")
                                
                                if all_data:
                                    # 合併所有股票資料
                                    test_stock_data = pl.concat(all_data)
                                    print_log(f"合併所有股票資料: {len(test_stock_data)} 筆")
                                else:
                                    print_log(f"無法取得任何股票資料")
                                    
                            except Exception as e:
                                print_log(f"載入API資料失敗: {e}")
                        
                        # 如果仍然沒有資料，使用模擬資料
                        if test_stock_data is None:
                            cache_source = "模擬"
                            print_log(f"無法取得資料，使用模擬資料")
                            test_stock_data = _generate_mock_data()
                        
                        # 確保資料格式正確
                        if test_stock_data is not None and len(test_stock_data) > 0:
                            # 確保日期欄位是 datetime 格式
                            if 'date' in test_stock_data.columns:
                                if test_stock_data['date'].dtype != pl.Datetime:
                                    test_stock_data = Utils.standardize_date_column(test_stock_data, 'date')
                            
                            # 確保價格欄位是數值格式
                            price_columns = ['open', 'high', 'low', 'close']
                            for col in price_columns:
                                if col in test_stock_data.columns:
                                    if test_stock_data[col].dtype != pl.Float64:
                                        test_stock_data = test_stock_data.with_columns([
                                            pl.col(col).cast(pl.Float64, strict=False)
                                        ])
                        
                        if len(test_stock_data) > 0:
                            # 建立策略實例
                            
                            # 取得原始策略資訊
                            strategy_manager = request.app.state.strategy_manager
                            original_strategy = strategy_manager.get_strategy(strategy_id)
                            
                            if original_strategy:
                                # 從 trading_config 取得基礎參數
                                from config.trading_config import TradingConfig
                                
                                # 設定預設參數
                                default_parameters = {
                                    "commission_rate": TradingConfig.COMMISSION_RATE,  # 手續費
                                    "commission_discount": 0.3,  # 手續費折扣 0.3%
                                    "dstt_rate": TradingConfig.SECURITIES_TAX_RATE,  # 當沖證交稅
                                    "sstt_rate": TradingConfig.SECURITIES_TAX_RATE,  # 波段證交稅
                                    "slippage_rate": TradingConfig.DEFAULT_SLIPPAGE,  # 滑價
                                    "shares_per_trade": 1000,
                                    "share_type": "mixed",
                                    "initial_capital": 1_000_000.0
                                }
                                
                                # 合併原始策略參數和預設參數
                                strategy_parameters = original_strategy.get("parameters", {})
                                merged_parameters = {**default_parameters, **strategy_parameters}
                                
                                strategy_instance = DynamicStrategy(
                                    parameters=merged_parameters,
                                    strategy_code=fixed_code,
                                    strategy_name=original_strategy.get("name", "自定義策略")
                                )
                                
                                if strategy_instance:
                                    # 執行策略回測
                                    initial_capital = 1000000  # 100萬初始資金
                                    
                                    try:
                                        # 使用多執行緒處理多股票，就像回測一樣
                                        if len(stock_ids) == 1:
                                            # 單股票直接執行
                                            stock_id = stock_ids[0]
                                            # 過濾該股票的資料
                                            stock_excel_data = test_stock_data.filter(pl.col("stock_id") == stock_id)
                                            
                                            if len(stock_excel_data) == 0:
                                                backtest_results = {
                                                    "message": f"股票 {stock_id} 沒有資料"
                                                }
                                            else:
                                                strategy_instance.run_backtest(
                                                    stock_excel_data,  # 修正：使用該股票的資料
                                                    excel_pl_df,  # excel_pl_df 參數
                                                    initial_capital, 
                                                    stock_id,
                                                    f"{stock_id}股票"
                                                )
                                        else:
                                            # 多股票使用多執行緒處理
                                            print_log(f"使用多執行緒處理 {len(stock_ids)} 個股票")
                                            
                                            # 為每個股票創建獨立的策略實例
                                            strategy_instances = {}
                                            for stock_id in stock_ids:
                                                strategy_instances[stock_id] = DynamicStrategy(
                                                    parameters=merged_parameters.copy(),
                                                    strategy_code=fixed_code,
                                                    strategy_name=original_strategy.get("name", "自定義策略")
                                                )
                                            
                                            # 使用線程池執行多股票回測
                                            import concurrent.futures
                                            from concurrent.futures import ThreadPoolExecutor, as_completed
                                            
                                            with ThreadPoolExecutor(max_workers=min(len(stock_ids), 4)) as executor:
                                                # 提交所有任務
                                                future_to_stock = {}
                                                for stock_id in stock_ids:
                                                    # 過濾該股票的資料
                                                    stock_excel_data = test_stock_data.filter(pl.col("stock_id") == stock_id)
                                                    
                                                    if len(stock_excel_data) == 0:
                                                        print_log(f"股票 {stock_id} 沒有資料，跳過")
                                                        continue
                                                    
                                                    # 提交任務 - 修正：傳遞該股票的資料而不是全部資料
                                                    future = executor.submit(
                                                        strategy_instances[stock_id].run_backtest,
                                                        stock_excel_data,  # 修正：使用該股票的資料
                                                        excel_pl_df,  # excel_pl_df 參數
                                                        initial_capital,
                                                        stock_id,
                                                        f"股票{stock_id}"
                                                    )
                                                    future_to_stock[future] = stock_id
                                                
                                                # 收集結果
                                                for future in as_completed(future_to_stock):
                                                    stock_id = future_to_stock[future]
                                                    try:
                                                        result = future.result()
                                                    except Exception as e:
                                                        print_log(f"股票 {stock_id} 回測失敗: {e}")
                                            
                                            # 合併所有策略實例的交易記錄
                                            for stock_id, instance in strategy_instances.items():
                                                strategy_instance.trade_records.extend(instance.trade_records)
                                        
                                        # 取得回測結果
                                        backtest_result = strategy_instance.get_strategy_result(initial_capital)
                                        
                                        if backtest_result:
                                            # 準備交易記錄資料
                                            trade_records = []
                                            if hasattr(strategy_instance, 'trade_records') and strategy_instance.trade_records:
                                                for trade in strategy_instance.trade_records:
                                                    trade_records.append({
                                                        "entry_date": trade.entry_date.isoformat() if hasattr(trade.entry_date, 'isoformat') else str(trade.entry_date),
                                                        "exit_date": trade.exit_date.isoformat() if hasattr(trade.exit_date, 'isoformat') else str(trade.exit_date),
                                                        "stock_id": trade.stock_id,
                                                        "stock_name": trade.stock_name,
                                                        "entry_price": trade.entry_price,
                                                        "exit_price": trade.exit_price,
                                                        "shares": trade.shares,
                                                        "profit_loss": trade.profit_loss,
                                                        "profit_loss_rate": trade.profit_loss_rate,
                                                        "net_profit_loss": trade.net_profit_loss,
                                                        "holding_days": trade.holding_days,
                                                        "exit_reason": trade.exit_reason
                                                    })
                                            
                                            # 準備持有部位資料
                                            holding_positions = []
                                            if hasattr(strategy_instance, 'holding_positions') and strategy_instance.holding_positions:
                                                for position in strategy_instance.holding_positions:
                                                    holding_positions.append({
                                                        "entry_date": position.entry_date.isoformat() if hasattr(position.entry_date, 'isoformat') else str(position.entry_date),
                                                        "stock_id": position.stock_id,
                                                        "stock_name": position.stock_name,
                                                        "trade_direction": "買入" if position.trade_direction == 1 else "賣出",
                                                        "entry_price": position.entry_price,
                                                        "current_price": position.current_price,
                                                        "shares": position.shares,
                                                        "unrealized_profit_loss": position.unrealized_profit_loss,
                                                        "unrealized_profit_loss_rate": position.unrealized_profit_loss_rate,
                                                        "holding_days": position.holding_days,
                                                        "take_profit_price": position.take_profit_price,
                                                        "stop_loss_price": position.stop_loss_price
                                                    })
                                            
                                            # 生成圖表
                                            charts = []
                                            if trade_records and len(trade_records) > 0:
                                                try:
                                                    # 強制轉換 trade_records 為 list of dict
                                                    if isinstance(trade_records, pl.DataFrame):
                                                        trade_records = trade_records.to_dicts()
                                                    elif isinstance(trade_records, list) and len(trade_records) > 0 and hasattr(trade_records[0], 'to_dict'):
                                                        trade_records = [row.to_dict() for row in trade_records]
                                                    elif isinstance(trade_records, list) and len(trade_records) > 0 and isinstance(trade_records[0], dict):
                                                        pass  # already correct
                                                    else:
                                                        print_log(f"trade_records 型態異常: {type(trade_records)}")

                                                    from api.chart_api import ChartAPI
                                                    from fastapi import Request as FastAPIRequest
                                                    
                                                    # 生成主要圖表類型
                                                    chart_types = [
                                                        "drawdown_merge",
                                                        "heatmap", 
                                                        "monthly_return_heatmap",
                                                        "win_rate_heatmap"
                                                    ]
                                                    
                                                    for chart_type in chart_types:
                                                        try:
                                                            # 創建模擬請求
                                                            class MockChartRequest:
                                                                async def json(self):
                                                                    return {
                                                                        "chart_type": chart_type,
                                                                        "trade_records": trade_records
                                                                    }
                                                            
                                                            chart_result = await ChartAPI.generate_charts(MockChartRequest())
                                                            
                                                            if chart_result.get("success"):
                                                                chart_title = {
                                                                    "drawdown_merge": "回撤分析圖",
                                                                    "heatmap": "月損益熱力圖",
                                                                    "monthly_return_heatmap": "月收益率熱力圖",
                                                                    "win_rate_heatmap": "月勝率熱力圖"
                                                                }.get(chart_type, f"圖表 {chart_type}")
                                                                
                                                                charts.append({
                                                                    "id": chart_type,
                                                                    "title": chart_title,
                                                                    "html": chart_result.get("chart_html", ""),
                                                                    "type": chart_type
                                                                })
                                                        except Exception as chart_error:
                                                            print_log(f"生成圖表 {chart_type} 失敗: {chart_error}")
                                                except Exception as e:
                                                    print_log(f"圖表生成失敗: {e}")
                                            
                                            backtest_results = {
                                                "total_trades": backtest_result.get("total_trades", 0),
                                                "final_capital": initial_capital + backtest_result.get("total_profit_loss", 0),
                                                "total_return": backtest_result.get("total_profit_loss_rate", 0),
                                                "win_rate": backtest_result.get("win_rate", 0),
                                                "max_drawdown": backtest_result.get("max_drawdown_rate", 0),
                                                "sharpe_ratio": backtest_result.get("sharpe_ratio", 0),
                                                "data_source": f"Excel檔案: {excel_file.filename} -> {cache_source}",
                                                "data_count": len(test_stock_data),
                                                "strategy_table": strategy_table,
                                                "stock_id": f"{len(stock_ids)}個股票: {', '.join(stock_ids[:3])}{'...' if len(stock_ids) > 3 else ''}",
                                                "data_type": "excel_upload",
                                                "date_range": f"{min(dates)} 到 {max(dates)}",
                                                "trade_records": trade_records,
                                                "holding_positions": holding_positions,
                                                "charts": charts
                                            }
                                        else:
                                            backtest_results = {
                                                "message": "無法取得回測結果"
                                            }
                                            
                                    except Exception as e:
                                        print_log(f"回測執行錯誤: {e}")
                                        backtest_results = {
                                            "message": f"回測執行錯誤: {str(e)}"
                                        }
                                else:
                                    backtest_results = {
                                        "message": "無法建立策略實例"
                                    }
                            else:
                                backtest_results = {
                                    "message": "找不到指定的策略"
                                }
                        
                except Exception as e:
                    print_log(f"Excel 檔案處理錯誤: {e}")
                    backtest_results = {
                        "message": f"Excel 檔案處理錯誤: {str(e)}"
                    }
            else:
                backtest_results = {
                    "message": "策略程式碼語法錯誤，無法執行回測"
                }
            
            results = {
                "validation": validation,
                "functions": functions,
                "errors": errors,
                "backtest_results": backtest_results
            }
            
            return {"status": "success", "results": results}
        except Exception as e:
            print_log(f"test_custom_strategy_with_excel error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def export_strategy(strategy_id: str, request: Request):
        """匯出策略為 .py 或 .json 檔案，並將策略設為確認版"""
        try:
            data = await request.json()
            export_format = data.get("format", "python")
            file_name = data.get("file_name", f"strategy_{strategy_id}")
            strategy_manager = request.app.state.strategy_manager
            
            if strategy_id not in strategy_manager.strategies:
                raise HTTPException(status_code=404, detail="策略不存在")
            
            strategy_info = strategy_manager.strategies[strategy_id]
            
            # 將策略設為確認版
            strategy_manager.update_strategy(
                strategy_id=strategy_id,
                is_confirmed=True
            )
            
            print_log(f"策略 {strategy_id} 已設為確認版")
            
            # 確保 exports 目錄存在
            os.makedirs("data/exports", exist_ok=True)
            
            if export_format == "python":
                file_path = f"data/exports/{file_name}.py"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(strategy_info["code"])
                return FileResponse(file_path, filename=f"{file_name}.py", media_type="text/x-python")
            else:
                file_path = f"data/exports/{file_name}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(strategy_info, f, ensure_ascii=False, indent=2)
                return FileResponse(file_path, filename=f"{file_name}.json", media_type="application/json")
        except Exception as e:
            print(f"export_strategy error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def download_excel_template():
        """下載策略測試用的 Excel 範本檔案（只包含股票代碼和日期）"""
        try:
            # 建立範例資料 - 只包含股票代碼和日期
            dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
            
            # 建立多個股票的測試資料
            data = []
            stock_ids = ['2330', '2317', '2454']  # 台積電、鴻海、聯發科
            
            for stock_id in stock_ids:
                for date in dates[::3]:  # 每3天一個資料點
                    row = {
                        'stock_id': stock_id,
                        'date': date.strftime('%Y-%m-%d')
                    }
                    data.append(row)
            
            # 建立 DataFrame
            df = pd.DataFrame(data)
            
            # 建立臨時檔案
            temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            df.to_excel(temp_file.name, index=False, sheet_name='股票清單')
            
            # 讀取檔案內容
            with open(temp_file.name, 'rb') as f:
                file_content = f.read()
            
            # 清理臨時檔案
            os.unlink(temp_file.name)
            
            # 回傳檔案
            return Response(
                content=file_content,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': 'attachment; filename="strategy_test_template.xlsx"'
                }
            )
            
        except Exception as e:
            print_log(f"download_excel_template error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_strategy_parameters(strategy_type: str):
        """取得指定策略的參數設定"""
        # 只支援自定義策略
        if not strategy_type.startswith('custom_'):
            return {"status": "error", "message": f"不支援的策略類型: {strategy_type}，只支援自定義策略"}
        
        try:
            # 從策略類型中提取策略ID
            strategy_id = strategy_type.replace('custom_', '')
            
            # 這裡可以實作自定義策略的參數取得邏輯
            # 從 trading_config 取得基礎參數
            from config.trading_config import TradingConfig
            
            # 目前返回預設的自定義策略參數設定
            strategy_parameters = {
                "commission_rate": {
                    "type": "number",
                    "label": "手續費率",
                    "default": TradingConfig.COMMISSION_RATE,
                    "min": 0,
                    "max": 0.01,
                    "step": 0.0001,
                    "description": "股票交易手續費率"
                },
                "securities_tax_rate": {
                    "type": "number",
                    "label": "證券交易稅率",
                    "default": TradingConfig.SECURITIES_TAX_RATE,
                    "min": 0,
                    "max": 0.01,
                    "step": 0.0001,
                    "description": "賣出時的證券交易稅率"
                }
            }
            
            strategy_description = "自定義策略 - 可根據策略程式碼定義的參數進行設定"
            parameter_sources = {
                "stock_source": {
                    "description": "請選擇股票代碼來源"
                },
                "price_source": {
                    "description": "請選擇股價資料來源"
                },
                "date_range": {
                    "required": True
                }
            }
            
            print_log(f"自定義策略 {strategy_type} 參數載入成功，參數數量: {len(strategy_parameters)}")
            
            return {
                "status": "success",
                "strategy_parameters": strategy_parameters,
                "strategy_description": strategy_description,
                "parameter_sources": parameter_sources
            }
        except Exception as e:
            print_log(f"載入自定義策略 {strategy_type} 參數失敗: {e}")
            return {"status": "error", "message": f"載入策略參數失敗: {str(e)}"} 