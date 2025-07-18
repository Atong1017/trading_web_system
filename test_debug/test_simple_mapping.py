#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試欄位映射功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from core.utils import Utils

def test_simple_mapping():
    """測試簡單的欄位映射"""
    print("=== 測試欄位映射功能 ===")
    
    # 使用您提供的資料格式
    test_data = {
        "年月日": ["01-19-23", "01-20-23"],
        "證券代碼": ["6462 神盾", "2330 台積電"]
    }
    
    df = pl.DataFrame(test_data)
    print(f"原始資料:")
    print(df)
    print(f"原始欄位: {df.columns}")
    
    try:
        # 測試欄位映射
        column_mapping = Utils.validate_stock_data(df, ["stock_id", "date"])
        print(f"✅ 欄位映射成功: {column_mapping}")
        
        # 測試標準化
        standardized_data = df.clone()
        rename_dict = {}
        for standard_col, actual_col in column_mapping.items():
            if actual_col != standard_col:
                rename_dict[actual_col] = standard_col
        
        if rename_dict:
            standardized_data = standardized_data.rename(rename_dict)
            print(f"✅ 欄位標準化成功:")
            print(standardized_data)
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_simple_mapping() 