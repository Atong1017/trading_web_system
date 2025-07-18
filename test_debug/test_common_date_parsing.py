#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試共用日期解析函數
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from core.utils import Utils

def test_parse_date_string():
    """測試單一日期字串解析"""
    print("=== 測試單一日期字串解析 ===")
    
    test_cases = [
        ("01-19-23", "MM-DD-YY 格式"),
        ("2024-01-19", "YYYY-MM-DD 格式"),
        ("01/19/23", "MM/DD/YY 格式"),
        ("2024/01/19", "YYYY/MM/DD 格式"),
        ("20240119", "YYYYMMDD 格式")
    ]
    
    for date_str, description in test_cases:
        try:
            parsed_date = Utils.parse_date_string(date_str)
            print(f"✅ {description}: '{date_str}' -> {parsed_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"❌ {description}: '{date_str}' -> 錯誤: {e}")

def test_parse_date_list():
    """測試日期列表解析"""
    print("\n=== 測試日期列表解析 ===")
    
    date_strings = ["01-19-23", "01-20-23", "invalid-date", "2024-01-21"]
    
    try:
        parsed_dates = Utils.parse_date_list(date_strings)
        print(f"✅ 解析結果: {[d.strftime('%Y-%m-%d') for d in parsed_dates]}")
    except Exception as e:
        print(f"❌ 解析失敗: {e}")

def test_get_date_range():
    """測試日期範圍取得"""
    print("\n=== 測試日期範圍取得 ===")
    
    test_cases = [
        {
            "dates": ["01-19-23", "01-20-23", "01-21-23"],
            "days_before": 0,
            "description": "不往前推"
        },
        {
            "dates": ["01-19-23", "01-20-23", "01-21-23"],
            "days_before": -50,
            "description": "往前推50天"
        }
    ]
    
    for test_case in test_cases:
        try:
            start_date, end_date = Utils.get_date_range_from_list(
                test_case["dates"], 
                days_before=test_case["days_before"]
            )

            print(f"✅ {test_case['description']}: {start_date} ~ {end_date}")
        except Exception as e:
            print(f"❌ {test_case['description']}: 錯誤: {e}")

def test_strategy_integration():
    """測試策略整合"""
    print("\n=== 測試策略整合 ===")
    
    from strategies.swing_trading import SwingTradingStrategy
    
    test_data = {
        "證券代碼": ["6462 神盾", "2330 台積電"],
        "年月日": ["01-19-23", "01-20-23"]
    }
    
    df = pl.DataFrame(test_data)
    print(f"測試資料:")
    print(df)
    
    try:
        strategy = SwingTradingStrategy()
        result = strategy.process_excel_data(df, end_date="2025-01-20")
        
        print(f"✅ 策略處理結果:")
        print(f"股票代碼: {result['stock_ids']}")
        print(f"股票名稱: {result['stock_names']}")
        print(f"開始日期: {result['start_date']}")
        print(f"結束日期: {result['end_date']}")
        
    except Exception as e:
        print(f"❌ 策略處理失敗: {e}")

if __name__ == "__main__":
    test_parse_date_string()
    test_parse_date_list()
    test_get_date_range()
    test_strategy_integration() 