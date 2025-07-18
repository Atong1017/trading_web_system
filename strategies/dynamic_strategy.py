# 動態策略類別
import ast
import inspect
import tempfile
import os
import sys
import threading
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import polars as pl
from strategies.base_strategy import BaseStrategy, TradeRecord, HoldingPosition
from core.price_utils import PriceUtils
from core.utils import Utils
import copy
from core.technical_indicators import generate_indicators

def print_log(message):
    print(f"********** dynamic_strategy.py - {message}")

class DynamicStrategy(BaseStrategy):
    """動態策略類別，允許用戶透過程式碼字串來定義策略"""
    
    def __init__(self, parameters: Dict[str, Any], strategy_code: str = "", strategy_name: str = "自定義策略", data: Dict[str, Any] = None):
        """
        初始化動態策略
        
        Args:
            parameters (Dict[str, Any]): 策略參數
            strategy_code (str): 策略程式碼字串
            strategy_name (str): 策略名稱
        """
        print_log(f"__init__")
        self.strategy_code = strategy_code
        self.custom_strategy_name = strategy_name
        self.compiled_code = None
        self.strategy_functions = {}

        # 創建參數副本，避免修改原始參數
        parameters_copy = copy.deepcopy(parameters)
        # 初始化基礎參數（先不處理字典類型的參數配置）
        super().__init__(parameters_copy)
        
        # 設定基礎參數預設值
        self.parameters.setdefault("record_holdings", 0)  # 持有記錄功能，預設關閉
        # 動態參數管理
        self.dynamic_parameters = {}  # 儲存動態參數
        self.parameter_history = {}   # 儲存參數變更歷史
        
        for key, value in parameters.items():
            if isinstance(value, dict) and 'default' in value:
                self.parameters[key] = value['default']

        # 編譯策略程式碼
        if strategy_code:
            if data:
                self._last_df = data[0]
                self._last_stock_df = data[1]
                
            self._compile_strategy_code()
            
        # 編譯完成後，處理參數中的字典類型配置
        self._process_parameter_configs()
    
    def _process_parameter_configs(self):
        """處理參數中的字典類型配置，提取實際值"""
        print_log(f"_process_parameter_configs")
        if not hasattr(self, 'parameters') or not self.parameters:
            return
            
        for key, value in list(self.parameters.items()):
            # 若 value 是 dict，則提取其 default 值作為實際參數值
            if isinstance(value, dict) and 'default' in value:
                self.parameters[key] = value['default']
    
    def _compile_strategy_code(self):
        """編譯策略程式碼"""
        print_log(f"_compile_strategy_code")
        try:
            # 解析程式碼
            tree = ast.parse(self.strategy_code)
            
            # 提取函數定義
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.strategy_functions[node.name] = node
            
            # 建立執行環境
            exec_globals = {
                'pl': pl,
                'datetime': datetime,
                'TradeRecord': TradeRecord,
                'HoldingPosition': HoldingPosition,
                'PriceUtils': PriceUtils,
                'Utils': Utils,
                'generate_indicators': generate_indicators,
                'self': self
            }
            
            # 若有 self._last_df df/stock_data 變數
            if hasattr(self, '_last_df') and self._last_df is not None:
                # 編輯器模式
                exec_globals['df'] = self._last_df
                exec_globals['stock_df'] = self._last_stock_df
                exec_globals['parameters'] = self.parameters
            elif "Jupyter" in self.custom_strategy_name:
                # 回測模式
                exec_globals['df'] = pl.DataFrame()
                exec_globals['stock_df'] = pl.DataFrame()
                exec_globals['parameters'] = {}
                # Jupyter 模式只做語法檢查，不執行 exec
                self.compiled_code = exec_globals
                self.custom_parameters = {}
                return

            # 執行程式碼
            exec(self.strategy_code, exec_globals)
            
            # 儲存編譯後的程式碼
            self.compiled_code = exec_globals
            
            # 提取自定義參數
            if 'custom_parameters' in exec_globals:
                self.custom_parameters = exec_globals['custom_parameters']
                # 初始化動態參數
                self._initialize_dynamic_parameters()
            else:
                self.custom_parameters = {}  # 沒有定義時也設為空 dict
            
        except Exception as e:
            raise ValueError(f"策略程式碼編譯錯誤: {str(e)}")
    
    def _initialize_dynamic_parameters(self):
        """初始化動態參數"""
        print_log(f"_initialize_dynamic_parameters")
        if hasattr(self, 'custom_parameters'):
            for param_name, param_config in self.custom_parameters.items():
                if param_config.get('type') == 'dynamic':
                    # 動態參數，需要特殊處理
                    self.dynamic_parameters[param_name] = param_config.get('default', 0)
                    self.parameter_history[param_name] = []
    
    def get_dynamic_parameter(self, param_name: str, default=None):
        """
        取得動態參數值
        注意：這裡只針對 type=dynamic 的參數，值來自 self.dynamic_parameters
        結構描述（型別、default）查 self.custom_parameters，實際值查 self.dynamic_parameters
        Args:
            param_name: 參數名稱
            default: 預設值
        Returns:
            參數值
        """
        print_log(f"get_dynamic_parameter")
        return self.dynamic_parameters.get(param_name, default)
    
    def set_dynamic_parameter(self, param_name: str, value, record_history=True):
        """
        設定動態參數值
        注意：這裡只針對 type=dynamic 的參數，值存 self.dynamic_parameters
        結構描述查 self.custom_parameters，實際值存 self.dynamic_parameters
        Args:
            param_name: 參數名稱
            value: 參數值
            record_history: 是否記錄歷史
        """
        print_log(f"set_dynamic_parameter")
        old_value = self.dynamic_parameters.get(param_name)
        self.dynamic_parameters[param_name] = value
        if record_history and param_name in self.parameter_history:
            self.parameter_history[param_name].append({
                'timestamp': datetime.now(),
                'old_value': old_value,
                'new_value': value
            })
    
    def increment_dynamic_parameter(self, param_name: str, increment=1):
        """
        增加動態參數值
        
        Args:
            param_name: 參數名稱
            increment: 增加量
        """
        print_log(f"increment_dynamic_parameter")
        current_value = self.get_dynamic_parameter(param_name, 0)
        self.set_dynamic_parameter(param_name, current_value + increment)
    
    def reset_dynamic_parameter(self, param_name: str):
        """
        重置動態參數值
        注意：default 只查 self.custom_parameters，值存 self.dynamic_parameters
        Args:
            param_name: 參數名稱
        """
        print_log(f"reset_dynamic_parameter")
        if param_name in self.custom_parameters:
            default_value = self.custom_parameters[param_name].get('default', 0)
            self.set_dynamic_parameter(param_name, default_value)
    
    def get_parameter_history(self, param_name: str):
        """
        取得參數變更歷史
        
        Args:
            param_name: 參數名稱
            
        Returns:
            參數變更歷史列表
        """
        print_log(f"get_parameter_history")
        return self.parameter_history.get(param_name, [])
    
    @property
    def strategy_name(self) -> str:
        print_log(f"strategy_name {self.custom_strategy_name}")
        return self.custom_strategy_name
    
    @property
    def strategy_description(self) -> str:
        print_log(f"strategy_description")
        return "用戶自定義策略"
    
    @property
    def parameter_sources(self) -> Dict[str, Dict[str, Any]]:
        """取得策略所需的參數來源"""
        print_log(f"parameter_sources")
        return {
            "stock_source": {
                "type": "excel",
                "required": True,
                "description": "股票代碼來源",
                "columns": ["stock_id", "date"]
            },
            "price_source": {
                "type": "api",
                "required": True,
                "description": "股價資料來源"
            },
            "date_range": {
                "type": "excel",
                "required": False,
                "description": "日期範圍設定"
            }
        }
    
    @property
    def strategy_parameters(self) -> Dict[str, Dict[str, Any]]:
        """取得策略參數配置"""
        print_log(f"strategy_parameters")
        # 從 trading_config 取得基礎參數
        from config.trading_config import TradingConfig
        
        # 基礎參數
        base_params = {
            "commission_rate": {
                "type": "number",
                "label": "手續費率",
                "default": TradingConfig.COMMISSION_RATE,
                "min": 0.0001,
                "max": 0.01,
                "step": 0.0001,
                "description": "買賣手續費率"
            },
            "commission_discount": {
                "type": "number",
                "label": "手續費折數",
                "default": 0.3,
                "min": 0.1,
                "max": 1.0,
                "step": 0.1,
                "description": "手續費折數"
            },
            "securities_tax_rate": {
                "type": "number",
                "label": "當沖證交稅率",
                "default": TradingConfig.SECURITIES_TAX_RATE,
                "min": 0.001,
                "max": 0.01,
                "step": 0.0001,
                "description": "當沖證交稅率"
            },
            "sstt_rate": {
                "type": "number",
                "label": "波段證交稅率",
                "default": TradingConfig.SECURITIES_TAX_RATE,
                "min": 0.001,
                "max": 0.01,
                "step": 0.0001,
                "description": "波段證交稅率"
            },
            "shares_per_trade": {
                "type": "number",
                "label": "每次交易股數",
                "default": 1000,
                "min": 100,
                "max": 10000,
                "step": 100,
                "description": "每次交易的股數"
            },
            "holding_days": {
                "type": "number",
                "label": "持有天數",
                "default": 0,
                "min": 0,
                "max": 365,
                "step": 1,
                "description": "當前持有天數（系統自動計算）"
            }
        }
        
        # 如果策略程式碼中有定義參數，則加入
        if hasattr(self, 'custom_parameters'):
            base_params.update(self.custom_parameters)
        
        return base_params
    
    def get_parameter_default(self, param_name: str, fallback=None):
        """從 custom_parameters 的 default 值取得參數"""
        print_log(f"get_parameter_default")
        # 先從 strategy_parameters 中查找
        strategy_params = self.strategy_parameters
        
        if param_name in strategy_params:
            return strategy_params[param_name].get("default", fallback)
        else:
            if isinstance(fallback, dict):
                return fallback.get("default", fallback)
        
        # 如果沒有找到，返回 fallback 值
        return fallback
    
    def get_parameter_value(self, param_name: str, fallback=None):
        """
        取得參數值，優先從 self.parameters 取得（用戶實際值），如果沒有則從 default 值取得（查結構）
        Args:
            param_name: 參數名稱
            fallback: 預設值
        Returns:
            參數值
        """
        print_log(f"get_parameter_value")
        # 優先從 self.parameters 取得（用戶實際值）
        if hasattr(self, 'parameters') and self.parameters and param_name in self.parameters:
            param_value = self.parameters[param_name]
            
            # 如果參數值是字典（參數配置），則取得其 default 值
            if isinstance(param_value, dict) and 'default' in param_value:
                return param_value['default']
            # 否則直接返回參數值
            return param_value
        # 如果沒有，從 default 值取得（查結構）
        return self.get_parameter_default(param_name, fallback)
    
    def process_parameters(self, parameters: Dict[str, Any], stock_df: pl.DataFrame = None) -> Dict[str, Any]:
        """處理策略參數"""
        print_log(f"process_parameters")
        # 檢查是否有策略程式碼
        if not self.strategy_code or not self.strategy_code.strip():
            raise ValueError("沒有選擇策略(策略管理中其中一個)或未輸入指令")
        
        # 如果有自定義的參數處理函數，則使用它
        if 'process_parameters' in self.strategy_functions:
            return self._execute_function('process_parameters', parameters, stock_df)
        
        # 如果沒有定義 process_parameters 函數，拋出錯誤
        raise ValueError("策略程式碼中未定義 process_parameters 函數")
    
    def validate_special_parameters(self, parameters: Dict[str, Any]) -> None:
        """驗證策略特定的參數"""
        print_log(f"validate_special_parameters")
        # 如果有自定義的驗證函數，則使用它
        if 'validate_parameters' in self.strategy_functions:
            self._execute_function('validate_parameters', parameters)
    
    async def process_api_data(self, stock_data: pl.DataFrame, stock_api, excel_pl_df: pl.DataFrame = None) -> pl.DataFrame:
        """處理API取得的資料"""
        print_log(f"process_api_data")
        # 檢查是否有策略程式碼
        if not self.strategy_code or not self.strategy_code.strip():
            raise ValueError("沒有選擇策略(策略管理中其中一個)或未輸入指令")
        
        # 如果有自定義的API資料處理函數，則使用它
        if 'process_api_data' in self.strategy_functions:
            return self._execute_function('process_api_data', stock_data, stock_api, excel_pl_df)
        
        # 如果沒有定義 process_api_data 函數，拋出錯誤
        raise ValueError("策略程式碼中未定義 process_api_data 函數")
    
    def process_excel_data(self, excel_data: pl.DataFrame, excel_pl_df: pl.DataFrame = None) -> Dict[str, Any]:
        """處理Excel資料"""
        print_log(f"process_excel_data")
        # 檢查是否有策略程式碼
        if not self.strategy_code or not self.strategy_code.strip():
            raise ValueError("沒有選擇策略(策略管理中其中一個)或未輸入指令")
        
        # 如果有自定義的Excel資料處理函數，則使用它
        if 'process_excel_data' in self.strategy_functions:
            return self._execute_function('process_excel_data', excel_data, excel_pl_df)
        
        # 如果沒有定義 process_excel_data 函數，拋出錯誤
        raise ValueError("策略程式碼中未定義 process_excel_data 函數")
    
    def should_entry(self, stock_data: pl.DataFrame, current_index: int, excel_pl_df: pl.DataFrame = None) -> Tuple[bool, Dict[str, Any]]:        
        """判斷是否應該進場"""
        print_log(f"should_entry")
        # 檢查是否有策略程式碼
        if not self.strategy_code or not self.strategy_code.strip():
            raise ValueError("沒有選擇策略(策略管理中其中一個)或未輸入指令")
        
        if 'should_entry' in self.strategy_functions:
            kwargs = self._prepare_parameters()
            return self._execute_function('should_entry', stock_data, current_index, excel_pl_df, **kwargs)
        
        # 如果沒有定義 should_entry 函數，拋出錯誤
        raise ValueError("策略程式碼中未定義 should_entry 函數")
    
    def should_exit(self, stock_data: pl.DataFrame, current_index: int, position: Dict[str, Any], excel_pl_df: pl.DataFrame = None) -> Tuple[bool, Dict[str, Any]]:
        """判斷是否應該出場"""
        print_log(f"should_exit")
        # 檢查是否有策略程式碼
        if not self.strategy_code or not self.strategy_code.strip():
            raise ValueError("沒有選擇策略(策略管理中其中一個)或未輸入指令")
        
        if 'should_exit' in self.strategy_functions:
            try:
                kwargs = self._prepare_parameters()
                # 執行自定義函數
                result = self._execute_function('should_exit', stock_data, current_index, position, excel_pl_df, **kwargs)
                
                # 處理動態參數更新
                self._update_dynamic_parameters_after_exit(result[0])
                
                return result
            except Exception as e:
                print_log(f"should_exit 執行錯誤: {e}")
                return False, {}
        
        # 如果沒有定義 should_exit 函數，拋出錯誤
        raise ValueError("策略程式碼中未定義 should_exit 函數")
    
    def _prepare_parameters(self):
        """
        準備傳給自定義策略函數的 kwargs
        只查 self.custom_parameters 取得型別/結構/預設值，實際值一律用 self.parameters
        """
        print_log(f"_prepare_parameters")
        kwargs = {}
        # 添加基礎參數（用戶實際值）
        base_params = ["commission_rate", "commission_discount", "securities_tax_rate", "sstt_rate", "shares_per_trade", "holding_days"]
        for param_name in base_params:
            kwargs[param_name] = self.get_parameter_value(param_name, 0)
        
        # 添加自定義參數
        if hasattr(self, 'custom_parameters'):
            for param_name, param_config in self.custom_parameters.items():
                if param_config.get('type') == 'dynamic':
                    # 動態參數，從 self.dynamic_parameters 取得實際值
                    kwargs[param_name] = self.get_dynamic_parameter(param_name, param_config.get('default', 0))
                else:
                    # 靜態參數，從 self.parameters 取得用戶實際值
                    kwargs[param_name] = self.get_parameter_value(param_name, param_config.get('default', 0))

        # 添加其他參數（確保所有參數都被包含）
        for param_name, param_value in self.parameters.items():
            if param_name not in kwargs:
                kwargs[param_name] = param_value    
                
        return kwargs
        
    def _update_dynamic_parameters_after_exit(self, should_exit: bool):
        """
        出場後更新動態參數
        
        Args:
            should_exit: 是否出場
        """
        print_log(f"_update_dynamic_parameters_after_exit")
        if hasattr(self, 'custom_parameters'):
            for param_name, param_config in self.custom_parameters.items():
                if param_config.get('type') == 'dynamic':
                    if should_exit:
                        # 出場時重置參數
                        self.reset_dynamic_parameter(param_name)
                    else:
                        # 不出場時增加參數
                        increment = param_config.get('increment', 1)
                        self.increment_dynamic_parameter(param_name, increment)
    
    def run_backtest(self, stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame, initial_capital: float, stock_id: str, stock_name: str):
        """執行回測"""
        print_log(f"run_backtest")
        # 檢查是否有策略程式碼
        if not self.strategy_code or not self.strategy_code.strip():
            raise ValueError("沒有選擇策略(策略管理中其中一個)或未輸入指令")
        
        # 如果有自定義的回測函數，則使用它
        if 'run_backtest' in self.strategy_functions:
            self._execute_function('run_backtest', stock_data, excel_pl_df, initial_capital, stock_id, stock_name)
            return
        
        # 檢查是否有基本的策略函數（進場或出場）
        if not self.strategy_functions and "Jupyter" not in self.strategy_name:
            raise ValueError("策略程式碼中未定義任何策略函數，請至少定義 should_entry 或 should_exit 函數")
        
        # 確保 parameters 有預設值
        if not hasattr(self, 'parameters') or self.parameters is None:
            self.parameters = {}

        # 檢查 excel_pl_df 中的股票代碼
        if excel_pl_df is None or len(excel_pl_df) == 0:
            raise ValueError("Excel 資料為空，無法執行回測")
        
        # 直接執行單股票回測（strategy_api.py 已經處理了多執行緒）
        self._run_single_stock_backtest(stock_data, excel_pl_df, stock_id, stock_name)
    
    def _run_single_stock_backtest(self, stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame, stock_id: str, stock_name: str):
        """執行單股票回測"""
        print_log(f"_run_single_stock_backtest")
        # 使用狀態機模式
        if "Jupyter" not in self.strategy_name and self.compiled_code.get('should_entry', None) and self.compiled_code.get('calculate_entry_signals', None):
            # 完全向量化模式（實驗性，適用於簡單策略）
            self._execute_fully_vectorized_backtest(stock_data, excel_pl_df, stock_id, stock_name)                   
        
        elif 'should_entry' in self.compiled_code:
            self._calculate_signals_state_machine(stock_data, excel_pl_df, stock_id, stock_name) 
        else:
            if "Jupyter" not in self.strategy_name:
                # 使用操作計算進出場信號
                stock_data = self._calculate_entry_exit_signals(stock_data, excel_pl_df)
                # 混合模式（推薦，向後相容）
                # self._execute_vectorized_backtest(stock_data, excel_pl_df, stock_id, stock_name)
            # Jupyter 模式
            else:
                # 策略編輯器
                if "Jupyter 編輯器策略" not in self.strategy_name:
                    # 非"Jupyter 編輯器策略"的模式：執行策略程式碼來計算 df
                    try:
                        # 建立執行環境
                        exec_globals = {
                            'pl': pl,
                            'datetime': datetime,
                            'TradeRecord': TradeRecord,
                            'HoldingPosition': HoldingPosition,
                            'PriceUtils': PriceUtils,
                            'Utils': Utils,
                            'generate_indicators': generate_indicators,
                            'self': self,
                            'df': stock_data,
                            'stock_df': excel_pl_df,
                            'stock_data': stock_data,
                            'parameters': self.parameters
                        }
                        
                        # 執行 Jupyter 編輯器策略程式碼
                        exec(self.strategy_code, exec_globals)
                        
                        # 從執行環境中提取計算結果
                        if 'df' in exec_globals:
                            stock_data = exec_globals['df']
                            print_log(f"Jupyter 編輯器策略執行完成，df 形狀: {stock_data.shape}")
                        
                        stock_data = exec_globals['df']
                        excel_pl_df = exec_globals['stock_data']
                        
                    except Exception as e:
                        print_log(f"Jupyter 編輯器策略執行失敗: {e}")
                        # 如果執行失敗，至少保留原始資料

            self._execute_vectorized_backtest(stock_data, excel_pl_df, stock_id, stock_name) 
    
    def _calculate_entry_exit_signals(self, stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame) -> pl.DataFrame:
        """使用向量化操作計算進出場信號"""
        print_log(f"_calculate_entry_exit_signals")
        try:
            # 初始化進出場信號欄位
            df = stock_data.with_columns([
                pl.lit("").alias("entry_date"),
                pl.lit(0).alias("entry_price"),
                pl.lit(0).alias("shares"),
                pl.lit(0).alias("holding_days"),
                pl.lit(0).alias("should_entry"),
                pl.lit(0).alias("should_exit"),
                pl.lit("").alias("entry_reason"),
                pl.lit("").alias("exit_reason")
            ])
            # 向量化模式
            try:
                df = self._execute_function('calculate_entry_signals', df, excel_pl_df)     
                
                # 如果有自定義的向量化出場函數，使用它
                if 'calculate_exit_signals' in self.strategy_functions:
                    df = self._execute_function('calculate_exit_signals', df, excel_pl_df)      
                    
                return df                    
            except Exception as e:
                print_log(f"向量化計算失敗，回退到狀態機模式: {e}")
                return self._calculate_signals_state_machine(stock_data, excel_pl_df)
            
        except Exception as e:
            print_log(f"計算進出場信號失敗: {e}")
            return stock_data
    
    def _calculate_signals_state_machine(self, stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame, stock_id: str, stock_name: str) -> pl.DataFrame:
        """使用狀態機模式計算進出場信號（適用於複雜邏輯）"""
        print_log(f"_calculate_signals_state_machine")
        try:
            # 預設回測邏輯
            capital = self.parameters.get("initial_capital", 0)
            current_position = None  # 當前持有部位
            
            # 初始化 holding_days
            if "holding_days" not in self.parameters:
                self.parameters["holding_days"] = 0
            
            # 使用狀態機逐行處理
            for i in range(len(stock_data)):
                current_row = stock_data.row(i, named=True)
                previous_row = stock_data.row(i-1, named=True) if i > 0 else current_row
                
                if not current_position:  # 空手狀態
                    self.parameters["holding_days"] = 0
                    # 檢查進場信號
                    should_entry, entry_info = self.should_entry(stock_data, i, excel_pl_df)
                    
                    if should_entry:
                        # 計算進場價格和股數
                        entry_price = self.calculate_entry_price(stock_data, i)
                        share_type = self.parameters.get("share_type", "mixed")
                        shares = self.calculate_shares(capital, entry_price, share_type)
                            
                        if shares > 0:
                            position_id = f"{stock_id}_{current_row['date']}_{entry_price}_{uuid.uuid4().hex[:8]}"
                            current_position = {
                                "position_id": position_id,
                                "entry_date": current_row["date"],
                                "entry_price": entry_price,
                                "shares": shares,
                                "entry_index": i,
                                "holding_days": self.parameters["holding_days"]
                            }
                
                elif current_position:  # 持有狀態
                    # 增加持有天數
                    self.parameters["holding_days"] += 1
                    
                    should_exit, exit_info = self.should_exit(stock_data, i, current_position, excel_pl_df)
                    current_entry_price = previous_row.get("open") if self.parameters.get("entry_price_condition", "open") == "open" else previous_row.get("close")
                    current_exit_price = current_row.get("open") if self.parameters.get("exit_price_condition", "open") == "open" else current_row.get("close")
                    exit_price = exit_info.get("exit_price", 0) if should_exit else current_exit_price
                    profit_loss = (exit_price - current_position["entry_price"]) * current_position["shares"] if should_exit else 0
                    current_profit_loss = (exit_price - current_entry_price) * current_position["shares"]
                    current_profit_loss_rate = ((current_exit_price - current_entry_price) / current_entry_price) * 100
                    net_profit_loss = current_profit_loss
                    net_profit_loss = 0 if not should_exit else profit_loss
                    # 計算交易記錄
                    trade_record = TradeRecord(
                        position_id=current_position["position_id"],  # 使用相同的 position_id
                        entry_date=current_position["entry_date"],  # 進場日期
                        exit_date=current_row["date"],  # 出場日期
                        stock_id=stock_id,
                        stock_name=stock_name,
                        trade_direction=1 if self.parameters.get("trade_direction", "long") == "long" else -1,  # 做多
                        entry_price=current_position["entry_price"], # 進場價格
                        exit_price=exit_price, # 出場價格
                        shares=current_position["shares"], # 股數
                        profit_loss=(exit_price - current_position["entry_price"]) * current_position["shares"], # 損益
                        profit_loss_rate=((exit_price - current_position["entry_price"]) / current_position["entry_price"]) * 100,
                        commission=0 if not should_exit else self.calculate_commission(current_position["entry_price"] * current_position["shares"]),  # 手續費
                        securities_tax=0 if not should_exit else self.calculate_securities_tax(exit_price * current_position["shares"]),  # 證交稅
                        net_profit_loss=net_profit_loss,  # 淨損益
                        exit_reason=exit_info.get("reason", "未出場"), # 出場原因
                        holding_days=self.parameters["holding_days"], # 持有天數
                        # 與 HoldingPosition 相同的欄位，用於 Excel 匯出
                        current_price=current_entry_price,  # 當前價格等於出場價格
                        unrealized_profit_loss=(exit_price - current_position["entry_price"]) * current_position["shares"],  # 未實現損益等於實際損益
                        unrealized_profit_loss_rate=((exit_price - current_position["entry_price"]) / current_position["entry_price"]) * 100,  # 未實現損益率等於實際損益率
                        current_date=current_row["date"],  # 當前日期等於出場日期
                        exit_price_type=self.parameters.get("exit_price_condition", "close"),  # 出場價類型
                        # current_entry_price=current_entry_price,  # 當日進場價格等於前一日收盤價
                        current_exit_price=current_exit_price,  # 當前出場價格等於出場價格
                        current_profit_loss=current_profit_loss,  # 當前損益等於實際損益
                        current_profit_loss_rate=current_profit_loss_rate,  # 當前損益率等於實際損益率
                        take_profit_price=current_position.get("take_profit_price", 0.0),  # 停利價格
                        stop_loss_price=current_position.get("stop_loss_price", 0.0),  # 停損價格
                        open_price=current_row.get("open"),  # 開盤價
                        high_price=current_row.get("high"),  # 最高價
                        low_price=current_row.get("low"),  # 最低價
                        close_price=current_row.get("close")  # 收盤價
                    )        
                    if should_exit:# 計算淨損益
                        trade_record.net_profit_loss = trade_record.profit_loss - trade_record.commission - trade_record.securities_tax
                        
                        # 更新資金
                        capital += trade_record.net_profit_loss
                        
                        # 加入交易記錄
                        self.add_trade_record(trade_record)
                        
                        # 狀態改為空手
                        current_position = None
                        print_log(f"出場: {stock_id} 進場價: {trade_record.entry_price} 出場價: {exit_price} 損益: {trade_record.net_profit_loss}")
                        self.parameters["holding_days"] = 0

                    elif self.parameters.get("record_holdings", 0) == 1:
                        # 加入交易記錄
                        self.add_trade_record(trade_record)
                
                # 更新權益曲線
                self.update_equity_curve(capital, current_row["date"])            
            
        except Exception as e:
            print_log(f"狀態機計算失敗: {e}")
            return stock_data
    
    def _execute_vectorized_backtest(self, stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame, stock_id: str, stock_name: str):
        """使用向量化操作執行回測"""        
        print_log(f"_execute_vectorized_backtest")
        try:
            capital = self.parameters.get("initial_capital", 1000000.0)
            current_position = None
            holding_days = 0
            
            # 初始化 holding_days
            if "holding_days" not in self.parameters:
                self.parameters["holding_days"] = 0
            
            # 使用 Polars 的 apply 或 map_rows 來處理每一行
            # 由於需要維護狀態（current_position, capital），我們仍然需要逐行處理
            # 但可以優化為只在有進出場信號時才執行複雜的判斷邏輯
            
            for i in range(len(stock_data)):
                current_row = stock_data.row(i, named=True)
                previous_row = stock_data.row(i-1, named=True) if i > 0 else current_row
                
                # 檢查進場信號
                if not current_position and current_row.get("should_entry", 0) == 1:
                    entry_price = self.calculate_entry_price(stock_data, i)
                    share_type = self.parameters.get("share_type", "mixed")
                    shares = self.calculate_shares(capital, entry_price, share_type)
                    
                    if shares > 0:
                        position_id = f"{stock_id}_{current_row['date']}_{entry_price}_{uuid.uuid4().hex[:8]}"
                        current_position = {
                            "position_id": position_id,
                            "entry_date": current_row["date"],
                            "entry_price": entry_price,
                            "shares": shares,
                            "entry_index": i,
                            "holding_days": 0
                        }
                        holding_days = 0
                        
                        # print_log(f"進場: {stock_id} 價格: {entry_price} 股數: {shares} 原因: {current_row.get('entry_reason', '')}")
                
                # 檢查出場信號
                if current_position and current_row.get("should_exit", 0) == 1:
                    holding_days += 1
                    self.parameters["holding_days"] = holding_days
                    
                    # 檢查是否有出場信號
                    should_exit = current_row.get("should_exit", 0) == 1
                    exit_reason = current_row.get("exit_reason", "")
                    
                    # 如果沒有向量化出場信號，使用傳統邏輯
                    if not should_exit:
                        should_exit, exit_info = self.should_exit(stock_data, i, current_position, excel_pl_df)
                        exit_reason = exit_info.get("reason", "")
                    
                    if should_exit:
                        if current_row.get("exit_price", 0) > 0:
                            exit_price = current_row.get("exit_price", 0)
                            current_entry_price = current_row.get("entry_price")
                            current_exit_price = exit_price
                        else:
                            # 計算出場價格
                            current_entry_price = previous_row.get("open") if self.parameters.get("entry_price_condition", "open") == "open" else previous_row.get("close")
                            current_exit_price = current_row.get("open") if self.parameters.get("exit_price_condition", "open") == "open" else current_row.get("close")
                            exit_price = current_exit_price
                        
                        # 計算損益
                        profit_loss = (exit_price - current_position["entry_price"]) * current_position["shares"]
                        current_profit_loss = (exit_price - current_entry_price) * current_position["shares"]
                        current_profit_loss_rate = ((current_exit_price - current_entry_price) / current_entry_price) * 100
                        
                        # 計算交易記錄
                        trade_record = TradeRecord(
                            position_id=current_position["position_id"],
                            entry_date=current_position["entry_date"],
                            exit_date=current_row["date"],
                            stock_id=stock_id,
                            stock_name=stock_name,
                            trade_direction=1 if self.parameters.get("trade_direction", "long") == "long" else -1,
                            entry_price=current_position["entry_price"],
                            exit_price=exit_price,
                            shares=current_position["shares"],
                            profit_loss=profit_loss,
                            profit_loss_rate=((exit_price - current_position["entry_price"]) / current_position["entry_price"]) * 100,
                            commission=self.calculate_commission(current_position["entry_price"] * current_position["shares"]),
                            securities_tax=self.calculate_securities_tax(exit_price * current_position["shares"]),
                            net_profit_loss=0,  # 稍後計算
                            exit_reason=exit_reason,
                            holding_days=holding_days,
                            current_price=current_entry_price,
                            unrealized_profit_loss=profit_loss,
                            unrealized_profit_loss_rate=((exit_price - current_position["entry_price"]) / current_position["entry_price"]) * 100,
                            current_date=current_row["date"],
                            exit_price_type=self.parameters.get("exit_price_condition", "close"),
                            current_exit_price=current_exit_price,
                            current_profit_loss=current_profit_loss,
                            current_profit_loss_rate=current_profit_loss_rate,
                            take_profit_price=current_position.get("take_profit_price", 0.0),
                            stop_loss_price=current_position.get("stop_loss_price", 0.0),
                            open_price=current_row.get("open"),
                            high_price=current_row.get("high"),
                            low_price=current_row.get("low"),
                            close_price=current_row.get("close")
                        )
                        
                        # 計算淨損益
                        trade_record.net_profit_loss = trade_record.profit_loss - trade_record.commission - trade_record.securities_tax
                        
                        # 更新資金
                        capital += trade_record.net_profit_loss
                        
                        # 加入交易記錄
                        self.add_trade_record(trade_record)
                        
                        # 重置狀態
                        current_position = None
                        holding_days = 0
                        self.parameters["holding_days"] = 0
                        
                        # print_log(f"出場: {stock_id} 進場價: {trade_record.entry_price} 出場價: {exit_price} 損益: {trade_record.net_profit_loss} 原因: {exit_reason}")
                # 更新權益曲線
                self.update_equity_curve(capital, current_row["date"])
                
        except Exception as e:
            print_log(f"向量化回測執行失敗: {e}")
            raise e
    
    def _execute_fully_vectorized_backtest(self, stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame, stock_id: str, stock_name: str):
        """
        完全向量化的回測方法（實驗性）
        使用 Polars 的窗口函數和累積操作來避免 for 迴圈
        """
        print_log(f"_execute_fully_vectorized_backtest")
        try:
            # 使用窗口函數計算持有狀態
            df = stock_data.with_columns([
                # 計算進場信號的累積和，用於追蹤持倉狀態
                pl.col("should_entry").cum_sum().alias("entry_count"),
                
                # 計算出場信號的累積和
                pl.col("should_exit").cum_sum().alias("exit_count"),
                
                # 計算持有天數（從進場開始累積）
                pl.when(pl.col("should_entry") == 1)
                .then(0)  # 進場日重置為0
                .otherwise(
                    pl.when(pl.col("entry_count") > pl.col("exit_count"))
                    .then(pl.lit(1))  # 持有中，天數+1
                    .otherwise(pl.lit(0))  # 未持有
                )
                .cum_sum()
                .alias("holding_days")
            ])
            
            # 計算進場價格和股數
            df = df.with_columns([
                pl.when(pl.col("should_entry") == 1)
                .then(pl.col("open"))  # 以開盤價進場
                .otherwise(pl.lit(0.0))
                .alias("entry_price"),
                
                pl.when(pl.col("should_entry") == 1)
                .then(pl.lit(self.parameters.get("shares_per_trade", 1000)))
                .otherwise(pl.lit(0))
                .alias("shares")
            ])
            
            # 使用窗口函數向前填充進場價格和股數
            df = df.with_columns([
                pl.col("entry_price").forward_fill().alias("current_entry_price"),
                pl.col("shares").forward_fill().alias("current_shares")
            ])
            
            # 計算損益
            df = df.with_columns([
                pl.when(pl.col("should_exit") == 1)
                .then((pl.col("close") - pl.col("current_entry_price")) * pl.col("current_shares"))
                .otherwise(pl.lit(0.0))
                .alias("profit_loss"),
                
                pl.when(pl.col("should_exit") == 1)
                .then(((pl.col("close") - pl.col("current_entry_price")) / pl.col("current_entry_price")) * 100)
                .otherwise(pl.lit(0.0))
                .alias("profit_loss_rate")
            ])
            
            # 計算手續費和證交稅
            df = df.with_columns([
                pl.when(pl.col("should_exit") == 1)
                .then(self.calculate_commission(pl.col("current_entry_price") * pl.col("current_shares")))
                .otherwise(pl.lit(0.0))
                .alias("commission"),
                
                pl.when(pl.col("should_exit") == 1)
                .then(self.calculate_securities_tax(pl.col("close") * pl.col("current_shares")))
                .otherwise(pl.lit(0.0))
                .alias("securities_tax")
            ])
            
            # 計算淨損益
            df = df.with_columns([
                (pl.col("profit_loss") - pl.col("commission") - pl.col("securities_tax"))
                .alias("net_profit_loss")
            ])
            
            # 計算累積資金
            df = df.with_columns([
                (pl.lit(self.parameters.get("initial_capital", 0)) + pl.col("net_profit_loss").cum_sum())
                .alias("cumulative_capital")
            ])
            
            # 生成交易記錄
            trades_df = df.filter(pl.col("should_exit") == 1)
            
            for i in range(len(trades_df)):
                trade_row = trades_df.row(i, named=True)
                
                # 找到對應的進場記錄
                entry_df = df.filter(
                    (pl.col("should_entry") == 1) & 
                    (pl.col("date") <= trade_row["date"])
                ).tail(1)
                
                if len(entry_df) > 0:
                    entry_row = entry_df.row(0, named=True)
                    
                    trade_record = TradeRecord(
                        position_id=f"{stock_id}_{entry_row['date']}_{trade_row['date']}_{uuid.uuid4().hex[:8]}",
                        entry_date=entry_row["date"],
                        exit_date=trade_row["date"],
                        stock_id=stock_id,
                        stock_name=stock_name,
                        trade_direction=1 if self.parameters.get("trade_direction", "long") == "long" else -1,
                        entry_price=trade_row["current_entry_price"],
                        exit_price=trade_row["close"],
                        shares=trade_row["current_shares"],
                        profit_loss=trade_row["profit_loss"],
                        profit_loss_rate=trade_row["profit_loss_rate"],
                        commission=trade_row["commission"],
                        securities_tax=trade_row["securities_tax"],
                        net_profit_loss=trade_row["net_profit_loss"],
                        exit_reason=trade_row.get("exit_reason", "向量化出場"),
                        holding_days=trade_row["holding_days"],
                        current_price=trade_row["close"],
                        unrealized_profit_loss=trade_row["profit_loss"],
                        unrealized_profit_loss_rate=trade_row["profit_loss_rate"],
                        current_date=trade_row["date"],
                        exit_price_type=self.parameters.get("exit_price_condition", "close"),
                        current_exit_price=trade_row["close"],
                        current_profit_loss=trade_row["profit_loss"],
                        current_profit_loss_rate=trade_row["profit_loss_rate"],
                        take_profit_price=0.0,
                        stop_loss_price=0.0,
                        open_price=trade_row["open"],
                        high_price=trade_row["high"],
                        low_price=trade_row["low"],
                        close_price=trade_row["close"]
                    )
                    
                    self.add_trade_record(trade_record)
            
            # 更新權益曲線
            for i in range(len(df)):
                row = df.row(i, named=True)
                self.update_equity_curve(row["cumulative_capital"], row["date"])
                
        except Exception as e:
            print_log(f"完全向量化回測執行失敗: {e}")
            # 如果完全向量化失敗，回退到混合模式
            self._execute_vectorized_backtest(stock_data, excel_pl_df, stock_id, stock_name)
    
    def get_strategy_result(self, initial_capital: float) -> Dict[str, Any]:
        """取得策略結果"""
        print_log(f"get_strategy_result")
        if not self.trade_records:
            return {
                "strategy_name": self.strategy_name,
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
                "equity_curve": self.equity_curve,
                "dates": self.dates,
                "parameters": self.parameters,
                "charts": self.supported_charts,
                "holding_positions": []
            }
        
        # 計算統計資料
        total_trades = len(self.trade_records)
        winning_trades = len([t for t in self.trade_records if t.net_profit_loss > 0])
        losing_trades = len([t for t in self.trade_records if t.net_profit_loss < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_profit_loss = sum(t.net_profit_loss for t in self.trade_records)
        total_profit_loss_rate = (total_profit_loss / initial_capital) * 100
        
        # 計算最大回撤
        max_drawdown = 0.0
        max_drawdown_rate = 0.0
        peak = initial_capital
        
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            drawdown_rate = (drawdown / peak) * 100
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_rate = drawdown_rate
        
        # 計算夏普比率
        if len(self.equity_curve) > 1:
            returns = []
            for i in range(1, len(self.equity_curve)):
                if self.equity_curve[i-1] > 0:
                    returns.append((self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1])
            
            if returns:
                avg_return = sum(returns) / len(returns)
                std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # 將 TradeRecord 物件轉換為字典
        trade_records_dict = []
        for trade in self.trade_records:
            trade_dict = {
                "position_id": trade.position_id,
                "entry_date": trade.entry_date.strftime("%Y-%m-%d") if trade.entry_date else "",
                "exit_date": trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else "",
                "stock_id": trade.stock_id,
                "stock_name": trade.stock_name,
                "trade_direction": trade.trade_direction,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "shares": trade.shares,
                "profit_loss": trade.profit_loss,
                "profit_loss_rate": trade.profit_loss_rate,
                "commission": trade.commission,
                "securities_tax": trade.securities_tax,
                "net_profit_loss": trade.net_profit_loss,
                "holding_days": trade.holding_days,
                "exit_reason": trade.exit_reason,
                "current_price": trade.current_price,
                "unrealized_profit_loss": trade.unrealized_profit_loss,
                "unrealized_profit_loss_rate": trade.unrealized_profit_loss_rate,
                "current_date": trade.current_date.strftime("%Y-%m-%d") if trade.current_date else "",
                "exit_price_type": trade.exit_price_type,
                "current_entry_price": trade.current_entry_price,
                "current_exit_price": trade.current_exit_price,
                "current_profit_loss": trade.current_profit_loss,
                "current_profit_loss_rate": trade.current_profit_loss_rate,
                "take_profit_price": trade.take_profit_price,
                "stop_loss_price": trade.stop_loss_price,
                "open_price": trade.open_price,
                "high_price": trade.high_price,
                "low_price": trade.low_price,
                "close_price": trade.close_price
            }
            trade_records_dict.append(trade_dict)
        
        # 將 HoldingPosition 物件轉換為字典
        holding_positions_dict = []
        for position in self.holding_positions:
            position_dict = {
                "position_id": position.position_id,
                "entry_date": position.entry_date.strftime("%Y-%m-%d") if position.entry_date else "",
                "stock_id": position.stock_id,
                "stock_name": position.stock_name,
                "trade_direction": position.trade_direction,
                "entry_price": position.entry_price,
                "shares": position.shares,
                "current_price": position.current_price,
                "unrealized_profit_loss": position.unrealized_profit_loss,
                "unrealized_profit_loss_rate": position.unrealized_profit_loss_rate,
                "holding_days": position.holding_days,
                "current_date": position.current_date.strftime("%Y-%m-%d") if position.current_date else "",
                "exit_price_type": position.exit_price_type,
                "current_entry_price": position.current_entry_price,
                "current_exit_price": position.current_exit_price,
                "current_profit_loss": position.current_profit_loss,
                "current_profit_loss_rate": position.current_profit_loss_rate,
                "take_profit_price": position.take_profit_price,
                "stop_loss_price": position.stop_loss_price,
                "open_price": position.open_price,
                "high_price": position.high_price,
                "low_price": position.low_price,
                "close_price": position.close_price
            }
            holding_positions_dict.append(position_dict)
        
        return {
            "strategy_name": self.strategy_name,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_profit_loss": total_profit_loss,
            "total_profit_loss_rate": total_profit_loss_rate,
            "max_drawdown": max_drawdown,
            "max_drawdown_rate": max_drawdown_rate,
            "sharpe_ratio": sharpe_ratio,
            "trade_records": trade_records_dict,
            "equity_curve": self.equity_curve,
            "dates": self.dates,
            "parameters": self.parameters,
            "charts": self.supported_charts,
            "holding_positions": holding_positions_dict
        }
    
    def _execute_function(self, function_name: str, *args, **kwargs):
        """執行策略函數"""
        print_log(f"_execute_function")
        if function_name in self.compiled_code:
            try:
                # 取得函數對象
                func = self.compiled_code[function_name]
                
                # 為 Jupyter 模式注入 DataFrame 變數
                if hasattr(self, '_last_df') and self._last_df is not None:
                    # 將 DataFrame 變數注入到函數的 globals 中
                    func_globals = func.__globals__.copy()
                    func_globals['df'] = self._last_df
                    func_globals['stock_df'] = self._last_stock_df
                    func_globals['parameters'] = self.parameters
                    
                    # 創建新的函數對象，使用更新的 globals
                    import types
                    new_func = types.FunctionType(
                        func.__code__,
                        func_globals,
                        func.__name__,
                        func.__defaults__,
                        func.__closure__
                    )
                    func = new_func
                
                # 檢查函數的參數數量
                import inspect
                sig = inspect.signature(func)
                param_count = len(sig.parameters)

                # 根據參數數量調整傳遞的參數
                if param_count == 1 and len(args) > 1:
                    # 如果函數只接受一個參數，但我們傳遞了多個，只傳遞第一個
                    return func(args[0], **kwargs)
                elif param_count == 0 and len(args) > 0:
                    # 如果函數不接受參數，但我們傳遞了參數，不傳遞任何參數
                    return func(**kwargs)
                else:
                    # 正常情況，傳遞所有參數
                    return func(*args, **kwargs)
                
            except ValueError as e:
                if "max() arg is an empty sequence" in str(e):
                    # 對於 max() 錯誤，返回安全的預設值
                    if function_name == 'should_entry':
                        return False, {}
                    elif function_name == 'should_exit':
                        return False, {}
                    elif function_name == 'calculate_entry_price':
                        return 0.0
                    elif function_name == 'calculate_shares':
                        return 0
                    else:
                        return None
                else:
                    print_log(f"-------_execute_function------ValueError: {e}")
                    raise e
            except Exception as e:
                print_log(f"-------_execute_function------e: {e}")
                raise e
        else:
            raise ValueError(f"策略函數 {function_name} 不存在")
    
    @property
    def required_parameters(self) -> List[str]:
        print_log(f"required_parameters")
        return ["commission_rate", "commission_discount", "securities_tax_rate", "shares_per_trade"]
    
    @property
    def supported_charts(self) -> List[str]:
        print_log(f"supported_charts")
        return ["price_chart", "volume_chart", "profit_loss_chart"]
    
    @property
    def data_source(self) -> str:
        print_log(f"data_source")
        return "excel"
    
    @property
    def stock_source(self) -> str:
        print_log(f"stock_source")
        return "excel"
    
    @property
    def need_date_range(self) -> bool:
        print_log(f"need_date_range")
        return False 