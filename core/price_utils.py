# 價格計算工具模組
from typing import Tuple, Optional
import math

def print_log(message: str):
    """日誌輸出"""
    print(f"********** price_utils.py - {message}")

class PriceUtils:
    """價格計算工具類別"""
    
    @staticmethod
    def get_tick_size(price: float) -> float:
        """
        根據股價取得最小變動單位（tick size）
        
        Args:
            price (float): 股價
            
        Returns:
            float: 最小變動單位
        """
        if price < 10:
            return 0.01
        elif price < 50:
            return 0.05
        elif price < 100:
            return 0.1
        elif price < 500:
            return 0.5
        elif price < 1000:
            return 1.0
        else:
            return 5.0
    
    @staticmethod
    def calculate_limit_price(base_price: float, limit_percent: float) -> float:
        """
        計算漲跌停、停利、停損價格，並調整到符合最小變動單位
        
        Args:
            base_price (float): 基準價格
            limit_percent (float): 漲跌停百分比（正數為漲停，負數為跌停）
            
        Returns:
            float: 調整後的漲跌停、停利、停損
        """
        tick_size = PriceUtils.get_tick_size(base_price)
        # 計算漲跌停價格
        limit_price = base_price * (1 + limit_percent / 100)
        # 調整到最接近的 tick size
        adjusted_price = round(limit_price / tick_size) * tick_size
        
        return adjusted_price
    
    @staticmethod
    def calculate_up_down_limit_prices(base_price: float, up_limit_percentage: float = 9.0, down_limit_percentage: float = 9.0) -> Tuple[float, float]:
        """
        計算漲跌停價格
        
        Args:
            base_price (float): 基準價格
            up_limit_percentage (float): 漲停百分比，預設為9.0%
            down_limit_percentage (float): 跌停百分比，預設為9.0%
            
        Returns:
            Tuple[float, float]: (漲停價, 跌停價)
        """
        up_limit = PriceUtils.calculate_limit_price(base_price, up_limit_percentage)
        down_limit = PriceUtils.calculate_limit_price(base_price, -down_limit_percentage)
        return up_limit, down_limit
    
    @staticmethod
    def is_limit_down(open_price: float, high: float, low: float, close: float, 
                     prev_close: float, up_limit_percentage: float = 9.0, down_limit_percentage: float = 9.0, trade_direction: str = 'long') -> Optional[int]:
        """
        判斷是否為跌停板
        
        Args:
            open_price (float): 開盤價
            high (float): 最高價
            low (float): 最低價
            close (float): 收盤價
            base_price (float): 基準價格，用於計算漲跌停價
            up_limit_percentage (float): 漲停百分比，預設為9.0%
            down_limit_percentage (float): 跌停百分比，預設為9.0%
            trade_direction (str): 交易方向，long為做多，short為做空
            
        Returns:
            Optional[int]: 1為跌停，2為開盤跌停但未一字跌停，False為正常
        """
        up_limit_price = PriceUtils.calculate_limit_price(prev_close, up_limit_percentage)
        down_limit_price = PriceUtils.calculate_limit_price(prev_close, down_limit_percentage)
        
        if trade_direction == 'long':    # 做多
            if max(open_price, high, low, close) <= down_limit_price:           # 一字跌停
                return 1
            elif open_price <= down_limit_price and high > down_limit_price:    # 開盤跌停，但未一字跌停
                return 2
            else:
                return None
        else:                       # 做空
            if min(open_price, high, low, close) >= up_limit_price:             # 一字漲停
                return 1
            elif open_price >= up_limit_price and high < up_limit_price:        # 開盤漲停，但未一字漲停
                return 2
            else:
                return None
    
    @staticmethod
    def calculate_shares(amount: float, price: float, share_type: str = "mixed") -> int:
        """
        計算股數
        
        Args:
            amount (float): 投資金額
            price (float): 股價
            share_type (str): 股數類型 ("mixed", "whole", "fractional", "整股", "零股", "整股優先")
                - mixed: 整股+零股（優先整股，不足則用零股）
                - whole: 只買整股
                - fractional: 可買零股
                - 整股: 只買整股（舊格式，相容性）
                - 零股: 可買零股（舊格式，相容性）
                - 整股優先: 整股優先，無法整股則使用零股（舊格式，相容性）
            
        Returns:
            int: 股數
        """
        # 新格式對應到舊格式
        if share_type == "mixed":
            share_type = "整股優先"
        elif share_type == "whole":
            share_type = "整股"
        elif share_type == "fractional":
            share_type = "零股"
        
        # 處理舊格式
        if share_type == "整股":
            # 只買整股
            return int(amount // (price * 1000)) * 1000
        elif share_type == "零股":
            # 可買零股
            return int(amount // price)
        elif share_type == "整股優先":
            # 整股優先，無法整股則使用零股
            shares = int(amount // price)
            if shares >= 1000:
                return (shares // 1000) * 1000
            else:
                return shares
        else:
            raise ValueError(f"不支援的股數類型: {share_type}")
    
    @staticmethod
    def calculate_trade_price(price: float, trade_direction: str, 
                            slippage: float = 0.001) -> float:
        """
        計算交易價格（考慮滑點）
        
        Args:
            price (float): 基準價格
            trade_direction (int): 交易方向 (1: 買入, -1: 賣出)
            slippage (float): 滑點比例
            
        Returns:
            float: 實際交易價格
        """
        if trade_direction == 'long':  # 買入
            return price * (1 + slippage)
        elif trade_direction == 'short':  # 賣出
            return price * (1 - slippage)
        else:
            raise ValueError(f"不支援的交易方向: {trade_direction}")
    
    @staticmethod
    def adjust_price_to_tick(price: float) -> float:
        """
        將價格調整到符合最小變動單位
        
        Args:
            price (float): 原始價格
            
        Returns:
            float: 調整後的價格
        """
        tick_size = PriceUtils.get_tick_size(price)
        return round(price / tick_size) * tick_size
    
    @staticmethod
    def calculate_profit_loss(entry_price: float, exit_price: float, 
                            shares: int, trade_direction: str) -> float:
        """
        計算損益
        
        Args:
            entry_price (float): 進場價
            exit_price (float): 出場價
            shares (int): 股數
            trade_direction (str): 交易方向 (long: 做多, short: 做空)
            
        Returns:
            float: 損益金額
        """
        if trade_direction == 'long':  # 做多
            return (exit_price - entry_price) * shares
        elif trade_direction == 'short':  # 做空
            return (entry_price - exit_price) * shares
        else:
            raise ValueError(f"不支援的交易方向: {trade_direction}")
    
    @staticmethod
    def calculate_profit_loss_rate(entry_price: float, exit_price: float, 
                                 trade_direction: str) -> float:
        """
        計算損益率
        
        Args:
            entry_price (float): 進場價
            exit_price (float): 出場價
            trade_direction (str): 交易方向 (long: 做多, short: 做空)
            
        Returns:
            float: 損益率
        """
        if trade_direction == 'long':  # 做多
            return (exit_price - entry_price) / entry_price
        elif trade_direction == 'short':  # 做空
            return (entry_price - exit_price) / entry_price
        else:
            raise ValueError(f"不支援的交易方向: {trade_direction}") 