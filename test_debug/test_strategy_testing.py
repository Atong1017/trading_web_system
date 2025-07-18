#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試策略測試功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# 測試配置
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10

def test_strategy_testing():
    """測試策略測試功能"""
    print("測試策略測試功能...")
    
    try:
        # 1. 建立測試策略
        strategy_data = {
            "name": "測試策略",
            "description": "用於測試策略測試功能的策略",
            "type": "template"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/strategies/custom",
            json=strategy_data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code != 200:
            print(f"❌ 建立策略失敗: HTTP {response.status_code}")
            return False
        
        result = response.json()
        if result.get('status') != 'success':
            print(f"❌ 建立策略失敗: {result}")
            return False
        
        strategy_id = result.get('strategy_id')
        print(f"✅ 成功建立策略: {strategy_id}")
        
        # 2. 更新策略程式碼
        test_code = """def should_entry(stock_data, current_index):
    current_row = stock_data.row(current_index, named=True)
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    return False, {}

def should_exit(stock_data, current_index, position):
    current_row = stock_data.row(current_index, named=True)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    entry_row = stock_data.row(entry_index, named=True)
    holding_days = (current_row["date"] - entry_row["date"]).days
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 5 or loss_rate <= -5:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    return False, {}"""
        
        update_data = {
            "name": "測試策略",
            "description": "用於測試策略測試功能的策略",
            "code": test_code
        }
        
        response = requests.put(
            f"{BASE_URL}/api/strategies/custom/{strategy_id}",
            json=update_data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code != 200:
            print(f"❌ 更新策略失敗: HTTP {response.status_code}")
            return False
        
        print("✅ 成功更新策略程式碼")
        
        # 3. 測試策略
        test_data = {
            "strategy_id": strategy_id,
            "code": test_code
        }
        
        response = requests.post(
            f"{BASE_URL}/api/strategies/custom/test",
            json=test_data,
            timeout=TEST_TIMEOUT
        )
        
        print(f"測試策略回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"測試策略回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('status') == 'success':
                results = data.get('results', {})
                
                # 檢查語法驗證
                if results.get('validation'):
                    print("✅ 語法驗證通過")
                else:
                    print("❌ 語法驗證失敗")
                
                # 檢查函數檢測
                functions = results.get('functions', [])
                if functions:
                    print(f"✅ 檢測到函數: {functions}")
                else:
                    print("⚠️  未檢測到函數")
                
                # 檢查回測結果
                backtest_results = results.get('backtest_results')
                if backtest_results:
                    if 'message' in backtest_results:
                        print(f"ℹ️  回測訊息: {backtest_results['message']}")
                    else:
                        print("✅ 回測結果:")
                        for key, value in backtest_results.items():
                            print(f"  {key}: {value}")
                else:
                    print("⚠️  沒有回測結果")
                
                # 清理測試策略
                response = requests.delete(
                    f"{BASE_URL}/api/strategies/custom/{strategy_id}",
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    print("✅ 測試策略清理完成")
                
                return True
            else:
                print(f"❌ 策略測試失敗: {data}")
                return False
        else:
            print(f"❌ 策略測試 HTTP 錯誤: {response.status_code}")
            print(f"錯誤內容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("開始測試策略測試功能")
    print(f"測試目標: {BASE_URL}")
    
    result = test_strategy_testing()
    
    if result:
        print("✅ 策略測試功能正常")
    else:
        print("❌ 策略測試功能異常") 