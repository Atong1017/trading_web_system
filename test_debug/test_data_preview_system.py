#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試資料預覽系統功能
包含範例資料載入、資料預覽、資料類型管理等功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
from datetime import datetime

# 測試配置
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

def print_test_header(test_name):
    """印出測試標題"""
    print(f"\n{'='*60}")
    print(f"測試: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name, success, message=""):
    """印出測試結果"""
    status = "✅ 通過" if success else "❌ 失敗"
    print(f"{test_name}: {status}")
    if message:
        print(f"  訊息: {message}")

def test_sample_data_types():
    """測試取得範例資料類型"""
    print_test_header("取得範例資料類型")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sample-data/types", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'types' in data:
                types = data['types']
                print(f"找到 {len(types)} 種資料類型:")
                
                for data_type in types:
                    print(f"  - {data_type['name']} ({data_type['id']})")
                    print(f"    類別: {data_type['category']}")
                    print(f"    描述: {data_type['description']}")
                    if data_type.get('parameters'):
                        print(f"    參數: {len(data_type['parameters'])} 個")
                    print()
                
                print_test_result("取得範例資料類型", True, f"成功取得 {len(types)} 種資料類型")
                return types
            else:
                print_test_result("取得範例資料類型", False, "回應格式錯誤")
                return None
        else:
            print_test_result("取得範例資料類型", False, f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("取得範例資料類型", False, str(e))
        return None

def test_load_daily_price_data():
    """測試載入每日股價資料"""
    print_test_header("載入每日股價資料")
    
    try:
        # 準備測試參數
        test_params = {
            'data_type': 'daily_price',
            'parameters': {
                'stock_id': '2330',
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sample-data/load",
            json=test_params,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'data' in data:
                result_data = data['data']
                print(f"成功載入 {len(result_data)} 筆每日股價資料")
                
                if result_data:
                    # 顯示前幾筆資料
                    print("\n前5筆資料範例:")
                    for i, row in enumerate(result_data[:5]):
                        print(f"  {i+1}. 日期: {row['date']}, 開盤: {row['open']}, 收盤: {row['close']}, 成交量: {row['volume']}")
                    
                    # 檢查資料結構
                    expected_columns = ['date', 'stock_id', 'open', 'high', 'low', 'close', 'volume']
                    first_row = result_data[0]
                    missing_columns = [col for col in expected_columns if col not in first_row]
                    
                    if not missing_columns:
                        print_test_result("載入每日股價資料", True, f"成功載入 {len(result_data)} 筆資料")
                        return result_data
                    else:
                        print_test_result("載入每日股價資料", False, f"缺少欄位: {missing_columns}")
                        return None
                else:
                    print_test_result("載入每日股價資料", False, "沒有載入到資料")
                    return None
            else:
                print_test_result("載入每日股價資料", False, "回應格式錯誤")
                return None
        else:
            print_test_result("載入每日股價資料", False, f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("載入每日股價資料", False, str(e))
        return None

def test_load_minute_price_data():
    """測試載入分K股價資料"""
    print_test_header("載入分K股價資料")
    
    try:
        # 準備測試參數
        test_params = {
            'data_type': 'minute_price',
            'parameters': {
                'stock_id': '2330',
                'interval': '5',
                'date': '2024-01-15'
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sample-data/load",
            json=test_params,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'data' in data:
                result_data = data['data']
                print(f"成功載入 {len(result_data)} 筆分K股價資料")
                
                if result_data:
                    # 顯示前幾筆資料
                    print("\n前5筆資料範例:")
                    for i, row in enumerate(result_data[:5]):
                        print(f"  {i+1}. 時間: {row['datetime']}, 開盤: {row['open']}, 收盤: {row['close']}, 間隔: {row['interval']}")
                    
                    print_test_result("載入分K股價資料", True, f"成功載入 {len(result_data)} 筆資料")
                    return result_data
                else:
                    print_test_result("載入分K股價資料", False, "沒有載入到資料")
                    return None
            else:
                print_test_result("載入分K股價資料", False, "回應格式錯誤")
                return None
        else:
            print_test_result("載入分K股價資料", False, f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("載入分K股價資料", False, str(e))
        return None

def test_load_dividend_data():
    """測試載入除權息資料"""
    print_test_header("載入除權息資料")
    
    try:
        # 準備測試參數
        test_params = {
            'data_type': 'dividend',
            'parameters': {
                'stock_id': '2330',
                'start_date': '2023-01-01',
                'end_date': '2024-12-31'
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sample-data/load",
            json=test_params,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'data' in data:
                result_data = data['data']
                print(f"成功載入 {len(result_data)} 筆除權息資料")
                
                if result_data:
                    # 顯示前幾筆資料
                    print("\n前3筆資料範例:")
                    for i, row in enumerate(result_data[:3]):
                        print(f"  {i+1}. 日期: {row['date']}, 類型: {row['dividend_type']}, 現金股利: {row['cash_dividend']}")
                    
                    print_test_result("載入除權息資料", True, f"成功載入 {len(result_data)} 筆資料")
                    return result_data
                else:
                    print_test_result("載入除權息資料", False, "沒有載入到資料")
                    return None
            else:
                print_test_result("載入除權息資料", False, "回應格式錯誤")
                return None
        else:
            print_test_result("載入除權息資料", False, f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("載入除權息資料", False, str(e))
        return None

def test_load_technical_indicators_data():
    """測試載入技術指標資料"""
    print_test_header("載入技術指標資料")
    
    try:
        # 準備測試參數
        test_params = {
            'data_type': 'technical_indicators',
            'parameters': {
                'stock_id': '2330',
                'start_date': '2024-01-01',
                'end_date': '2024-01-31',
                'indicators': 'all'
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sample-data/load",
            json=test_params,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'data' in data:
                result_data = data['data']
                print(f"成功載入 {len(result_data)} 筆技術指標資料")
                
                if result_data:
                    # 顯示前幾筆資料
                    print("\n前3筆資料範例:")
                    for i, row in enumerate(result_data[:3]):
                        print(f"  {i+1}. 日期: {row['date']}, 收盤: {row['close']}, MA5: {row['ma5']}, RSI: {row['rsi']}")
                    
                    # 檢查技術指標欄位
                    technical_columns = ['ma5', 'ma10', 'ma20', 'rsi', 'macd', 'bb_upper', 'bb_middle', 'bb_lower']
                    first_row = result_data[0]
                    available_indicators = [col for col in technical_columns if col in first_row and first_row[col] is not None]
                    
                    print(f"可用的技術指標: {available_indicators}")
                    
                    print_test_result("載入技術指標資料", True, f"成功載入 {len(result_data)} 筆資料")
                    return result_data
                else:
                    print_test_result("載入技術指標資料", False, "沒有載入到資料")
                    return None
            else:
                print_test_result("載入技術指標資料", False, "回應格式錯誤")
                return None
        else:
            print_test_result("載入技術指標資料", False, f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("載入技術指標資料", False, str(e))
        return None

def test_data_type_management():
    """測試資料類型管理功能"""
    print_test_header("資料類型管理功能")
    
    try:
        # 測試新增自定義資料類型
        custom_data_type = {
            'id': 'test_custom_data',
            'name': '測試自定義資料',
            'description': '用於測試的自定義資料類型',
            'category': '測試資料',
            'parameters': {
                'test_param': {
                    'type': 'text',
                    'label': '測試參數',
                    'default': 'test_value',
                    'placeholder': '請輸入測試參數'
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sample-data/types",
            json=custom_data_type,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ 成功新增自定義資料類型")
                
                # 測試取得特定資料類型
                response = requests.get(
                    f"{BASE_URL}/api/sample-data/types/test_custom_data",
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        print("✅ 成功取得特定資料類型")
                        
                        # 測試移除資料類型
                        response = requests.delete(
                            f"{BASE_URL}/api/sample-data/types/test_custom_data",
                            timeout=TEST_TIMEOUT
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'success':
                                print("✅ 成功移除自定義資料類型")
                                print_test_result("資料類型管理功能", True, "所有操作都成功")
                                return True
                            else:
                                print_test_result("資料類型管理功能", False, "移除資料類型失敗")
                                return False
                        else:
                            print_test_result("資料類型管理功能", False, f"移除資料類型 HTTP {response.status_code}")
                            return False
                    else:
                        print_test_result("資料類型管理功能", False, "取得特定資料類型失敗")
                        return False
                else:
                    print_test_result("資料類型管理功能", False, f"取得特定資料類型 HTTP {response.status_code}")
                    return False
            else:
                print_test_result("資料類型管理功能", False, "新增資料類型失敗")
                return False
        else:
            print_test_result("資料類型管理功能", False, f"新增資料類型 HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("資料類型管理功能", False, str(e))
        return False

def test_strategy_editor_integration():
    """測試策略編輯器整合功能"""
    print_test_header("策略編輯器整合功能")
    
    try:
        # 測試策略編輯器頁面是否可訪問
        response = requests.get(f"{BASE_URL}/strategy-editor", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            print("✅ 策略編輯器頁面可正常訪問")
            
            # 測試自定義策略相關 API
            response = requests.get(f"{BASE_URL}/api/strategies/custom", timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    strategies = data.get('strategies', [])
                    print(f"✅ 成功取得 {len(strategies)} 個自定義策略")
                    
                    # 測試策略模板
                    response = requests.get(f"{BASE_URL}/api/strategies/custom/template", timeout=TEST_TIMEOUT)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 'success' and 'template' in data:
                            print("✅ 成功取得策略模板")
                            print_test_result("策略編輯器整合功能", True, "所有功能正常")
                            return True
                        else:
                            print_test_result("策略編輯器整合功能", False, "取得策略模板失敗")
                            return False
                    else:
                        print_test_result("策略編輯器整合功能", False, f"取得策略模板 HTTP {response.status_code}")
                        return False
                else:
                    print_test_result("策略編輯器整合功能", False, "取得自定義策略失敗")
                    return False
            else:
                print_test_result("策略編輯器整合功能", False, f"取得自定義策略 HTTP {response.status_code}")
                return False
        else:
            print_test_result("策略編輯器整合功能", False, f"策略編輯器頁面 HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("策略編輯器整合功能", False, str(e))
        return False

def main():
    """主測試函數"""
    print("開始測試資料預覽系統功能")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"測試目標: {BASE_URL}")
    
    # 測試結果統計
    test_results = []
    
    # 執行各項測試
    tests = [
        ("範例資料類型", test_sample_data_types),
        ("每日股價資料", test_load_daily_price_data),
        ("分K股價資料", test_load_minute_price_data),
        ("除權息資料", test_load_dividend_data),
        ("技術指標資料", test_load_technical_indicators_data),
        ("資料類型管理", test_data_type_management),
        ("策略編輯器整合", test_strategy_editor_integration)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"測試 {test_name} 發生異常: {e}")
            test_results.append((test_name, False))
    
    # 輸出測試總結
    print(f"\n{'='*60}")
    print("測試總結")
    print(f"{'='*60}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試都通過！資料預覽系統功能正常。")
    else:
        print("⚠️  部分測試失敗，請檢查相關功能。")
    
    print(f"\n測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 