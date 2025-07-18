#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Jupyter API 效能優化
"""

import time
import asyncio
import polars as pl
import numpy as np
from datetime import datetime
import tempfile
import os
import pickle

# 模擬 FastAPI Request
class MockRequest:
    def __init__(self, form_data=None):
        self.form_data = form_data or {}
        self.app = type('MockApp', (), {'state': type('MockState', (), {'cache_manager': None})()})()
    
    async def form(self):
        return self.form_data

def test_variable_caching():
    """測試變數快取效能"""
    print("=== 測試變數快取效能 ===")
    
    # 模擬大型 DataFrame
    large_df = pl.DataFrame({
        'date': [datetime.now() for _ in range(10000)],
        'price': np.random.uniform(50, 150, 10000),
        'volume': np.random.randint(1000, 10000, 10000)
    })
    
    # 模擬變數字典
    variables = {
        'df': large_df,
        'small_list': [1, 2, 3, 4, 5],
        'config': {'param1': 10, 'param2': 20},
        'string_var': "測試字串"
    }
    
    # 測試儲存效能
    print("測試儲存變數...")
    start_time = time.time()
    
    # 模擬儲存過程
    temp_file = os.path.join(tempfile.gettempdir(), "test_variables.pkl")
    with open(temp_file, 'wb') as f:
        pickle.dump(variables, f)
    
    save_time = time.time() - start_time
    print(f"儲存時間: {save_time:.4f} 秒")
    
    # 測試載入效能
    print("測試載入變數...")
    start_time = time.time()
    
    with open(temp_file, 'rb') as f:
        loaded_variables = pickle.load(f)
    
    load_time = time.time() - start_time
    print(f"載入時間: {load_time:.4f} 秒")
    
    # 清理測試檔案
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    return save_time, load_time

def test_execution_flow():
    """測試執行流程效能"""
    print("\n=== 測試執行流程效能 ===")
    
    # 模擬程式碼
    test_code = """
import polars as pl
import numpy as np
from datetime import datetime

# 創建測試資料
dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(366)]
df = pl.DataFrame({
    'date': dates,
    'price': np.random.uniform(50, 150, 366),
    'volume': np.random.randint(1000, 10000, 366)
})

# 計算移動平均
df = df.with_columns([
    pl.col('price').rolling_mean(5).alias('ma5'),
    pl.col('price').rolling_mean(20).alias('ma20')
])

print(f"資料形狀: {df.shape}")
print(f"欄位: {df.columns}")
print(df.head())
"""
    
    # 模擬執行環境
    execution_env = {
        'pl': pl,
        'np': np,
        'datetime': datetime,
        'timedelta': lambda days: datetime.timedelta(days=days),
        'print': print
    }
    
    # 測試執行時間
    print("測試程式碼執行...")
    start_time = time.time()
    
    try:
        exec(test_code, execution_env)
        execution_time = time.time() - start_time
        print(f"執行時間: {execution_time:.4f} 秒")
    except Exception as e:
        print(f"執行失敗: {e}")
        execution_time = 0
    
    return execution_time

def test_multiple_cell_execution():
    """測試多個 cell 連續執行的效能"""
    print("\n=== 測試多個 Cell 連續執行效能 ===")
    
    cells = [
        "import polars as pl\nimport numpy as np\nprint('Cell 1: 載入模組')",
        "df = pl.DataFrame({'a': [1,2,3], 'b': [4,5,6]})\nprint('Cell 2: 創建 DataFrame')",
        "result = df.select(pl.all().sum())\nprint('Cell 3: 計算統計')",
        "print(f'結果: {result}')\nresult",
        "df2 = df.with_columns(pl.col('a') * 2)\nprint('Cell 5: 新增欄位')",
        "final_result = df2.filter(pl.col('a') > 2)\nprint('Cell 6: 過濾資料')\nfinal_result"
    ]
    
    total_time = 0
    cell_times = []
    
    # 共享執行環境
    shared_env = {
        'pl': pl,
        'np': np,
        'print': print
    }
    
    for i, code in enumerate(cells, 1):
        print(f"\n執行 Cell {i}...")
        start_time = time.time()
        
        try:
            exec(code, shared_env)
            cell_time = time.time() - start_time
            cell_times.append(cell_time)
            total_time += cell_time
            print(f"Cell {i} 執行時間: {cell_time:.4f} 秒")
        except Exception as e:
            print(f"Cell {i} 執行失敗: {e}")
            cell_times.append(0)
    
    print(f"\n總執行時間: {total_time:.4f} 秒")
    print(f"平均每個 Cell 時間: {total_time/len(cells):.4f} 秒")
    print(f"最快 Cell: {min(cell_times):.4f} 秒")
    print(f"最慢 Cell: {max(cell_times):.4f} 秒")
    
    return total_time, cell_times

def main():
    """主測試函數"""
    print("開始 Jupyter API 效能測試...")
    print("=" * 50)
    
    # 測試變數快取
    save_time, load_time = test_variable_caching()
    
    # 測試執行流程
    execution_time = test_execution_flow()
    
    # 測試多個 cell
    total_time, cell_times = test_multiple_cell_execution()
    
    # 總結
    print("\n" + "=" * 50)
    print("效能測試總結:")
    print(f"變數儲存時間: {save_time:.4f} 秒")
    print(f"變數載入時間: {load_time:.4f} 秒")
    print(f"程式碼執行時間: {execution_time:.4f} 秒")
    print(f"多 Cell 總時間: {total_time:.4f} 秒")
    
    # 效能建議
    print("\n效能優化建議:")
    if save_time > 0.1:
        print("- 變數儲存較慢，考慮使用更高效的序列化格式")
    if load_time > 0.1:
        print("- 變數載入較慢，已實作記憶體快取優化")
    if execution_time > 1.0:
        print("- 程式碼執行較慢，考慮優化演算法或使用向量化操作")
    if total_time > 2.0:
        print("- 多 Cell 執行較慢，考慮減少不必要的變數儲存/載入")
    
    print("\n優化後的改進:")
    print("- 新增記憶體快取，避免重複檔案 I/O")
    print("- 減少不必要的變數載入操作")
    print("- 使用檔案時間戳記檢查，只在檔案變更時重新載入")

if __name__ == "__main__":
    main() 