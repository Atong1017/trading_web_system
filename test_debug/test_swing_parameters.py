#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試波段策略的新參數設定
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from datetime import datetime, timedelta
from strategies.swing_trading import SwingTradingStrategy

def test_parameter_configuration():
    """測試參數配置"""
    print("=== 測試波段策略參數配置 ===")
    
    # 建立策略實例
    parameters = {}
    strategy = SwingTradingStrategy(parameters)
    
    print("策略名稱:", strategy.strategy_name)
    print("策略描述:", strategy.strategy_description)
    print()
    
    # 檢查參數配置
    param_config = strategy.strategy_parameters
    print("參數配置:")
    for param_name, param_config in param_config.items():
        print(f"  {param_name}: {param_config['label']} ({param_config['type']})")
        print(f"    預設值: {param_config['default']}")
        print(f"    描述: {param_config['description']}")
        print()

def test_parameter_validation():
    """測試參數驗證"""
    print("=== 測試參數驗證 ===")
    
    # 測試不同參數組合
    test_cases = [
        {
            "name": "預設參數",
            "parameters": {}
        },
        {
            "name": "自定義參數",
            "parameters": {
                "commission_rate": 0.001425,
                "commission_discount": 0.3,
                "securities_tax_rate": 0.003,
                "shares_per_trade": 1000,
                "entry_condition": "next_open",
                "exit_price_condition": "next_close",
                "use_limit_restriction": True,
                "limit_percentage": 9.0,
                "use_take_profit": True,
                "take_profit_percentage": 20.0,
                "use_stop_loss": True,
                "stop_loss_percentage": -20.0,
                "use_max_holding_days": True,
                "max_holding_days": 30,
                "force_exit": True,
                "high_period": 20
            }
        },
        {
            "name": "停利停損關閉",
            "parameters": {
                "use_take_profit": False,
                "use_stop_loss": False,
                "use_max_holding_days": False
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"--- {test_case['name']} ---")
        try:
            strategy = SwingTradingStrategy(test_case['parameters'])
            print("✅ 參數驗證成功")
            print(f"   手續費率: {strategy.parameters.get('commission_rate')}")
            print(f"   手續費折數: {strategy.parameters.get('commission_discount')}")
            print(f"   證交稅率: {strategy.parameters.get('securities_tax_rate')}")
            print(f"   交易股數: {strategy.parameters.get('shares_per_trade')}")
            print(f"   進場條件: {strategy.parameters.get('entry_condition')}")
            print(f"   出場價條件: {strategy.parameters.get('exit_price_condition')}")
            print(f"   使用停利: {strategy.parameters.get('use_take_profit')}")
            print(f"   停利百分比: {strategy.parameters.get('take_profit_percentage')}%")
            print(f"   使用停損: {strategy.parameters.get('use_stop_loss')}")
            print(f"   停損百分比: {strategy.parameters.get('stop_loss_percentage')}%")
            print()
        except Exception as e:
            print(f"❌ 參數驗證失敗: {e}")
            print()

def test_trading_logic():
    """測試交易邏輯"""
    print("=== 測試交易邏輯 ===")
    
    # 建立測試資料
    test_data = {
        "date": [
            datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3),
            datetime(2024, 1, 4), datetime(2024, 1, 5), datetime(2024, 1, 8),
            datetime(2024, 1, 9), datetime(2024, 1, 10), datetime(2024, 1, 11),
            datetime(2024, 1, 12), datetime(2024, 1, 15), datetime(2024, 1, 16)
        ],
        "open": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        "high": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113],
        "low": [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        "close": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112]
    }
    
    df = pl.DataFrame(test_data)
    
    # 建立策略實例
    parameters = {
        "use_take_profit": True,
        "take_profit_percentage": 20.0,
        "use_stop_loss": True,
        "stop_loss_percentage": -20.0,
        "use_limit_restriction": True,
        "limit_percentage": 9.0,
        "use_max_holding_days": True,
        "max_holding_days": 30,
        "entry_condition": "next_open",
        "exit_price_condition": "next_open"
    }
    
    strategy = SwingTradingStrategy(parameters)
    
    print("測試資料:")
    print(df)
    print()
    
    # 測試進場邏輯
    print("測試進場邏輯:")
    for i in range(20, len(df)):
        should_entry, entry_info = strategy.should_entry(df, i)
        if should_entry:
            print(f"  第{i}天: 應該進場 - {entry_info}")
    
    print()
    
    # 測試出場邏輯
    print("測試出場邏輯:")
    # 模擬一個持倉
    position = {
        "entry_date": datetime(2024, 1, 1),
        "entry_price": 100.0,
        "base_price": 99.0,
        "shares": 1000
    }
    
    for i in range(20, len(df)):
        should_exit, exit_info = strategy.should_exit(df, i, position)
        if should_exit:
            print(f"  第{i}天: 應該出場 - {exit_info}")

if __name__ == "__main__":
    test_parameter_configuration()
    test_parameter_validation()
    test_trading_logic() 