#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jupyter 風格程式碼執行 API 模組
提供程式碼執行、即時輸出、圖表生成等功能
"""

import ast
import re
import json
import base64
import io
import sys
import os
import pickle
import tempfile
from io import BytesIO
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from contextlib import redirect_stdout, redirect_stderr
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端
import seaborn as sns
from io import StringIO
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "png"

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from core.utils import Utils
from core.price_utils import PriceUtils
from core.technical_indicators import generate_indicators
from strategies.base_strategy import TradeRecord, HoldingPosition
from strategies.dynamic_strategy import DynamicStrategy
from config.trading_config import TradingConfig

def print_log(message: str):
    """日誌輸出"""
    print(f"********** jupyter_api.py - {message}")

class JupyterAPI:
    """Jupyter 風格程式碼執行 API"""
    
    # 使用檔案系統來實現跨進程變數共享
    _variables_file = os.path.join(tempfile.gettempdir(), "jupyter_variables.pkl")
    _variables_lock_file = os.path.join(tempfile.gettempdir(), "jupyter_variables.lock")
    
    # 新增：記憶體快取，避免重複載入
    _variables_cache = {}
    _cache_timestamp = 0
    
    @staticmethod
    def _save_variables(variables: Dict[str, Any]):
        """將變數儲存到檔案"""
        print_log(f"_save_variables")
        try:
            os.makedirs(os.path.dirname(JupyterAPI._variables_file), exist_ok=True)
            processed_variables = {}
            for key, value in variables.items():
                if isinstance(value, pl.DataFrame):
                    try:
                        if len(value) > 10000:
                            temp_file = os.path.join(tempfile.gettempdir(), f"temp_df_{key}.parquet")
                            value.write_parquet(temp_file)
                            processed_variables[key] = {
                                '_type': 'polars_dataframe_parquet',
                                'file_path': temp_file,
                                'shape': value.shape,
                                'columns': value.columns
                            }
                        else:
                            processed_variables[key] = {
                                '_type': 'polars_dataframe',
                                'data': value.to_dicts(),
                                'schema': value.schema,
                                'shape': value.shape
                            }                            
                    except Exception as df_error:
                        print_log(f"處理 DataFrame 變數 {key} 失敗: {df_error}")
                        try:
                            processed_variables[key] = {
                                '_type': 'polars_dataframe_dict',
                                'data': value.to_dict(as_series=False),
                                'columns': value.columns,
                                'shape': value.shape
                            }
                        except:
                            print_log(f"無法處理 DataFrame 變數: {key}")
                elif isinstance(value, pl.Series):
                    try:
                        processed_variables[key] = {
                            '_type': 'polars_series',
                            'data': value.to_list(),
                            'dtype': str(value.dtype),
                            'name': value.name
                        }
                    except Exception as series_error:
                        print_log(f"處理 Series 變數 {key} 失敗: {series_error}")
                else:
                    processed_variables[key] = value
            temp_file = JupyterAPI._variables_file + ".tmp"
            with open(temp_file, 'wb') as f:
                pickle.dump(processed_variables, f)
            if os.path.exists(JupyterAPI._variables_file):
                os.remove(JupyterAPI._variables_file)
            os.rename(temp_file, JupyterAPI._variables_file)
            
            # 更新快取
            JupyterAPI._variables_cache = variables
            JupyterAPI._cache_timestamp = os.path.getmtime(JupyterAPI._variables_file) if os.path.exists(JupyterAPI._variables_file) else 0
            
        except Exception as e:
            print_log(f"儲存變數失敗: {e}")
    
    @staticmethod
    def _load_variables() -> Dict[str, Any]:
        """從檔案載入變數（使用快取優化）"""
        print_log(f"_load_variables")
        try:
            if not os.path.exists(JupyterAPI._variables_file):
                return {}
            
            # 檢查檔案是否被修改
            current_timestamp = os.path.getmtime(JupyterAPI._variables_file)
            if (JupyterAPI._variables_cache and 
                current_timestamp == JupyterAPI._cache_timestamp):
                # 未修改，直接返回快取
                return JupyterAPI._variables_cache.copy()
            
            # 檔案已修改，重新載入
            with open(JupyterAPI._variables_file, 'rb') as f:
                processed_variables = pickle.load(f)
            restored_variables = {}
            for key, value in processed_variables.items():                
                if isinstance(value, dict) and '_type' in value:
                    if value['_type'] == 'polars_dataframe':
                        try:
                            restored_variables[key] = pl.DataFrame(value['data'], schema=value['schema'])
                        except Exception as df_error:
                            print_log(f"還原 DataFrame 變數 {key} 失敗: {df_error}")
                    elif value['_type'] == 'polars_dataframe_parquet':
                        try:
                            restored_variables[key] = pl.read_parquet(value['file_path'])
                        except Exception as df_error:
                            print_log(f"還原 DataFrame 變數 (parquet) {key} 失敗: {df_error}")
                    elif value['_type'] == 'polars_dataframe_dict':
                        try:
                            restored_variables[key] = pl.DataFrame(value['data'])
                        except Exception as df_error:
                            print_log(f"還原 DataFrame 變數 (字典格式) {key} 失敗: {df_error}")
                    elif value['_type'] == 'polars_series':
                        try:
                            restored_variables[key] = pl.Series(value['name'], value['data'], dtype=value['dtype'])
                        except Exception as series_error:
                            print_log(f"還原 Series 變數 {key} 失敗: {series_error}")
                    else:
                        restored_variables[key] = value
                else:
                    restored_variables[key] = value
            
            # 更新快取
            JupyterAPI._variables_cache = restored_variables
            JupyterAPI._cache_timestamp = current_timestamp
            
            print_log(f"載入變數完成（共 {len(restored_variables)} 個）")
            return restored_variables
        except Exception as e:
            print_log(f"載入變數失敗: {e}")
        return {}
    
    @staticmethod
    async def execute_code(request: Request):
        """執行程式碼並返回結果"""
        print_log(f"execute_code")
        try:
            form = await request.form()
            
            code = form.get("code", "")
            cell_id = form.get("cell_id", "cell_1")
            strategy_table = form.get("strategy_table")
            excel_file = form.get("excel_file")  # 這是 UploadFile 物件
            parameters_json = form.get("parameters", "{}")

            # 解析策略參數
            try:
                parameters = json.loads(parameters_json) if parameters_json else {}
            except json.JSONDecodeError:
                parameters = {}
    
            # 從檔案載入全域變數（使用快取）
            global_variables = JupyterAPI._load_variables()
            
            # 建立執行環境，先注入所有全域變數
            execution_env = JupyterAPI._create_execution_environment()
            execution_env.update(global_variables)  # 更新執行環境

            # Excel 優先，只在第一次載入或 stock_df 不存在時載入
            if excel_file is not None and hasattr(excel_file, 'read'):
                # 檢查執行環境中是否已經有 stock_df
                if 'stock_df' not in execution_env:
                    excel_content = await excel_file.read()
                    excel_df = pl.read_excel(BytesIO(excel_content))
                    excel_df = Utils.standardize_columns(excel_df, ['stock_id', 'date'])
                    execution_env['stock_df'] = excel_df
            
            # 快取資料，只在第一次載入或 df 不存在時載入
            cache_manager = request.app.state.cache_manager
            if strategy_table and strategy_table != "auto" and cache_manager:
                cache_key = strategy_table
                cache_file = cache_manager._get_cache_file_path(cache_key)
                if os.path.exists(cache_file):
                    # 檢查執行環境中是否已經有 df
                    if 'df' not in execution_env:
                        with open(cache_file, 'rb') as f:
                            cached_data = pickle.load(f)
                            cached_data = Utils.standardize_columns(cached_data, ['stock_id', 'date'])
                            execution_env['df'] = cached_data
                            
            # 參數注入
            if parameters:
                new_parameters = {}
                for key, config in parameters.items():
                    if isinstance(config, dict) and 'default' in config:
                        new_parameters[key] = config['default']
                execution_env['parameters'] = new_parameters

            if not code.strip():                
                return {
                    "status": "success",
                    "cell_id": cell_id,
                    "outputs": [],
                    "execution_count": 1
                }

            # 執行程式碼並捕獲輸出
            outputs = JupyterAPI._execute_code_with_outputs(code, execution_env)            
            
            # 更新全域變數，保存執行後的變數到檔案
            JupyterAPI._update_global_variables(execution_env)
            
            # 直接從快取檢查 DataFrame 變數，避免重複載入
            df_variables = [k for k, v in JupyterAPI._variables_cache.items() if isinstance(v, pl.DataFrame)]
            
            return {
                "status": "success",
                "cell_id": cell_id,
                "outputs": outputs,
                "execution_count": 1,
                "execution_time": datetime.now().isoformat()
            }
        except Exception as e:
            print_log(f"execute_code error: {e}")
            return {
                "status": "error",
                "cell_id": cell_id,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    @staticmethod
    async def execute_strategy_cell(request: Request):
        """執行策略相關的程式碼單元格"""
        print_log(f"execute_strategy_cell")
        try:
            data = await request.json()
            code = data.get("code", "")
            cell_id = data.get("cell_id", "strategy_cell_1")
            strategy_context = data.get("strategy_context", {})
            
            if not code.strip():
                return {
                    "status": "success",
                    "cell_id": cell_id,
                    "outputs": [],
                    "execution_count": 1
                }
            
            # 建立策略執行環境
            execution_env = JupyterAPI._create_strategy_environment(strategy_context)
            
            # 執行程式碼並捕獲輸出
            outputs = JupyterAPI._execute_code_with_outputs(code, execution_env)
            
            return {
                "status": "success",
                "cell_id": cell_id,
                "outputs": outputs,
                "execution_count": 1,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print_log(f"execute_strategy_cell error: {e}")
            return {
                "status": "error",
                "cell_id": cell_id,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    @staticmethod
    async def get_sample_data(request: Request):
        """取得範例資料"""
        print_log(f"get_sample_data")
        try:
            data = await request.json()
            data_type = data.get("data_type", "stock_data")
            
            sample_data = JupyterAPI._generate_sample_data(data_type)
            
            return {
                "status": "success",
                "data": sample_data,
                "data_type": data_type
            }
            
        except Exception as e:
            print_log(f"get_sample_data error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    async def analyze_strategy_type(request: Request):
        """分析策略類型（狀態機/向量化/混合式）"""
        print_log(f"analyze_strategy_type")
        try:
            data = await request.json()
            code = data.get("code", "")
            
            if not code.strip():
                return {
                    "status": "success",
                    "strategy_type": "unknown",
                    "analysis": {
                        "has_should_entry": False,
                        "has_calculate_entry_signals": False,
                        "functions_found": [],
                        "description": "無程式碼可分析"
                    }
                }
            
            # 分析程式碼中的函數
            analysis = JupyterAPI._analyze_strategy_functions(code)
            
            # 根據分析結果判斷策略類型
            strategy_type = JupyterAPI._determine_strategy_type(analysis)
            
            return {
                "status": "success",
                "strategy_type": strategy_type,
                "analysis": analysis
            }
            
        except Exception as e:
            print_log(f"analyze_strategy_type error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    @staticmethod
    def _create_execution_environment() -> Dict[str, Any]:
        """建立程式碼執行環境"""
        print_log(f"_create_execution_environment")
        env = {
            # 基本 Python 模組
            'np': np,
            'pl': pl,
            'plt': plt,
            'sns': sns,
            'go': go,
            'px': px,
            'make_subplots': make_subplots,
            
            # 策略工具類別
            'Utils': Utils,
            'PriceUtils': PriceUtils,
            'TradeRecord': TradeRecord,
            'HoldingPosition': HoldingPosition,
            'generate_indicators': generate_indicators,
            'DynamicStrategy': DynamicStrategy,
            'TradingConfig': TradingConfig,
            
            # 常用函數
            'print': print,
            'len': len,
            'range': range,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'type': type,
            'isinstance': isinstance,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            'dir': dir,
            'help': help,
            
            # 數學函數
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            
            # 日期時間
            'datetime': datetime,
            
            # 圖表設定
            'plt_style': 'default',
            'sns_style': 'whitegrid'
        }
        
        # 設定 matplotlib 中文字體
        try:
            plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass
        
        return env
    
    @staticmethod
    def _update_global_variables(execution_env: Dict[str, Any]):
        """更新全域變數，保存執行後的變數到檔案"""
        print_log(f"_update_global_variables")
        # 要保存的變數類型
        saveable_types = (
            pl.DataFrame, pl.Series, np.ndarray, 
            list, dict, tuple, set, 
            int, float, str, bool
        )
        
        # 使用快取避免重複載入
        global_variables = JupyterAPI._load_variables()
        
        # 過濾出需要保存的變數
        new_variables = {}
        for key, value in execution_env.items():
            # 跳過內建模組和函數
            if (key.startswith('_') or callable(value) or 
                key in ['print', 'len', 'range', 'list', 'dict', 'tuple', 'set', 'str', 'int', 'float', 'bool', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'dir', 'help', 'abs', 'round', 'min', 'max', 'sum', 'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter', 'datetime', 'plt_style', 'sns_style']):
                continue
            
            # 只保存可序列化的變數
            if isinstance(value, saveable_types):
                new_variables[key] = value
        
        # 合併變數
        global_variables.update(new_variables)
        
        # 儲存到檔案
        JupyterAPI._save_variables(global_variables)
    
    @staticmethod
    def clear_global_variables():
        """清除全域變數"""
        print_log(f"clear_global_variables")
        try:
            if os.path.exists(JupyterAPI._variables_file):
                os.remove(JupyterAPI._variables_file)
            
            # 清理臨時 parquet 檔案
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.startswith("temp_df_") and file.endswith(".parquet"):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                    except:
                        pass
            
            # 清除記憶體快取
            JupyterAPI._variables_cache = {}
            JupyterAPI._cache_timestamp = 0
            
        except Exception as e:
            print_log(f"清除全域變數失敗: {e}")
    
    @staticmethod
    def get_global_variables():
        """獲取當前全域變數列表"""
        print_log(f"get_global_variables")
        try:
            # 優先使用快取，如果快取為空才載入
            if not JupyterAPI._variables_cache:
                JupyterAPI._load_variables()
            
            variables = JupyterAPI._variables_cache
            return {
                "status": "success",
                "variables": list(variables.keys()),
                "count": len(variables),
                "file_path": JupyterAPI._variables_file
            }
        except Exception as e:
            print_log(f"獲取全域變數失敗: {e}")
            return {
                "status": "error",
                "error": str(e),
                "variables": [],
                "count": 0
            }
    
    @staticmethod
    def _create_strategy_environment(strategy_context: Dict[str, Any]) -> Dict[str, Any]:
        """建立策略執行環境"""
        print_log(f"_create_strategy_environment")
        env = JupyterAPI._create_execution_environment()
        
        # 添加策略相關的變數
        if 'stock_data' in strategy_context:
            env['stock_data'] = strategy_context['stock_data']
        if 'parameters' in strategy_context:
            env['parameters'] = strategy_context['parameters']
        if 'current_position' in strategy_context:
            env['current_position'] = strategy_context['current_position']
        if 'trade_history' in strategy_context:
            env['trade_history'] = strategy_context['trade_history']
        
        return env
    
    @staticmethod
    def _execute_code_with_outputs(code: str, env: Dict[str, Any]) -> List[Dict[str, Any]]:
        """執行程式碼並捕獲所有輸出"""
        print_log(f"_execute_code_with_outputs")
        outputs = []
        
        # 捕獲標準輸出
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # 執行程式碼
                exec_result = exec(code, env)
                
                # 檢查是否有最後的表達式結果
                last_expr = None
                try:
                    # 嘗試解析最後一行作為表達式
                    lines = code.strip().split('\n')
                    if lines:
                        last_line = lines[-1].strip()
                        if last_line and not last_line.startswith('#') and not last_line.endswith(':'):
                            # 嘗試執行最後一行作為表達式
                            last_expr = eval(last_line, env)
                except:
                    pass
                
                # 處理標準輸出
                stdout_content = stdout_capture.getvalue()
                if stdout_content:
                    outputs.append({
                        "output_type": "stream",
                        "name": "stdout",
                        "text": stdout_content.split('\n')
                    })
                
                # 處理標準錯誤
                stderr_content = stderr_capture.getvalue()
                if stderr_content:
                    outputs.append({
                        "output_type": "stream",
                        "name": "stderr",
                        "text": stderr_content.split('\n')
                    })
                
                # 處理最後表達式結果
                if last_expr is not None:
                    output = JupyterAPI._format_output(last_expr)
                    if output:
                        outputs.append(output)
                
                # 檢查是否有圖表輸出
                if 'plt' in env and plt.get_fignums():
                    for fig_num in plt.get_fignums():
                        fig = plt.figure(fig_num)
                        output = JupyterAPI._figure_to_output(fig)
                        if output:
                            outputs.append(output)
                        plt.close(fig)
                
        except Exception as e:
            # 處理執行錯誤
            error_output = {
                "output_type": "error",
                "ename": type(e).__name__,
                "evalue": str(e),
                "traceback": traceback.format_exc().split('\n')
            }
            outputs.append(error_output)
        
        return outputs
    
    @staticmethod
    def _format_output(obj: Any) -> Optional[Dict[str, Any]]:
        """格式化輸出對象"""
        print_log(f"_format_output")
        if obj is None:
            return None
        
        # 處理 Polars DataFrame
        if isinstance(obj, pl.DataFrame):
            # 對於大型 DataFrame，只顯示前幾行
            if len(obj) > 1000:
                display_df = obj.head(10)
                return {
                    "output_type": "display_data",
                    "data": {
                        "text/html": f"<div><p><strong>顯示前 10 行（共 {len(obj)} 行）</strong></p>{display_df.to_html()}</div>",
                        "text/plain": f"顯示前 10 行（共 {len(obj)} 行）\n{display_df.to_string()}"
                    },
                    "metadata": {
                        "shape": obj.shape,
                        "columns": obj.columns,
                        "dtypes": obj.dtypes,
                        "truncated": True
                    }
                }
            else:
                return {
                    "output_type": "display_data",
                    "data": {
                        "text/html": obj.to_html(),
                        "text/plain": obj.to_string()
                    },
                    "metadata": {
                        "shape": obj.shape,
                        "columns": obj.columns,
                        "dtypes": obj.dtypes
                    }
                }
        
        # 處理 Series
        elif isinstance(obj, pl.Series):
            return {
                "output_type": "display_data",
                "data": {
                    "text/html": obj.to_frame().to_html(),
                    "text/plain": obj.to_string()
                },
                "metadata": {
                    "length": len(obj),
                    "dtype": str(obj.dtype)
                }
            }
        
        # 處理 numpy 數組
        elif isinstance(obj, np.ndarray):
            return {
                "output_type": "display_data",
                "data": {
                    "text/plain": str(obj),
                    "text/html": f"<pre>{str(obj)}</pre>"
                },
                "metadata": {
                    "shape": obj.shape,
                    "dtype": str(obj.dtype)
                }
            }
        
        # 處理字典
        elif isinstance(obj, dict):
            return {
                "output_type": "display_data",
                "data": {
                    "text/plain": str(obj),
                    "text/html": f"<pre>{json.dumps(obj, indent=2, ensure_ascii=False)}</pre>"
                }
            }
        
        # 處理列表
        elif isinstance(obj, list):
            return {
                "output_type": "display_data",
                "data": {
                    "text/plain": str(obj),
                    "text/html": f"<pre>{str(obj)}</pre>"
                },
                "metadata": {
                    "length": len(obj)
                }
            }
        
        # 處理基本類型
        else:
            return {
                "output_type": "execute_result",
                "data": {
                    "text/plain": str(obj)
                },
                "execution_count": 1
            }
    
    @staticmethod
    def _figure_to_output(fig) -> Optional[Dict[str, Any]]:
        """將 matplotlib 圖表轉換為輸出格式"""
        print_log(f"_figure_to_output")
        try:
            # 將圖表轉換為 base64 編碼的 PNG
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                "output_type": "display_data",
                "data": {
                    "image/png": img_base64,
                    "text/plain": "<matplotlib.figure.Figure>"
                },
                "metadata": {
                    "image/png": {
                        "width": fig.get_figwidth() * 100,
                        "height": fig.get_figheight() * 100
                    }
                }
            }
        except Exception as e:
            print_log(f"Error converting figure to output: {e}")
            return None
    
    @staticmethod
    def _analyze_strategy_functions(code: str) -> Dict[str, Any]:
        """分析策略程式碼中的函數"""
        print_log(f"_analyze_strategy_functions")
        try:
            # 解析程式碼
            tree = ast.parse(code)
            
            functions_found = []
            has_should_entry = False
            has_calculate_entry_signals = False
            
            # 遍歷 AST 尋找函數定義
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    functions_found.append(func_name)
                    
                    # 檢查關鍵函數
                    if func_name == 'should_entry':
                        has_should_entry = True
                    elif func_name == 'calculate_entry_signals':
                        has_calculate_entry_signals = True
            
            # 也檢查類別中的方法
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            func_name = item.name
                            functions_found.append(f"{node.name}.{func_name}")
                            
                            # 檢查關鍵函數
                            if func_name == 'should_entry':
                                has_should_entry = True
                            elif func_name == 'calculate_entry_signals':
                                has_calculate_entry_signals = True
            
            return {
                "has_should_entry": has_should_entry,
                "has_calculate_entry_signals": has_calculate_entry_signals,
                "functions_found": functions_found,
                "description": f"找到 {len(functions_found)} 個函數"
            }
            
        except Exception as e:
            return {
                "has_should_entry": False,
                "has_calculate_entry_signals": False,
                "functions_found": [],
                "description": f"分析失敗: {str(e)}"
            }
    
    @staticmethod
    def _determine_strategy_type(analysis: Dict[str, Any]) -> str:
        """根據分析結果判斷策略類型"""
        print_log(f"_determine_strategy_type")
        has_should_entry = analysis.get("has_should_entry", False)
        has_calculate_entry_signals = analysis.get("has_calculate_entry_signals", False)
        
        if has_should_entry and has_calculate_entry_signals:
            return "mixed"
        elif has_should_entry:
            return "state_machine"
        elif has_calculate_entry_signals:
            return "vectorized"
        else:
            return "unknown"
    
    @staticmethod
    def _generate_sample_data(data_type: str) -> Any:
        """生成範例資料"""
        print_log(f"_generate_sample_data")
        if data_type == "stock_data":
            # 生成股票資料
            import numpy as np
            import polars as pl
            from datetime import datetime, timedelta
            dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(366)]
            np.random.seed(42)
            data = []
            for i, date in enumerate(dates):
                if i == 0:
                    close = 100.0
                else:
                    change = np.random.normal(0, 0.02)
                    close = data[-1]['close'] * (1 + change)
                data.append({
                    'date': date,
                    'open': close * (1 + np.random.normal(0, 0.01)),
                    'high': close * (1 + abs(np.random.normal(0, 0.015))),
                    'low': close * (1 - abs(np.random.normal(0, 0.015))),
                    'close': close,
                    'volume': int(np.random.uniform(1000000, 5000000))
                })
            return pl.DataFrame(data)
        elif data_type == "trade_data":
            import numpy as np
            import polars as pl
            from datetime import datetime, timedelta
            dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(100)]
            return pl.DataFrame({
                'date': dates,
                'entry_price': np.random.uniform(50, 150, 100),
                'exit_price': np.random.uniform(50, 150, 100),
                'shares': np.random.randint(1000, 10000, 100),
                'profit_loss': np.random.uniform(-10000, 10000, 100)
            })
        elif data_type == "indicators":
            import numpy as np
            import polars as pl
            from datetime import datetime, timedelta
            dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(366)]
            close_prices = 100 + np.cumsum(np.random.normal(0, 0.5, len(dates)))
            df = pl.DataFrame({
                'date': dates,
                'close': close_prices
            })
            # 計算移動平均
            df = df.with_columns([
                pl.col('close').rolling_mean(5).alias('ma5'),
                pl.col('close').rolling_mean(20).alias('ma20'),
                pl.col('close').rolling_mean(60).alias('ma60')
            ])
            return df
        else:
            return pl.DataFrame() 

    @staticmethod
    async def save_notebook(strategy_id: str, request: Request):
        """儲存 Jupyter notebook 的 cell 結構"""
        print_log(f"save_notebook")
        try:
            data = await request.json()
            cells = data.get("cells", [])
            
            # 確保 strategies 目錄存在
            import os
            strategies_dir = "data/strategies"
            os.makedirs(strategies_dir, exist_ok=True)
            
            # 儲存 notebook 結構到 JSON 檔案
            notebook_file = os.path.join(strategies_dir, f"jupyter_{strategy_id}.json")
            notebook_data = {
                "strategy_id": strategy_id,
                "cells": cells,
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "total_cells": len(cells),
                    "version": "1.0"
                }
            }
            
            with open(notebook_file, 'w', encoding='utf-8') as f:
                json.dump(notebook_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": "Jupyter notebook 儲存成功",
                "cells_count": len(cells)
            }
            
        except Exception as e:
            print_log(f"save_notebook error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    @staticmethod
    async def load_notebook(strategy_id: str, request: Request):
        """載入 Jupyter notebook 的 cell 結構"""
        print_log(f"load_notebook")
        try:
            import os
            strategies_dir = "data/strategies"
            notebook_file = os.path.join(strategies_dir, f"jupyter_{strategy_id}.json")
            
            if not os.path.exists(notebook_file):
                return {
                    "status": "not_found",
                    "message": "找不到 Jupyter notebook 檔案"
                }
            
            with open(notebook_file, 'r', encoding='utf-8') as f:
                notebook_data = json.load(f)
            
            return {
                "status": "success",
                "notebook": notebook_data
            }
            
        except Exception as e:
            print_log(f"load_notebook error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    @staticmethod
    async def execute_strategy_backtest(request: Request):
        """執行策略回測並返回交易記錄和圖表"""
        print_log(f"execute_strategy_backtest")
        try:
            data = await request.json()
            strategy_code = data.get("strategy_code", "")
            parameters = data.get("parameters", {})
            stock_data = data.get("stock_data")  # 這應該是 polars DataFrame 的序列化資料
            
            if not strategy_code.strip():
                return {
                    "status": "error",
                    "error": "策略程式碼不能為空"
                }
            
            # 建立策略實例
            strategy_instance = DynamicStrategy(
                parameters=parameters,
                strategy_code=strategy_code,
                strategy_name="Jupyter 編輯器策略"
            )
            
            # 執行回測
            if stock_data:
                # 如果有提供股票資料，直接使用
                result_df = strategy_instance.execute(stock_data)
            else:
                # 否則使用預設資料
                result_df = strategy_instance.execute()
            
            # 取得交易記錄
            trade_records = strategy_instance.get_trade_records()
            holding_positions = strategy_instance.get_holding_positions()
            
            # 計算回測統計
            backtest_stats = strategy_instance.calculate_backtest_statistics()
            
            # 生成圖表
            charts = strategy_instance.generate_charts()
            
            return {
                "status": "success",
                "result_df": result_df.to_dicts() if result_df is not None else None,
                "trade_records": [record.to_dict() for record in trade_records],
                "holding_positions": [pos.to_dict() for pos in holding_positions],
                "backtest_stats": backtest_stats,
                "charts": charts
            }
            
        except Exception as e:
            print_log(f"execute_strategy_backtest error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            } 

    @staticmethod
    async def execute_jupyter_strategy_backtest(request: Request):
        """執行 Jupyter 編輯器策略回測，整合 Jupyter 變數和 dynamic_strategy"""
        print_log(f"execute_jupyter_strategy_backtest")
        try:
            data = await request.json()
            strategy_code = data.get("strategy_code", "")
            parameters = data.get("parameters", {})
            strategy_table = data.get("strategy_table", "")
            excel_file = data.get("excel_file")  # 這應該是 base64 編碼的檔案內容
            initial_capital = TradingConfig.BACKTEST_INITIAL_CAPITAL
            
            if not strategy_code.strip():
                return {
                    "status": "error",
                    "error": "策略程式碼不能為空"
                }
            
            # 載入 Jupyter 全域變數（使用快取）
            global_variables = JupyterAPI._load_variables()
            
            # 尋找股票資料變數
            stock_data = None
            excel_pl_df = None
            
            # 優先使用 Jupyter 中的股票資料變數
            for var_name, var_value in global_variables.items():
                if isinstance(var_value, pl.DataFrame):
                    # 檢查是否包含必要的股票資料欄位
                    if 'date' in var_value.columns and ('close' in var_value.columns or 'price' in var_value.columns):
                        if stock_data is None:  # 第一個符合條件的 DataFrame
                            stock_data = var_value
                            break  # 找到第一個就停止
                        
            # 如果沒有找到股票資料，嘗試從快取或 Excel 載入
            if stock_data is None:
                # 從快取載入
                cache_manager = request.app.state.cache_manager
                if strategy_table and strategy_table != "auto" and cache_manager:
                    cache_key = strategy_table
                    cache_file = cache_manager._get_cache_file_path(cache_key)
                    if os.path.exists(cache_file):
                        with open(cache_file, 'rb') as f:
                            stock_data = pickle.load(f)
                
                # 如果還是沒有，嘗試從 Excel 載入
                if stock_data is None and excel_file:
                    try:
                        import base64
                        excel_content = base64.b64decode(excel_file.split(',')[1])
                        stock_data = pl.read_excel(BytesIO(excel_content))
                    except Exception as e:
                        print_log(f"Excel 載入失敗: {e}") 
            # 取得 Jupyter 全域變數
            global_variables = JupyterAPI._load_variables()
            stock_df = global_variables.get('stock_df')   
            
            # 建立 DynamicStrategy 實例        
            strategy_instance = DynamicStrategy(
                parameters=parameters,
                strategy_code=strategy_code,
                strategy_name="Jupyter 編輯器策略",
                data=(stock_data, stock_df)
            )

            # 檢查是否有多個股票
            if 'stock_id' in stock_data.columns:
                # 取得所有股票代碼
                stock_ids = stock_data.select('stock_id').unique().to_series().to_list()
                
                if len(stock_ids) > 1:
                    # 多股票使用多執行緒處理
                    print_log(f"使用多執行緒處理 {len(stock_ids)} 個股票")
                    
                    # 為每個股票創建獨立的策略實例
                    strategy_instances = {}
                    for stock_id in stock_ids:
                        strategy_instances[stock_id] = DynamicStrategy(
                            parameters=parameters.copy(),
                            strategy_code=strategy_code,
                            strategy_name="Jupyter 編輯器策略",
                            data=(stock_data, stock_df)
                        )
                    
                    # 使用線程池執行多股票回測
                    import concurrent.futures
                    from concurrent.futures import ThreadPoolExecutor, as_completed
                    
                    with ThreadPoolExecutor(max_workers=min(len(stock_ids), 4)) as executor:
                        # 提交所有任務
                        future_to_stock = {}
                        for stock_id in stock_ids:
                            # 過濾該股票的資料
                            stock_excel_data = stock_data.filter(pl.col("stock_id") == stock_id)
                            
                            if len(stock_excel_data) == 0:
                                print_log(f"股票 {stock_id} 沒有資料，跳過")
                                continue
                            
                            # 提交任務
                            future = executor.submit(
                                strategy_instances[stock_id].run_backtest,
                                stock_excel_data,
                                stock_df,
                                initial_capital,
                                stock_id,
                                f"股票{stock_id}"
                            )
                            future_to_stock[future] = stock_id
                        
                        # 收集結果
                        for future in as_completed(future_to_stock):
                            stock_id = future_to_stock[future]
                            try:
                                future.result()  # 等待完成
                                print_log(f"股票 {stock_id} 回測完成")
                            except Exception as e:
                                print_log(f"股票 {stock_id} 回測失敗: {e}")
                    
                    # 合併所有策略實例的結果
                    for stock_id, instance in strategy_instances.items():
                        strategy_instance.trade_records.extend(instance.trade_records)
                        # strategy_instance.holding_positions.extend(instance.holding_positions)
                    
                else:
                    # 單股票直接執行
                    stock_id = str(stock_ids[0])
                    strategy_instance.run_backtest(stock_data, stock_df, initial_capital, stock_id, f"{stock_id}股票")
            else:
                # 沒有 stock_id 欄位，使用預設值
                stock_id = "UNKNOWN"
                strategy_instance.run_backtest(stock_data, stock_df, initial_capital, stock_id, "未知股票")
            
            # 取得回測結果
            result = strategy_instance.get_strategy_result(initial_capital)

            # 生成圖表
            charts = []
            trade_records = result.get("trade_records", [])
            if trade_records and len(trade_records) > 0:
                try:
                    # 準備交易記錄資料（轉換為字典格式，和傳統編輯器一致）
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
                    
                    # 強制轉換 trade_records 為 list of dict（和傳統編輯器一致）
                    if isinstance(trade_records, pl.DataFrame):
                        trade_records = trade_records.to_dicts()
                    elif isinstance(trade_records, list) and len(trade_records) > 0 and hasattr(trade_records[0], 'to_dict'):
                        trade_records = [row.to_dict() for row in trade_records]
                    elif isinstance(trade_records, list) and len(trade_records) > 0 and isinstance(trade_records[0], dict):
                        pass  # already correct
                    else:
                        print_log(f"trade_records 型態異常: {type(trade_records)}")
                    
                    from api.chart_api import ChartAPI

                    # 生成各種圖表
                    chart_types = ["drawdown_merge", "heatmap", "monthly_return_heatmap", "win_rate_heatmap"]
                    chart_titles = {
                        "drawdown_merge": "回撤分析圖",
                        "heatmap": "月損益熱力圖", 
                        "monthly_return_heatmap": "月收益率熱力圖",
                        "win_rate_heatmap": "月勝率熱力圖"
                    }

                    for chart_type in chart_types:
                        try:
                            # 創建對應的請求物件
                            class MockChartRequest:
                                async def json(self):
                                    return {
                                        "chart_type": chart_type,
                                        "trade_records": trade_records
                                    }

                            chart_result = await ChartAPI.generate_charts(MockChartRequest())

                            if chart_result.get("success"):
                                charts.append({
                                    "id": chart_type,
                                    "title": chart_titles.get(chart_type, f"圖表 {chart_type}"),
                                    "html": chart_result.get("chart_html", ""),
                                    "type": chart_type
                                })
                                print_log(f"成功生成圖表: {chart_type}")
                            else:
                                print_log(f"圖表生成失敗: {chart_type}")
                        except Exception as chart_error:
                            print_log(f"生成圖表 {chart_type} 失敗: {chart_error}")
                except Exception as e:
                    print_log(f"圖表生成失敗: {e}")
            
            # 確保回傳的資料結構與前端期望一致
            return {
                "status": "success",
                "result": {
                    "trade_records": trade_records if 'trade_records' in locals() and isinstance(trade_records, list) else result.get("trade_records", []),
                    "holding_positions": result.get("holding_positions", []),
                    "backtest_statistics": {
                        "total_trades": result.get("total_trades", 0),
                        "winning_trades": result.get("winning_trades", 0),
                        "losing_trades": result.get("losing_trades", 0),
                        "win_rate": result.get("win_rate", 0),
                        "total_profit_loss": result.get("total_profit_loss", 0),
                        "total_profit_loss_rate": result.get("total_profit_loss_rate", 0),
                        "max_drawdown": result.get("max_drawdown", 0),
                        "max_drawdown_rate": result.get("max_drawdown_rate", 0),
                        "sharpe_ratio": result.get("sharpe_ratio", 0),
                        "total_return": result.get("total_profit_loss_rate", 0)  # 使用總損益率作為總報酬率
                    },
                    "charts": charts,
                    "result_df": None,  # 暫時設為 None，因為 DynamicStrategy 沒有這個欄位
                    "strategy_info": {
                        "strategy_name": result.get("strategy_name", "Jupyter 編輯器策略"),
                        "parameters": result.get("parameters", {})
                    }
                },
                "stock_data_shape": stock_data.shape if stock_data is not None else None,
                "excel_data_shape": excel_pl_df.shape if excel_pl_df is not None else None,
                "jupyter_variables": list(global_variables.keys())
            }
            
        except Exception as e:
            print_log(f"execute_jupyter_strategy_backtest error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            } 