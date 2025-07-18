#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由整合模組
包含所有API路由的註冊
"""

from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, Response
from typing import Optional
from datetime import datetime
import json
import copy

from api.strategy_api import StrategyAPI
from api.cache_api import CacheAPI
from api.backtest_api import BacktestAPI
from api.chart_api import ChartAPI
from api.sample_data_api import SampleDataAPI
from api.stock_list_api import StockListAPI
from api.jupyter_api import JupyterAPI
from config.trading_config import TradingConfig

# 建立路由器
router = APIRouter()

def print_log(message: str):
    """日誌輸出"""
    print(f"********** api_routes.py - {message}")

# 策略相關API路由 - 統一使用 StrategyAPI
@router.get("/api/strategies")
async def get_strategies(request: Request):
    return await StrategyAPI.get_custom_strategies(request)

@router.get("/api/strategy/parameters")
async def get_strategy_parameters(strategy_type: str):
    return await StrategyAPI.get_strategy_parameters(strategy_type)

# 自定義策略API路由
@router.get("/api/strategies/custom")
async def get_custom_strategies(request: Request):
    return await StrategyAPI.get_custom_strategies(request)

@router.get("/api/strategies/custom/template")
async def get_strategy_template(request: Request):
    return await StrategyAPI.get_strategy_template(request)

@router.get("/api/strategies/custom/{strategy_id}")
async def get_custom_strategy(strategy_id: str, request: Request):
    return await StrategyAPI.get_custom_strategy(strategy_id, request)

@router.post("/api/strategies/custom")
async def create_custom_strategy(request: Request):
    return await StrategyAPI.create_custom_strategy(request)

@router.put("/api/strategies/custom/{strategy_id}")
async def update_custom_strategy(strategy_id: str, request: Request):
    return await StrategyAPI.update_custom_strategy(strategy_id, request)

@router.delete("/api/strategies/custom/{strategy_id}")
async def delete_custom_strategy(strategy_id: str, request: Request):
    return await StrategyAPI.delete_custom_strategy(strategy_id, request)

@router.post("/api/strategies/custom/validate")
async def validate_strategy_code(request: Request):
    return await StrategyAPI.validate_strategy_code(request)

@router.post("/api/strategies/custom/format")
async def format_strategy_code(request: Request):
    return await StrategyAPI.format_strategy_code(request)

@router.post("/api/strategies/custom/test")
async def test_custom_strategy(
    strategy_id: str = Form(...),
    code: str = Form(...),
    strategy_table: str = Form(...),
    excel_file: Optional[UploadFile] = File(None),
    request: Request = None
):
    return await StrategyAPI.test_custom_strategy(strategy_id, code, strategy_table, excel_file, request)

@router.post("/api/strategies/custom/test-excel")
async def test_custom_strategy_with_excel(
    strategy_id: str = Form(...),
    code: str = Form(...),
    strategy_table: str = Form(...),
    excel_file: UploadFile = File(...),
    request: Request = None
):
    return await StrategyAPI.test_custom_strategy_with_excel(strategy_id, code, strategy_table, excel_file, request)

@router.post("/api/strategies/custom/{strategy_id}/export")
async def export_strategy(strategy_id: str, request: Request):
    return await StrategyAPI.export_strategy(strategy_id, request)

@router.get("/api/strategies/custom/excel-template")
async def download_excel_template():
    return await StrategyAPI.download_excel_template()

# 快取管理API路由
@router.get("/api/cache/info")
async def get_cache_info():
    return await CacheAPI.get_cache_info()

@router.get("/api/cache/files")
async def get_cache_files():
    return await CacheAPI.get_cache_files()

@router.post("/api/cache/clear")
async def clear_cache(request: Request):
    return await CacheAPI.clear_cache(request)

@router.delete("/api/cache/remove/{cache_key}")
async def remove_cache_item(cache_key: str):
    return await CacheAPI.remove_cache_item(cache_key)

@router.post("/api/cache/data")
async def get_cache_data(request: Request):
    return await CacheAPI.get_cache_data_api(request)

# 回測API路由 - 直接轉發到 BacktestAPI
@router.post("/api/backtest/execute")
async def execute_backtest(
    excel_file: Optional[UploadFile] = File(None),
    strategy_id: str = Form(...),
    stock_source: str = Form(...),
    price_source: str = Form(...),
    initial_capital: float = Form(...),
    manual_stock_ids: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    start_year: Optional[str] = Form(None),
    end_year: Optional[str] = Form(None),
    request: Request = None
):
    return await BacktestAPI.execute_backtest(
        excel_file, strategy_id, stock_source, price_source, 
        initial_capital, manual_stock_ids, start_date, end_date, 
        start_year, end_year, request
    )

@router.post("/api/backtest/export-excel")
async def export_backtest_excel(request: Request):
    return await BacktestAPI.export_backtest_excel(request)

@router.post("/api/backtest/export-detailed")
async def export_detailed_records(request: Request):
    return await BacktestAPI.export_detailed_records(request)

@router.post("/api/backtest/excel/detailed-records")
async def get_detailed_records(
    excel_file: UploadFile = File(...),
    strategy_name: str = Form(...),
    dataSource: str = Form(...),
    config: str = Form(...)
):
    return await BacktestAPI.get_detailed_records(excel_file, strategy_name, dataSource, config)

@router.get("/api/excel/format")
async def get_excel_format():
    return await BacktestAPI.get_excel_format()

@router.get("/api/backtest/data-structure")
async def get_data_structure():
    return await BacktestAPI.get_data_structure()

@router.post("/api/backtest/complete-trade-data")
async def get_complete_trade_data(request: Request):
    return await BacktestAPI.get_complete_trade_data(request)

@router.post("/api/backtest/charts")
async def generate_charts(request: Request):
    return await ChartAPI.generate_charts(request)

# 範例資料API路由
@router.get("/api/sample-data/types")
async def get_sample_data_types(request: Request):
    return await SampleDataAPI.get_sample_data_types(request)

@router.post("/api/sample-data/load")
async def load_sample_data(request: Request):
    return await SampleDataAPI.load_sample_data(request)

@router.get("/api/sample-data/types/{data_type_id}")
async def get_sample_data_type(data_type_id: str, request: Request):
    return await SampleDataAPI.get_sample_data_type(data_type_id, request)

@router.post("/api/sample-data/types")
async def add_sample_data_type(request: Request):
    return await SampleDataAPI.add_sample_data_type(request)

@router.delete("/api/sample-data/types/{data_type_id}")
async def remove_sample_data_type(data_type_id: str, request: Request):
    return await SampleDataAPI.remove_sample_data_type(data_type_id, request)

# 選股列表API路由
@router.get("/api/stock-lists")
async def get_stock_lists(request: Request):
    return await StockListAPI.get_stock_lists(request)

@router.get("/api/stock-lists/{stock_list_id}")
async def get_stock_list(stock_list_id: str, request: Request):
    return await StockListAPI.get_stock_list(stock_list_id, request)

@router.post("/api/stock-lists")
async def create_stock_list(request: Request):
    return await StockListAPI.create_stock_list(request)

@router.put("/api/stock-lists/{stock_list_id}")
async def update_stock_list(stock_list_id: str, request: Request):
    return await StockListAPI.update_stock_list(stock_list_id, request)

@router.delete("/api/stock-lists/{stock_list_id}")
async def delete_stock_list(stock_list_id: str, request: Request):
    return await StockListAPI.delete_stock_list(stock_list_id, request)

@router.post("/api/stock-lists/import-excel")
async def import_stocks_from_excel(file: UploadFile = File(...), request: Request = None):
    return await StockListAPI.import_stocks_from_excel(file, request)

@router.post("/api/stock-lists/apply-conditions")
async def apply_stock_conditions(request: Request):
    return await StockListAPI.apply_stock_conditions(request)

@router.post("/api/stock-lists/export-to-strategy")
async def export_stock_list_to_strategy(request: Request):
    return await StockListAPI.export_stock_list_to_strategy(request)

# 其他API路由
@router.get("/api/trades/recent")
async def get_recent_trades(limit: int = 10):
    """取得最近的交易記錄"""
    # 這裡應該從資料庫或檔案系統取得實際的交易記錄
    # 目前返回模擬資料
    return {
        "status": "success",
        "trades": []
    }

@router.get("/api/system/status")
async def get_system_status():
    """取得系統狀態"""
    try:
        # 取得自動下單狀態
        auto_status = auto_trading_manager.get_status()
        
        return {
            "status": "success",
            "status_info": {
                "auto_trading_status": auto_status['auto_trading_status'],
                "active_strategies": auto_status['active_strategies'],
                "total_strategies": auto_status['total_strategies'],
                "system_time": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print_log(f"取得系統狀態失敗: {e}")
        return {
            "status": "success",
            "status_info": {
                "auto_trading_status": "stopped",
                "active_strategies": 0,
                "total_strategies": 0,
                "system_time": datetime.now().isoformat()
            }
        }

# 自動下單管理器
class AutoTradingManager:
    """自動下單管理器"""
    
    def __init__(self):
        self.active_trades = {}  # 儲存活躍的交易任務
        self.strategy_instances = {}  # 儲存策略實例
    
    def start_strategy(self, strategy_id: str, strategy_instance, broker: str, capital: float, parameters: dict):
        """啟動策略的自動下單"""
        try:
            print_log(f"啟動策略自動下單: {strategy_id}")
            
            # 儲存策略實例
            self.strategy_instances[strategy_id] = {
                'instance': strategy_instance,
                'broker': broker,
                'capital': capital,
                'parameters': parameters,
                'status': 'running',
                'start_time': datetime.now()
            }
            
            # 這裡應該實作實際的自動下單邏輯
            # 例如：
            # 1. 設定定時任務，定期執行策略
            # 2. 連接券商API，取得即時股價
            # 3. 根據策略邏輯產生交易信號
            # 4. 執行實際的下單操作
            
            print_log(f"策略 {strategy_id} 自動下單已啟動")
            return True
            
        except Exception as e:
            print_log(f"啟動策略自動下單失敗: {e}")
            return False
    
    def stop_strategy(self, strategy_id: str):
        """停止策略的自動下單"""
        try:
            if strategy_id in self.strategy_instances:
                self.strategy_instances[strategy_id]['status'] = 'stopped'
                print_log(f"策略 {strategy_id} 自動下單已停止")
                return True
            return False
        except Exception as e:
            print_log(f"停止策略自動下單失敗: {e}")
            return False
    
    def get_status(self):
        """取得自動下單狀態"""
        active_count = sum(1 for info in self.strategy_instances.values() if info['status'] == 'running')
        return {
            'auto_trading_status': 'running' if active_count > 0 else 'stopped',
            'active_strategies': active_count,
            'total_strategies': len(self.strategy_instances)
        }

# 全域自動下單管理器
auto_trading_manager = AutoTradingManager()

@router.post("/api/auto-trading/start")
async def start_auto_trading(
    strategy: str = Form(...),
    parameters: str = Form(...),
    broker: str = Form(...),
    capital: float = Form(...),
    request: Request = None
):
    """啟動自動下單"""
    try:
        print_log(f"啟動自動下單 - 策略: {strategy}, 券商: {broker}, 資金: {capital}")
        
        # 解析策略參數
        try:
            strategy_params = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="策略參數格式錯誤")
        
        # 檢查是否為自定義策略
        if not strategy.startswith('custom_'):
            raise HTTPException(status_code=400, detail="只支援自定義策略")
        
        # 從策略ID中提取實際ID
        strategy_id = strategy.replace('custom_', '')
        
        # 取得策略管理器
        strategy_manager = request.app.state.strategy_manager if hasattr(request.app.state, 'strategy_manager') else None
        if strategy_manager is None:
            raise HTTPException(status_code=500, detail="策略管理器未初始化")
        
        # 檢查策略是否存在
        strategy_data = strategy_manager.get_strategy(strategy_id)
        if not strategy_data:
            raise HTTPException(status_code=404, detail=f"策略不存在: {strategy_id}")
        
        # 建立策略實例
        from strategies.dynamic_strategy import DynamicStrategy
        strategy_instance = DynamicStrategy(
            parameters=copy.deepcopy(strategy_params),
            strategy_code=strategy_data['code'],
            strategy_name=strategy_data['name']
        )
        
        # 使用自動下單管理器啟動策略
        success = auto_trading_manager.start_strategy(
            strategy_id, strategy_instance, broker, capital, strategy_params
        )
        
        if success:
            print_log(f"自動下單啟動成功 - 策略: {strategy_data['name']}")
            return {
                "status": "success",
                "message": f"自動下單已啟動 - 策略: {strategy_data['name']}",
                "strategy_info": {
                    "id": strategy_id,
                    "name": strategy_data['name'],
                    "broker": broker,
                    "capital": capital,
                    "parameters": strategy_params
                }
            }
        else:
            raise HTTPException(status_code=500, detail="啟動自動下單失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        print_log(f"啟動自動下單失敗: {e}")
        raise HTTPException(status_code=500, detail=f"啟動自動下單失敗: {str(e)}")

@router.post("/api/auto-trading/stop")
async def stop_auto_trading(request: Request = None):
    """停止自動下單"""
    try:
        # 停止所有活躍的策略
        stopped_count = 0
        for strategy_id in list(auto_trading_manager.strategy_instances.keys()):
            if auto_trading_manager.stop_strategy(strategy_id):
                stopped_count += 1
        
        return {
            "status": "success",
            "message": f"自動下單已停止，共停止 {stopped_count} 個策略"
        }
    except Exception as e:
        print_log(f"停止自動下單失敗: {e}")
        raise HTTPException(status_code=500, detail=f"停止自動下單失敗: {str(e)}")

@router.get("/api/brokers")
async def get_brokers():
    """取得支援的券商列表"""
    return {
        "status": "success",
        "brokers": [
            {"id": "fugle", "name": "富果證券", "description": "富果證券API"},
            {"id": "yuantafutures", "name": "元大期貨", "description": "元大期貨API"},
            {"id": "kgi", "name": "凱基證券", "description": "凱基證券API"}
        ]
    }

# Jupyter 風格程式碼執行 API 路由
@router.post("/api/jupyter/execute")
async def execute_jupyter_code(request: Request):
    """執行 Jupyter 風格的程式碼"""
    print_log(f"執行 Jupyter 風格的程式碼")
    return await JupyterAPI.execute_code(request)

@router.post("/api/jupyter/execute-strategy")
async def execute_strategy_cell(request: Request):
    """執行策略相關的程式碼單元格"""
    return await JupyterAPI.execute_strategy_cell(request)

@router.post("/api/jupyter/sample-data")
async def get_jupyter_sample_data(request: Request):
    """取得 Jupyter 範例資料"""
    return await JupyterAPI.get_sample_data(request)

@router.post("/api/jupyter/analyze-strategy")
async def analyze_strategy_type(request: Request):
    """分析策略類型（狀態機/向量化/混合式）"""
    return await JupyterAPI.analyze_strategy_type(request)

# Jupyter Notebook 儲存和載入 API
@router.put("/api/jupyter/notebook/{strategy_id}")
async def save_jupyter_notebook(strategy_id: str, request: Request):
    return await JupyterAPI.save_notebook(strategy_id, request)

@router.get("/api/jupyter/notebook/{strategy_id}")
async def load_jupyter_notebook(strategy_id: str, request: Request):
    return await JupyterAPI.load_notebook(strategy_id, request)

# Jupyter 策略回測 API
@router.post("/api/jupyter/backtest")
async def execute_jupyter_backtest(request: Request):
    return await JupyterAPI.execute_strategy_backtest(request)

@router.post("/api/jupyter/strategy-backtest")
async def execute_jupyter_strategy_backtest(request: Request):
    return await JupyterAPI.execute_jupyter_strategy_backtest(request)

# Jupyter 清除全域變數 API
@router.post("/api/jupyter/clear-variables")
async def clear_jupyter_variables(request: Request):
    JupyterAPI.clear_global_variables()
    return {"status": "success", "message": "全域變數已清除"}

# Jupyter 獲取全域變數 API
@router.get("/api/jupyter/variables")
async def get_jupyter_variables(request: Request):
    return JupyterAPI.get_global_variables()