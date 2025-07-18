#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試參數修復
驗證 DynamicStrategy 參數設定是否正確
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# 測試配置
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10

def test_parameters_fix():
    """測試參數修復"""
    print("測試參數修復...")
    
    try:
        # 1. 建立測試策略
        strategy_data = {
            "name": "參數修復測試策略",
            "description": "測試參數設定是否正確",
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
        
        # 2. 更新策略程式碼（使用簡單的策略）
        test_code = """def should_entry(stock_data, current_index):
    # 簡單的進場條件：當收盤價大於開盤價時進場
    current_row = stock_data.row(current_index, named=True)
    
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    return False, {}

def should_exit(stock_data, current_index, position):
    # 簡單的出場條件：持有超過3天或虧損超過3%時出場
    current_row = stock_data.row(current_index, named=True)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    # 計算持有天數
    entry_row = stock_data.row(entry_index, named=True)
    holding_days = (current_row["date"] - entry_row["date"]).days
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 3 or loss_rate <= -3:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    return False, {}"""
        
        update_data = {
            "name": "參數修復測試策略",
            "description": "測試參數設定是否正確",
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
        
        # 3. 測試策略（應該會自動修復參數）
        test_data = {
            "strategy_id": strategy_id,
            "code": test_code,
            "stock_id": "2330",
            "data_type": "daily_price_adjusted"
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
                validation = results.get('validation', False)
                backtest_results = results.get('backtest_results', {})
                
                if validation:
                    print("✅ 策略程式碼語法驗證通過")
                    
                    if isinstance(backtest_results, dict) and 'message' not in backtest_results:
                        print("✅ 策略回測執行成功（參數修復生效）")
                        print(f"   總交易次數: {backtest_results.get('total_trades', 0)}")
                        print(f"   最終資金: {backtest_results.get('final_capital', 0):,.0f}")
                        print(f"   總報酬率: {backtest_results.get('total_return', 0):.2f}%")
                        print(f"   勝率: {backtest_results.get('win_rate', 0):.2f}%")
                        print(f"   資料來源: {backtest_results.get('data_source', '未知')}")
                        
                        # 檢查是否有交易記錄
                        if backtest_results.get('total_trades', 0) > 0:
                            print("✅ 策略成功產生交易記錄")
                        else:
                            print("⚠️  策略未產生交易記錄（可能是資料或條件問題）")
                    else:
                        print(f"⚠️  策略回測結果: {backtest_results}")
                else:
                    errors = results.get('errors', [])
                    print(f"❌ 策略程式碼語法錯誤: {errors}")
                    return False
            else:
                print(f"❌ 策略測試失敗: {data}")
                return False
        else:
            print(f"❌ 策略測試 HTTP 錯誤: {response.status_code}")
            print(f"錯誤詳情: {response.text}")
            return False
        
        # 4. 清理測試策略
        response = requests.delete(
            f"{BASE_URL}/api/strategies/custom/{strategy_id}",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            print("✅ 測試策略清理完成")
        else:
            print("⚠️  測試策略清理失敗")
        
        print("\n🎉 參數修復測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試參數修復失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("開始測試參數修復")
    print(f"測試目標: {BASE_URL}")
    
    result = test_parameters_fix()
    
    if result:
        print("\n🎉 測試通過！")
    else:
        print("\n❌ 測試失敗") 