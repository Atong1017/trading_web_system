# 策略基礎類別
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import polars as pl
from datetime import datetime
from dataclasses import dataclass

def print_log(message):
    print(f"********** base_strategy.py - {message}")

@dataclass
class TradeRecord:
    """交易記錄資料類別"""
    position_id: str  # 唯一識別符：stock_id + entry_date + entry_time
    entry_date: datetime
    exit_date: datetime
    stock_id: str
    stock_name: str
    trade_direction: int  # 1: 做多, -1: 做空
    entry_price: float
    exit_price: float
    shares: int
    profit_loss: float
    profit_loss_rate: float
    commission: float
    securities_tax: float
    net_profit_loss: float  # 實際淨損益
    holding_days: int = 0
    exit_reason: str = ""
    # 與 HoldingPosition 相同的欄位，用於 Excel 匯出
    current_price: float = 0.0  # 當前價格（出場時等於 exit_price）
    unrealized_profit_loss: float = 0.0  # 未實現損益（出場時等於 profit_loss）
    unrealized_profit_loss_rate: float = 0.0  # 未實現損益率（出場時等於 profit_loss_rate）
    current_date: Optional[datetime] = None  # 當前日期（出場時等於 exit_date）
    exit_price_type: str = "close"  # 出場價類型
    current_entry_price: float = 0.0  # 當日進場價格
    current_exit_price: float = 0.0  # 當前出場價格（出場時等於 exit_price）
    current_profit_loss: float = 0.0  # 當前損益（出場時等於 profit_loss）
    current_profit_loss_rate: float = 0.0  # 當前損益率（出場時等於 profit_loss_rate）
    take_profit_price: float = 0.0
    stop_loss_price: float = 0.0
    open_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    close_price: float = 0.0

@dataclass
class HoldingPosition:
    """持有未出場部位資料類別"""
    position_id: str  # 唯一識別符：stock_id + entry_date + entry_time
    entry_date: datetime
    stock_id: str
    stock_name: str
    trade_direction: int  # 1: 做多, -1: 做空
    entry_price: float
    shares: int
    current_price: float
    unrealized_profit_loss: float
    unrealized_profit_loss_rate: float
    holding_days: int
    current_date: datetime  # 未出場日期(或持有日期)
    exit_price_type: str  # 出場價類型：open, close, high, low
    current_entry_price: float  # 當日進場價
    current_exit_price: float  # 當日未出場價
    current_profit_loss: float  # 未出場報酬
    current_profit_loss_rate: float  # 未出場報酬率
    take_profit_price: float = 0.0
    stop_loss_price: float = 0.0
    open_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    close_price: float = 0.0

@dataclass
class StrategyResult:
    """策略回測結果資料類別"""
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit_loss: float
    total_profit_loss_rate: float
    max_drawdown: float
    max_drawdown_rate: float
    sharpe_ratio: float
    trade_records: List[TradeRecord]
    equity_curve: List[float]
    dates: List[datetime]
    parameters: Dict[str, Any]
    charts: List[str]

