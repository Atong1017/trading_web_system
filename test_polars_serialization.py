#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Polars DataFrame 序列化功能
"""

import os
import pickle
import tempfile
import polars as pl
import numpy as np
from datetime import datetime

def test_polars_serialization():
    """測試 Polars DataFrame 序列化"""
    print("測試 Polars DataFrame 序列化功能")
    print("=" * 50)
    
    # 創建測試 DataFrame
    print("1. 創建測試 DataFrame...")
    df = pl.DataFrame({
        'date': [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3)],
        'close': [100, 105, 102],
        'volume': [1000000, 1200000, 1100000]
    })
    
    # 添加計算欄位
    df = df.with_columns([
        pl.lit(0).alias("matched_stock_id"),
        pl.arange(0, df.height).alias("row_index")
    ])
    
    # 修改 matched_stock_id 欄位
    df = df.with_columns([
        pl.when(pl.col("row_index") == 1)
        .then(1)
        .otherwise(0)
        .alias("matched_stock_id")
    ])
    
    print(f"原始 DataFrame 欄位: {df.columns}")
    print(f"原始 DataFrame 形狀: {df.shape}")
    print(f"matched_stock_id 值: {df['matched_stock_id'].to_list()}")
    
    # 測試序列化
    print("\n2. 測試序列化...")
    processed_df = {
        '_type': 'polars_dataframe',
        'data': df.to_dicts(),
        'schema': df.schema,
        'shape': df.shape
    }
    
    # 儲存到檔案
    test_file = os.path.join(tempfile.gettempdir(), "test_polars.pkl")
    with open(test_file, 'wb') as f:
        pickle.dump(processed_df, f)
    
    print(f"序列化完成，檔案大小: {os.path.getsize(test_file)} bytes")
    
    # 測試反序列化
    print("\n3. 測試反序列化...")
    with open(test_file, 'rb') as f:
        loaded_processed_df = pickle.load(f)
    
    # 還原 DataFrame
    restored_df = pl.DataFrame(loaded_processed_df['data'], schema=loaded_processed_df['schema'])
    
    print(f"還原後 DataFrame 欄位: {restored_df.columns}")
    print(f"還原後 DataFrame 形狀: {restored_df.shape}")
    print(f"還原後 matched_stock_id 值: {restored_df['matched_stock_id'].to_list()}")
    
    # 驗證是否一致
    print("\n4. 驗證一致性...")
    if df.columns == restored_df.columns:
        print("✓ 欄位名稱一致")
    else:
        print("✗ 欄位名稱不一致")
        print(f"  原始: {df.columns}")
        print(f"  還原: {restored_df.columns}")
    
    if df.shape == restored_df.shape:
        print("✓ 形狀一致")
    else:
        print("✗ 形狀不一致")
        print(f"  原始: {df.shape}")
        print(f"  還原: {restored_df.shape}")
    
    if df['matched_stock_id'].to_list() == restored_df['matched_stock_id'].to_list():
        print("✓ matched_stock_id 值一致")
    else:
        print("✗ matched_stock_id 值不一致")
        print(f"  原始: {df['matched_stock_id'].to_list()}")
        print(f"  還原: {restored_df['matched_stock_id'].to_list()}")
    
    # 清理測試檔案
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n測試完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_polars_serialization() 