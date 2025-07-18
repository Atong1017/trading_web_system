#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試欄位名稱映射功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from core.utils import Utils

def test_column_mapping():
    """測試欄位名稱映射功能"""
    print("=== 測試欄位名稱映射功能 ===")
    
    # 測試案例1：使用中文欄位名稱
    test_data1 = {
        "證券代碼": ["2330", "2317", "2330", "2317"],
        "日期": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
        "開盤價": [100.0, 50.0, 101.0, 51.0],
        "最高價": [105.0, 55.0, 106.0, 56.0],
        "最低價": [98.0, 48.0, 99.0, 49.0],
        "收盤價": [103.0, 53.0, 104.0, 54.0]
    }
    
    df1 = pl.DataFrame(test_data1)
    print(f"測試案例1 - 中文欄位名稱:")
    print(f"原始欄位: {df1.columns}")
    
    try:
        column_mapping = Utils.validate_stock_data(df1, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 欄位映射成功: {column_mapping}")
    except Exception as e:
        print(f"❌ 欄位映射失敗: {e}")
    
    print()
    
    # 測試案例2：使用英文欄位名稱
    test_data2 = {
        "stock_id": ["2330", "2317"],
        "date": ["2024-01-01", "2024-01-02"],
        "open": [100.0, 101.0],
        "high": [105.0, 106.0],
        "low": [98.0, 99.0],
        "close": [103.0, 104.0]
    }
    
    df2 = pl.DataFrame(test_data2)
    print(f"測試案例2 - 英文欄位名稱:")
    print(f"原始欄位: {df2.columns}")
    
    try:
        column_mapping = Utils.validate_stock_data(df2, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 欄位映射成功: {column_mapping}")
    except Exception as e:
        print(f"❌ 欄位映射失敗: {e}")
    
    print()
    
    # 測試案例3：混合欄位名稱
    test_data3 = {
        "股票代碼": ["2330", "2317"],
        "交易日期": ["2024-01-01", "2024-01-02"],
        "open": [100.0, 101.0],
        "high": [105.0, 106.0],
        "low": [98.0, 99.0],
        "close": [103.0, 104.0]
    }
    
    df3 = pl.DataFrame(test_data3)
    print(f"測試案例3 - 混合欄位名稱:")
    print(f"原始欄位: {df3.columns}")
    
    try:
        column_mapping = Utils.validate_stock_data(df3, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 欄位映射成功: {column_mapping}")
    except Exception as e:
        print(f"❌ 欄位映射失敗: {e}")
    
    print()
    
    # 測試案例4：缺少必要欄位
    test_data4 = {
        "證券代碼": ["2330", "2317"],
        "開盤價": [100.0, 101.0],
        "收盤價": [103.0, 104.0]
    }
    
    df4 = pl.DataFrame(test_data4)
    print(f"測試案例4 - 缺少必要欄位:")
    print(f"原始欄位: {df4.columns}")
    
    try:
        column_mapping = Utils.validate_stock_data(df4, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 欄位映射成功: {column_mapping}")
    except Exception as e:
        print(f"❌ 欄位映射失敗: {e}")

if __name__ == "__main__":
    test_column_mapping() 