#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試布林參數配置功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("開始執行布林參數配置測試...")

try:
    from config.trading_config import TradingConfig
    print("成功導入 TradingConfig")
except Exception as e:
    print(f"導入 TradingConfig 失敗: {e}")
    sys.exit(1)

def test_boolean_parameters_config():
    """測試布林參數配置功能"""
    print("=== 測試布林參數配置功能 ===")
    
    # 測試取得所有布林參數
    boolean_params = TradingConfig.get_boolean_parameters()
    print(f"所有布林參數: {list(boolean_params.keys())}")
    
    # 測試取得布林參數名稱列表
    param_names = TradingConfig.get_boolean_parameter_names()
    print(f"布林參數名稱列表: {param_names}")
    
    # 測試檢查參數是否為布林類型
    test_params = [
        "use_limit_restriction",
        "use_take_profit", 
        "use_stop_loss",
        "use_max_holding_days",
        "force_exit",
        "use_limit_orders",
        "commission_rate",  # 非布林參數
        "shares_per_trade"  # 非布林參數
    ]
    
    print("\n=== 參數類型檢查 ===")
    for param in test_params:
        is_bool = TradingConfig.is_boolean_parameter(param)
        print(f"{param}: {'布林參數' if is_bool else '非布林參數'}")
    
    # 測試取得布林參數預設值
    print("\n=== 布林參數預設值 ===")
    for param_name in param_names:
        default_value = TradingConfig.get_boolean_parameter_default(param_name)
        param_info = boolean_params[param_name]
        print(f"{param_name}: {default_value} ({param_info['name']})")
    
    # 測試參數詳細資訊
    print("\n=== 布林參數詳細資訊 ===")
    for param_name, param_info in boolean_params.items():
        print(f"參數: {param_name}")
        print(f"  名稱: {param_info['name']}")
        print(f"  描述: {param_info['description']}")
        print(f"  預設值: {param_info['default']}")
        print()

def test_parameter_conversion():
    """測試參數轉換邏輯"""
    print("=== 測試參數轉換邏輯 ===")
    
    # 模擬表單資料
    form_data = {
        "param-use_limit_restriction": "true",
        "param-use_take_profit": "false", 
        "param-use_stop_loss": "1",
        "param-force_exit": "0",
        "param-use_limit_orders": "on",
        "param-commission_rate": "0.001425",
        "param-shares_per_trade": "1000"
    }
    
    strategy_params = {}
    
    for key, value in form_data.items():
        if key.startswith('param-'):
            param_name = key[6:]  # 移除 'param-' 前綴
            
            # 根據參數類型轉換值
            if TradingConfig.is_boolean_parameter(param_name):
                strategy_params[param_name] = value.lower() == 'true' if isinstance(value, str) else bool(value)
            elif param_name in ['commission_rate', 'commission_discount', 'securities_tax_rate', 
                              'take_profit_percentage', 'stop_loss_percentage', 'limit_percentage']:
                strategy_params[param_name] = float(value) if value else 0.0
            elif param_name in ['shares_per_trade', 'max_holding_days', 'high_period', 
                              'max_holding_time', 'announcement_delay']:
                strategy_params[param_name] = int(value) if value else 0
            else:
                strategy_params[param_name] = value
    
    print("轉換後的策略參數:")
    for param_name, value in strategy_params.items():
        param_type = type(value).__name__
        print(f"  {param_name}: {value} ({param_type})")

def test_config_consistency():
    """測試配置一致性"""
    print("=== 測試配置一致性 ===")
    
    # 檢查所有布林參數是否都有完整的配置
    boolean_params = TradingConfig.get_boolean_parameters()
    
    required_fields = ["name", "description", "default"]
    
    for param_name, param_info in boolean_params.items():
        print(f"檢查參數: {param_name}")
        
        # 檢查必要欄位
        for field in required_fields:
            if field not in param_info:
                print(f"  錯誤: 缺少欄位 '{field}'")
            else:
                print(f"  {field}: {param_info[field]}")
        
        # 檢查預設值類型
        if not isinstance(param_info.get("default"), bool):
            print(f"  錯誤: 預設值不是布林類型")
        
        print()

if __name__ == "__main__":
    try:
        test_boolean_parameters_config()
        test_parameter_conversion()
        test_config_consistency()
        print("所有測試完成！")
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc() 