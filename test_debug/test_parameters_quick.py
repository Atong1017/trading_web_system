#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試參數設定
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_swing_parameters():
    """快速測試波段策略參數"""
    try:
        from strategies.swing_trading import SwingTradingStrategy
        
        # 測試預設參數
        strategy = SwingTradingStrategy({})
        
        # 檢查共用參數
        assert strategy.parameters.get('commission_rate') == 0.001425
        assert strategy.parameters.get('commission_discount') == 0.3
        assert strategy.parameters.get('securities_tax_rate') == 0.003
        assert strategy.parameters.get('shares_per_trade') == 1000
        
        # 檢查策略參數
        assert strategy.parameters.get('entry_condition') == 'next_open'
        assert strategy.parameters.get('exit_price_condition') == 'next_open'
        assert strategy.parameters.get('use_limit_restriction') == True
        assert strategy.parameters.get('limit_percentage') == 9.0
        assert strategy.parameters.get('use_take_profit') == True
        assert strategy.parameters.get('take_profit_percentage') == 20.0
        assert strategy.parameters.get('use_stop_loss') == True
        assert strategy.parameters.get('stop_loss_percentage') == -20.0
        assert strategy.parameters.get('use_max_holding_days') == True
        assert strategy.parameters.get('max_holding_days') == 30
        
        print("✅ 波段策略參數測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 波段策略參數測試失敗: {e}")
        return False

def test_day_trading_parameters():
    """快速測試當沖策略參數"""
    try:
        from strategies.day_trading import DayTradingStrategy
        
        # 測試預設參數
        strategy = DayTradingStrategy({})
        
        # 檢查共用參數
        assert strategy.parameters.get('commission_rate') == 0.001425
        assert strategy.parameters.get('commission_discount') == 0.3
        assert strategy.parameters.get('securities_tax_rate') == 0.0015  # 當沖證交稅
        assert strategy.parameters.get('shares_per_trade') == 1000
        
        # 檢查策略參數
        assert strategy.parameters.get('entry_condition') == 'next_open'
        assert strategy.parameters.get('exit_price_condition') == 'next_open'
        assert strategy.parameters.get('use_limit_restriction') == True
        assert strategy.parameters.get('limit_percentage') == 9.0
        assert strategy.parameters.get('use_limit_orders') == True
        assert strategy.parameters.get('max_holding_time') == 1
        assert strategy.parameters.get('force_exit') == False
        
        print("✅ 當沖策略參數測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 當沖策略參數測試失敗: {e}")
        return False

def test_bookbuilding_parameters():
    """快速測試詢圈公告策略參數"""
    try:
        from strategies.bookbuilding import BookbuildingStrategy
        
        # 測試預設參數
        strategy = BookbuildingStrategy({})
        
        # 檢查共用參數
        assert strategy.parameters.get('commission_rate') == 0.001425
        assert strategy.parameters.get('commission_discount') == 0.3
        assert strategy.parameters.get('securities_tax_rate') == 0.003
        assert strategy.parameters.get('shares_per_trade') == 1000
        
        # 檢查策略參數
        assert strategy.parameters.get('announcement_delay') == 1
        assert strategy.parameters.get('position_size') == 0.1
        assert strategy.parameters.get('max_holding_days') == 30
        assert strategy.parameters.get('force_exit') == True
        
        print("✅ 詢圈公告策略參數測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 詢圈公告策略參數測試失敗: {e}")
        return False

def test_parameter_configuration():
    """測試參數配置"""
    try:
        from strategies.swing_trading import SwingTradingStrategy
        from strategies.day_trading import DayTradingStrategy
        from strategies.bookbuilding import BookbuildingStrategy
        
        strategies = [
            SwingTradingStrategy({}),
            DayTradingStrategy({}),
            BookbuildingStrategy({})
        ]
        
        for strategy in strategies:
            param_config = strategy.strategy_parameters
            
            # 檢查是否有共用參數
            common_params = ["commission_rate", "commission_discount", "securities_tax_rate", "shares_per_trade"]
            for param in common_params:
                assert param in param_config, f"缺少共用參數: {param}"
            
            # 檢查參數配置格式
            for param_name, config in param_config.items():
                assert 'type' in config, f"參數 {param_name} 缺少 type"
                assert 'label' in config, f"參數 {param_name} 缺少 label"
                assert 'default' in config, f"參數 {param_name} 缺少 default"
                assert 'description' in config, f"參數 {param_name} 缺少 description"
        
        print("✅ 參數配置測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 參數配置測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("=== 快速參數測試 ===")
    
    results = []
    results.append(test_swing_parameters())
    results.append(test_day_trading_parameters())
    results.append(test_bookbuilding_parameters())
    results.append(test_parameter_configuration())
    
    if all(results):
        print("\n🎉 所有測試通過！")
    else:
        print("\n❌ 部分測試失敗！") 