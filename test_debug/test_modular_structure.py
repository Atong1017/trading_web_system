#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試重構後的模組化結構
"""

import os
import sys
import importlib

def test_module_imports():
    """測試所有模組是否能正常導入"""
    print("=" * 60)
    print("測試模組化結構")
    print("=" * 60)
    
    # 測試API模組
    api_modules = [
        "api.strategy_api",
        "api.cache_api", 
        "api.backtest_api",
        "api.sample_data_api",
        "api.stock_list_api"
    ]
    
    print("\n1. 測試API模組導入:")
    for module_name in api_modules:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ {module_name} - 導入成功")
        except Exception as e:
            print(f"✗ {module_name} - 導入失敗: {e}")
    
    # 測試路由模組
    route_modules = [
        "routes.pages",
        "routes.api_routes"
    ]
    
    print("\n2. 測試路由模組導入:")
    for module_name in route_modules:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ {module_name} - 導入成功")
        except Exception as e:
            print(f"✗ {module_name} - 導入失敗: {e}")
    
    # 測試簡化的main模組
    print("\n3. 測試簡化main模組:")
    try:
        module = importlib.import_module("main_simplified")
        print(f"✓ main_simplified - 導入成功")
    except Exception as e:
        print(f"✗ main_simplified - 導入失敗: {e}")

def test_file_structure():
    """測試檔案結構"""
    print("\n4. 檢查檔案結構:")
    
    expected_files = [
        "api/strategy_api.py",
        "api/cache_api.py",
        "api/backtest_api.py", 
        "api/sample_data_api.py",
        "api/stock_list_api.py",
        "routes/__init__.py",
        "routes/pages.py",
        "routes/api_routes.py",
        "main_simplified.py"
    ]
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} - 存在")
        else:
            print(f"✗ {file_path} - 不存在")

def compare_file_sizes():
    """比較檔案大小"""
    print("\n5. 檔案大小比較:")
    
    if os.path.exists("main.py"):
        main_size = os.path.getsize("main.py")
        print(f"原始 main.py: {main_size:,} bytes ({main_size/1024:.1f} KB)")
    
    if os.path.exists("main_simplified.py"):
        simplified_size = os.path.getsize("main_simplified.py")
        print(f"簡化 main_simplified.py: {simplified_size:,} bytes ({simplified_size/1024:.1f} KB)")
        
        if os.path.exists("main.py"):
            reduction = (main_size - simplified_size) / main_size * 100
            print(f"減少: {reduction:.1f}%")
    
    # 計算API模組總大小
    api_modules = [
        "api/strategy_api.py",
        "api/cache_api.py",
        "api/backtest_api.py",
        "api/sample_data_api.py", 
        "api/stock_list_api.py"
    ]
    
    total_api_size = 0
    for file_path in api_modules:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            total_api_size += size
            print(f"  {file_path}: {size:,} bytes")
    
    print(f"API模組總大小: {total_api_size:,} bytes ({total_api_size/1024:.1f} KB)")
    
    # 計算路由模組總大小
    route_modules = [
        "routes/pages.py",
        "routes/api_routes.py"
    ]
    
    total_route_size = 0
    for file_path in route_modules:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            total_route_size += size
            print(f"  {file_path}: {size:,} bytes")
    
    print(f"路由模組總大小: {total_route_size:,} bytes ({total_route_size/1024:.1f} KB)")

def test_functionality():
    """測試基本功能"""
    print("\n6. 測試基本功能:")
    
    try:
        # 測試策略API類別
        from api.strategy_api import StrategyAPI
        print("✓ StrategyAPI 類別導入成功")
        
        # 測試快取API類別
        from api.cache_api import CacheAPI
        print("✓ CacheAPI 類別導入成功")
        
        # 測試回測API類別
        from api.backtest_api import BacktestAPI
        print("✓ BacktestAPI 類別導入成功")
        
        # 測試範例資料API類別
        from api.sample_data_api import SampleDataAPI
        print("✓ SampleDataAPI 類別導入成功")
        
        # 測試選股列表API類別
        from api.stock_list_api import StockListAPI
        print("✓ StockListAPI 類別導入成功")
        
    except Exception as e:
        print(f"✗ 功能測試失敗: {e}")

def main():
    """主測試函數"""
    print("開始測試重構後的模組化結構...")
    
    test_module_imports()
    test_file_structure()
    compare_file_sizes()
    test_functionality()
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)
    
    print("\n重構總結:")
    print("1. 將原本的 main.py (2000+ 行) 拆分為多個模組")
    print("2. API功能按功能分類到不同模組:")
    print("   - strategy_api.py: 策略相關API")
    print("   - cache_api.py: 快取管理API") 
    print("   - backtest_api.py: 回測相關API")
    print("   - sample_data_api.py: 範例資料API")
    print("   - stock_list_api.py: 選股列表API")
    print("3. 路由功能分離到 routes/ 目錄:")
    print("   - pages.py: 頁面路由")
    print("   - api_routes.py: API路由整合")
    print("4. main_simplified.py: 簡化的主程式，只負責初始化和路由註冊")
    print("5. 提高程式碼的可維護性和可讀性")

if __name__ == "__main__":
    main() 