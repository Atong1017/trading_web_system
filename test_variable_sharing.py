#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Jupyter 變數共享功能
"""

import os
import pickle
import tempfile
import numpy as np
from datetime import datetime

def test_variable_sharing():
    """測試變數共享功能"""
    print("測試 Jupyter 變數共享功能")
    print("=" * 50)
    
    # 模擬 JupyterAPI 的變數檔案路徑
    variables_file = os.path.join(tempfile.gettempdir(), "jupyter_variables.pkl")
    
    def load_variables():
        """從檔案載入變數"""
        try:
            if os.path.exists(variables_file):
                with open(variables_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"載入變數失敗: {e}")
        return {}
    
    def save_variables(variables):
        """將變數儲存到檔案"""
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(variables_file), exist_ok=True)
            
            # 使用臨時檔案來避免寫入衝突
            temp_file = variables_file + ".tmp"
            with open(temp_file, 'wb') as f:
                pickle.dump(variables, f)
            
            # 原子性地替換檔案
            if os.path.exists(variables_file):
                os.remove(variables_file)
            os.rename(temp_file, variables_file)
            
            print(f"變數已儲存到: {variables_file}")
        except Exception as e:
            print(f"儲存變數失敗: {e}")
    
    def clear_variables():
        """清除變數"""
        try:
            if os.path.exists(variables_file):
                os.remove(variables_file)
            print("已清除變數檔案")
        except Exception as e:
            print(f"清除變數失敗: {e}")
    
    # 清除舊的變數檔案
    clear_variables()
    
    # 測試 1: 模擬第一個 cell 執行
    print("\n1. 模擬第一個 cell 執行...")
    cell1_variables = {
        'stock_id': '2330',
        'matched_stock_id': '2330',
        'test_value': 42,
        'test_array': np.array([1, 2, 3, 4, 5]),
        'test_list': [1, 2, 3, 4, 5],
        'test_dict': {'a': 1, 'b': 2, 'c': 3}
    }
    
    save_variables(cell1_variables)
    print(f"第一個 cell 變數: {list(cell1_variables.keys())}")
    
    # 測試 2: 模擬第二個 cell 執行
    print("\n2. 模擬第二個 cell 執行...")
    loaded_variables = load_variables()
    print(f"載入的變數: {list(loaded_variables.keys())}")
    
    # 檢查是否包含第一個 cell 的變數
    if 'matched_stock_id' in loaded_variables:
        print(f"✓ 成功找到 matched_stock_id: {loaded_variables['matched_stock_id']}")
    else:
        print("✗ 未找到 matched_stock_id")
    
    if 'test_array' in loaded_variables:
        print(f"✓ 成功找到 test_array: {loaded_variables['test_array']}")
    else:
        print("✗ 未找到 test_array")
    
    # 測試 3: 第二個 cell 添加新變數
    print("\n3. 第二個 cell 添加新變數...")
    cell2_variables = loaded_variables.copy()
    cell2_variables['new_variable'] = '這是第二個 cell 的變數'
    cell2_variables['calculated_value'] = loaded_variables.get('test_value', 0) * 2
    
    save_variables(cell2_variables)
    print(f"第二個 cell 變數: {list(cell2_variables.keys())}")
    
    # 測試 4: 驗證變數是否正確保存
    print("\n4. 驗證變數保存...")
    final_variables = load_variables()
    print(f"最終變數: {list(final_variables.keys())}")
    
    if 'new_variable' in final_variables:
        print(f"✓ 成功保存新變數: {final_variables['new_variable']}")
    else:
        print("✗ 新變數保存失敗")
    
    if 'calculated_value' in final_variables:
        print(f"✓ 成功保存計算值: {final_variables['calculated_value']}")
    else:
        print("✗ 計算值保存失敗")
    
    # 測試 5: 清除變數
    print("\n5. 清除變數...")
    clear_variables()
    
    remaining_variables = load_variables()
    if not remaining_variables:
        print("✓ 變數清除成功")
    else:
        print(f"✗ 變數清除失敗，剩餘: {list(remaining_variables.keys())}")
    
    print("\n測試完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_variable_sharing() 