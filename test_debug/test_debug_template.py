#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試策略模板問題
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback

def test_strategy_manager_direct():
    """直接測試 StrategyManager"""
    print("=" * 60)
    print("直接測試 StrategyManager")
    print("=" * 60)
    
    try:
        print("1. 導入 StrategyManager...")
        from strategies.strategy_manager import StrategyManager
        print("✅ StrategyManager 導入成功")
        
        print("2. 建立 StrategyManager 實例...")
        strategy_manager = StrategyManager()
        print("✅ StrategyManager 實例建立成功")
        
        print("3. 測試 get_strategy_template 方法...")
        template = strategy_manager.get_strategy_template()
        print(f"✅ 成功取得策略模板，長度: {len(template)} 字元")
        
        # 檢查模板內容
        if 'def should_entry' in template and 'def should_exit' in template:
            print("✅ 模板包含必要的函數定義")
        else:
            print("⚠️  模板可能缺少必要的函數定義")
        
        # 檢查是否有 polars 相關的程式碼
        if 'stock_data.row(' in template:
            print("✅ 模板使用正確的 polars DataFrame 存取方式", named=True)
        else:
            print("⚠️  模板可能未使用正確的 polars DataFrame 存取方式")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        traceback.print_exc()
        return False

def test_dynamic_strategy():
    """測試 DynamicStrategy"""
    print("\n" + "=" * 60)
    print("測試 DynamicStrategy")
    print("=" * 60)
    
    try:
        print("1. 導入 DynamicStrategy...")
        from strategies.dynamic_strategy import DynamicStrategy
        print("✅ DynamicStrategy 導入成功")
        
        print("2. 測試簡單的策略程式碼...")
        test_code = """def should_entry(stock_data, current_index):
    return False, {}

def should_exit(stock_data, current_index, position):
    return False, {}"""
        
        strategy = DynamicStrategy({}, test_code, "測試策略")
        print("✅ DynamicStrategy 實例建立成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        traceback.print_exc()
        return False

def test_api_simulation():
    """模擬 API 調用"""
    print("\n" + "=" * 60)
    print("模擬 API 調用")
    print("=" * 60)
    
    try:
        print("1. 導入必要模組...")
        from strategies.strategy_manager import StrategyManager
        print("✅ 模組導入成功")
        
        print("2. 建立 StrategyManager...")
        strategy_manager = StrategyManager()
        print("✅ StrategyManager 建立成功")
        
        print("3. 模擬 API 調用...")
        try:
            template = strategy_manager.get_strategy_template()
            print("✅ 策略模板取得成功")
            print(f"模板長度: {len(template)} 字元")
            
            # 模擬 API 回應
            response = {"status": "success", "template": template}
            print("✅ API 回應模擬成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 策略模板取得失敗: {e}")
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 模擬失敗: {e}")
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("開始調試策略模板問題")
    print(f"Python 版本: {sys.version}")
    
    # 測試 StrategyManager
    strategy_manager_result = test_strategy_manager_direct()
    
    # 測試 DynamicStrategy
    dynamic_strategy_result = test_dynamic_strategy()
    
    # 模擬 API 調用
    api_simulation_result = test_api_simulation()
    
    # 總結
    print("\n" + "=" * 60)
    print("調試總結")
    print("=" * 60)
    print(f"StrategyManager: {'✅ 通過' if strategy_manager_result else '❌ 失敗'}")
    print(f"DynamicStrategy: {'✅ 通過' if dynamic_strategy_result else '❌ 失敗'}")
    print(f"API 模擬: {'✅ 通過' if api_simulation_result else '❌ 失敗'}")
    
    if strategy_manager_result and dynamic_strategy_result and api_simulation_result:
        print("\n🎉 所有測試都通過！問題可能出在伺服器端。")
    else:
        print("\n⚠️  部分測試失敗，請檢查相關功能。")

if __name__ == "__main__":
    main() 