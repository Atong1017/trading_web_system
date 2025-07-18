#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試策略編輯器 Excel 檔案上傳功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import pandas as pd
import tempfile
from datetime import datetime, timedelta
import json

def create_test_excel_file():
    """建立測試用的 Excel 檔案"""
    
    # 建立測試資料
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    # 模擬股票價格資料
    base_price = 100.0
    data = []
    
    for i, date in enumerate(dates):
        # 模擬價格波動
        change = (i % 7 - 3) * 0.02  # 每週循環
        price = base_price * (1 + change)
        
        row = {
            'date': date.strftime('%Y-%m-%d'),
            'stock_id': '2330',
            'open': price * 0.99,
            'high': price * 1.02,
            'low': price * 0.98,
            'close': price,
            'volume': 1000000 + (i * 50000)
        }
        data.append(row)
    
    # 建立 DataFrame
    df = pd.DataFrame(data)
    
    # 建立臨時檔案
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    
    return temp_file.name

def test_excel_upload_functionality():
    """測試 Excel 檔案上傳功能"""
    
    print("=== 測試策略編輯器 Excel 檔案上傳功能 ===")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 建立測試 Excel 檔案
    excel_file_path = create_test_excel_file()
    print(f"✓ 建立測試 Excel 檔案: {excel_file_path}")
    
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
    
    try:
        # 建立測試策略
        response = requests.post('http://localhost:8000/api/strategies/custom', 
                               json={
                                   'name': 'Excel測試策略',
                                   'description': '測試 Excel 檔案上傳功能的策略',
                                   'code': test_strategy_code
                               })
        
        if response.status_code == 200:
            strategy_data = response.json()
            strategy_id = strategy_data.get('strategy_id')
            print(f"✓ 策略建立成功，ID: {strategy_id}")
            
            # 測試 Excel 檔案上傳
            with open(excel_file_path, 'rb') as f:
                files = {'excel_file': ('test_data.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                data = {
                    'strategy_id': strategy_id,
                    'code': test_strategy_code,
                    'data_type': 'excel_upload',
                    'strategy_table': 'auto'
                }
                
                test_response = requests.post('http://localhost:8000/api/strategies/custom/test-excel',
                                            files=files,
                                            data=data)
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                if test_data['status'] == 'success':
                    results = test_data['results']
                    backtest_results = results.get('backtest_results', {})
                    
                    print(f"✓ Excel 檔案上傳測試成功")
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
                        
                    # 檢查錯誤
                    if results.get('errors'):
                        print(f"  警告: 發現 {len(results['errors'])} 個錯誤")
                        for error in results['errors']:
                            print(f"    - {error}")
                else:
                    print(f"✗ Excel 檔案上傳測試失敗: {test_data.get('message', '未知錯誤')}")
            else:
                print(f"✗ Excel 檔案上傳請求失敗: {test_response.status_code}")
                print(f"  回應內容: {test_response.text}")
            
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
    
    finally:
        # 清理臨時檔案
        try:
            os.unlink(excel_file_path)
            print(f"✓ 臨時檔案已清理")
        except:
            pass
    
    print("-" * 50)
    print()

def test_excel_format_validation():
    """測試 Excel 檔案格式驗證"""
    
    print("=== 測試 Excel 檔案格式驗證 ===")
    
    # 建立缺少必要欄位的 Excel 檔案
    invalid_data = [
        {'date': '2024-01-01', 'price': 100},  # 缺少 open, high, low, close
        {'date': '2024-01-02', 'price': 101}
    ]
    
    df_invalid = pd.DataFrame(invalid_data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df_invalid.to_excel(temp_file.name, index=False)
    
    print(f"測試缺少必要欄位的 Excel 檔案: {temp_file.name}")
    
    try:
        # 建立測試策略
        response = requests.post('http://localhost:8000/api/strategies/custom', 
                               json={
                                   'name': '格式驗證測試策略',
                                   'description': '測試 Excel 檔案格式驗證',
                                   'code': 'def should_entry(stock_data, current_index): return False'
                               })
        
        if response.status_code == 200:
            strategy_data = response.json()
            strategy_id = strategy_data.get('strategy_id')
            
            # 測試無效格式的 Excel 檔案
            with open(temp_file.name, 'rb') as f:
                files = {'excel_file': ('invalid_data.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                data = {
                    'strategy_id': strategy_id,
                    'code': 'def should_entry(stock_data, current_index): return False',
                    'data_type': 'excel_upload',
                    'strategy_table': 'auto'
                }
                
                test_response = requests.post('http://localhost:8000/api/strategies/custom/test-excel',
                                            files=files,
                                            data=data)
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                if test_data['status'] == 'success':
                    results = test_data['results']
                    backtest_results = results.get('backtest_results', {})
                    
                    if 'message' in backtest_results:
                        print(f"✓ 格式驗證正確: {backtest_results['message']}")
                    else:
                        print(f"⚠ 格式驗證未按預期工作")
                else:
                    print(f"✗ 格式驗證測試失敗: {test_data.get('message', '未知錯誤')}")
            else:
                print(f"✗ 格式驗證請求失敗: {test_response.status_code}")
            
            # 清理
            requests.delete(f'http://localhost:8000/api/strategies/custom/{strategy_id}')
            
    except Exception as e:
        print(f"✗ 格式驗證測試錯誤: {e}")
    
    finally:
        # 清理臨時檔案
        try:
            os.unlink(temp_file.name)
        except:
            pass
    
    print()

if __name__ == "__main__":
    print("策略編輯器 Excel 檔案上傳功能測試")
    print("=" * 50)
    
    # 檢查服務是否運行
    try:
        response = requests.get('http://localhost:8000/api/system/status')
        if response.status_code == 200:
            print("✓ 服務正在運行")
            print()
            
            # 執行測試
            test_excel_upload_functionality()
            test_excel_format_validation()
            
        else:
            print("✗ 服務回應異常")
    except requests.exceptions.ConnectionError:
        print("✗ 無法連接到服務，請確保服務正在運行")
        print("  執行指令: python main.py")
    except Exception as e:
        print(f"✗ 連接錯誤: {e}") 