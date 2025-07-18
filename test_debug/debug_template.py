#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試策略模板問題
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback

def test_strategy_manager():
    """測試 StrategyManager"""
    print("測試 StrategyManager...")
    
    try:
        from strategies.strategy_manager import StrategyManager
        print("✅ StrategyManager 導入成功")
        
        strategy_manager = StrategyManager()
        print("✅ StrategyManager 實例建立成功")
        
        template = strategy_manager.get_strategy_template()
        print(f"✅ 成功取得策略模板，長度: {len(template)} 字元")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_strategy_manager() 