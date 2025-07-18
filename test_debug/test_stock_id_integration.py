#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試策略編輯器中股票代碼功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime

def test_strategy_with_stock_id():
    """測試策略編輯器使用特定股票代碼"""
    
    # 測試用的策略程式碼
    test_strategy_code = '''
def should_entry(stock_data, current_index):
    """判斷是否應該進場"""
    if current_index < 5:
        return False
    
    current_row = stock_data.row(current_index, named=True)
    prev_row = stock_data.row(current_index - 1, named=True)
    
    # 簡單的進場條件：收盤價上漲超過2%
    price_change = (current_row['close'] - prev_row['close']) / prev_row['close']
    return price_change > 0.02

def should_exit(stock_data, current_index, position):
    """判斷是否應該出場"""
    if current_index < 5:
        return False
    
    current_row = stock_data.row(current_index, named=True)
    entry_price = position['entry_price']
    
    # 簡單的出場條件：獲利超過5%或虧損超過3%
    profit_rate = (current_row['close'] - entry_price) / entry_price
    return profit_rate > 0.05 or profit_rate < -0.03

def calculate_entry_price(stock_data, current_index):
    """計算進場價格"""
    current_row = stock_data.row(current_index, named=True)
    return current_row['close']

def calculate_shares(capital, entry_price, share_type):
    """計算股數"""
    if share_type == "mixed":
        # 混合模式：整股 + 零股
        whole_shares = int(capital * 0.95 / entry_price / 1000) * 1000
        fractional_shares = int((capital * 0.05) / entry_price)
        return whole_shares + fractional_shares
    elif share_type == "whole":
        # 整股模式
        return int(capital / entry_price / 1000) * 1000
    elif share_type == "fractional":
        # 零股模式
        return int(capital / entry_price)
    else:
        # 預設混合模式
        whole_shares = int(capital * 0.95 / entry_price / 1000) * 1000
        fractional_shares = int((capital * 0.05) / entry_price)
        return whole_shares + fractional_shares
'''
    
    # 測試不同的股票代碼
    test_cases = [
        {
            "stock_id": "2330",
            "data_type": "daily_price_adjusted",
            "description": "台積電每日股價"
        },
        {
            "stock_id": "2317",
            "data_type": "daily_price_adjusted", 
            "description": "鴻海每日股價"
        },
        {
            "stock_id": "2454",
            "data_type": "daily_price_adjusted",
            "description": "聯發科每日股價"
        }
    ]
    
    print("=== 測試策略編輯器股票代碼功能 ===")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"測試案例 {i}: {test_case['description']}")
        print(f"股票代碼: {test_case['stock_id']}")
        print(f"資料類型: {test_case['data_type']}")
        
        try:
            # 建立測試策略
            response = requests.post('http://localhost:8000/api/strategies/custom', 
                                   json={
                                       'name': f'測試策略_{test_case["stock_id"]}',
                                       'description': f'測試股票代碼 {test_case["stock_id"]} 的策略',
                                       'code': test_strategy_code
                                   })
            
            if response.status_code == 200:
                strategy_data = response.json()
                strategy_id = strategy_data.get('strategy_id')
                print(f"✓ 策略建立成功，ID: {strategy_id}")
                
                # 測試策略
                test_response = requests.post('http://localhost:8000/api/strategies/custom/test',
                                            json={
                                                'strategy_id': strategy_id,
                                                'code': test_strategy_code,
                                                'data_type': test_case['data_type'],
                                                'stock_id': test_case['stock_id'],
                                                'strategy_table': 'auto'
                                            })
                
                if test_response.status_code == 200:
                    test_data = test_response.json()
                    if test_data['status'] == 'success':
                        results = test_data['results']
                        backtest_results = results.get('backtest_results', {})
                        
                        print(f"✓ 策略測試成功")
                        print(f"  資料來源: {backtest_results.get('data_source', 'N/A')}")
                        print(f"  測試股票代碼: {backtest_results.get('stock_id', 'N/A')}")
                        print(f"  資料類型: {backtest_results.get('data_type', 'N/A')}")
                        print(f"  資料筆數: {backtest_results.get('data_count', 'N/A')}")
                        
                        if 'total_trades' in backtest_results:
                            print(f"  總交易次數: {backtest_results['total_trades']}")
                            print(f"  最終資金: {backtest_results.get('final_capital', 0):,.0f}")
                            print(f"  總報酬率: {backtest_results.get('total_return', 0):.2f}%")
                            print(f"  勝率: {backtest_results.get('win_rate', 0):.2f}%")
                        else:
                            print(f"  回測訊息: {backtest_results.get('message', 'N/A')}")
                    else:
                        print(f"✗ 策略測試失敗: {test_data.get('message', '未知錯誤')}")
                else:
                    print(f"✗ 策略測試請求失敗: {test_response.status_code}")
                
                # 清理：刪除測試策略
                delete_response = requests.delete(f'http://localhost:8000/api/strategies/custom/{strategy_id}')
                if delete_response.status_code == 200:
                    print(f"✓ 測試策略已清理")
                else:
                    print(f"⚠ 清理策略失敗")
                    
            else:
                print(f"✗ 策略建立失敗: {response.status_code}")
                
        except Exception as e:
            print(f"✗ 測試過程發生錯誤: {e}")
        
        print("-" * 50)
        print()

def test_stock_id_validation():
    """測試股票代碼驗證"""
    
    print("=== 測試股票代碼驗證 ===")
    
    # 測試無效的股票代碼
    invalid_stock_ids = ["", "ABC", "123", "台積電"]
    
    for stock_id in invalid_stock_ids:
        print(f"測試無效股票代碼: '{stock_id}'")
        
        try:
            response = requests.post('http://localhost:8000/api/strategies/custom/test',
                                   json={
                                       'strategy_id': 'test_id',
                                       'code': 'def should_entry(stock_data, current_index): return False',
                                       'data_type': 'daily_price_adjusted',
                                       'stock_id': stock_id,
                                       'strategy_table': 'auto'
                                   })
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    results = data['results']
                    backtest_results = results.get('backtest_results', {})
                    
                    if 'message' in backtest_results:
                        print(f"  結果: {backtest_results['message']}")
                    else:
                        print(f"  結果: 使用模擬資料進行測試")
                else:
                    print(f"  結果: {data.get('message', '未知錯誤')}")
            else:
                print(f"  結果: 請求失敗 ({response.status_code})")
                
        except Exception as e:
            print(f"  結果: 錯誤 - {e}")
        
        print()

if __name__ == "__main__":
    print("策略編輯器股票代碼功能測試")
    print("=" * 50)
    
    # 檢查服務是否運行
    try:
        response = requests.get('http://localhost:8000/api/system/status')
        if response.status_code == 200:
            print("✓ 服務正在運行")
            print()
            
            # 執行測試
            test_strategy_with_stock_id()
            test_stock_id_validation()
            
        else:
            print("✗ 服務回應異常")
    except requests.exceptions.ConnectionError:
        print("✗ 無法連接到服務，請確保服務正在運行")
        print("  執行指令: python main.py")
    except Exception as e:
        print(f"✗ 連接錯誤: {e}") 