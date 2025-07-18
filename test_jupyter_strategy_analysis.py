#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Jupyter 策略分析功能
"""

import requests
import json
import time

def test_jupyter_strategy_analysis():
    """測試 Jupyter 策略分析功能"""
    base_url = "http://localhost:8000"
    
    print("=== 測試 Jupyter 策略分析功能 ===")
    
    # 測試案例：不同類型的策略程式碼
    test_cases = [
        {
            "name": "狀態機策略",
            "code": """
def should_entry(data, position):
    # 狀態機策略：檢查是否應該進場
    if position.is_empty():
        return data['close'] > data['ma20']
    return False

def should_exit(data, position):
    # 檢查是否應該出場
    return data['close'] < data['ma10']
""",
            "expected_type": "state_machine"
        },
        {
            "name": "向量化策略",
            "code": """
def calculate_entry_signals(data):
    # 向量化策略：一次性計算所有進場訊號
    signals = data['close'] > data['ma20']
    return signals

def calculate_exit_signals(data):
    # 計算出場訊號
    signals = data['close'] < data['ma10']
    return signals
""",
            "expected_type": "vectorized"
        },
        {
            "name": "混合式策略",
            "code": """
def should_entry(data, position):
    # 狀態機函數
    if position.is_empty():
        return data['close'] > data['ma20']
    return False

def calculate_entry_signals(data):
    # 向量化函數
    signals = data['close'] > data['ma20']
    return signals

def should_exit(data, position):
    return data['close'] < data['ma10']
""",
            "expected_type": "mixed"
        },
        {
            "name": "未知類型策略",
            "code": """
def analyze_data(data):
    # 一般分析函數
    result = data['close'].mean()
    return result

def plot_chart(data):
    # 繪圖函數
    import matplotlib.pyplot as plt
    plt.plot(data['close'])
    plt.show()
""",
            "expected_type": "unknown"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 測試 {test_case['name']}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/jupyter/analyze-strategy",
                json={"code": test_case['code']},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    strategy_type = data.get("strategy_type")
                    analysis = data.get("analysis", {})
                    
                    print(f"✅ 策略類型: {strategy_type}")
                    print(f"✅ 預期類型: {test_case['expected_type']}")
                    print(f"✅ 分析結果: {analysis.get('description', 'N/A')}")
                    print(f"✅ 找到 should_entry: {analysis.get('has_should_entry', False)}")
                    print(f"✅ 找到 calculate_entry_signals: {analysis.get('has_calculate_entry_signals', False)}")
                    print(f"✅ 發現的函數: {analysis.get('functions_found', [])}")
                    
                    if strategy_type == test_case['expected_type']:
                        print("✅ 類型判斷正確！")
                    else:
                        print(f"❌ 類型判斷錯誤！預期 {test_case['expected_type']}，實際 {strategy_type}")
                else:
                    print(f"❌ 分析失敗: {data.get('error', '未知錯誤')}")
            else:
                print(f"❌ 請求失敗: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 測試異常: {e}")
    
    print("\n=== 測試完成 ===")

def test_jupyter_default_mode_fix():
    """測試 Jupyter 模式預設修復"""
    base_url = "http://localhost:8000"
    
    print("\n=== 測試 Jupyter 模式預設修復 ===")
    
    # 測試新建策略
    strategy_data = {
        "name": "測試 Jupyter 預設修復",
        "description": "測試新建策略後是否正確顯示 Jupyter 模式",
        "type": "mixed",
        "editor_mode": "jupyter",
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
                
                # 驗證策略資訊
                strategy_response = requests.get(f"{base_url}/api/strategies/custom/{strategy_id}")
                
                if strategy_response.status_code == 200:
                    strategy_data = strategy_response.json()
                    if strategy_data.get("status") == "success":
                        strategy = strategy_data.get("strategy", {})
                        editor_mode = strategy.get("editor_mode", "jupyter")
                        jupyter_type = strategy.get("jupyter_strategy_type", "analysis")
                        
                        print(f"✅ 編輯模式: {editor_mode}")
                        print(f"✅ Jupyter 類型: {jupyter_type}")
                        
                        if editor_mode == "jupyter":
                            print("✅ Jupyter 模式設定正確！")
                        else:
                            print("❌ Jupyter 模式設定錯誤")
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

if __name__ == "__main__":
    test_jupyter_strategy_analysis()
    test_jupyter_default_mode_fix() 