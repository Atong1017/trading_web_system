# 交易設定檔
from typing import Dict, Any, List

class TradingConfig:
    """交易設定類別"""
    
    # 交易時間設定
    MARKET_OPEN_TIME = "09:00:00"
    MARKET_CLOSE_TIME = "13:30:00"
    PRE_MARKET_TIME = "08:30:00"
    POST_MARKET_TIME = "14:00:00"
    
    # 手續費設定
    COMMISSION_RATE = 0.001425  # 手續費率 0.1425%
    MIN_COMMISSION = 20  # 最低手續費 20元
    MAX_COMMISSION = 1000000  # 最高手續費 1000元
    
    # 證交稅設定
    SECURITIES_TAX_RATE = 0.003  # 證交稅率 0.3%
    
    # 漲跌停設定
    UP_LIMIT_PERCENT = 10.0  # 漲停百分比
    DOWN_LIMIT_PERCENT = -10.0  # 跌停百分比
    
    # 零股交易設定
    ODD_LOT_ENABLED = True  # 是否啟用零股交易
    ODD_LOT_MIN_UNITS = 1  # 零股最小單位
    
    # 風險控制設定
    MAX_POSITION_SIZE = 0.1  # 單一股票最大部位比例 10%
    MAX_DAILY_LOSS = 0.05  # 單日最大虧損比例 5%
    MAX_TOTAL_LOSS = 0.2  # 總虧損最大比例 20%
    
    # 回測設定
    BACKTEST_INITIAL_CAPITAL = 1000000.0  # 回測初始資金 100萬
    BACKTEST_COMMISSION_ENABLED = True  # 回測是否包含手續費
    BACKTEST_SLIPPAGE_ENABLED = True  # 回測是否包含滑點
    
    # 滑點設定
    DEFAULT_SLIPPAGE = 0.001  # 預設滑點 0.1%
    
    # 布林參數配置 - 統一管理所有布林類型參數
    BOOLEAN_PARAMETERS = {
        "use_limit_restriction": {
            "name": "使用漲跌停限制",
            "description": "是否使用漲跌停限制進行交易",
            "default": True
        },
        "use_take_profit": {
            "name": "使用停利",
            "description": "是否使用停利機制",
            "default": True
        },
        "use_stop_loss": {
            "name": "使用停損",
            "description": "是否使用停損機制",
            "default": True
        },
        "use_max_holding_days": {
            "name": "使用最大持有天數",
            "description": "是否使用最大持有天數限制",
            "default": True
        },
        "force_exit": {
            "name": "強制出場",
            "description": "是否在回測結束時強制出場",
            "default": False
        },
        "use_limit_orders": {
            "name": "使用漲跌停單",
            "description": "是否使用漲跌停單進行交易",
            "default": True
        }
    }
    
    # 浮點數參數配置 - 統一管理所有浮點數類型參數
    FLOAT_PARAMETERS = {
        "commission_rate": {
            "name": "手續費率",
            "description": "交易手續費率",
            "default": 0.001425,
            "min": 0.0,
            "max": 0.1
        },
        "commission_discount": {
            "name": "手續費折扣",
            "description": "手續費折扣率",
            "default": 0.0,
            "min": 0.0,
            "max": 1.0
        },
        "securities_tax_rate": {
            "name": "證交稅率",
            "description": "證券交易稅率",
            "default": 0.003,
            "min": 0.0,
            "max": 0.1
        },
        "take_profit_percentage": {
            "name": "停利百分比",
            "description": "停利百分比",
            "default": 0.2,
            "min": 0.01,
            "max": 1.0
        },
        "stop_loss_percentage": {
            "name": "停損百分比",
            "description": "停損百分比",
            "default": -0.2,
            "min": -1.0,
            "max": -0.01
        },
        "limit_percentage": {
            "name": "漲跌停百分比",
            "description": "漲跌停百分比",
            "default": 10.0,
            "min": 1.0,
            "max": 50.0
        },
        "position_size": {
            "name": "部位大小",
            "description": "每次交易的部位大小比例",
            "default": 0.1,
            "min": 0.01,
            "max": 1.0
        },
        "up_limit_percentage": {
            "name": "漲停百分比",
            "description": "漲停百分比",
            "default": 10.0,
            "min": 1.0,
            "max": 50.0
        },
        "down_limit_percentage": {
            "name": "跌停百分比",
            "description": "跌停百分比",
            "default": -10.0,
            "min": -50.0,
            "max": -1.0
        }
    }
    
    # 整數參數配置 - 統一管理所有整數類型參數
    INT_PARAMETERS = {
        "shares_per_trade": {
            "name": "每次交易股數",
            "description": "每次交易的股數",
            "default": 1000,
            "min": 1,
            "max": 1000000
        },
        "max_holding_days": {
            "name": "最大持有天數",
            "description": "最大持有天數",
            "default": 30,
            "min": 1,
            "max": 365
        },
        "high_period": {
            "name": "新高計算期間",
            "description": "計算新高的期間",
            "default": 20,
            "min": 5,
            "max": 60
        },
        "low_period": {
            "name": "新低計算期間",
            "description": "計算新低的期間",
            "default": 20,
            "min": 5,
            "max": 60
        },
        "max_holding_time": {
            "name": "最大持有時間",
            "description": "最大持有時間（天）",
            "default": 1,
            "min": 1,
            "max": 7
        },
        "announcement_delay": {
            "name": "公告延遲天數",
            "description": "公告延遲天數",
            "default": 1,
            "min": 0,
            "max": 10
        }
    }
    
    # 字串參數配置 - 統一管理所有字串類型參數
    STRING_PARAMETERS = {
        "strategy_name": {
            "name": "策略名稱",
            "description": "策略的名稱",
            "default": "",
            "max_length": 100
        },
        "strategy_description": {
            "name": "策略描述",
            "description": "策略的描述",
            "default": "",
            "max_length": 500
        }
    }
    
    # 特殊參數配置 - 需要特殊處理的參數
    SPECIAL_PARAMETERS = {
        "record_holdings": {
            "name": "記錄持有",
            "description": "是否記錄持有狀況",
            "type": "int",  # 特殊：轉換為 0/1
            "default": 0
        }
    }
    
    # 策略預設參數
    STRATEGY_DEFAULTS = {
        "day_trading": {
            "name": "當沖策略",
            "description": "當日沖銷策略，以漲跌停為進出場依據",
            "parameters": {
                "use_limit_orders": {
                    "type": "boolean",
                    "label": "使用漲跌停單",
                    "default": True
                },
                "max_holding_time": {
                    "type": "number",
                    "label": "最大持有天數",
                    "default": 1,
                    "min": 1,
                    "max": 7
                },
                "force_exit": {
                    "type": "boolean",
                    "label": "強制出場",
                    "default": False
                }
            },
            "charts": ["price_chart", "volume_chart", "profit_loss_chart"],
            "data_source": "excel",  # excel, api
            "stock_source": "excel"  # excel, api
        },
        "swing_trading": {
            "name": "波段策略",
            "description": "波段交易策略，以20日新高為進場依據",
            "parameters": {
                "take_profit": {
                    "type": "number",
                    "label": "停利比例",
                    "default": 0.2,
                    "min": 0.01,
                    "max": 1.0,
                    "step": 0.01
                },
                "stop_loss": {
                    "type": "number",
                    "label": "停損比例",
                    "default": -0.2,
                    "min": -1.0,
                    "max": -0.01,
                    "step": 0.01
                },
                "max_holding_days": {
                    "type": "number",
                    "label": "最大持有天數",
                    "default": 30,
                    "min": 1,
                    "max": 365
                },
                "force_exit": {
                    "type": "boolean",
                    "label": "強制出場",
                    "default": True
                },
                "high_period": {
                    "type": "number",
                    "label": "新高計算期間",
                    "default": 20,
                    "min": 5,
                    "max": 60
                }
            },
            "charts": ["price_chart", "volume_chart", "profit_loss_chart", "drawdown_chart"],
            "data_source": "excel",  # excel, api
            "stock_source": "excel"  # excel, api
        },
        "bookbuilding": {
            "name": "詢圈公告策略",
            "description": "詢圈公告策略，基於詢圈公告進行交易",
            "parameters": {
                "announcement_delay": {
                    "type": "number",
                    "label": "公告延遲天數",
                    "default": 1,
                    "min": 0,
                    "max": 10
                },
                "position_size": {
                    "type": "number",
                    "label": "部位大小比例",
                    "default": 0.1,
                    "min": 0.01,
                    "max": 1.0,
                    "step": 0.01
                },
                "max_holding_days": {
                    "type": "number",
                    "label": "最大持有天數",
                    "default": 30,
                    "min": 1,
                    "max": 365
                }
            },
            "charts": ["price_chart", "volume_chart", "profit_loss_chart"],
            "data_source": "api",  # 詢圈公告策略只支援API
            "stock_source": "api",   # 詢圈公告策略只支援API
            "need_date_range": True  # 需要指定開始和結束年度
        }
    }
    
    # 圖表類型
    CHART_TYPES = {
        "price_chart": {
            "name": "價格圖表",
            "description": "顯示股票價格走勢",
            "type": "candlestick"
        },
        "volume_chart": {
            "name": "成交量圖表",
            "description": "顯示成交量變化",
            "type": "bar"
        },
        "profit_loss_chart": {
            "name": "損益圖表",
            "description": "顯示策略損益變化",
            "type": "line"
        },
        "drawdown_chart": {
            "name": "回撤圖表",
            "description": "顯示最大回撤",
            "type": "area"
        },
        "trade_points_chart": {
            "name": "交易點位圖表",
            "description": "顯示進出場點位",
            "type": "scatter"
        }
    }
    
    # Excel匯出欄位設定
    EXPORT_COLUMNS = {
        "basic": [
            "交易日期", "股票代碼", "股票名稱", "交易方向", 
            "進場價", "出場價", "股數", "損益", "損益率"
        ],
        "detailed": [
            "交易日期", "股票代碼", "股票名稱", "交易方向", 
            "進場價", "出場價", "開盤價", "最高價", "最低價", "收盤價",
            "股數", "損益", "損益率", "手續費", "證交稅", "淨損益",
            "停利價", "停損價", "出場原因", "持有天數"
        ],
        "custom": []  # 自訂欄位
    }
    
    @classmethod
    def get_boolean_parameters(cls) -> Dict[str, Dict[str, Any]]:
        """取得所有布林參數配置"""
        return cls.BOOLEAN_PARAMETERS
    
    @classmethod
    def get_boolean_parameter_names(cls) -> List[str]:
        """取得所有布林參數名稱列表"""
        return list(cls.BOOLEAN_PARAMETERS.keys())
    
    @classmethod
    def is_boolean_parameter(cls, param_name: str) -> bool:
        """檢查參數是否為布林類型"""
        return param_name in cls.BOOLEAN_PARAMETERS
    
    @classmethod
    def get_boolean_parameter_default(cls, param_name: str) -> bool:
        """取得布林參數的預設值"""
        return cls.BOOLEAN_PARAMETERS.get(param_name, {}).get("default", False)
    
    @classmethod
    def get_float_parameters(cls) -> Dict[str, Dict[str, Any]]:
        """取得所有浮點數參數配置"""
        return cls.FLOAT_PARAMETERS
    
    @classmethod
    def get_float_parameter_names(cls) -> List[str]:
        """取得所有浮點數參數名稱列表"""
        return list(cls.FLOAT_PARAMETERS.keys())
    
    @classmethod
    def is_float_parameter(cls, param_name: str) -> bool:
        """檢查參數是否為浮點數類型"""
        return param_name in cls.FLOAT_PARAMETERS
    
    @classmethod
    def get_float_parameter_default(cls, param_name: str) -> float:
        """取得浮點數參數的預設值"""
        return cls.FLOAT_PARAMETERS.get(param_name, {}).get("default", 0.0)
    
    @classmethod
    def get_int_parameters(cls) -> Dict[str, Dict[str, Any]]:
        """取得所有整數參數配置"""
        return cls.INT_PARAMETERS
    
    @classmethod
    def get_int_parameter_names(cls) -> List[str]:
        """取得所有整數參數名稱列表"""
        return list(cls.INT_PARAMETERS.keys())
    
    @classmethod
    def is_int_parameter(cls, param_name: str) -> bool:
        """檢查參數是否為整數類型"""
        return param_name in cls.INT_PARAMETERS
    
    @classmethod
    def get_int_parameter_default(cls, param_name: str) -> int:
        """取得整數參數的預設值"""
        return cls.INT_PARAMETERS.get(param_name, {}).get("default", 0)
    
    @classmethod
    def get_string_parameters(cls) -> Dict[str, Dict[str, Any]]:
        """取得所有字串參數配置"""
        return cls.STRING_PARAMETERS
    
    @classmethod
    def get_string_parameter_names(cls) -> List[str]:
        """取得所有字串參數名稱列表"""
        return list(cls.STRING_PARAMETERS.keys())
    
    @classmethod
    def is_string_parameter(cls, param_name: str) -> bool:
        """檢查參數是否為字串類型"""
        return param_name in cls.STRING_PARAMETERS
    
    @classmethod
    def get_string_parameter_default(cls, param_name: str) -> str:
        """取得字串參數的預設值"""
        return cls.STRING_PARAMETERS.get(param_name, {}).get("default", "")
    
    @classmethod
    def get_special_parameters(cls) -> Dict[str, Dict[str, Any]]:
        """取得所有特殊參數配置"""
        return cls.SPECIAL_PARAMETERS
    
    @classmethod
    def get_special_parameter_names(cls) -> List[str]:
        """取得所有特殊參數名稱列表"""
        return list(cls.SPECIAL_PARAMETERS.keys())
    
    @classmethod
    def is_special_parameter(cls, param_name: str) -> bool:
        """檢查參數是否為特殊類型"""
        return param_name in cls.SPECIAL_PARAMETERS
    
    @classmethod
    def get_special_parameter_default(cls, param_name: str) -> Any:
        """取得特殊參數的預設值"""
        return cls.SPECIAL_PARAMETERS.get(param_name, {}).get("default", None)
    
    @classmethod
    def get_parameter_type(cls, param_name: str) -> str:
        """取得參數的類型"""
        if cls.is_boolean_parameter(param_name):
            return "boolean"
        elif cls.is_float_parameter(param_name):
            return "float"
        elif cls.is_int_parameter(param_name):
            return "int"
        elif cls.is_string_parameter(param_name):
            return "string"
        elif cls.is_special_parameter(param_name):
            return cls.SPECIAL_PARAMETERS.get(param_name, {}).get("type", "unknown")
        else:
            return "unknown"
    
    @classmethod
    def get_all_parameter_names(cls) -> List[str]:
        """取得所有參數名稱列表"""
        all_params = []
        all_params.extend(cls.get_boolean_parameter_names())
        all_params.extend(cls.get_float_parameter_names())
        all_params.extend(cls.get_int_parameter_names())
        all_params.extend(cls.get_string_parameter_names())
        all_params.extend(cls.get_special_parameter_names())
        return all_params
    
    @classmethod
    def get_parameter_info(cls, param_name: str) -> Dict[str, Any]:
        """取得參數的完整資訊"""
        if cls.is_boolean_parameter(param_name):
            return cls.BOOLEAN_PARAMETERS.get(param_name, {})
        elif cls.is_float_parameter(param_name):
            return cls.FLOAT_PARAMETERS.get(param_name, {})
        elif cls.is_int_parameter(param_name):
            return cls.INT_PARAMETERS.get(param_name, {})
        elif cls.is_string_parameter(param_name):
            return cls.STRING_PARAMETERS.get(param_name, {})
        elif cls.is_special_parameter(param_name):
            return cls.SPECIAL_PARAMETERS.get(param_name, {})
        else:
            return {}
    
    @classmethod
    def get_strategy_config(cls, strategy_name: str) -> Dict[str, Any]:
        """取得策略設定"""
        return cls.STRATEGY_DEFAULTS.get(strategy_name, {})
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """取得可用策略列表"""
        return list(cls.STRATEGY_DEFAULTS.keys())
    
    @classmethod
    def get_chart_config(cls, chart_name: str) -> Dict[str, Any]:
        """取得圖表設定"""
        return cls.CHART_TYPES.get(chart_name, {})
    
    @classmethod
    def get_available_charts(cls) -> List[str]:
        """取得可用圖表列表"""
        return list(cls.CHART_TYPES.keys())
    
    @classmethod
    def calculate_commission(cls, trade_amount: float) -> float:
        """計算手續費"""
        commission = trade_amount * cls.COMMISSION_RATE
        return max(cls.MIN_COMMISSION, min(commission, cls.MAX_COMMISSION))
    
    @classmethod
    def calculate_securities_tax(cls, trade_amount: float) -> float:
        """計算證交稅"""
        return trade_amount * cls.SECURITIES_TAX_RATE 