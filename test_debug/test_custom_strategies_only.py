#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專門測試 get_custom_strategies API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# 測試配置
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10

def test_get_custom_strategies():
    """測試取得自定義策略列表"""
    print("測試取得自定義策略列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/strategies/custom", timeout=TEST_TIMEOUT)
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"回應狀態: {data.get('status')}")
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

if __name__ == "__main__":
    print("開始測試 get_custom_strategies API")
    print(f"測試目標: {BASE_URL}")
    
    result = test_get_custom_strategies()
    
    if result:
        print("✅ 測試通過")
    else:
        print("❌ 測試失敗") 