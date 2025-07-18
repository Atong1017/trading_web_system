#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Jupyter API 功能
"""

import requests
import json

def test_jupyter_api():
    """測試 Jupyter API 功能"""
    base_url = "http://localhost:8000"
    
    print("測試 Jupyter API 功能...")
    
    # 測試 1: 基本程式碼執行
    print("\n1. 測試基本程式碼執行")
    test_code = """
import numpy as np
import pandas as pd

# 生成簡單資料
data = np.random.randn(10, 3)
df = pd.DataFrame(data, columns=['A', 'B', 'C'])
print("生成的資料:")
print(df)
df
"""
    
    response = requests.post(
        f"{base_url}/api/jupyter/execute",
        json={
            "code": test_code,
            "cell_id": "test_cell_1"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 基本程式碼執行成功")
        print(f"輸出數量: {len(result.get('outputs', []))}")
        for i, output in enumerate(result.get('outputs', [])):
            print(f"  輸出 {i+1}: {output.get('output_type', 'unknown')}")
    else:
        print(f"❌ 基本程式碼執行失敗: {response.status_code}")
        print(response.text)
    
    # 測試 2: 圖表生成
    print("\n2. 測試圖表生成")
    plot_code = """
import matplotlib.pyplot as plt
import numpy as np

# 生成資料
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 繪製圖表
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.plot(x, np.cos(x), 'r--', linewidth=2, label='cos(x)')
plt.title('三角函數圖表')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
"""
    
    response = requests.post(
        f"{base_url}/api/jupyter/execute",
        json={
            "code": plot_code,
            "cell_id": "test_cell_2"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 圖表生成成功")
        outputs = result.get('outputs', [])
        for output in outputs:
            if output.get('output_type') == 'display_data':
                if 'image/png' in output.get('data', {}):
                    print("  包含圖片輸出")
                if 'text/html' in output.get('data', {}):
                    print("  包含 HTML 輸出")
    else:
        print(f"❌ 圖表生成失敗: {response.status_code}")
        print(response.text)
    
    # 測試 3: 錯誤處理
    print("\n3. 測試錯誤處理")
    error_code = """
# 故意製造錯誤
undefined_variable + 1
"""
    
    response = requests.post(
        f"{base_url}/api/jupyter/execute",
        json={
            "code": error_code,
            "cell_id": "test_cell_3"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'error':
            print("✅ 錯誤處理正常")
            print(f"錯誤訊息: {result.get('error', 'unknown')}")
        else:
            print("❌ 錯誤處理異常")
    else:
        print(f"❌ 錯誤處理測試失敗: {response.status_code}")
        print(response.text)
    
    # 測試 4: 範例資料載入
    print("\n4. 測試範例資料載入")
    response = requests.post(
        f"{base_url}/api/jupyter/sample-data",
        json={
            "data_type": "stock_data"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print("✅ 範例資料載入成功")
            data = result.get('data')
            if hasattr(data, 'shape'):
                print(f"  資料形狀: {data.shape}")
            elif isinstance(data, list):
                print(f"  資料筆數: {len(data)}")
        else:
            print("❌ 範例資料載入失敗")
            print(result.get('error', 'unknown'))
    else:
        print(f"❌ 範例資料載入測試失敗: {response.status_code}")
        print(response.text)
    
    print("\n測試完成！")

if __name__ == "__main__":
    test_jupyter_api() 