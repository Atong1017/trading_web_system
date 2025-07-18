#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易工具模組
提供交易相關的工具函數
"""

from typing import Dict, Any, Optional
from datetime import datetime
import polars as pl
from config.trading_config import TradingConfig

def print_log(message: str):
    """日誌輸出"""
    print(f"********** trading_utils.py - {message}")

class TradingUtils:
    """交易工具類別"""
    
    @staticmethod
    def calculate_trade_price(price: float, direction: str = "buy") -> float:
        """
        計算交易價格
        
        Args:
            price (float): 基準價格
            direction (str): 交易方向 ("buy" 或 "sell")
            
        Returns:
            float: 交易價格
        """
        # 這裡可以實作更複雜的價格計算邏輯
        # 例如：考慮滑點、手續費等
        return price
    
    @staticmethod
    def calculate_position_size(capital: float, price: float, 
                              position_ratio: float = 0.95) -> int:
        """
        計算部位大小
        
        Args:
            capital (float): 可用資金
            price (float): 股票價格
            position_ratio (float): 部位比例（0-1）
            
        Returns:
            int: 可買股數
        """
        from core.price_utils import PriceUtils
        
        available_capital = capital * position_ratio
        return PriceUtils.calculate_shares(available_capital, price)
    
    @staticmethod
    def calculate_trade_cost(trade_amount: float, direction: str = "buy") -> Dict[str, float]:
        """
        計算交易成本
        
        Args:
            trade_amount (float): 交易金額
            direction (str): 交易方向 ("buy" 或 "sell")
            
        Returns:
            Dict[str, float]: 交易成本明細
        """
        # 計算手續費
        commission = TradingConfig.calculate_commission(trade_amount)
        
        # 計算證交稅（只有賣出時收取）
        securities_tax = 0.0
        if direction == "sell":
            securities_tax = TradingConfig.calculate_securities_tax(trade_amount)
        
        return {
            "commission": commission,
            "securities_tax": securities_tax,
            "total_cost": commission + securities_tax
        }
    
    @staticmethod
    def calculate_profit_loss(entry_price: float, exit_price: float, 
                            shares: int, direction: int = 1) -> Dict[str, float]:
        """
        計算損益
        
        Args:
            entry_price (float): 進場價格
            exit_price (float): 出場價格
            shares (int): 股數
            direction (int): 交易方向 (1: 做多, -1: 做空)
            
        Returns:
            Dict[str, float]: 損益明細
        """
        # 計算價差損益
        if direction == 1:  # 做多
            price_profit = (exit_price - entry_price) * shares
        else:  # 做空
            price_profit = (entry_price - exit_price) * shares
        
        # 計算交易成本
        entry_cost = TradingUtils.calculate_trade_cost(entry_price * shares, "buy")
        exit_cost = TradingUtils.calculate_trade_cost(exit_price * shares, "sell")
        total_cost = entry_cost["total_cost"] + exit_cost["total_cost"]
        
        # 淨損益
        net_profit = price_profit - total_cost
        
        return {
            "price_profit": price_profit,
            "total_cost": total_cost,
            "net_profit": net_profit,
            "profit_rate": (net_profit / (entry_price * shares)) * 100 if entry_price * shares > 0 else 0
        }
    
    @staticmethod
    def validate_trade_parameters(parameters: Dict[str, Any]) -> bool:
        """
        驗證交易參數
        
        Args:
            parameters (Dict[str, Any]): 交易參數
            
        Returns:
            bool: 驗證結果
        """
        required_fields = ["capital", "price"]
        
        for field in required_fields:
            if field not in parameters:
                raise ValueError(f"缺少必要參數: {field}")
            
            if parameters[field] <= 0:
                raise ValueError(f"參數 {field} 必須大於0")
        
        return True
    
    @staticmethod
    def format_trade_record(trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化交易記錄
        
        Args:
            trade_data (Dict[str, Any]): 原始交易資料
            
        Returns:
            Dict[str, Any]: 格式化後的交易記錄
        """
        return {
            "entry_date": trade_data.get("entry_date"),
            "exit_date": trade_data.get("exit_date"),
            "stock_id": trade_data.get("stock_id"),
            "stock_name": trade_data.get("stock_name"),
            "entry_price": round(trade_data.get("entry_price", 0), 2),
            "exit_price": round(trade_data.get("exit_price", 0), 2),
            "shares": trade_data.get("shares", 0),
            "profit_loss": round(trade_data.get("profit_loss", 0), 2),
            "profit_rate": round(trade_data.get("profit_rate", 0), 2),
            "commission": round(trade_data.get("commission", 0), 2),
            "securities_tax": round(trade_data.get("securities_tax", 0), 2),
            "net_profit_loss": round(trade_data.get("net_profit_loss", 0), 2),
            "exit_reason": trade_data.get("exit_reason", "")
        }
    
    @staticmethod
    def calculate_holding_days(entry_date: datetime, exit_date: datetime) -> int:
        """
        計算持有天數
        
        Args:
            entry_date (datetime): 進場日期
            exit_date (datetime): 出場日期
            
        Returns:
            int: 持有天數
        """
        return (exit_date - entry_date).days
    
    @staticmethod
    def is_valid_trade_time(trade_time: datetime) -> bool:
        """
        檢查是否為有效交易時間
        
        Args:
            trade_time (datetime): 交易時間
            
        Returns:
            bool: 是否為有效交易時間
        """
        # 檢查是否為工作日
        if trade_time.weekday() >= 5:  # 週末
            return False
        
        # 檢查是否為交易時間（9:00-13:30）
        hour = trade_time.hour
        minute = trade_time.minute
        
        if hour < 9 or hour > 13:
            return False
        
        if hour == 13 and minute > 30:
            return False
        
        return True
    
    @staticmethod
    def calculate_risk_metrics(trades: list) -> Dict[str, float]:
        """
        計算風險指標
        
        Args:
            trades (list): 交易記錄列表
            
        Returns:
            Dict[str, float]: 風險指標
        """
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0
            }
        
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.get("net_profit_loss", 0) > 0]
        losing_trades = [t for t in trades if t.get("net_profit_loss", 0) < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0
        
        avg_profit = sum(t.get("net_profit_loss", 0) for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(t.get("net_profit_loss", 0) for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
        
        profit_factor = abs(avg_profit / avg_loss) if avg_loss != 0 else 0.0
        
        # 計算最大回撤
        max_drawdown = 0.0
        peak = 0.0
        cumulative_profit = 0.0
        
        for trade in trades:
            cumulative_profit += trade.get("net_profit_loss", 0)
            if cumulative_profit > peak:
                peak = cumulative_profit
            drawdown = peak - cumulative_profit
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate * 100,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown
        } 