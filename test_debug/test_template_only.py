#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專門測試 get_strategy_template API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# 測試配置
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10

def test_get_strategy_template():
    """測試取得策略模板"""
    print("測試取得策略模板...")
    try:
        response = requests.get(f"{BASE_URL}/api/strategies/custom/template", timeout=TEST_TIMEOUT)
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.text[:200]}...")
        
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

if __name__ == "__main__":
    print("開始測試 get_strategy_template API")
    print(f"測試目標: {BASE_URL}")
    
    result = test_get_strategy_template()
    
    if result:
        print("✅ 測試通過")
    else:
        print("❌ 測試失敗") 