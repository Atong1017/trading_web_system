#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試策略參數配置
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.day_trading import DayTradingStrategy
from strategies.swing_trading import SwingTradingStrategy
from strategies.bookbuilding import BookbuildingStrategy

def test_strategy_parameters():
    """測試所有策略的參數配置"""
    
    print("=== 測試策略參數配置 ===")
    
    # 測試當沖策略
    print("\n1. 當沖策略參數:")
    day_strategy = DayTradingStrategy({})
    print(f"策略名稱: {day_strategy.strategy_name}")
    print(f"策略描述: {day_strategy.strategy_description}")
    print(f"參數數量: {len(day_strategy.strategy_parameters)}")
    
    for key, param in day_strategy.strategy_parameters.items():
        print(f"  - {key}: {param['label']} ({param['type']})")
    
    # 測試波段策略
    print("\n2. 波段策略參數:")
    swing_strategy = SwingTradingStrategy({})
    print(f"策略名稱: {swing_strategy.strategy_name}")
    print(f"策略描述: {swing_strategy.strategy_description}")
    print(f"參數數量: {len(swing_strategy.strategy_parameters)}")
    
    for key, param in swing_strategy.strategy_parameters.items():
        print(f"  - {key}: {param['label']} ({param['type']})")
    
    # 測試詢圈公告策略
    print("\n3. 詢圈公告策略參數:")
    book_strategy = BookbuildingStrategy({})
    print(f"策略名稱: {book_strategy.strategy_name}")
    print(f"策略描述: {book_strategy.strategy_description}")
    print(f"參數數量: {len(book_strategy.strategy_parameters)}")
    
    for key, param in book_strategy.strategy_parameters.items():
        print(f"  - {key}: {param['label']} ({param['type']})")

if __name__ == "__main__":
    test_strategy_parameters() 