#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試 Excel 檔案上傳功能
"""

import requests
import pandas as pd
import tempfile
import os

def test_excel_template_download():
    """測試 Excel 範本下載功能"""
    print("=== 測試 Excel 範本下載 ===")
    
    try:
        response = requests.get('http://localhost:8000/api/strategies/custom/excel-template')
        
        if response.status_code == 200:
            # 儲存下載的檔案
            with open('test_template.xlsx', 'wb') as f:
                f.write(response.content)
            
            print("✓ Excel 範本下載成功")
            
            # 驗證檔案內容
            df = pd.read_excel('test_template.xlsx')
            print(f"  檔案包含 {len(df)} 筆資料")
            print(f"  欄位: {list(df.columns)}")
            
            # 檢查必要欄位
            required_columns = ['stock_id', 'date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"✗ 缺少必要欄位: {missing_columns}")
            else:
                print("✓ 所有必要欄位都存在")
            
            # 顯示範例資料
            print("  範例資料:")
            print(df.head())
            
            # 清理測試檔案
            os.unlink('test_template.xlsx')
            print("✓ 測試檔案已清理")
            
        else:
            print(f"✗ 下載失敗: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 測試錯誤: {e}")

def test_excel_upload_api():
    """測試 Excel 檔案上傳 API"""
    print("\n=== 測試 Excel 檔案上傳 API ===")
    
    # 建立測試 Excel 檔案 - 只包含股票代碼和日期
    test_data = [
        {'stock_id': '2330', 'date': '2024-01-01'},
        {'stock_id': '2330', 'date': '2024-01-02'},
        {'stock_id': '2330', 'date': '2024-01-03'},
        {'stock_id': '2317', 'date': '2024-01-01'},
        {'stock_id': '2317', 'date': '2024-01-02'},
        {'stock_id': '2454', 'date': '2024-01-01'}
    ]
    
    df = pd.DataFrame(test_data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    
    print(f"✓ 建立測試 Excel 檔案: {temp_file.name}")
    print(f"  包含 {len(df)} 筆股票代碼和日期組合")
    print(f"  股票代碼: {df['stock_id'].unique().tolist()}")
    print(f"  日期範圍: {df['date'].min()} 到 {df['date'].max()}")
    
    try:
        # 測試上傳
        with open(temp_file.name, 'rb') as f:
            files = {'excel_file': ('test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {
                'strategy_id': 'test_id',
                'code': 'def should_entry(stock_data, current_index): return False',
                'data_type': 'excel_upload',
                'strategy_table': 'auto'
            }
            
            response = requests.post('http://localhost:8000/api/strategies/custom/test-excel',
                                   files=files,
                                   data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Excel 檔案上傳 API 測試成功")
            print(f"  回應狀態: {result.get('status')}")
            
            if result.get('status') == 'success':
                results = result.get('results', {})
                backtest_results = results.get('backtest_results', {})
                
                if 'message' in backtest_results:
                    print(f"  回測訊息: {backtest_results['message']}")
                else:
                    print(f"  資料來源: {backtest_results.get('data_source', 'N/A')}")
                    print(f"  股票代碼: {backtest_results.get('stock_id', 'N/A')}")
                    print(f"  日期範圍: {backtest_results.get('date_range', 'N/A')}")
                    print(f"  資料筆數: {backtest_results.get('data_count', 'N/A')}")
            else:
                print(f"  錯誤: {result.get('message', '未知錯誤')}")
        else:
            print(f"✗ API 測試失敗: {response.status_code}")
            print(f"  回應內容: {response.text}")
            
    except Exception as e:
        print(f"✗ 測試錯誤: {e}")
    
    finally:
        # 清理臨時檔案
        try:
            os.unlink(temp_file.name)
            print("✓ 臨時檔案已清理")
        except:
            pass

if __name__ == "__main__":
    print("Excel 檔案上傳功能簡單測試")
    print("=" * 40)
    
    # 檢查服務是否運行
    try:
        response = requests.get('http://localhost:8000/api/system/status')
        if response.status_code == 200:
            print("✓ 服務正在運行")
            print()
            
            test_excel_template_download()
            test_excel_upload_api()
            
        else:
            print("✗ 服務回應異常")
    except requests.exceptions.ConnectionError:
        print("✗ 無法連接到服務，請確保服務正在運行")
        print("  執行指令: python main.py")
    except Exception as e:
        print(f"✗ 連接錯誤: {e}") 