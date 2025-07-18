#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試策略編輯器的測試功能
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os

def test_strategy_editor():
    """測試策略編輯器的測試功能"""
    base_url = "http://localhost:8000"
    
    print("=== 測試策略編輯器功能 ===")
    
    # 1. 測試取得策略列表
    print("\n1. 測試取得策略列表...")
    try:
        response = requests.get(f"{base_url}/api/strategies/custom")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 成功取得 {len(data.get('strategies', []))} 個策略")
            
            # 取得第一個策略的 ID
            strategies = data.get('strategies', [])
            if strategies:
                strategy_id = strategies[0]['id']
                print(f"使用策略 ID: {strategy_id}")
            else:
                print("沒有找到策略，建立一個測試策略...")
                strategy_id = create_test_strategy(base_url)
        else:
            print(f"✗ 取得策略列表失敗: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ 取得策略列表錯誤: {e}")
        return
    
    # 2. 測試沒有 Excel 檔案的測試（原來的功能）
    print("\n2. 測試沒有 Excel 檔案的測試功能...")
    test_code = """
def should_entry(stock_data, current_index):
    if current_index < 5:
        return False
    
    current_row = stock_data.row(current_index, named=True)
    prev_row = stock_data.row(current_index - 1, named=True)
    
    # 簡單的進場條件：收盤價上漲超過2%
    price_change = (current_row['close'] - prev_row['close']) / prev_row['close']
    return price_change > 0.02

def should_exit(stock_data, current_index, entry_index, entry_price):
    if current_index - entry_index < 3:
        return False
    
    current_row = stock_data.row(current_index, named=True)
    
    # 簡單的出場條件：獲利超過5%或虧損超過3%
    profit_rate = (current_row['close'] - entry_price) / entry_price
    return profit_rate > 0.05 or profit_rate < -0.03

def calculate_entry_price(stock_data, current_index):
    current_row = stock_data.row(current_index, named=True)
    return current_row['close']

def calculate_shares(stock_data, current_index, available_capital):
    current_row = stock_data.row(current_index, named=True)
    price = current_row['close']
    return int(available_capital * 0.1 / price / 1000) * 1000
"""
    
    try:
        # 使用 FormData 格式
        form_data = {
            'strategy_id': strategy_id,
            'code': test_code,
            'strategy_table': 'auto'
        }
        
        response = requests.post(f"{base_url}/api/strategies/custom/test", data=form_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 沒有 Excel 檔案的測試成功")
            print(f"  驗證結果: {data.get('results', {}).get('validation', False)}")
            print(f"  函數列表: {data.get('results', {}).get('functions', [])}")
            
            backtest_results = data.get('results', {}).get('backtest_results', {})
            if 'message' in backtest_results:
                print(f"  回測結果: {backtest_results['message']}")
            else:
                print(f"  回測結果: 總交易次數={backtest_results.get('total_trades', 0)}")
        else:
            print(f"✗ 沒有 Excel 檔案的測試失敗: {response.status_code}")
            print(f"  錯誤: {response.text}")
    except Exception as e:
        print(f"✗ 沒有 Excel 檔案的測試錯誤: {e}")
    
    # 3. 測試有 Excel 檔案的測試
    print("\n3. 測試有 Excel 檔案的測試功能...")
    
    # 建立測試 Excel 檔案
    test_excel_data = []
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    stock_ids = ['2330', '2317', '2454']
    
    for stock_id in stock_ids:
        for date in dates[::3]:  # 每3天一個資料點
            test_excel_data.append({
                'stock_id': stock_id,
                'date': date.strftime('%Y-%m-%d')
            })
    
    df = pd.DataFrame(test_excel_data)
    
    # 建立臨時 Excel 檔案
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        df.to_excel(temp_file.name, index=False)
        temp_file_path = temp_file.name
    
    try:
        # 使用 FormData 格式上傳 Excel 檔案
        with open(temp_file_path, 'rb') as f:
            files = {'excel_file': ('test_stocks.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            form_data = {
                'strategy_id': strategy_id,
                'code': test_code,
                'strategy_table': 'auto'
            }
            
            response = requests.post(f"{base_url}/api/strategies/custom/test", data=form_data, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 有 Excel 檔案的測試成功")
            print(f"  驗證結果: {data.get('results', {}).get('validation', False)}")
            print(f"  函數列表: {data.get('results', {}).get('functions', [])}")
            
            backtest_results = data.get('results', {}).get('backtest_results', {})
            if 'message' in backtest_results:
                print(f"  回測結果: {backtest_results['message']}")
            else:
                print(f"  回測結果: 總交易次數={backtest_results.get('total_trades', 0)}")
                print(f"  資料來源: {backtest_results.get('data_source', 'unknown')}")
                print(f"  股票代碼: {backtest_results.get('stock_id', 'unknown')}")
                print(f"  日期範圍: {backtest_results.get('date_range', 'unknown')}")
        else:
            print(f"✗ 有 Excel 檔案的測試失敗: {response.status_code}")
            print(f"  錯誤: {response.text}")
    except Exception as e:
        print(f"✗ 有 Excel 檔案的測試錯誤: {e}")
    finally:
        # 清理臨時檔案
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    print("\n=== 測試完成 ===")

def create_test_strategy(base_url):
    """建立測試策略"""
    print("建立測試策略...")
    
    strategy_data = {
        "name": "測試策略",
        "description": "用於測試的策略",
        "type": "template"
    }
    
    try:
        response = requests.post(f"{base_url}/api/strategies/custom", json=strategy_data)
        if response.status_code == 200:
            data = response.json()
            strategy_id = data.get('strategy_id')
            print(f"✓ 成功建立測試策略: {strategy_id}")
            return strategy_id
        else:
            print(f"✗ 建立測試策略失敗: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ 建立測試策略錯誤: {e}")
        return None

if __name__ == "__main__":
    test_strategy_editor() 