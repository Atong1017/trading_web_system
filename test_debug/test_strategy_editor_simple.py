#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試策略編輯器功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# 測試配置
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10

def test_strategy_editor_page():
    """測試策略編輯器頁面"""
    print("測試策略編輯器頁面...")
    try:
        response = requests.get(f"{BASE_URL}/strategy-editor", timeout=TEST_TIMEOUT)
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            print("✅ 策略編輯器頁面可正常訪問")
            return True
        else:
            print(f"❌ 策略編輯器頁面無法訪問: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 測試策略編輯器頁面失敗: {e}")
        return False

def test_get_custom_strategies():
    """測試取得自定義策略列表"""
    print("\n測試取得自定義策略列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/strategies/custom", timeout=TEST_TIMEOUT)
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if data.get('status') == 'success':
                strategies = data.get('strategies', [])
                print(f"✅ 成功取得 {len(strategies)} 個自定義策略")
                return True
            else:
                print(f"❌ 取得自定義策略失敗: {data}")
                return False
        else:
            print(f"❌ 取得自定義策略 HTTP 錯誤: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 測試取得自定義策略失敗: {e}")
        return False

def test_get_strategy_template():
    """測試取得策略模板"""
    print("\n測試取得策略模板...")
    try:
        response = requests.get(f"{BASE_URL}/api/strategies/custom/template", timeout=TEST_TIMEOUT)
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"回應狀態: {data.get('status')}")
            if data.get('status') == 'success' and 'template' in data:
                template = data['template']
                print(f"✅ 成功取得策略模板，長度: {len(template)}")
                print(f"模板前100字: {template[:100]}...")
                return True
            else:
                print(f"❌ 取得策略模板失敗: {data}")
                return False
        else:
            print(f"❌ 取得策略模板 HTTP 錯誤: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 測試取得策略模板失敗: {e}")
        return False

def test_create_custom_strategy():
    """測試建立自定義策略"""
    print("\n測試建立自定義策略...")
    try:
        test_strategy = {
            "name": "測試策略",
            "description": "這是一個測試策略",
            "type": "template"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/strategies/custom",
            json=test_strategy,
            timeout=TEST_TIMEOUT
        )
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if data.get('status') == 'success' and 'strategy_id' in data:
                strategy_id = data['strategy_id']
                print(f"✅ 成功建立策略，ID: {strategy_id}")
                return strategy_id
            else:
                print(f"❌ 建立策略失敗: {data}")
                return None
        else:
            print(f"❌ 建立策略 HTTP 錯誤: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 測試建立策略失敗: {e}")
        return None

def main():
    """主測試函數"""
    print("開始測試策略編輯器功能")
    print(f"測試目標: {BASE_URL}")
    
    # 測試結果
    results = []
    
    # 測試策略編輯器頁面
    results.append(("策略編輯器頁面", test_strategy_editor_page()))
    
    # 測試取得自定義策略列表
    results.append(("取得自定義策略列表", test_get_custom_strategies()))
    
    # 測試取得策略模板
    results.append(("取得策略模板", test_get_strategy_template()))
    
    # 測試建立自定義策略
    strategy_id = test_create_custom_strategy()
    results.append(("建立自定義策略", strategy_id is not None))
    
    # 輸出測試總結
    print(f"\n{'='*50}")
    print("測試總結")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試都通過！策略編輯器功能正常。")
    else:
        print("⚠️  部分測試失敗，請檢查相關功能。")

if __name__ == "__main__":
    main() 