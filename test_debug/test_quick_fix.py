#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試修復功能
使用方法: & C:/Users/Allen/AppData/Local/Programs/Python/Python310/python.exe d:/Python/requests_parse/trading_web_system/test_debug/test_quick_fix.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_quick_fix():
    """快速測試修復"""
    print("=== 快速測試修復 ===")
    
    # 1. 測試API連線
    try:
        response = requests.get(f"{BASE_URL}/api/system/status", timeout=5)
        if response.status_code != 200:
            print("✗ API連線失敗")
            return False
        print("✓ API連線正常")
    except Exception as e:
        print(f"✗ API連線錯誤: {e}")
        return False
    
    # 2. 測試波段策略參數
    try:
        response = requests.get(f"{BASE_URL}/api/strategy/parameters?strategy_type=swing_trading")
        if response.status_code != 200:
            print("✗ 波段策略參數API失敗")
            return False
        
        result = response.json()
        if result["status"] != "success":
            print("✗ 波段策略參數API回應錯誤")
            return False
        
        params = result["strategy_parameters"]
        print(f"✓ 波段策略參數正常，共 {len(params)} 個參數")
        
        # 檢查關鍵參數
        key_params = ["commission_rate", "shares_per_trade", "use_take_profit"]
        for param in key_params:
            if param in params:
                print(f"  ✓ {param}: {params[param]['label']}")
            else:
                print(f"  ✗ 缺少參數: {param}")
                return False
                
    except Exception as e:
        print(f"✗ 波段策略參數測試失敗: {e}")
        return False
    
    # 3. 測試自定義策略API
    try:
        response = requests.get(f"{BASE_URL}/api/strategies/custom")
        if response.status_code != 200:
            print("✗ 自定義策略API失敗")
            return False
        
        result = response.json()
        if result["status"] != "success":
            print("✗ 自定義策略API回應錯誤")
            return False
        
        strategies = result["strategies"]
        print(f"✓ 自定義策略API正常，共 {len(strategies)} 個策略")
        
    except Exception as e:
        print(f"✗ 自定義策略API測試失敗: {e}")
        return False
    
    print("\n🎉 所有測試通過！")
    return True

if __name__ == "__main__":
    test_quick_fix() 