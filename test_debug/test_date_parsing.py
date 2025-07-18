#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試日期解析功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from datetime import datetime
from strategies.swing_trading import SwingTradingStrategy

def test_date_parsing():
    """測試日期解析功能"""
    print("=== 測試日期解析功能 ===")
    
    # 測試不同日期格式
    test_cases = [
        {
            "name": "MM-DD-YY 格式",
            "data": {
                "證券代碼": ["6462 神盾", "2330 台積電"],
                "年月日": ["01-19-23", "01-20-23"]
            }
        },
        {
            "name": "YYYY-MM-DD 格式",
            "data": {
                "證券代碼": ["6462 神盾", "2330 台積電"],
                "年月日": ["2024-01-19", "2024-01-20"]
            }
        },
        {
            "name": "MM/DD/YY 格式",
            "data": {
                "證券代碼": ["6462 神盾", "2330 台積電"],
                "年月日": ["01/19/23", "01/20/23"]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        df = pl.DataFrame(test_case['data'])
        print(f"原始資料:")
        print(df)
        
        try:
            strategy = SwingTradingStrategy()
            result = strategy.process_excel_data(df)
            
            print(f"✅ 處理結果:")
            print(f"股票代碼: {result['stock_ids']}")
            print(f"股票名稱: {result['stock_names']}")
            print(f"開始日期: {result['start_date']}")
            print(f"結束日期: {result['end_date']}")
            
        except Exception as e:
            print(f"❌ 測試失敗: {e}")

def test_invalid_date():
    """測試無效日期"""
    print("\n=== 測試無效日期 ===")
    
    test_data = {
        "證券代碼": ["6462 神盾"],
        "年月日": ["invalid-date"]
    }
    
    df = pl.DataFrame(test_data)
    print(f"無效日期資料:")
    print(df)
    
    try:
        strategy = SwingTradingStrategy()
        result = strategy.process_excel_data(df)
        print(f"✅ 處理結果: {result}")
    except Exception as e:
        print(f"❌ 預期的錯誤: {e}")

if __name__ == "__main__":
    test_date_parsing()
    test_invalid_date() 