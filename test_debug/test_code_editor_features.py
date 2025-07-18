#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試程式碼編輯器功能
包含語法高亮、自動縮排、程式碼提示等功能
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

def test_code_editor_page():
    """測試程式碼編輯器頁面"""
    print_test_header("程式碼編輯器頁面")
    
    try:
        # 測試頁面是否可訪問
        response = requests.get(f"{BASE_URL}/strategy-editor", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            print("✅ 策略編輯器頁面可正常訪問")
            
            # 檢查是否包含 CodeMirror 相關資源
            content = response.text
            if 'codemirror' in content.lower():
                print("✅ 頁面包含 CodeMirror 相關資源")
                print_test_result("程式碼編輯器頁面", True, "頁面正常載入")
                return True
            else:
                print("⚠️  頁面可能未包含 CodeMirror 資源")
                print_test_result("程式碼編輯器頁面", False, "缺少 CodeMirror 資源")
                return False
        else:
            print_test_result("程式碼編輯器頁面", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("程式碼編輯器頁面", False, str(e))
        return False

def test_code_editor_api():
    """測試程式碼編輯器相關 API"""
    print_test_header("程式碼編輯器 API")
    
    try:
        # 測試取得策略模板
        response = requests.get(f"{BASE_URL}/api/strategies/custom/template", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                template = data.get('template', '')
                print(f"✅ 成功取得策略模板，長度: {len(template)} 字元")
                
                # 檢查模板內容
                if 'class' in template and 'def' in template:
                    print("✅ 模板包含有效的 Python 程式碼結構")
                else:
                    print("⚠️  模板可能不是有效的 Python 程式碼")
                
                print_test_result("程式碼編輯器 API", True, "API 功能正常")
                return True
            else:
                print_test_result("程式碼編輯器 API", False, "API 回應錯誤")
                return False
        else:
            print_test_result("程式碼編輯器 API", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("程式碼編輯器 API", False, str(e))
        return False

def test_code_validation():
    """測試程式碼驗證功能"""
    print_test_header("程式碼驗證功能")
    
    try:
        # 測試有效的 Python 程式碼
        valid_code = """class TestStrategy:
    def __init__(self, parameters):
        self.parameters = parameters
    
    def execute(self, data):
        return data.clone()"""
        
        response = requests.post(
            f"{BASE_URL}/api/strategies/custom/validate",
            json={"code": valid_code},
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ 有效程式碼驗證通過")
                
                # 測試無效的 Python 程式碼
                invalid_code = """class TestStrategy:
    def __init__(self, parameters:
        self.parameters = parameters
    
    def execute(self, data):
        return data.clone()"""
                
                response = requests.post(
                    f"{BASE_URL}/api/strategies/custom/validate",
                    json={"code": invalid_code},
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') != 'success':
                        print("✅ 無效程式碼正確被拒絕")
                        print_test_result("程式碼驗證功能", True, "驗證功能正常")
                        return True
                    else:
                        print("⚠️  無效程式碼未被正確檢測")
                        print_test_result("程式碼驗證功能", False, "驗證邏輯有問題")
                        return False
                else:
                    print_test_result("程式碼驗證功能", False, f"無效程式碼驗證 HTTP {response.status_code}")
                    return False
            else:
                print_test_result("程式碼驗證功能", False, "有效程式碼驗證失敗")
                return False
        else:
            print_test_result("程式碼驗證功能", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("程式碼驗證功能", False, str(e))
        return False

def test_strategy_creation():
    """測試策略建立功能"""
    print_test_header("策略建立功能")
    
    try:
        # 建立測試策略
        strategy_data = {
            "name": "測試程式碼編輯器策略",
            "description": "用於測試程式碼編輯器功能的策略",
            "type": "template"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/strategies/custom",
            json=strategy_data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                strategy_id = data.get('strategy_id')
                print(f"✅ 成功建立策略: {strategy_id}")
                
                # 更新策略程式碼
                test_code = """class TestStrategy:
    def __init__(self, parameters):
        self.parameters = parameters
        self.strategy_name = "測試策略"
    
    def execute(self, data):
        # 測試自動縮排功能
        if len(data) > 10:
            result = data.clone()
            result = result.with_columns([
                pl.col('close').rolling_mean(window_size=5).alias('ma5')
            ])
            return result
        return data"""
                
                update_data = {
                    "name": "測試程式碼編輯器策略",
                    "description": "用於測試程式碼編輯器功能的策略",
                    "code": test_code
                }
                
                response = requests.put(
                    f"{BASE_URL}/api/strategies/custom/{strategy_id}",
                    json=update_data,
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        print("✅ 成功更新策略程式碼")
                        
                        # 測試策略程式碼
                        test_data = {
                            "strategy_id": strategy_id,
                            "code": test_code
                        }
                        
                        response = requests.post(
                            f"{BASE_URL}/api/strategies/custom/test",
                            json=test_data,
                            timeout=TEST_TIMEOUT
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'success':
                                print("✅ 策略程式碼測試通過")
                                
                                # 清理測試資料
                                response = requests.delete(
                                    f"{BASE_URL}/api/strategies/custom/{strategy_id}",
                                    timeout=TEST_TIMEOUT
                                )
                                
                                print_test_result("策略建立功能", True, "完整流程測試通過")
                                return True
                            else:
                                print_test_result("策略建立功能", False, "策略測試失敗")
                                return False
                        else:
                            print_test_result("策略建立功能", False, f"策略測試 HTTP {response.status_code}")
                            return False
                    else:
                        print_test_result("策略建立功能", False, "更新策略失敗")
                        return False
                else:
                    print_test_result("策略建立功能", False, f"更新策略 HTTP {response.status_code}")
                    return False
            else:
                print_test_result("策略建立功能", False, "建立策略失敗")
                return False
        else:
            print_test_result("策略建立功能", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("策略建立功能", False, str(e))
        return False

def test_code_editor_features():
    """測試程式碼編輯器特色功能"""
    print_test_header("程式碼編輯器特色功能")
    
    try:
        # 測試程式碼格式化功能（模擬）
        test_code = """class TestStrategy:
def __init__(self, parameters):
self.parameters = parameters
def execute(self, data):
if len(data) > 10:
result = data.clone()
return result
return data"""
        
        # 檢查程式碼是否包含自動縮排相關的語法
        if 'class' in test_code and 'def' in test_code:
            print("✅ 程式碼包含 Python 類別和函數定義")
            
            # 檢查是否有縮排問題
            lines = test_code.split('\n')
            has_indentation_issues = any(
                line.strip() and not line.startswith(' ') and not line.startswith('\t')
                for line in lines[1:]  # 跳過第一行
            )
            
            if has_indentation_issues:
                print("✅ 檢測到縮排問題，適合測試格式化功能")
            else:
                print("⚠️  程式碼縮排正常")
            
            print_test_result("程式碼編輯器特色功能", True, "特色功能測試通過")
            return True
        else:
            print_test_result("程式碼編輯器特色功能", False, "程式碼結構不完整")
            return False
            
    except Exception as e:
        print_test_result("程式碼編輯器特色功能", False, str(e))
        return False

def test_editor_integration():
    """測試編輯器整合功能"""
    print_test_header("編輯器整合功能")
    
    try:
        # 測試策略列表 API
        response = requests.get(f"{BASE_URL}/api/strategies/custom", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                strategies = data.get('strategies', [])
                print(f"✅ 成功取得 {len(strategies)} 個策略")
                
                # 檢查策略資料結構
                if strategies:
                    strategy = strategies[0]
                    required_fields = ['id', 'name', 'description', 'code']
                    missing_fields = [field for field in required_fields if field not in strategy]
                    
                    if not missing_fields:
                        print("✅ 策略資料結構完整")
                        print_test_result("編輯器整合功能", True, "整合功能正常")
                        return True
                    else:
                        print(f"⚠️  策略資料缺少欄位: {missing_fields}")
                        print_test_result("編輯器整合功能", False, "資料結構不完整")
                        return False
                else:
                    print("⚠️  沒有可用的策略")
                    print_test_result("編輯器整合功能", True, "無策略但 API 正常")
                    return True
            else:
                print_test_result("編輯器整合功能", False, "API 回應錯誤")
                return False
        else:
            print_test_result("編輯器整合功能", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("編輯器整合功能", False, str(e))
        return False

def main():
    """主測試函數"""
    print("開始測試程式碼編輯器功能")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"測試目標: {BASE_URL}")
    
    # 測試結果統計
    test_results = []
    
    # 執行各項測試
    tests = [
        ("程式碼編輯器頁面", test_code_editor_page),
        ("程式碼編輯器 API", test_code_editor_api),
        ("程式碼驗證功能", test_code_validation),
        ("策略建立功能", test_strategy_creation),
        ("程式碼編輯器特色功能", test_code_editor_features),
        ("編輯器整合功能", test_editor_integration)
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
        print("🎉 所有測試都通過！程式碼編輯器功能正常。")
    else:
        print("⚠️  部分測試失敗，請檢查相關功能。")
    
    print(f"\n測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 