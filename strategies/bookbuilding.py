# 詢圈公告策略
from typing import Dict, List, Any, Optional, Tuple
import polars as pl
from datetime import datetime, timedelta
import uuid
from strategies.base_strategy import BaseStrategy, TradeRecord, HoldingPosition
from core.price_utils import PriceUtils
from core.utils import Utils

def print_log(message: str):
    print(f"****** bookbuilding.py : {message}")

class BookbuildingStrategy(BaseStrategy):
    """詢圈公告策略"""
    
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(parameters)
        self.trade_records: List[TradeRecord] = []
        self.equity_curve: List[float] = []
        self.dates: List[datetime] = []
        self.active_positions = []  # 改為追蹤多個活躍部位
        
        # 共用參數
        self._common_parameters = [
            "commission_rate", "commission_discount", "securities_tax_rate", "shares_per_trade", "share_type"
        ]
        
        # 策略專用參數
        self._strategy_parameters = [
            "announcement_delay", "position_size", "max_holding_days", "force_exit"
        ]
        
        self._required_parameters = self._common_parameters + self._strategy_parameters
        self._supported_charts = ["price_chart", "volume_chart", "profit_loss_chart"]
        self._data_source = "excel"
        self._stock_source = "excel"
        self._need_date_range = True
        
        # 從 trading_config 取得基礎參數
        from config.trading_config import TradingConfig
        
        # 設定共用參數預設值
        self.parameters.setdefault("commission_rate", TradingConfig.COMMISSION_RATE)  # 手續費率
        self.parameters.setdefault("commission_discount", 0.3)   # 手續費折數
        self.parameters.setdefault("securities_tax_rate", TradingConfig.SECURITIES_TAX_RATE) # 波段證交稅率
        self.parameters.setdefault("shares_per_trade", 1000)     # 每次交易股數
        self.parameters.setdefault("share_type", "mixed")        # 股數類型：mixed(整股+零股)、whole(整股)、fractional(零股)
        self.parameters.setdefault("record_holdings", 0)         # 持有記錄功能，預設關閉
        
        # 設定策略參數預設值
        self.parameters.setdefault("announcement_delay", 1)      # 公告延遲天數
        self.parameters.setdefault("position_size", 0.1)         # 部位大小比例
        self.parameters.setdefault("max_holding_days", 30)       # 最大持有天數
        self.parameters.setdefault("force_exit", False)           # 是否強制出場
        
        self.validate_parameters()
    
    @property
    def strategy_name(self) -> str:
        return "詢圈公告策略"
    
    @property
    def strategy_description(self) -> str:
        return "詢圈公告策略，基於詢圈公告進行交易"
    
    @property
    def parameter_sources(self) -> Dict[str, Dict[str, Any]]:
        """取得策略所需的參數來源"""
        return {
            "stock_source": {
                "type": "excel",  # 或 "manual"
                "required": True,
                "description": "股票代碼來源",
                "columns": ["stock_id"]  # Excel模式需要的欄位
            },
            "price_source": {
                "type": "api",  # 或 "excel"
                "required": True,
                "description": "股價資料來源"
            },
            "date_range": {
                "type": "manual",  # 需要手動指定年度
                "required": True,
                "description": "日期範圍設定（年度）"
            }
        }
    
    @property
    def strategy_parameters(self) -> Dict[str, Dict[str, Any]]:
        """取得策略參數配置"""
        return {
            # 共用參數
            "commission_rate": {
                "type": "number",
                "label": "手續費率",
                "default": TradingConfig.COMMISSION_RATE,
                "min": 0.0001,
                "max": 0.01,
                "step": 0.0001,
                "description": "買賣手續費率，預設為0.1425%"
            },
            "commission_discount": {
                "type": "number",
                "label": "手續費折數",
                "default": 0.3,
                "min": 0.1,
                "max": 1.0,
                "step": 0.1,
                "description": "手續費折數，預設為0.3折"
            },
            "securities_tax_rate": {
                "type": "number",
                "label": "證交稅率",
                "default": TradingConfig.SECURITIES_TAX_RATE,
                "min": 0.001,
                "max": 0.01,
                "step": 0.0001,
                "description": "賣出證交稅率，波段為0.3%，當沖為0.15%"
            },
            "shares_per_trade": {
                "type": "number",
                "label": "每次交易股數",
                "default": 1000,
                "min": 100,
                "max": 10000,
                "step": 100,
                "description": "每次交易的股數，預設為1000股"
            },
            "share_type": {
                "type": "select",
                "label": "股數類型",
                "default": "mixed",
                "options": [
                    {"value": "mixed", "label": "整股+零股"},
                    {"value": "whole", "label": "整股"},
                    {"value": "fractional", "label": "零股"}
                ],
                "description": "整股+零股：能>1000時使用整股，不然就是零股；整股：只限整股；零股：不論股數多少，都進場"
            },
            
            # 策略專用參數
            "announcement_delay": {
                "type": "number",
                "label": "公告延遲天數",
                "default": 1,
                "min": 0,
                "max": 10,
                "description": "公告後延遲幾天進場"
            },
            "position_size": {
                "type": "number",
                "label": "部位大小比例",
                "default": 0.1,
                "min": 0.01,
                "max": 1.0,
                "step": 0.01,
                "description": "每次交易的資金比例"
            },
            "max_holding_days": {
                "type": "number",
                "label": "最大持有天數",
                "default": 30,
                "min": 1,
                "max": 365,
                "description": "最大持有天數"
            },
            "force_exit": {
                "type": "boolean",
                "label": "強制出場",
                "default": False,
                "description": "是否在達到最大持有天數後強制出場"
            }
        }
    
    def process_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """處理詢圈公告策略參數Args:
            parameters (Dict[str, Any]): 包含各種來源的參數
                - excel_data: pl.DataFrame (如果stock_source為excel)
                - stock_ids: List[str] (如果stock_source為manual)
                - start_year: str (如果date_range為manual)
                - end_year: str (如果date_range為manual)
                - price_data: pl.DataFrame (如果price_source為excel)
                
        Returns:
            Dict[str, Any]: 處理後的參數
        """
        processed_params = {}
        
        # 處理Excel資料
        if "excel_data" in parameters:
            excel_data = parameters["excel_data"]
            processed_params.update(self.process_excel_data(excel_data))
        
        # 處理手動輸入的股票代碼
        if "stock_ids" in parameters:
            processed_params["stock_ids"] = parameters["stock_ids"]
        
        # 處理日期範圍
        if "start_date" in parameters:
            processed_params["start_date"] = parameters["start_date"]
        if "end_date" in parameters:
            processed_params["end_date"] = parameters["end_date"]
        
        # 處理股價資料
        if "price_data" in parameters:
            processed_params["price_data"] = parameters["price_data"]
        
        return processed_params
    
    def validate_special_parameters(self, parameters: Dict[str, Any]) -> None:
        """驗證詢圈公告策略特定參數"""
        # 詢圈公告策略需要年度參數
        if "start_year" not in parameters or "end_year" not in parameters:
            raise ValueError("詢圈公告策略需要指定開始和結束年度")
        
        start_year = parameters["start_year"]
        end_year = parameters["end_year"]
        
        if not start_year or not end_year:
            raise ValueError("詢圈公告策略需要指定開始和結束年度")
    
    async def process_api_data(self, stock_data: pl.DataFrame, stock_api) -> pl.DataFrame:
        """處理詢圈公告策略的API資料"""
        # 詢圈公告策略不需要額外的API資料處理
        return stock_data
    
    def should_entry(self, stock_data: pl.DataFrame, current_index: int) -> Tuple[bool, Dict[str, Any]]:
        """
        判斷是否應該進場
        
        詢圈公告策略進場條件：
        1. 有詢圈公告
        2. 公告延遲天數後進場
        """
        if current_index == 0:
            return False, {}
        
        current_row = stock_data.row(current_index, named=True)
        
        # 這裡應該檢查是否有詢圈公告
        # 目前簡化處理，假設有公告
        has_announcement = True  # 實際應該從資料中檢查
        
        if has_announcement:
            entry_info = {
                "entry_price": current_row['open'],
                "reason": "詢圈公告進場"
            }
            return True, entry_info
        
        return False, {}
    
    def should_exit(self, stock_data: pl.DataFrame, current_index: int, 
                   position: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        判斷是否應該出場
        
        詢圈公告策略出場條件：
        1. 最大持有天數
        2. 強制出場
        """
        current_row = stock_data.row(current_index, named=True)
        entry_date = position.get("entry_date")
        
        # 檢查持有天數
        current_date = current_row['date']
        
        if entry_date and current_date:
            holding_days = (current_date - entry_date).days
            if holding_days >= self.parameters["max_holding_days"]:
                return True, {
                    "exit_price": current_row['close'],
                    "exit_type": "時間出場",
                    "reason": f"持有{holding_days}天"
                }
        
        # 檢查是否為最後一筆資料且強制出場開啟
        if self.parameters.get("force_exit", False) and current_index == len(stock_data) - 1:
            return True, {
                "exit_price": current_row['close'],
                "exit_type": "強制出場",
                "reason": "回測結束強制出場"
            }
        
        return False, {}
    
    def execute_trade(self, stock_data: pl.DataFrame, current_index: int, 
                     capital: float, stock_id: str, stock_name: str) -> Optional[TradeRecord]:
        """
        執行交易
        
        Args:
            stock_data (pl.DataFrame): 股票資料
            current_index (int): 當前資料索引
            capital (float): 可用資金
            stock_id (str): 股票代碼
            stock_name (str): 股票名稱
            
        Returns:
            Optional[TradeRecord]: 交易記錄
        """
        current_row = stock_data.row(current_index, named=True)
        
        # 檢查是否已持有該股票
        has_position = any(position["stock_id"] == stock_id for position in self.active_positions)
        
        if has_position:
            # 有持有部位時，檢查是否應該出場
            positions_to_remove = []
            trade_record = None
            
            for position in self.active_positions:
                if position["stock_id"] == stock_id:
                    # 增加持有天數
                    if "holding_days" not in position:
                        position["holding_days"] = 0
                    position["holding_days"] += 1
                    
                    should_exit, exit_info = self.should_exit(stock_data, current_index, position)
                    if should_exit:
                        # 計算出場價格
                        exit_price = exit_info["exit_price"]
                        entry_price = position["entry_price"]
                        shares = position["shares"]
                        
                        # 計算損益
                        profit_loss = PriceUtils.calculate_profit_loss(entry_price, exit_price, shares, 1)
                        profit_loss_rate = PriceUtils.calculate_profit_loss_rate(entry_price, exit_price, 1)
                        
                        # 計算手續費和證交稅
                        entry_amount = entry_price * shares
                        exit_amount = exit_price * shares
                        entry_commission = self.calculate_commission(entry_amount)
                        exit_commission = self.calculate_commission(exit_amount)
                        securities_tax = self.calculate_securities_tax(exit_amount)
                        total_commission = entry_commission + exit_commission
                        net_profit_loss = profit_loss - total_commission - securities_tax
                        
                        # 計算持有天數
                        holding_days = position["holding_days"]
                        
                        # 建立交易記錄
                        trade_record = TradeRecord(
                            position_id=f"{stock_id}_{position['entry_date'].strftime('%Y%m%d')}_{current_row['date'].strftime('%Y%m%d')}",
                            entry_date=position["entry_date"],
                            exit_date=current_row['date'],
                            stock_id=stock_id,
                            stock_name=stock_name,
                            trade_direction=1,  # 做多
                            entry_price=entry_price,
                            exit_price=exit_price,
                            shares=shares,
                            profit_loss=profit_loss,
                            profit_loss_rate=profit_loss_rate,
                            commission=total_commission,
                            securities_tax=securities_tax,
                            net_profit_loss=net_profit_loss,
                            exit_reason=exit_info["reason"],
                            holding_days=holding_days,
                            # 與 HoldingPosition 相同的欄位，用於 Excel 匯出
                            current_price=exit_price,  # 當前價格等於出場價格
                            unrealized_profit_loss=profit_loss,  # 未實現損益等於實際損益
                            unrealized_profit_loss_rate=profit_loss_rate,  # 未實現損益率等於實際損益率
                            current_date=current_row['date'],  # 當前日期等於出場日期
                            exit_price_type="close",  # 出場價類型
                            current_entry_price=entry_price,  # 當日進場價格
                            current_exit_price=exit_price,  # 當前出場價格等於出場價格
                            current_profit_loss=profit_loss,  # 當前損益等於實際損益
                            current_profit_loss_rate=profit_loss_rate,  # 當前損益率等於實際損益率
                            take_profit_price=0.0,  # 停利價格
                            stop_loss_price=0.0,  # 停損價格
                            open_price=current_row.get('open'),
                            high_price=current_row.get('high'),
                            low_price=current_row.get('low'),
                            close_price=current_row.get('close')
                        )
                        
                        # 標記要移除的部位
                        positions_to_remove.append(position)
                        
                        print_log(f"出場: {stock_id} 進場價: {entry_price} 出場價: {exit_price} 損益: {net_profit_loss}")
            
            # 移除已出場的部位
            for position in positions_to_remove:
                self.active_positions.remove(position)
            
            return trade_record
        
        else:
            # 沒有持有部位時，檢查是否應該進場
            should_entry, entry_info = self.should_entry(stock_data, current_index)
            if should_entry:
                # 計算進場價格和股數
                entry_price = entry_info["entry_price"]
                position_size = self.parameters["position_size"]
                available_capital = capital * position_size
                shares = self.calculate_shares(available_capital, entry_price, "整股")
                
                if shares > 0:
                    # 產生唯一識別符
                    position_id = f"{stock_id}_{current_row['date']}_{entry_price}_{uuid.uuid4().hex[:8]}"
                    
                    # 記錄進場部位
                    position = {
                        "position_id": position_id,
                        "entry_date": current_row['date'],
                        "entry_price": entry_price,
                        "shares": shares,
                        "stock_id": stock_id,
                        "stock_name": stock_name,
                        "holding_days": 0
                    }
                    
                    # 添加到活躍部位
                    self.active_positions.append(position)
                    
                    return None
        
        return None
    
    def run_backtest(self, stock_data: pl.DataFrame, initial_capital: float, stock_id: str, stock_name: str):
        """
        執行回測
        
        Args:
            stock_data (pl.DataFrame): 股票資料
            initial_capital (float): 初始資金
            stock_id (str): 股票代碼
            stock_name (str): 股票名稱
        """
        # 重置策略狀態
        self.reset()
        
        # 初始化權益曲線
        current_capital = initial_capital
        self.update_equity_curve(current_capital, stock_data.row(0, named=True)['date'])
        
        # 逐日執行策略
        for i in range(len(stock_data)):
            # 執行交易
            trade_record = self.execute_trade(stock_data, i, current_capital, stock_id, stock_name)
            
            # 更新資金
            if trade_record:
                current_capital += trade_record.net_profit_loss
            
            # 更新權益曲線
            if i < len(stock_data) - 1:
                self.update_equity_curve(current_capital, stock_data.row(i + 1, named=True)['date'])
    
    def get_strategy_description(self) -> str:
        """取得策略描述"""
        return "詢圈公告策略：基於詢圈公告進行交易，在公告延遲指定天數後進場，持有至最大天數或強制出場"
    
    def process_excel_data(self, excel_data: pl.DataFrame) -> Dict[str, Any]:
        """處理詢圈公告策略的Excel資料"""
        # 驗證必要欄位並取得欄位映射
        required_columns = ["stock_id"]
        column_mapping = Utils.validate_stock_data(excel_data, required_columns)
        
        # 標準化欄位名稱
        standardized_data = excel_data.clone()
        
        # 重新命名欄位為標準名稱
        rename_dict = {}
        for standard_col, actual_col in column_mapping.items():
            if actual_col != standard_col:
                rename_dict[actual_col] = standard_col
        
        if rename_dict:
            standardized_data = standardized_data.rename(rename_dict)
        
        # 提取並分離股票代碼和股票名稱
        stock_data = standardized_data.select("stock_id").unique().to_series().to_list()
        stock_ids = []
        stock_names = []
        
        for stock_item in stock_data:
            if isinstance(stock_item, str) and ' ' in stock_item:
                # 格式: "6462 神盾" -> 分離為代碼和名稱
                parts = stock_item.split(' ', 1)  # 最多分割一次
                if len(parts) == 2:
                    stock_ids.append(parts[0].strip())
                    stock_names.append(parts[1].strip())
                else:
                    # 如果無法分離，整個作為代碼
                    stock_ids.append(stock_item.strip())
                    stock_names.append("")
            else:
                # 如果沒有空格，整個作為代碼
                stock_ids.append(str(stock_item).strip())
                stock_names.append("")
        
        return {
            "stock_ids": stock_ids,
            "stock_names": stock_names
        }
    
    def get_strategy_result(self, initial_capital: float) -> Dict[str, Any]:
        """取得詢圈公告策略結果"""
        if not self.trade_records:
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
        
        # 計算統計資料
        total_trades = len(self.trade_records)
        winning_trades = len([t for t in self.trade_records if t.net_profit_loss > 0])
        losing_trades = len([t for t in self.trade_records if t.net_profit_loss < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        total_profit_loss = sum(t.net_profit_loss for t in self.trade_records)
        total_profit_loss_rate = total_profit_loss / initial_capital if initial_capital > 0 else 0.0
        
        # 計算最大回撤
        drawdown_info = Utils.calculate_drawdown(self.equity_curve) if self.equity_curve else {"max_drawdown": 0.0, "max_drawdown_pct": 0.0}
        max_drawdown = drawdown_info.get("max_drawdown", 0.0)
        max_drawdown_rate = drawdown_info.get("max_drawdown_pct", 0.0)
        
        # 計算夏普比率
        returns = []
        for i in range(1, len(self.equity_curve)):
            if self.equity_curve[i-1] > 0:
                returns.append((self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1])
        
        sharpe_ratio = Utils.calculate_sharpe_ratio(returns)
        
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
                "take_profit_price": trade.take_profit_price,
                "stop_loss_price": trade.stop_loss_price,
                "open_price": trade.open_price,
                "high_price": trade.high_price,
                "low_price": trade.low_price,
                "close_price": trade.close_price
            }
            trade_records_dict.append(trade_dict)
        
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
            "trade_records": trade_records_dict,
            "equity_curve": self.equity_curve,
            "dates": self.dates,
            "charts": []
        }

    @property
    def required_parameters(self):
        return self._required_parameters

    @property
    def supported_charts(self):
        return self._supported_charts

    @property
    def data_source(self):
        return self._data_source

    @property
    def stock_source(self):
        return self._stock_source

    @property
    def need_date_range(self):
        return self._need_date_range 