class BaseStrategy(ABC):
    """策略基礎類別"""
    
    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters
        self.trade_records: List[TradeRecord] = []
        self.holding_positions: List[HoldingPosition] = []  # 持有未出場部位列表
        self.equity_curve: List[float] = []
        self.dates: List[datetime] = []
        self.current_position: Optional[Dict[str, Any]] = None
        self._validate_parameters()
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """取得策略名稱"""
        pass
    
    @property
    @abstractmethod
    def strategy_description(self) -> str:
        """取得策略描述"""
        pass
    
    @property
    @abstractmethod
    def parameter_sources(self) -> Dict[str, Dict[str, Any]]:
        """
        取得策略所需的參數來源
        
        Returns:
            Dict[str, Dict[str, Any]]: 參數來源配置
            例如：
            {
                "stock_source": {
                    "type": "excel",  # 或 "api", "manual"
                    "required": True,
                    "description": "股票代碼來源",
                    "columns": ["stock_id", "date"]  # Excel模式需要的欄位
                },
                "price_source": {
                    "type": "api",  # 或 "excel"
                    "required": True,
                    "description": "股價資料來源"
                },
                "date_range": {
                    "type": "manual",  # 或 "excel"
                    "required": False,
                    "description": "日期範圍設定"
                }
            }
        """
        pass
    
    @property
    @abstractmethod
    def strategy_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        取得策略參數配置
        
        Returns:
            Dict[str, Dict[str, Any]]: 策略參數配置
        """
        pass
    
    @abstractmethod
    def process_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理策略參數，包括各種來源的參數
        
        Args:
            parameters (Dict[str, Any]): 包含各種來源的參數
            
        Returns:
            Dict[str, Any]: 處理後的參數，包含：
                - stock_ids: List[str] - 股票代碼列表
                - start_date: datetime - 開始日期
                - end_date: datetime - 結束日期
                - price_data: pl.DataFrame - 股價資料（如果提供）
        """
        pass
    
    @abstractmethod
    def validate_special_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        驗證策略特定的參數
        
        Args:
            parameters (Dict[str, Any]): 包含各種來源的參數
            
        Raises:
            ValueError: 當必要參數缺失或無效時
        """
        pass
    
    @abstractmethod
    async def process_api_data(self, stock_data: pl.DataFrame, stock_api) -> pl.DataFrame:
        """
        處理API取得的資料，每個策略可能有不同的處理邏輯
        
        Args:
            stock_data (pl.DataFrame): 從API取得的股價資料
            stock_api: StockAPI實例
            
        Returns:
            pl.DataFrame: 處理後的股價資料
        """
        pass
    
    @abstractmethod
    def run_backtest(self, stock_data: pl.DataFrame, initial_capital: float, stock_id: str, stock_name: str):
        """執行回測"""
        pass
    
    @abstractmethod
    def get_strategy_result(self, initial_capital: float) -> Dict[str, Any]:
        """取得策略結果"""
        pass
    
    def validate_parameters(self) -> bool:
        """驗證策略參數"""
        return True
    
    def _validate_parameters(self):
        """內部方法，用於驗證策略參數"""
        # 實現參數驗證邏輯
        pass
    
    @property
    @abstractmethod
    def required_parameters(self) -> List[str]:
        """必要參數列表"""
        pass
    
    @property
    @abstractmethod
    def supported_charts(self) -> List[str]:
        """支援的圖表類型"""
        pass
    
    @property
    @abstractmethod
    def data_source(self) -> str:
        """資料來源類型 (excel, api)"""
        pass
    
    @property
    @abstractmethod
    def stock_source(self) -> str:
        """股票來源類型 (excel, api)"""
        pass
    
    @property
    @abstractmethod
    def need_date_range(self) -> bool:
        """是否需要指定日期範圍"""
        pass
    
    @abstractmethod
    def process_excel_data(self, excel_data: pl.DataFrame) -> Dict[str, Any]:
        """
        處理Excel資料，每個策略有自己的處理邏輯
        
        Args:
            excel_data (pl.DataFrame): 原始Excel資料
            
        Returns:
            Dict[str, Any]: 處理後的資料，包含：
                - stock_ids: List[str] - 股票代碼列表
                - start_date: datetime - 開始日期
                - end_date: datetime - 結束日期
                - processed_data: pl.DataFrame - 處理後的資料（如果需要）
        """
        pass
    
    def calculate_entry_price(self, stock_data: pl.DataFrame, current_index: int) -> float:
        """計算進場價格"""
        row = stock_data.row(current_index, named=True)
        
        # 使用 get_parameter_value 來正確解析參數
        if hasattr(self, 'get_parameter_value'):
            # 如果是 DynamicStrategy，使用 get_parameter_value
            entry_type = self.get_parameter_value('entry_type', 'open')
        else:
            # 如果是其他策略，直接從 parameters 取得
            entry_type = self.parameters.get('entry_type', 'open')
        
        if entry_type == 'open':
            return row['open']
        elif entry_type == 'close':
            return row['close']
        else:
            # 預設使用開盤價
            return row['open']
    
    def calculate_exit_price(self, stock_data: pl.DataFrame, current_index: int, 
                           exit_type: str) -> float:
        """計算出場價格"""
        row = stock_data.row(current_index, named=True)
        
        if exit_type == "收盤":
            return row['close']
        elif exit_type == "開盤":
            return row['open']
        elif exit_type == "最高":
            return row['high']
        elif exit_type == "最低":
            return row['low']
        else:
            return row['close']  # 預設收盤價
    
    def calculate_shares(self, capital: float, price: float, 
                        share_type: str = "整股") -> int:
        """計算股數"""
        from core.price_utils import PriceUtils
        return PriceUtils.calculate_shares(capital, price, share_type)
    
    def calculate_commission(self, trade_amount: float) -> float:
        """計算手續費"""
        from config.trading_config import TradingConfig
        return TradingConfig.calculate_commission(trade_amount)
    
    def calculate_securities_tax(self, trade_amount: float) -> float:
        """計算證交稅"""
        from config.trading_config import TradingConfig
        return TradingConfig.calculate_securities_tax(trade_amount)
    
    def add_trade_record(self, trade_record: TradeRecord) -> None:
        """新增交易記錄"""
        self.trade_records.append(trade_record)
    
    def add_holding_position(self, holding_position: HoldingPosition) -> None:
        """新增持有未出場部位"""
        # 檢查是否啟用持有記錄功能
        record_holdings = self.parameters.get('record_holdings', 0)
        print(f"DEBUG: record_holdings = {record_holdings}, type = {type(record_holdings)}")
        if record_holdings == 1:
            print(f"DEBUG: 新增持有部位: {holding_position.stock_id} (ID: {holding_position.position_id})")
            self.holding_positions.append(holding_position)
        else:
            print(f"DEBUG: 持有記錄功能未啟用，跳過新增持有部位")
    
    def update_holding_position(self, position_id: str, current_price: float, current_date: datetime, 
                               current_row: Dict[str, Any] = None, exit_price_type: str = "close") -> None:
        """根據 position_id 更新持有部位的當前價格和未實現損益"""
        if self.parameters.get('record_holdings', 0) != 1:
            return
        for position in self.holding_positions:
            if position.position_id == position_id:
                position.current_price = current_price
                position.current_date = current_date
                position.holding_days = (current_date - position.entry_date).days
                
                # 根據出場價類型設定當日未出場價
                if current_row:
                    if exit_price_type == "open":
                        position.current_exit_price = current_row.get("open", current_price)
                    elif exit_price_type == "close":
                        position.current_exit_price = current_row.get("close", current_price)
                    elif exit_price_type == "high":
                        position.current_exit_price = current_row.get("high", current_price)
                    elif exit_price_type == "low":
                        position.current_exit_price = current_row.get("low", current_price)
                    else:
                        position.current_exit_price = current_price
                    
                    # 更新其他價格欄位
                    position.open_price = current_row.get("open", 0.0)
                    position.high_price = current_row.get("high", 0.0)
                    position.low_price = current_row.get("low", 0.0)
                    position.close_price = current_row.get("close", 0.0)
                else:
                    position.current_exit_price = current_price
                
                # 計算未出場報酬（使用當日未出場價）
                if position.trade_direction == 1:  # 做多
                    position.unrealized_profit_loss = (current_price - position.entry_price) * position.shares
                    position.unrealized_profit_loss_rate = ((current_price - position.entry_price) / position.entry_price) * 100
                    position.current_profit_loss = (position.current_exit_price - position.entry_price) * position.shares
                    position.current_profit_loss_rate = ((position.current_exit_price - position.entry_price) / position.entry_price) * 100
                else:  # 做空
                    position.unrealized_profit_loss = (position.entry_price - current_price) * position.shares
                    position.unrealized_profit_loss_rate = ((position.entry_price - current_price) / position.entry_price) * 100
                    position.current_profit_loss = (position.entry_price - position.current_exit_price) * position.shares
                    position.current_profit_loss_rate = ((position.entry_price - position.current_exit_price) / position.entry_price) * 100
                
                position.exit_price_type = exit_price_type
                break
    
    def remove_holding_position(self, position_id: str) -> None:
        """根據 position_id 移除持有部位記錄"""
        record_holdings = self.parameters.get('record_holdings', 0)
        if record_holdings == 1:
            print(f"DEBUG: 移除持有部位: {position_id}")
            self.holding_positions = [pos for pos in self.holding_positions if pos.position_id != position_id]
        else:
            print(f"DEBUG: 持有記錄功能未啟用，跳過移除持有部位")
    
    def get_holding_positions_data(self) -> pl.DataFrame:
        """取得持有部位資料用於匯出"""
        if not self.holding_positions:
            return pl.DataFrame()
        
        # 轉換持有部位為字典列表
        data = []
        for position in self.holding_positions:
            position_dict = {
                "position_id": position.position_id,
                "entry_date": position.entry_date.strftime("%Y-%m-%d") if position.entry_date else "",
                "stock_id": position.stock_id,
                "stock_name": position.stock_name,
                "trade_direction": "買入" if position.trade_direction == 1 else "賣出",
                "entry_price": position.entry_price,
                "current_price": position.current_price,
                "shares": position.shares,
                "unrealized_profit_loss": position.unrealized_profit_loss,
                "unrealized_profit_loss_rate": position.unrealized_profit_loss_rate,
                "holding_days": position.holding_days,
                "current_date": position.current_date.strftime("%Y-%m-%d") if position.current_date else "",
                "current_exit_price": position.current_exit_price,
                "current_profit_loss": position.current_profit_loss,
                "current_profit_loss_rate": position.current_profit_loss_rate,
                "exit_price_type": position.exit_price_type,
                "take_profit_price": position.take_profit_price,
                "stop_loss_price": position.stop_loss_price,
                "open_price": position.open_price,
                "high_price": position.high_price,
                "low_price": position.low_price,
                "close_price": position.close_price
            }
            data.append(position_dict)
        
        return pl.DataFrame(data)
    
    def update_equity_curve(self, current_capital: float, date: datetime) -> None:
        """更新權益曲線"""
        self.equity_curve.append(current_capital)
        self.dates.append(date)
    
    def get_export_data(self, export_type: str = "detailed") -> pl.DataFrame:
        """
        取得匯出資料
        
        Args:
            export_type (str): 匯出類型 (detailed, basic)
            
        Returns:
            pl.DataFrame: 匯出資料
        """
        if not self.trade_records:
            return pl.DataFrame()
        
        # 轉換交易記錄為字典列表
        data = []
        for trade in self.trade_records:
            trade_dict = {
                "position_id": trade.position_id,
                "entry_date": trade.entry_date.strftime("%Y-%m-%d") if trade.entry_date else "",
                "exit_date": trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else "",
                "stock_id": trade.stock_id,
                "stock_name": trade.stock_name,
                "trade_direction": "買入" if trade.trade_direction == 1 else "賣出",
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "shares": trade.shares,
                "profit_loss": trade.profit_loss,
                "profit_loss_rate": trade.profit_loss_rate,
                "commission": trade.commission,
                "securities_tax": trade.securities_tax,
                "net_profit_loss": trade.net_profit_loss,
                "take_profit_price": trade.take_profit_price,
                "stop_loss_price": trade.stop_loss_price,
                "exit_reason": trade.exit_reason,
                "holding_days": trade.holding_days,
                "current_price": trade.current_price,
                "unrealized_profit_loss": trade.unrealized_profit_loss,
                "unrealized_profit_loss_rate": trade.unrealized_profit_loss_rate,
                "current_date": trade.current_date.strftime("%Y-%m-%d") if trade.current_date else "",
                "exit_price_type": trade.exit_price_type,
                "current_entry_price": trade.current_entry_price,
                "current_exit_price": trade.current_exit_price,
                "current_profit_loss": trade.current_profit_loss,
                "current_profit_loss_rate": trade.current_profit_loss_rate,
                "open_price": trade.open_price,
                "high_price": trade.high_price,
                "low_price": trade.low_price,
                "close_price": trade.close_price
            }
            
            if export_type == "basic":
                # 基本匯出只包含重要欄位
                basic_fields = ["entry_date", "stock_id", "stock_name", "trade_direction", 
                              "entry_price", "exit_price", "shares", "profit_loss", "profit_loss_rate"]
                trade_dict = {k: v for k, v in trade_dict.items() if k in basic_fields}
            
            data.append(trade_dict)
        
        return pl.DataFrame(data)
    
    def reset(self) -> None:
        """重置策略狀態"""
        self.trade_records.clear()
        self.holding_positions.clear()
        self.equity_curve.clear()
        self.dates.clear()
        self.current_position = None 