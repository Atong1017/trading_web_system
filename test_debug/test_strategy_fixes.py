#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試策略修復功能
使用方法: & C:/Users/Allen/AppData/Local/Programs/Python/Python310/python.exe d:/Python/requests_parse/trading_web_system/test_debug/test_strategy_fixes.py
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_api_connection():
    """測試API連線"""
    print("=== 測試API連線 ===")
    try:
        response = requests.get(f"{BASE_URL}/api/system/status", timeout=5)
        if response.status_code == 200:
            print("✓ API連線正常")
            return True
        else:
            print(f"✗ API連線失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API連線錯誤: {e}")
        return False

def test_custom_strategy_integration():
    """測試自定義策略整合到回測系統"""
    print("\n=== 測試自定義策略整合 ===")
    
    # 1. 建立自定義策略
    print("1. 建立自定義策略...")
    strategy_data = {
        "name": "測試移動平均策略",
        "description": "簡單的移動平均交叉策略",
        "type": "template"
    }
    
    response = requests.post(f"{BASE_URL}/api/strategies/custom", json=strategy_data)
    print(f"建立策略回應: {response.status_code}")
    if response.status_code != 200:
        print(f"建立策略失敗: {response.text}")
        return None
    
    result = response.json()
    print(f"建立策略結果: {result}")
    if result["status"] != "success":
        print(f"建立策略失敗: {result}")
        return None
    
    strategy_id = result["strategy_id"]
    print(f"策略建立成功，ID: {strategy_id}")
    
    # 2. 更新策略程式碼
    print("2. 更新策略程式碼...")
    strategy_code = '''
class MyStrategy:
    def __init__(self, parameters):
        self.parameters = parameters
        self.strategy_name = "移動平均策略"
        self.strategy_description = "簡單的移動平均交叉策略"
    
    def execute(self, data):
        """
        策略執行邏輯
        data: 股票資料 (polars DataFrame)
        """
        # 在這裡實作您的策略邏輯
        result = data.clone()
        
        # 範例：簡單的移動平均策略
        if len(data) > 20:
            result = result.with_columns([
                pl.col('close').rolling_mean(window_size=20).alias('ma20'),
                pl.col('close').rolling_mean(window_size=5).alias('ma5')
            ])
            
            # 產生買賣訊號
            result = result.with_columns([
                pl.when(pl.col('ma5') > pl.col('ma20'))
                .then(1)  # 買入訊號
                .otherwise(0).alias('signal')
            ])
        
        return result
    
    def get_parameters(self):
        """取得策略參數"""
        return self.parameters
'''
    
    update_data = {
        "name": "測試移動平均策略",
        "description": "簡單的移動平均交叉策略",
        "code": strategy_code
    }
    
    response = requests.put(f"{BASE_URL}/api/strategies/custom/{strategy_id}", json=update_data)
    print(f"更新策略回應: {response.status_code}")
    if response.status_code != 200:
        print(f"更新策略失敗: {response.text}")
        return None
    
    print("策略程式碼更新成功")
    
    # 3. 檢查策略是否出現在回測頁面的選項中
    print("3. 檢查策略是否出現在回測選項中...")
    response = requests.get(f"{BASE_URL}/api/strategies/custom")
    print(f"取得策略列表回應: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"策略列表結果: {result}")
        if result["status"] == "success":
            strategies = result["strategies"]
            found = False
            for strategy in strategies:
                if strategy["id"] == strategy_id:
                    found = True
                    print(f"✓ 找到策略: {strategy['name']}")
                    break
            
            if not found:
                print("✗ 警告: 策略未出現在列表中")
        else:
            print(f"✗ 取得策略列表失敗: {result}")
    else:
        print(f"✗ 取得策略列表失敗: {response.text}")
    
    return strategy_id

def test_swing_trading_parameters():
    """測試波段策略參數"""
    print("\n=== 測試波段策略參數 ===")
    
    # 取得波段策略參數
    response = requests.get(f"{BASE_URL}/api/strategy/parameters?strategy_type=swing_trading")
    print(f"取得波段策略參數回應: {response.status_code}")
    if response.status_code != 200:
        print(f"取得波段策略參數失敗: {response.text}")
        return False
    
    result = response.json()
    print(f"波段策略參數結果: {result}")
    if result["status"] != "success":
        print(f"取得波段策略參數失敗: {result}")
        return False
    
    strategy_parameters = result["strategy_parameters"]
    print(f"策略名稱: {result['strategy_name']}")
    print(f"策略描述: {result['strategy_description']}")
    print(f"參數數量: {len(strategy_parameters)}")
    
    # 檢查關鍵參數是否存在
    key_params = [
        "commission_rate", "commission_discount", "securities_tax_rate", 
        "shares_per_trade", "entry_condition", "exit_price_condition",
        "use_take_profit", "take_profit_percentage", "use_stop_loss", 
        "stop_loss_percentage", "use_max_holding_days", "max_holding_days"
    ]
    
    missing_params = []
    for param in key_params:
        if param not in strategy_parameters:
            missing_params.append(param)
        else:
            param_info = strategy_parameters[param]
            print(f"✓ {param}: {param_info['label']} (預設值: {param_info.get('default', 'N/A')})")
    
    if missing_params:
        print(f"✗ 缺少參數: {missing_params}")
        return False
    else:
        print("✓ 所有關鍵參數都存在")
        return True

def test_day_trading_parameters():
    """測試當沖策略參數"""
    print("\n=== 測試當沖策略參數 ===")
    
    response = requests.get(f"{BASE_URL}/api/strategy/parameters?strategy_type=day_trading")
    print(f"取得當沖策略參數回應: {response.status_code}")
    if response.status_code != 200:
        print(f"取得當沖策略參數失敗: {response.text}")
        return False
    
    result = response.json()
    print(f"當沖策略參數結果: {result}")
    if result["status"] != "success":
        print(f"取得當沖策略參數失敗: {result}")
        return False
    
    strategy_parameters = result["strategy_parameters"]
    print(f"策略名稱: {result['strategy_name']}")
    print(f"策略描述: {result['strategy_description']}")
    print(f"參數數量: {len(strategy_parameters)}")
    
    # 檢查幾個關鍵參數
    for param_name, param_info in strategy_parameters.items():
        print(f"✓ {param_name}: {param_info['label']} (預設值: {param_info.get('default', 'N/A')})")
    
    return True

def test_custom_strategy_parameters():
    """測試自定義策略參數"""
    print("\n=== 測試自定義策略參數 ===")
    
    # 建立一個簡單的自定義策略
    strategy_data = {
        "name": "參數測試策略",
        "description": "測試參數功能的策略",
        "type": "template"
    }
    
    response = requests.post(f"{BASE_URL}/api/strategies/custom", json=strategy_data)
    print(f"建立參數測試策略回應: {response.status_code}")
    if response.status_code != 200:
        print(f"建立策略失敗: {response.text}")
        return False
    
    result = response.json()
    print(f"建立參數測試策略結果: {result}")
    if result["status"] != "success":
        print(f"建立策略失敗: {result}")
        return False
    
    strategy_id = result["strategy_id"]
    
    # 更新策略程式碼，包含參數定義
    strategy_code = '''
class MyStrategy:
    def __init__(self, parameters):
        self.parameters = parameters
        self.strategy_name = "參數測試策略"
        self.strategy_description = "測試參數功能的策略"
        
        # 定義自定義參數
        self.custom_parameters = {
            "ma_period": {
                "type": "number",
                "label": "移動平均週期",
                "default": 20,
                "min": 5,
                "max": 100,
                "step": 1,
                "description": "移動平均線的週期"
            },
            "signal_threshold": {
                "type": "number",
                "label": "訊號閾值",
                "default": 0.5,
                "min": 0.1,
                "max": 2.0,
                "step": 0.1,
                "description": "買賣訊號的閾值"
            }
        }
    
    def execute(self, data):
        return data
    
    def get_parameters(self):
        return self.parameters
'''
    
    update_data = {
        "name": "參數測試策略",
        "description": "測試參數功能的策略",
        "code": strategy_code
    }
    
    response = requests.put(f"{BASE_URL}/api/strategies/custom/{strategy_id}", json=update_data)
    print(f"更新參數測試策略回應: {response.status_code}")
    if response.status_code != 200:
        print(f"更新策略失敗: {response.text}")
        return False
    
    # 檢查自定義策略參數
    response = requests.get(f"{BASE_URL}/api/strategies/custom/{strategy_id}")
    print(f"取得參數測試策略回應: {response.status_code}")
    if response.status_code != 200:
        print(f"取得策略失敗: {response.text}")
        return False
    
    result = response.json()
    print(f"取得參數測試策略結果: {result}")
    if result["status"] != "success":
        print(f"取得策略失敗: {result}")
        return False
    
    strategy = result["strategy"]
    print(f"策略名稱: {strategy['name']}")
    print(f"策略描述: {strategy['description']}")
    
    # 清理測試策略
    response = requests.delete(f"{BASE_URL}/api/strategies/custom/{strategy_id}")
    if response.status_code == 200:
        print("✓ 測試策略清理完成")
    
    return True

def main():
    """主測試函數"""
    print("開始測試策略修復功能...")
    print("=" * 50)
    
    # 測試API連線
    if not test_api_connection():
        print("API連線失敗，請確認伺服器是否正在運行")
        return
    
    # 測試自定義策略整合
    strategy_id = test_custom_strategy_integration()
    
    # 測試波段策略參數
    swing_success = test_swing_trading_parameters()
    
    # 測試當沖策略參數
    day_success = test_day_trading_parameters()
    
    # 測試自定義策略參數
    custom_success = test_custom_strategy_parameters()
    
    # 清理測試策略
    if strategy_id:
        response = requests.delete(f"{BASE_URL}/api/strategies/custom/{strategy_id}")
        if response.status_code == 200:
            print(f"✓ 清理測試策略 {strategy_id}")
    
    print("\n" + "=" * 50)
    print("=== 測試結果總結 ===")
    print(f"自定義策略整合: {'✓ 成功' if strategy_id else '✗ 失敗'}")
    print(f"波段策略參數: {'✓ 成功' if swing_success else '✗ 失敗'}")
    print(f"當沖策略參數: {'✓ 成功' if day_success else '✗ 失敗'}")
    print(f"自定義策略參數: {'✓ 成功' if custom_success else '✗ 失敗'}")
    
    if strategy_id and swing_success and day_success and custom_success:
        print("\n🎉 所有測試都通過了！")
    else:
        print("\n⚠️  部分測試失敗，請檢查上述錯誤信息")

if __name__ == "__main__":
    main() 