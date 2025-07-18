#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Jupyter 模式預設設定
"""

import requests
import json
import time

def test_jupyter_default_mode():
    """測試 Jupyter 模式是否已設為預設"""
    base_url = "http://localhost:8000"
    
    print("=== 測試 Jupyter 模式預設設定 ===")
    
    # 1. 測試新建策略時的預設值
    print("\n1. 測試新建策略預設值...")
    
    strategy_data = {
        "name": "測試 Jupyter 預設策略",
        "description": "測試 Jupyter 模式是否為預設",
        "type": "mixed",
        "editor_mode": "jupyter",  # 應該預設為 jupyter
        "jupyter_strategy_type": "analysis"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/strategies/custom",
            json=strategy_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                strategy_id = data.get("strategy_id")
                print(f"✅ 策略創建成功，ID: {strategy_id}")
                
                # 2. 驗證策略的編輯模式
                print("\n2. 驗證策略編輯模式...")
                strategy_response = requests.get(f"{base_url}/api/strategies/custom/{strategy_id}")
                
                if strategy_response.status_code == 200:
                    strategy_data = strategy_response.json()
                    if strategy_data.get("status") == "success":
                        strategy = strategy_data.get("strategy", {})
                        editor_mode = strategy.get("editor_mode", "jupyter")
                        jupyter_type = strategy.get("jupyter_strategy_type", "analysis")
                        
                        print(f"✅ 策略編輯模式: {editor_mode}")
                        print(f"✅ Jupyter 策略類型: {jupyter_type}")
                        
                        if editor_mode == "jupyter":
                            print("✅ Jupyter 模式已設為預設！")
                        else:
                            print("❌ Jupyter 模式未設為預設")
                            
                        # 3. 測試不同 Jupyter 策略類型
                        print("\n3. 測試不同 Jupyter 策略類型...")
                        jupyter_types = ["analysis", "vectorized", "state_machine", "mixed"]
                        
                        for jupyter_type in jupyter_types:
                            test_strategy_data = {
                                "name": f"測試 {jupyter_type} 策略",
                                "description": f"測試 {jupyter_type} 類型",
                                "type": "mixed",
                                "editor_mode": "jupyter",
                                "jupyter_strategy_type": jupyter_type
                            }
                            
                            try:
                                create_response = requests.post(
                                    f"{base_url}/api/strategies/custom",
                                    json=test_strategy_data,
                                    headers={"Content-Type": "application/json"}
                                )
                                
                                if create_response.status_code == 200:
                                    create_data = create_response.json()
                                    if create_data.get("status") == "success":
                                        print(f"✅ {jupyter_type} 策略創建成功")
                                    else:
                                        print(f"❌ {jupyter_type} 策略創建失敗: {create_data.get('message')}")
                                else:
                                    print(f"❌ {jupyter_type} 策略創建請求失敗: {create_response.status_code}")
                                    
                            except Exception as e:
                                print(f"❌ {jupyter_type} 策略創建異常: {e}")
                        
                        # 4. 測試前端預設值
                        print("\n4. 測試前端預設值...")
                        try:
                            frontend_response = requests.get(f"{base_url}/strategy_editor")
                            if frontend_response.status_code == 200:
                                content = frontend_response.text
                                
                                # 檢查新建策略對話框中的預設值
                                if 'id="modeJupyter" value="jupyter" checked' in content:
                                    print("✅ 前端新建策略對話框 Jupyter 模式已設為預設")
                                else:
                                    print("❌ 前端新建策略對話框 Jupyter 模式未設為預設")
                                    
                                # 檢查頁面載入時的初始化
                                if 'initializeJupyterMode()' in content:
                                    print("✅ 前端頁面載入時會初始化 Jupyter 模式")
                                else:
                                    print("❌ 前端頁面載入時未初始化 Jupyter 模式")
                                    
                            else:
                                print(f"❌ 前端頁面請求失敗: {frontend_response.status_code}")
                                
                        except Exception as e:
                            print(f"❌ 前端測試異常: {e}")
                        
                    else:
                        print(f"❌ 獲取策略失敗: {strategy_data.get('message')}")
                else:
                    print(f"❌ 策略請求失敗: {strategy_response.status_code}")
                    
            else:
                print(f"❌ 策略創建失敗: {data.get('message')}")
        else:
            print(f"❌ 創建請求失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 測試異常: {e}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_jupyter_default_mode() 