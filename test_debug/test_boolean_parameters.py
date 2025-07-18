#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試布林值參數功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.dynamic_strategy import DynamicStrategy
import polars as pl
from datetime import datetime

def test_boolean_parameters():
    """測試布林值參數功能"""
    print("=== 測試布林值參數功能 ===")
    
    # 模擬網頁編輯器中新增的布林值參數
    web_parameters = {
        "enable_stop_loss": {
            "type": "boolean",
            "label": "啟用停損",
            "default": False,
            "description": "是否啟用停損功能"
        },
        "enable_take_profit": {
            "type": "boolean",
            "label": "啟用停利",
            "default": True,
            "description": "是否啟用停利功能"
        },
        "use_ma_filter": {
            "type": "boolean",
            "label": "使用均線過濾",
            "default": False,
            "description": "是否使用均線過濾"
        }
    }
    
    # 測試策略程式碼
    strategy_code = """
import polars as pl
from datetime import datetime

def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    enable_stop_loss = kwargs.get('enable_stop_loss', False)
    enable_take_profit = kwargs.get('enable_take_profit', True)
    use_ma_filter = kwargs.get('use_ma_filter', False)
    
    print(f"should_entry - enable_stop_loss: {enable_stop_loss}, enable_take_profit: {enable_take_profit}, use_ma_filter: {use_ma_filter}")
    
    # 簡單的進場條件
    if current_index > 0:
        current_price = stock_data['close'][current_index]
        prev_price = stock_data['close'][current_index - 1]
        
        # 如果啟用均線過濾，檢查價格是否在均線之上
        if use_ma_filter and current_index >= 5:
            ma5 = stock_data['close'][current_index-5:current_index].mean()
            if current_price < ma5:
                return False, {"reason": "價格低於5日均線"}
        
        if current_price > prev_price:
            return True, {"reason": f"價格上漲，停損:{enable_stop_loss}, 停利:{enable_take_profit}, 均線過濾:{use_ma_filter}"}
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df, **kwargs):
    enable_stop_loss = kwargs.get('enable_stop_loss', False)
    enable_take_profit = kwargs.get('enable_take_profit', True)
    use_ma_filter = kwargs.get('use_ma_filter', False)
    
    print(f"should_exit - enable_stop_loss: {enable_stop_loss}, enable_take_profit: {enable_take_profit}, use_ma_filter: {use_ma_filter}")
    
    # 簡單的出場條件
    if current_index > position['entry_index']:
        entry_price = position['entry_price']
        current_price = stock_data['close'][current_index]
        profit_rate = (current_price - entry_price) / entry_price
        
        # 停利條件
        if enable_take_profit and profit_rate >= 0.05:
            return True, {"reason": f"達到停利目標 5%"}
        
        # 停損條件
        if enable_stop_loss and profit_rate <= -0.03:
            return True, {"reason": f"觸發停損 -3%"}
    
    return False, {}
"""
    
    # 創建策略實例
    parameters = {
        "enable_stop_loss": False,
        "enable_take_profit": True,
        "use_ma_filter": False,
        "commission_rate": 0.001425,
        "securities_tax_rate": 0.003
    }
    
    strategy = DynamicStrategy(
        parameters=parameters,
        strategy_code=strategy_code,
        strategy_name="布林值測試策略"
    )
    
    # 手動設定 custom_parameters，模擬網頁編輯器的行為
    strategy.custom_parameters = web_parameters
    
    print(f"策略實例創建成功: {strategy.strategy_name}")
    print(f"布林值參數: {strategy.custom_parameters}")
    
    # 創建測試資料
    test_data = pl.DataFrame({
        "date": [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3), datetime(2024, 1, 4), datetime(2024, 1, 5), datetime(2024, 1, 6)],
        "close": [100, 102, 98, 105, 108, 95],
        "open": [100, 101, 99, 100, 105, 107],
        "high": [103, 104, 100, 106, 109, 108],
        "low": [99, 100, 97, 99, 104, 94],
        "volume": [1000, 1100, 900, 1200, 1300, 1400]
    })
    
    excel_data = pl.DataFrame({
        "stock_id": ["2330", "2330", "2330", "2330", "2330", "2330"],
        "date": [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3), datetime(2024, 1, 4), datetime(2024, 1, 5), datetime(2024, 1, 6)]
    })
    
    print("\n=== 測試 should_entry 布林值參數傳遞 ===")
    for i in range(len(test_data)):
        should_entry, entry_info = strategy.should_entry(test_data, i, excel_data)
        print(f"Index {i}: should_entry={should_entry}, info={entry_info}")
    
    print("\n=== 測試 should_exit 布林值參數傳遞 ===")
    # 模擬持倉
    position = {
        "entry_date": datetime(2024, 1, 1),
        "entry_price": 100,
        "shares": 1000,
        "entry_index": 0
    }
    
    for i in range(len(test_data)):
        should_exit, exit_info = strategy.should_exit(test_data, i, position, excel_data)
        print(f"Index {i}: should_exit={should_exit}, info={exit_info}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_boolean_parameters() 