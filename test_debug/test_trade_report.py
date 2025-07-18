#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試交易報表功能
"""
import requests
import json

def test_trade_report():
    """測試交易報表功能"""
    base_url = "http://localhost:8000"
    
    print("=== 測試交易報表功能 ===")
    
    # 1. 建立測試策略
    print("\n1. 建立測試策略...")
    strategy_data = {
        "name": "交易報表測試策略",
        "description": "用於測試交易報表功能的策略",
        "type": "template"
    }
    
    response = requests.post(f"{base_url}/api/strategies/custom", json=strategy_data)
    if response.status_code != 200:
        print(f"❌ 建立策略失敗: {response.status_code}")
        return False
    
    result = response.json()
    if result.get('status') != 'success':
        print(f"❌ 建立策略失敗: {result}")
        return False
    
    strategy_id = result.get('strategy_id')
    print(f"✅ 成功建立策略: {strategy_id}")
    
    # 2. 更新策略程式碼，包含會產生交易記錄的邏輯
    print("\n2. 更新策略程式碼...")
    test_code = '''
def should_entry(stock_data, current_index, excel_pl_df):
    """進場條件"""
    if current_index < 5:
        return False, {}
    
    current_row = stock_data.row(current_index, named=True)
    prev_row = stock_data.row(current_index - 1, named=True)
    
    # 簡單的進場條件：收盤價上漲超過1%
    price_change = (current_row['close'] - prev_row['close']) / prev_row['close']
    if price_change > 0.01:
        return True, {
            "entry_price": current_row['close'],
            "reason": "價格上漲超過1%"
        }
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df):
    """出場條件"""
    if current_index - position["entry_index"] < 3:
        return False, {}
    
    current_row = stock_data.row(current_index, named=True)
    
    # 簡單的出場條件：獲利超過2%或虧損超過1%
    profit_rate = (current_row['close'] - position["entry_price"]) / position["entry_price"]
    if profit_rate > 0.02 or profit_rate < -0.01:
        return True, {
            "exit_price": current_row['close'],
            "reason": "達到停利停損條件"
        }
    
    return False, {}

def calculate_entry_price(stock_data, current_index):
    """計算進場價格"""
    current_row = stock_data.row(current_index, named=True)
    return current_row['close']

def calculate_shares(stock_data, current_index, available_capital):
    """計算進場股數"""
    current_row = stock_data.row(current_index, named=True)
    price = current_row['close']
    return int(available_capital * 0.1 / price / 1000) * 1000
'''
    
    update_data = {
        "name": "交易報表測試策略",
        "description": "用於測試交易報表功能的策略",
        "code": test_code
    }
    
    response = requests.put(f"{base_url}/api/strategies/custom/{strategy_id}", json=update_data)
    if response.status_code != 200:
        print(f"❌ 更新策略失敗: {response.status_code}")
        return False
    
    result = response.json()
    if result.get('status') != 'success':
        print(f"❌ 更新策略失敗: {result}")
        return False
    
    print("✅ 成功更新策略程式碼")
    
    # 3. 測試策略
    print("\n3. 測試策略...")
    test_data = {
        "strategy_id": strategy_id,
        "code": test_code,
        "strategy_table": "auto"
    }
    
    response = requests.post(f"{base_url}/api/strategies/custom/test", json=test_data)
    if response.status_code != 200:
        print(f"❌ 測試策略失敗: {response.status_code}")
        return False
    
    result = response.json()
    if result.get('status') != 'success':
        print(f"❌ 測試策略失敗: {result}")
        return False
    
    results = result.get('results', {})
    backtest_results = results.get('backtest_results', {})
    
    print("✅ 策略測試成功")
    print(f"   總交易次數: {backtest_results.get('total_trades', 0)}")
    print(f"   勝率: {backtest_results.get('win_rate', 0):.2f}%")
    print(f"   總報酬率: {backtest_results.get('total_return', 0):.2f}%")
    
    # 4. 檢查交易記錄
    trade_records = backtest_results.get('trade_records', [])
    print(f"   交易記錄數量: {len(trade_records)}")
    
    if trade_records:
        print("\n   前3筆交易記錄:")
        for i, trade in enumerate(trade_records[:3]):
            print(f"   {i+1}. {trade['stock_id']} - 進場: {trade['entry_date']} 出場: {trade['exit_date']} 報酬: {trade['profit_loss_rate']:.2f}%")
    
    # 5. 清理測試資料
    print("\n4. 清理測試資料...")
    response = requests.delete(f"{base_url}/api/strategies/custom/{strategy_id}")
    if response.status_code == 200:
        print("✅ 測試資料清理完成")
    else:
        print("⚠️  測試資料清理失敗")
    
    print("\n🎉 交易報表功能測試完成！")
    return True

if __name__ == "__main__":
    test_trade_report() 