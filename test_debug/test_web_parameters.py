#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試網頁編輯器中新增參數的傳遞功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.dynamic_strategy import DynamicStrategy
import polars as pl
from datetime import datetime

def test_web_parameter_passing():
    """測試網頁編輯器新增參數的傳遞功能"""
    print("=== 測試網頁編輯器新增參數的傳遞功能 ===")
    
    # 模擬網頁編輯器中新增的參數
    web_parameters = {
        "profit": {
            "type": "number",
            "label": "獲利目標",
            "default": 0.05,
            "min": 0.01,
            "max": 0.5,
            "step": 0.01,
            "description": "獲利目標百分比"
        },
        "holding_days": {
            "type": "dynamic",
            "label": "持有天數",
            "default": 0,
            "increment": 1,
            "description": "動態持有天數"
        }
    }
    
    # 測試策略程式碼（不包含 custom_parameters 宣告）
    strategy_code = """
import polars as pl
from datetime import datetime

def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    profit = kwargs.get('profit', 0)
    holding_days = kwargs.get('holding_days', 0)
    print(f"should_entry - profit: {profit}, holding_days: {holding_days}")
    
    # 簡單的進場條件
    if current_index > 0:
        current_price = stock_data['close'][current_index]
        prev_price = stock_data['close'][current_index - 1]
        if current_price > prev_price:
            return True, {"reason": f"價格上漲，profit={profit}, holding_days={holding_days}"}
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df, **kwargs):
    profit = kwargs.get('profit', 0)
    holding_days = kwargs.get('holding_days', 0)
    print(f"should_exit - profit: {profit}, holding_days: {holding_days}")
    
    # 簡單的出場條件
    if current_index > position['entry_index']:
        entry_price = position['entry_price']
        current_price = stock_data['close'][current_index]
        profit_rate = (current_price - entry_price) / entry_price
        
        if profit_rate >= profit:
            return True, {"reason": f"達到獲利目標 {profit}, holding_days={holding_days}"}
    
    return False, {}
"""
    
    # 創建策略實例
    parameters = {
        "profit": 0.03,  # 設定獲利目標為 3%
        "commission_rate": 0.001425,
        "securities_tax_rate": 0.003
    }
    
    strategy = DynamicStrategy(
        parameters=parameters,
        strategy_code=strategy_code,
        strategy_name="測試策略"
    )
    
    # 手動設定 custom_parameters，模擬網頁編輯器的行為
    strategy.custom_parameters = web_parameters
    
    print(f"策略實例創建成功: {strategy.strategy_name}")
    print(f"網頁編輯器參數: {strategy.custom_parameters}")
    
    # 創建測試資料
    test_data = pl.DataFrame({
        "date": [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3), datetime(2024, 1, 4)],
        "close": [100, 102, 98, 105],
        "open": [100, 101, 99, 100],
        "high": [103, 104, 100, 106],
        "low": [99, 100, 97, 99],
        "volume": [1000, 1100, 900, 1200]
    })
    
    excel_data = pl.DataFrame({
        "stock_id": ["2330", "2330", "2330", "2330"],
        "date": [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3), datetime(2024, 1, 4)]
    })
    
    print("\n=== 測試 should_entry 參數傳遞 ===")
    for i in range(len(test_data)):
        should_entry, entry_info = strategy.should_entry(test_data, i, excel_data)
        print(f"Index {i}: should_entry={should_entry}, info={entry_info}")
    
    print("\n=== 測試 should_exit 參數傳遞 ===")
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
    
    print("\n=== 測試動態參數更新 ===")
    print(f"初始 holding_days: {strategy.get_dynamic_parameter('holding_days')}")
    
    # 模擬不出場的情況（holding_days 應該增加）
    strategy._update_dynamic_parameters_after_exit(False)
    print(f"不出場後 holding_days: {strategy.get_dynamic_parameter('holding_days')}")
    
    # 模擬出場的情況（holding_days 應該重置）
    strategy._update_dynamic_parameters_after_exit(True)
    print(f"出場後 holding_days: {strategy.get_dynamic_parameter('holding_days')}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_web_parameter_passing() 