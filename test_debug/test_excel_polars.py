#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Excel 檔案轉換為 Polars DataFrame 的功能
"""

import pandas as pd
import polars as pl
from datetime import datetime, timedelta
import tempfile
import os

def test_excel_to_polars():
    """測試 Excel 檔案轉換為 Polars DataFrame"""
    print("=== 測試 Excel 檔案轉換為 Polars DataFrame ===")
    
    # 建立測試資料
    test_data = []
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    stock_ids = ['2330', '2317', '2454']
    
    for stock_id in stock_ids:
        for date in dates[::3]:  # 每3天一個資料點
            test_data.append({
                'stock_id': stock_id,
                'date': date.strftime('%Y-%m-%d')
            })
    
    # 建立 pandas DataFrame
    df_pandas = pd.DataFrame(test_data)
    print(f"Pandas DataFrame: {df_pandas.shape}")
    print(f"Pandas DataFrame 類型: {type(df_pandas)}")
    print(f"Pandas DataFrame 欄位: {df_pandas.columns.tolist()}")
    
    # 轉換為 polars DataFrame
    df_polars = pl.from_pandas(df_pandas)
    print(f"\nPolars DataFrame: {df_polars.shape}")
    print(f"Polars DataFrame 類型: {type(df_polars)}")
    print(f"Polars DataFrame 欄位: {df_polars.columns}")
    
    # 測試欄位操作
    print(f"\n=== 測試欄位操作 ===")
    
    # 取得唯一股票代碼
    stock_ids_polars = df_polars['stock_id'].unique().to_list()
    print(f"Polars 唯一股票代碼: {stock_ids_polars}")
    
    # 取得日期列表
    dates_polars = df_polars['date'].to_list()
    print(f"Polars 日期列表 (前5個): {dates_polars[:5]}")
    
    # 測試篩選
    print(f"\n=== 測試篩選 ===")
    filtered_df = df_polars.filter(pl.col('stock_id') == '2330')
    print(f"篩選 2330 股票: {filtered_df.shape}")
    
    # 測試分組
    print(f"\n=== 測試分組 ===")
    grouped_df = df_polars.group_by('stock_id').count()
    print(f"按股票分組計數:\n{grouped_df}")
    
    # 建立 Excel 檔案並測試讀取
    print(f"\n=== 測試 Excel 檔案讀取 ===")
    
    # 建立臨時 Excel 檔案
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        df_pandas.to_excel(temp_file.name, index=False)
        temp_file_path = temp_file.name
    
    try:
        # 讀取 Excel 檔案
        excel_df = pd.read_excel(temp_file_path)
        print(f"從 Excel 讀取的 Pandas DataFrame: {excel_df.shape}")
        
        # 轉換為 Polars
        excel_pl_df = pl.from_pandas(excel_df)
        print(f"轉換後的 Polars DataFrame: {excel_pl_df.shape}")
        
        # 驗證資料是否一致
        print(f"資料是否一致: {df_polars.equals(excel_pl_df)}")
        
    finally:
        # 清理臨時檔案
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_excel_to_polars() 