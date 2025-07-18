#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接測試 StrategyManager 類別
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.strategy_manager import StrategyManager

def test_strategy_manager():
    """測試 StrategyManager 類別"""
    print("開始測試 StrategyManager 類別...")
    
    try:
        # 建立 StrategyManager 實例
        print("建立 StrategyManager 實例...")
        strategy_manager = StrategyManager()
        print("✅ StrategyManager 實例建立成功")
        
        # 測試 get_strategy_template 方法
        print("測試 get_strategy_template 方法...")
        template = strategy_manager.get_strategy_template()
        print(f"✅ 成功取得策略模板，長度: {len(template)}")
        print(f"模板前100字: {template[:100]}...")
        
        # 測試 get_all_strategies 方法
        print("測試 get_all_strategies 方法...")
        strategies = strategy_manager.get_all_strategies()
        print(f"✅ 成功取得 {len(strategies)} 個策略")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ 測試失敗: {e}")
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("開始直接測試 StrategyManager 類別")
    
    result = test_strategy_manager()
    
    if result:
        print("✅ 所有測試通過")
    else:
        print("❌ 測試失敗") 