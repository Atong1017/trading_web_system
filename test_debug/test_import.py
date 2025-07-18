#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 import
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback

def test_imports():
    """測試 import"""
    print("測試 import...")
    
    try:
        print("1. 測試 StrategyManager...")
        from strategies.strategy_manager import StrategyManager
        print("✅ StrategyManager import 成功")
        
        print("2. 測試 DynamicStrategy...")
        from strategies.dynamic_strategy import DynamicStrategy
        print("✅ DynamicStrategy import 成功")
        
        print("3. 測試 DataProvider...")
        from core.data_provider import DataProvider
        print("✅ DataProvider import 成功")
        
        print("4. 測試 StockListManager...")
        from core.stock_list_manager import StockListManager
        print("✅ StockListManager import 成功")
        
        print("5. 測試 main.py...")
        import main
        print("✅ main.py import 成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Import 失敗: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports() 