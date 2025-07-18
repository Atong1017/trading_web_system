#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的 API 測試
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_api():
    """測試 API"""
    print("測試策略模板 API...")
    
    try:
        # 測試策略模板 API
        response = requests.get("http://localhost:8000/api/strategies/custom/template")
        print(f"HTTP 狀態碼: {response.status_code}")
        print(f"回應內容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"狀態: {data.get('status')}")
            print(f"模板長度: {len(data.get('template', ''))}")
        else:
            print(f"錯誤: {response.text}")
            
    except Exception as e:
        print(f"請求失敗: {e}")

if __name__ == "__main__":
    test_api() 