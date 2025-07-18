#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試選股編輯器系統功能
包含選股列表管理、Excel匯入匯出、策略整合等功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
import pandas as pd
from datetime import datetime
import os

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

def test_stock_list_management():
    """測試選股列表管理功能"""
    print_test_header("選股列表管理功能")
    
    try:
        # 測試建立選股列表
        create_data = {
            "name": "測試選股列表",
            "description": "用於測試的選股列表"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/stock-lists",
            json=create_data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stock_list_id = data['stock_list_id']
                print(f"✅ 成功建立選股列表: {stock_list_id}")
                
                # 測試取得選股列表
                response = requests.get(
                    f"{BASE_URL}/api/stock-lists/{stock_list_id}",
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        stock_list = data['stock_list']
                        print(f"✅ 成功取得選股列表: {stock_list['name']}")
                        
                        # 測試更新選股列表
                        update_data = {
                            "name": "更新後的選股列表",
                            "description": "已更新的描述",
                            "stocks": [
                                {"stock_id": "2330", "stock_name": "台積電", "start_date": "2024-01-01", "end_date": "2024-12-31"},
                                {"stock_id": "2317", "stock_name": "鴻海", "start_date": "2024-01-01", "end_date": "2024-12-31"}
                            ]
                        }
                        
                        response = requests.put(
                            f"{BASE_URL}/api/stock-lists/{stock_list_id}",
                            json=update_data,
                            timeout=TEST_TIMEOUT
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'success':
                                print("✅ 成功更新選股列表")
                                
                                # 測試刪除選股列表
                                response = requests.delete(
                                    f"{BASE_URL}/api/stock-lists/{stock_list_id}",
                                    timeout=TEST_TIMEOUT
                                )
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get('status') == 'success':
                                        print("✅ 成功刪除選股列表")
                                        print_test_result("選股列表管理功能", True, "所有操作都成功")
                                        return True
                                    else:
                                        print_test_result("選股列表管理功能", False, "刪除選股列表失敗")
                                        return False
                                else:
                                    print_test_result("選股列表管理功能", False, f"刪除選股列表 HTTP {response.status_code}")
                                    return False
                            else:
                                print_test_result("選股列表管理功能", False, "更新選股列表失敗")
                                return False
                        else:
                            print_test_result("選股列表管理功能", False, f"更新選股列表 HTTP {response.status_code}")
                            return False
                    else:
                        print_test_result("選股列表管理功能", False, "取得選股列表失敗")
                        return False
                else:
                    print_test_result("選股列表管理功能", False, f"取得選股列表 HTTP {response.status_code}")
                    return False
            else:
                print_test_result("選股列表管理功能", False, "建立選股列表失敗")
                return False
        else:
            print_test_result("選股列表管理功能", False, f"建立選股列表 HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("選股列表管理功能", False, str(e))
        return False

def test_stock_conditions():
    """測試選股條件功能"""
    print_test_header("選股條件功能")
    
    try:
        # 測試套用選股條件
        conditions = [
            {
                "field": "stock_id",
                "operator": "contains",
                "value": "23"
            },
            {
                "field": "stock_name",
                "operator": "contains",
                "value": "台"
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/stock-lists/apply-conditions",
            json={"conditions": conditions},
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stocks = data.get('stocks', [])
                print(f"✅ 成功套用選股條件，找到 {len(stocks)} 檔股票")
                
                if stocks:
                    print("前3檔股票:")
                    for i, stock in enumerate(stocks[:3]):
                        print(f"  {i+1}. {stock['stock_id']} - {stock['stock_name']}")
                
                print_test_result("選股條件功能", True, f"找到 {len(stocks)} 檔股票")
                return True
            else:
                print_test_result("選股條件功能", False, "套用條件失敗")
                return False
        else:
            print_test_result("選股條件功能", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("選股條件功能", False, str(e))
        return False

def test_excel_import_export():
    """測試Excel匯入匯出功能"""
    print_test_header("Excel匯入匯出功能")
    
    try:
        # 建立測試Excel檔案
        test_data = [
            {"stock_id": "2330", "stock_name": "台積電", "start_date": "2024-01-01", "end_date": "2024-12-31"},
            {"stock_id": "2317", "stock_name": "鴻海", "start_date": "2024-01-01", "end_date": "2024-12-31"},
            {"stock_id": "2454", "stock_name": "聯發科", "start_date": "2024-01-01", "end_date": "2024-12-31"}
        ]
        
        test_file = "test_stocks.xlsx"
        df = pd.DataFrame(test_data)
        df.to_excel(test_file, index=False)
        
        # 測試Excel匯入
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{BASE_URL}/api/stock-lists/import-excel",
                files=files,
                timeout=TEST_TIMEOUT
            )
        
        # 清理測試檔案
        if os.path.exists(test_file):
            os.remove(test_file)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stocks = data.get('stocks', [])
                print(f"✅ 成功匯入Excel，載入 {len(stocks)} 檔股票")
                
                if stocks:
                    print("匯入的股票:")
                    for stock in stocks:
                        print(f"  - {stock['stock_id']} - {stock['stock_name']}")
                
                print_test_result("Excel匯入匯出功能", True, f"成功匯入 {len(stocks)} 檔股票")
                return True
            else:
                print_test_result("Excel匯入匯出功能", False, "匯入Excel失敗")
                return False
        else:
            print_test_result("Excel匯入匯出功能", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Excel匯入匯出功能", False, str(e))
        return False

def test_strategy_integration():
    """測試策略整合功能"""
    print_test_header("策略整合功能")
    
    try:
        # 先建立一個選股列表
        create_data = {
            "name": "整合測試選股列表",
            "description": "用於策略整合測試"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/stock-lists",
            json=create_data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stock_list_id = data['stock_list_id']
                
                # 更新選股列表內容
                update_data = {
                    "stocks": [
                        {"stock_id": "2330", "stock_name": "台積電", "start_date": "2024-01-01", "end_date": "2024-12-31"},
                        {"stock_id": "2317", "stock_name": "鴻海", "start_date": "2024-01-01", "end_date": "2024-12-31"}
                    ]
                }
                
                response = requests.put(
                    f"{BASE_URL}/api/stock-lists/{stock_list_id}",
                    json=update_data,
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    # 取得策略列表
                    response = requests.get(
                        f"{BASE_URL}/api/strategies/custom",
                        timeout=TEST_TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 'success' and data.get('strategies'):
                            strategy_id = data['strategies'][0]['id']
                            
                            # 測試匯出到策略
                            export_data = {
                                "stock_list_id": stock_list_id,
                                "strategy_id": strategy_id,
                                "stocks": update_data["stocks"]
                            }
                            
                            response = requests.post(
                                f"{BASE_URL}/api/stock-lists/export-to-strategy",
                                json=export_data,
                                timeout=TEST_TIMEOUT
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get('status') == 'success':
                                    print("✅ 成功匯出選股列表到策略")
                                    
                                    # 清理測試資料
                                    requests.delete(f"{BASE_URL}/api/stock-lists/{stock_list_id}")
                                    
                                    print_test_result("策略整合功能", True, "匯出成功")
                                    return True
                                else:
                                    print_test_result("策略整合功能", False, "匯出失敗")
                                    return False
                            else:
                                print_test_result("策略整合功能", False, f"匯出 HTTP {response.status_code}")
                                return False
                        else:
                            print_test_result("策略整合功能", False, "沒有可用的策略")
                            return False
                    else:
                        print_test_result("策略整合功能", False, f"取得策略列表 HTTP {response.status_code}")
                        return False
                else:
                    print_test_result("策略整合功能", False, "更新選股列表失敗")
                    return False
            else:
                print_test_result("策略整合功能", False, "建立選股列表失敗")
                return False
        else:
            print_test_result("策略整合功能", False, f"建立選股列表 HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("策略整合功能", False, str(e))
        return False

def test_stock_selector_page():
    """測試選股編輯器頁面"""
    print_test_header("選股編輯器頁面")
    
    try:
        # 測試頁面是否可訪問
        response = requests.get(f"{BASE_URL}/stock-selector", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            print("✅ 選股編輯器頁面可正常訪問")
            
            # 測試API端點
            response = requests.get(f"{BASE_URL}/api/stock-lists", timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    stock_lists = data.get('stock_lists', [])
                    print(f"✅ 成功取得 {len(stock_lists)} 個選股列表")
                    print_test_result("選股編輯器頁面", True, "頁面和API都正常")
                    return True
                else:
                    print_test_result("選股編輯器頁面", False, "API回應錯誤")
                    return False
            else:
                print_test_result("選股編輯器頁面", False, f"API HTTP {response.status_code}")
                return False
        else:
            print_test_result("選股編輯器頁面", False, f"頁面 HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("選股編輯器頁面", False, str(e))
        return False

def test_strategy_editor_integration():
    """測試策略編輯器整合"""
    print_test_header("策略編輯器整合")
    
    try:
        # 測試策略編輯器頁面
        response = requests.get(f"{BASE_URL}/strategy-editor", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            print("✅ 策略編輯器頁面可正常訪問")
            
            # 測試選股列表API是否可用於策略編輯器
            response = requests.get(f"{BASE_URL}/api/stock-lists", timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print("✅ 策略編輯器可正常取得選股列表")
                    print_test_result("策略編輯器整合", True, "整合功能正常")
                    return True
                else:
                    print_test_result("策略編輯器整合", False, "API回應錯誤")
                    return False
            else:
                print_test_result("策略編輯器整合", False, f"API HTTP {response.status_code}")
                return False
        else:
            print_test_result("策略編輯器整合", False, f"頁面 HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("策略編輯器整合", False, str(e))
        return False

def main():
    """主測試函數"""
    print("開始測試選股編輯器系統功能")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"測試目標: {BASE_URL}")
    
    # 測試結果統計
    test_results = []
    
    # 執行各項測試
    tests = [
        ("選股列表管理", test_stock_list_management),
        ("選股條件功能", test_stock_conditions),
        ("Excel匯入匯出", test_excel_import_export),
        ("策略整合功能", test_strategy_integration),
        ("選股編輯器頁面", test_stock_selector_page),
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
        print("🎉 所有測試都通過！選股編輯器系統功能正常。")
    else:
        print("⚠️  部分測試失敗，請檢查相關功能。")
    
    print(f"\n測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 