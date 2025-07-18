#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試下拉選單參數功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.dynamic_strategy import DynamicStrategy
from core.utils import load_strategy_from_file

def test_select_parameter():
    """測試下拉選單參數功能"""
    
    # 建立測試策略程式碼
    test_code = '''
def should_entry(data, **kwargs):
    """進場條件"""
    action = kwargs.get('action', 'buy')
    print(f"進場動作: {action}")
    return True

def should_exit(data, **kwargs):
    """出場條件"""
    action = kwargs.get('action', 'sell')
    print(f"出場動作: {action}")
    return True
'''
    
    # 建立測試參數配置
    test_parameters = {
        'action': {
            'type': 'select',
            'label': '交易動作',
            'description': '選擇買入或賣出動作',
            'default': 'buy',
            'options': [
                {'value': 'buy', 'label': '買入'},
                {'value': 'sell', 'label': '賣出'},
                {'value': 'hold', 'label': '持有'}
            ]
        },
        'strategy_type': {
            'type': 'select',
            'label': '策略類型',
            'description': '選擇策略類型',
            'default': 'momentum',
            'options': [
                {'value': 'momentum', 'label': '動能策略'},
                {'value': 'mean_reversion', 'label': '均值回歸'},
                {'value': 'breakout', 'label': '突破策略'}
            ]
        }
    }
    
    print("=== 測試下拉選單參數功能 ===")
    print(f"參數配置: {test_parameters}")
    
    # 建立動態策略實例
    strategy = DynamicStrategy(
        strategy_id="test_select",
        name="測試選項策略",
        description="測試下拉選單參數",
        code=test_code,
        parameters=test_parameters
    )
    
    # 測試參數獲取
    print("\n=== 測試參數獲取 ===")
    for param_name, param_config in test_parameters.items():
        if param_config['type'] == 'select':
            print(f"參數: {param_name}")
            print(f"  標籤: {param_config['label']}")
            print(f"  預設值: {param_config['default']}")
            print(f"  選項: {param_config['options']}")
            
            # 測試選項解析
            options = param_config['options']
            for option in options:
                print(f"    - {option['value']}: {option['label']}")
    
    # 測試策略執行
    print("\n=== 測試策略執行 ===")
    test_data = [{'close': 100, 'volume': 1000}]
    
    # 使用預設參數執行
    print("使用預設參數執行:")
    result = strategy.should_entry(test_data)
    print(f"進場結果: {result}")
    
    # 使用自訂參數執行
    print("\n使用自訂參數執行:")
    custom_params = {'action': 'sell', 'strategy_type': 'breakout'}
    result = strategy.should_entry(test_data, **custom_params)
    print(f"進場結果: {result}")
    
    print("\n=== 測試完成 ===")

def test_parameter_parsing():
    """測試參數解析功能"""
    
    print("=== 測試參數解析 ===")
    
    # 測試選項字串解析
    options_string = "buy:買入;sell:賣出;hold:持有"
    options = options_string.split(';')
    
    parsed_options = []
    for opt in options:
        if ':' in opt:
            value, label = opt.split(':', 1)
            parsed_options.append({
                'value': value.strip(),
                'label': label.strip()
            })
    
    print(f"原始字串: {options_string}")
    print(f"解析結果: {parsed_options}")
    
    # 測試參數值獲取
    test_params = {
        'action': 'sell',
        'strategy_type': 'momentum'
    }
    
    print(f"\n測試參數值獲取:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_select_parameter()
    test_parameter_parsing() 