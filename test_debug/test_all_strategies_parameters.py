#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試所有策略的新參數設定
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from strategies.swing_trading import SwingTradingStrategy
from strategies.day_trading import DayTradingStrategy
from strategies.bookbuilding import BookbuildingStrategy

def test_swing_trading_parameters():
    """測試波段策略參數"""
    print("=== 測試波段策略參數 ===")
    
    parameters = {}
    strategy = SwingTradingStrategy(parameters)
    
    print("策略名稱:", strategy.strategy_name)
    print("策略描述:", strategy.strategy_description)
    print()
    
    # 檢查共用參數
    print("共用參數:")
    print(f"  手續費率: {strategy.parameters.get('commission_rate')}")
    print(f"  手續費折數: {strategy.parameters.get('commission_discount')}")
    print(f"  證交稅率: {strategy.parameters.get('securities_tax_rate')}")
    print(f"  交易股數: {strategy.parameters.get('shares_per_trade')}")
    print()
    
    # 檢查策略專用參數
    print("策略專用參數:")
    print(f"  進場條件: {strategy.parameters.get('entry_condition')}")
    print(f"  出場價條件: {strategy.parameters.get('exit_price_condition')}")
    print(f"  使用漲跌停限制: {strategy.parameters.get('use_limit_restriction')}")
    print(f"  漲跌停百分比: {strategy.parameters.get('limit_percentage')}%")
    print(f"  使用停利: {strategy.parameters.get('use_take_profit')}")
    print(f"  停利百分比: {strategy.parameters.get('take_profit_percentage')}%")
    print(f"  使用停損: {strategy.parameters.get('use_stop_loss')}")
    print(f"  停損百分比: {strategy.parameters.get('stop_loss_percentage')}%")
    print(f"  使用最大持有天數: {strategy.parameters.get('use_max_holding_days')}")
    print(f"  最大持有天數: {strategy.parameters.get('max_holding_days')}")
    print(f"  強制出場: {strategy.parameters.get('force_exit')}")
    print(f"  新高計算期間: {strategy.parameters.get('high_period')}")
    print()

def test_day_trading_parameters():
    """測試當沖策略參數"""
    print("=== 測試當沖策略參數 ===")
    
    parameters = {}
    strategy = DayTradingStrategy(parameters)
    
    print("策略名稱:", strategy.strategy_name)
    print("策略描述:", strategy.strategy_description)
    print()
    
    # 檢查共用參數
    print("共用參數:")
    print(f"  手續費率: {strategy.parameters.get('commission_rate')}")
    print(f"  手續費折數: {strategy.parameters.get('commission_discount')}")
    print(f"  證交稅率: {strategy.parameters.get('securities_tax_rate')} (當沖)")
    print(f"  交易股數: {strategy.parameters.get('shares_per_trade')}")
    print()
    
    # 檢查策略專用參數
    print("策略專用參數:")
    print(f"  進場條件: {strategy.parameters.get('entry_condition')}")
    print(f"  出場價條件: {strategy.parameters.get('exit_price_condition')}")
    print(f"  使用漲跌停限制: {strategy.parameters.get('use_limit_restriction')}")
    print(f"  漲跌停百分比: {strategy.parameters.get('limit_percentage')}%")
    print(f"  使用漲跌停單: {strategy.parameters.get('use_limit_orders')}")
    print(f"  最大持有天數: {strategy.parameters.get('max_holding_time')}")
    print(f"  強制出場: {strategy.parameters.get('force_exit')}")
    print()

def test_bookbuilding_parameters():
    """測試詢圈公告策略參數"""
    print("=== 測試詢圈公告策略參數 ===")
    
    parameters = {}
    strategy = BookbuildingStrategy(parameters)
    
    print("策略名稱:", strategy.strategy_name)
    print("策略描述:", strategy.strategy_description)
    print()
    
    # 檢查共用參數
    print("共用參數:")
    print(f"  手續費率: {strategy.parameters.get('commission_rate')}")
    print(f"  手續費折數: {strategy.parameters.get('commission_discount')}")
    print(f"  證交稅率: {strategy.parameters.get('securities_tax_rate')}")
    print(f"  交易股數: {strategy.parameters.get('shares_per_trade')}")
    print()
    
    # 檢查策略專用參數
    print("策略專用參數:")
    print(f"  公告延遲天數: {strategy.parameters.get('announcement_delay')}")
    print(f"  部位大小比例: {strategy.parameters.get('position_size')}")
    print(f"  最大持有天數: {strategy.parameters.get('max_holding_days')}")
    print(f"  強制出場: {strategy.parameters.get('force_exit')}")
    print()

def test_parameter_configuration():
    """測試參數配置"""
    print("=== 測試參數配置 ===")
    
    strategies = [
        ("波段策略", SwingTradingStrategy({})),
        ("當沖策略", DayTradingStrategy({})),
        ("詢圈公告策略", BookbuildingStrategy({}))
    ]
    
    for strategy_name, strategy in strategies:
        print(f"--- {strategy_name} ---")
        param_config = strategy.strategy_parameters
        
        # 統計參數類型
        param_types = {}
        for param_name, config in param_config.items():
            param_type = config.get('type', 'unknown')
            param_types[param_type] = param_types.get(param_type, 0) + 1
        
        print(f"  總參數數量: {len(param_config)}")
        print(f"  參數類型分布: {param_types}")
        
        # 檢查是否有共用參數
        common_params = ["commission_rate", "commission_discount", "securities_tax_rate", "shares_per_trade"]
        has_common_params = all(param in param_config for param in common_params)
        print(f"  包含共用參數: {has_common_params}")
        print()

def test_custom_parameters():
    """測試自定義參數"""
    print("=== 測試自定義參數 ===")
    
    # 測試波段策略自定義參數
    swing_params = {
        "commission_rate": 0.001425,
        "commission_discount": 0.3,
        "securities_tax_rate": 0.003,
        "shares_per_trade": 1000,
        "entry_condition": "next_close",
        "exit_price_condition": "next_close",
        "use_limit_restriction": False,
        "use_take_profit": False,
        "use_stop_loss": False,
        "use_max_holding_days": False
    }
    
    try:
        strategy = SwingTradingStrategy(swing_params)
        print("✅ 波段策略自定義參數設定成功")
        print(f"   進場條件: {strategy.parameters.get('entry_condition')}")
        print(f"   使用停利: {strategy.parameters.get('use_take_profit')}")
        print(f"   使用停損: {strategy.parameters.get('use_stop_loss')}")
        print(f"   使用最大持有天數: {strategy.parameters.get('use_max_holding_days')}")
    except Exception as e:
        print(f"❌ 波段策略自定義參數設定失敗: {e}")
    
    print()
    
    # 測試當沖策略自定義參數
    day_params = {
        "securities_tax_rate": 0.0015,  # 當沖證交稅
        "max_holding_time": 1,
        "force_exit": True
    }
    
    try:
        strategy = DayTradingStrategy(day_params)
        print("✅ 當沖策略自定義參數設定成功")
        print(f"   證交稅率: {strategy.parameters.get('securities_tax_rate')}")
        print(f"   最大持有天數: {strategy.parameters.get('max_holding_time')}")
        print(f"   強制出場: {strategy.parameters.get('force_exit')}")
    except Exception as e:
        print(f"❌ 當沖策略自定義參數設定失敗: {e}")

if __name__ == "__main__":
    test_swing_trading_parameters()
    test_day_trading_parameters()
    test_bookbuilding_parameters()
    test_parameter_configuration()
    test_custom_parameters() 