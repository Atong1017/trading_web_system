#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Jupyter 策略創建功能
"""

import requests
import json

def test_jupyter_strategy_creation():
    """測試 Jupyter 策略創建"""
    
    # 測試伺服器 URL
    base_url = "http://localhost:8000"
    
    # 測試不同的 Jupyter 策略類型
    jupyter_strategy_types = [
        {
            "name": "向量化策略測試",
            "description": "測試向量化 Jupyter 策略",
            "editor_mode": "jupyter",
            "jupyter_strategy_type": "vectorized"
        },
        {
            "name": "狀態機策略測試", 
            "description": "測試狀態機 Jupyter 策略",
            "editor_mode": "jupyter",
            "jupyter_strategy_type": "state_machine"
        },
        {
            "name": "混合策略測試",
            "description": "測試混合 Jupyter 策略", 
            "editor_mode": "jupyter",
            "jupyter_strategy_type": "hybrid"
        },
        {
            "name": "分析模式測試",
            "description": "測試分析模式 Jupyter 策略",
            "editor_mode": "jupyter", 
            "jupyter_strategy_type": "analysis"
        }
    ]
    
    created_strategies = []
    
    for strategy_config in jupyter_strategy_types:
        try:
            print(f"\n正在創建 {strategy_config['name']}...")
            
            # 創建策略
            response = requests.post(
                f"{base_url}/api/strategies/custom",
                json=strategy_config,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    strategy_id = data["strategy_id"]
                    created_strategies.append({
                        "id": strategy_id,
                        "config": strategy_config
                    })
                    print(f"✅ {strategy_config['name']} 創建成功，ID: {strategy_id}")
                else:
                    print(f"❌ {strategy_config['name']} 創建失敗: {data.get('message', '未知錯誤')}")
            else:
                print(f"❌ {strategy_config['name']} 創建失敗，HTTP 狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {strategy_config['name']} 創建異常: {str(e)}")
    
    # 測試載入創建的策略
    print(f"\n正在測試載入創建的策略...")
    for strategy in created_strategies:
        try:
            strategy_id = strategy["id"]
            config = strategy["config"]
            
            response = requests.get(f"{base_url}/api/strategies/custom/{strategy_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    strategy_info = data["strategy"]
                    print(f"✅ 成功載入策略: {strategy_info['name']}")
                    print(f"   編輯模式: {strategy_info.get('editor_mode', 'traditional')}")
                    print(f"   Jupyter 類型: {strategy_info.get('jupyter_strategy_type', 'analysis')}")
                    print(f"   程式碼長度: {len(strategy_info.get('code', ''))}")
                else:
                    print(f"❌ 載入策略失敗: {data.get('message', '未知錯誤')}")
            else:
                print(f"❌ 載入策略失敗，HTTP 狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 載入策略異常: {str(e)}")
    
    # 測試 Jupyter API
    print(f"\n正在測試 Jupyter API...")
    try:
        # 測試基本程式碼執行
        test_code = """
import numpy as np
import pandas as pd
print("Hello from Jupyter!")
x = np.array([1, 2, 3, 4, 5])
print(f"Array: {x}")
print(f"Mean: {x.mean()}")
"""
        
        response = requests.post(
            f"{base_url}/api/jupyter/execute",
            json={"code": test_code, "cell_id": "test_cell"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print("✅ Jupyter 程式碼執行成功")
                print(f"   輸出數量: {len(data.get('outputs', []))}")
            else:
                print(f"❌ Jupyter 程式碼執行失敗: {data.get('error', '未知錯誤')}")
        else:
            print(f"❌ Jupyter API 請求失敗，HTTP 狀態碼: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Jupyter API 測試異常: {str(e)}")
    
    print(f"\n測試完成！")
    print(f"成功創建 {len(created_strategies)} 個 Jupyter 策略")

if __name__ == "__main__":
    test_jupyter_strategy_creation() 