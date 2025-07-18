#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試統一的欄位處理功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import polars as pl
import pandas as pd
from core.utils import Utils

def test_unified_column_processing():
    """測試統一的欄位處理功能"""
    print("=== 測試統一的欄位處理功能 ===")
    
    # 測試案例1：中文欄位名稱
    print("\n1. 測試中文欄位名稱")
    test_data1 = {
        "證券代碼": ["2330", "2317", "2330", "2317"],
        "日期": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
        "開盤價": [100.0, 50.0, 101.0, 51.0],
        "最高價": [105.0, 55.0, 106.0, 56.0],
        "最低價": [98.0, 48.0, 99.0, 49.0],
        "收盤價": [103.0, 53.0, 104.0, 54.0]
    }
    
    df1 = pl.DataFrame(test_data1)
    print(f"原始欄位: {df1.columns}")
    
    try:
        # 使用標準化函數
        standardized_df1 = Utils.standardize_columns(df1, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 標準化成功，標準化後欄位: {standardized_df1.columns}")
        print(f"標準化後資料:")
        print(standardized_df1)
    except Exception as e:
        print(f"❌ 標準化失敗: {e}")
    
    # 測試案例2：英文欄位名稱
    print("\n2. 測試英文欄位名稱")
    test_data2 = {
        "stock_id": ["2330", "2317"],
        "date": ["2024-01-01", "2024-01-02"],
        "open": [100.0, 101.0],
        "high": [105.0, 106.0],
        "low": [98.0, 99.0],
        "close": [103.0, 104.0]
    }
    
    df2 = pl.DataFrame(test_data2)
    print(f"原始欄位: {df2.columns}")
    
    try:
        standardized_df2 = Utils.standardize_columns(df2, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 標準化成功，標準化後欄位: {standardized_df2.columns}")
    except Exception as e:
        print(f"❌ 標準化失敗: {e}")
    
    # 測試案例3：混合欄位名稱
    print("\n3. 測試混合欄位名稱")
    test_data3 = {
        "股票代碼": ["2330", "2317"],
        "交易日期": ["2024-01-01", "2024-01-02"],
        "open": [100.0, 101.0],
        "high": [105.0, 106.0],
        "low": [98.0, 99.0],
        "close": [103.0, 104.0]
    }
    
    df3 = pl.DataFrame(test_data3)
    print(f"原始欄位: {df3.columns}")
    
    try:
        standardized_df3 = Utils.standardize_columns(df3, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 標準化成功，標準化後欄位: {standardized_df3.columns}")
    except Exception as e:
        print(f"❌ 標準化失敗: {e}")
    
    # 測試案例4：只包含必要欄位（Excel上傳模式）
    print("\n4. 測試Excel上傳模式（只包含stock_id和date）")
    test_data4 = {
        "證券代碼": ["2330", "2317", "2454"],
        "年月日": ["2024-01-01", "2024-01-02", "2024-01-03"]
    }
    
    df4 = pl.DataFrame(test_data4)
    print(f"原始欄位: {df4.columns}")
    
    try:
        standardized_df4 = Utils.standardize_columns(df4, ["stock_id", "date"])
        print(f"✅ 標準化成功，標準化後欄位: {standardized_df4.columns}")
        print(f"標準化後資料:")
        print(standardized_df4)
    except Exception as e:
        print(f"❌ 標準化失敗: {e}")
    
    # 測試案例5：缺少必要欄位
    print("\n5. 測試缺少必要欄位")
    test_data5 = {
        "證券代碼": ["2330", "2317"],
        "開盤價": [100.0, 101.0],
        "收盤價": [103.0, 104.0]
    }
    
    df5 = pl.DataFrame(test_data5)
    print(f"原始欄位: {df5.columns}")
    
    try:
        standardized_df5 = Utils.standardize_columns(df5, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 標準化成功，標準化後欄位: {standardized_df5.columns}")
    except Exception as e:
        print(f"❌ 標準化失敗: {e}")
    
    # 測試案例6：pandas DataFrame轉換
    print("\n6. 測試pandas DataFrame轉換")
    test_data6 = {
        "stock_id": ["2330", "2317"],
        "date": ["2024-01-01", "2024-01-02"],
        "open": [100.0, 101.0],
        "high": [105.0, 106.0],
        "low": [98.0, 99.0],
        "close": [103.0, 104.0]
    }
    
    pd_df6 = pd.DataFrame(test_data6)
    df6 = pl.from_pandas(pd_df6)
    print(f"pandas轉polars後欄位: {df6.columns}")
    
    try:
        standardized_df6 = Utils.standardize_columns(df6, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 標準化成功，標準化後欄位: {standardized_df6.columns}")
    except Exception as e:
        print(f"❌ 標準化失敗: {e}")

def test_column_mapping_function():
    """測試欄位映射函數"""
    print("\n=== 測試欄位映射函數 ===")
    
    # 測試validate_stock_data函數
    test_data = {
        "證券代碼": ["2330", "2317"],
        "日期": ["2024-01-01", "2024-01-02"],
        "開盤價": [100.0, 101.0],
        "收盤價": [103.0, 104.0]
    }
    
    df = pl.DataFrame(test_data)
    print(f"原始欄位: {df.columns}")
    
    try:
        # 測試欄位映射
        column_mapping = Utils.validate_stock_data(df, ["stock_id", "date", "open", "close"])
        print(f"✅ 欄位映射成功: {column_mapping}")
        
        # 測試缺少欄位的情況
        missing_mapping = Utils.validate_stock_data(df, ["stock_id", "date", "open", "high", "low", "close"])
        print(f"✅ 完整欄位映射: {missing_mapping}")
        
    except Exception as e:
        print(f"❌ 欄位映射失敗: {e}")

if __name__ == "__main__":
    test_unified_column_processing()
    test_column_mapping_function()
    print("\n=== 測試完成 ===") 