#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Jupyter 模式中 DataFrame 變數傳遞的修復
"""

import polars as pl
import tempfile
import os
import pickle
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.jupyter_api import JupyterAPI
from strategies.dynamic_strategy import DynamicStrategy

def test_dataframe_variable_persistence():
    """測試 DataFrame 變數的持久化"""
    print("=== 測試 DataFrame 變數持久化 ===")
    
    # 創建測試 DataFrame
    test_df = pl.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'close': [100, 101, 102],
        'volume': [1000, 1100, 1200]
    })
    
    test_stock_df = pl.DataFrame({
        'stock_id': ['2330', '2330', '2330'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'price': [100, 101, 102]
    })
    
    # 模擬執行環境
    execution_env = {
        'df': test_df,
        'stock_df': test_stock_df,
        'a': 1,
        'b': 'test'
    }
    
    # 保存變數
    JupyterAPI._update_global_variables(execution_env)
    
    # 載入變數
    loaded_variables = JupyterAPI._load_variables()
    
    print(f"保存的變數: {list(loaded_variables.keys())}")
    
    # 檢查 DataFrame 是否正確保存
    if 'df' in loaded_variables:
        print(f"df 變數存在，shape: {loaded_variables['df'].shape}")
        print(f"df 內容: {loaded_variables['df']}")
    else:
        print("df 變數不存在")
    
    if 'stock_df' in loaded_variables:
        print(f"stock_df 變數存在，shape: {loaded_variables['stock_df'].shape}")
        print(f"stock_df 內容: {loaded_variables['stock_df']}")
    else:
        print("stock_df 變數不存在")

def test_dynamic_strategy_dataframe_injection():
    """測試 DynamicStrategy 中的 DataFrame 注入"""
    print("\n=== 測試 DynamicStrategy DataFrame 注入 ===")
    
    # 創建測試 DataFrame
    test_df = pl.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'close': [100, 101, 102],
        'volume': [1000, 1100, 1200]
    })
    
    test_stock_df = pl.DataFrame({
        'stock_id': ['2330', '2330', '2330'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'price': [100, 101, 102]
    })
    
    # 創建測試策略程式碼
    strategy_code = """
def should_entry(stock_data, current_index, excel_pl_df=None):
    # 檢查是否能訪問到 DataFrame 變數
    print(f"df shape: {df.shape if 'df' in globals() else 'Not found'}")
    print(f"stock_df shape: {stock_df.shape if 'stock_df' in globals() else 'Not found'}")
    print(f"stock_data shape: {stock_data.shape}")
    return True, {'reason': 'test'}
"""
    
    # 創建 DynamicStrategy 實例
    strategy = DynamicStrategy(
        parameters={},
        strategy_code=strategy_code,
        strategy_name="測試策略",
        data=(test_df, test_stock_df)
    )
    
    # 測試 should_entry 函數
    try:
        result = strategy.should_entry(test_df, 0, test_stock_df)
        print(f"should_entry 結果: {result}")
    except Exception as e:
        print(f"should_entry 執行錯誤: {e}")

def test_jupyter_api_integration():
    """測試 Jupyter API 整合"""
    print("\n=== 測試 Jupyter API 整合 ===")
    
    # 創建測試 DataFrame
    test_df = pl.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'close': [100, 101, 102],
        'volume': [1000, 1100, 1200]
    })
    
    test_stock_df = pl.DataFrame({
        'stock_id': ['2330', '2330', '2330'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'price': [100, 101, 102]
    })
    
    # 模擬 Jupyter 執行環境
    execution_env = JupyterAPI._create_execution_environment()
    execution_env['df'] = test_df
    execution_env['stock_df'] = test_stock_df
    
    # 執行測試程式碼
    test_code = """
# 測試 DataFrame 變數
print(f"df shape: {df.shape}")
print(f"stock_df shape: {stock_df.shape}")

# 創建新的 DataFrame
new_df = df.filter(pl.col('close') > 100)
print(f"new_df shape: {new_df.shape}")
"""
    
    # 執行程式碼
    outputs = JupyterAPI._execute_code_with_outputs(test_code, execution_env)
    
    # 更新全域變數
    JupyterAPI._update_global_variables(execution_env)
    
    # 檢查保存的變數
    saved_variables = JupyterAPI._load_variables()
    print(f"保存的變數: {list(saved_variables.keys())}")
    
    # 檢查 new_df 是否被保存
    if 'new_df' in saved_variables:
        print(f"new_df 被正確保存，shape: {saved_variables['new_df'].shape}")
    else:
        print("new_df 沒有被保存")

if __name__ == "__main__":
    test_dataframe_variable_persistence()
    test_dynamic_strategy_dataframe_injection()
    test_jupyter_api_integration()
    
    print("\n=== 測試完成 ===") 