#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試參數值提取修正
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.dynamic_strategy import DynamicStrategy

def test_parameter_value_extraction():
    """測試參數值提取"""
    print("=== 測試參數值提取修正 ===")
    
    # 測試策略程式碼
    test_code = '''
def should_exit(stock_data, current_index, position, **kwargs):
    """判斷是否應該出場"""
    # 從動態參數中取得持有天數
    holding_days = kwargs.get('holding_days', 0)
    max_holding_days = kwargs.get('max_holding_days', 5)
    max_loss_rate = kwargs.get('max_loss_rate', 5.0)
    
    print(f"DEBUG: holding_days={holding_days}, type={type(holding_days)}")
    print(f"DEBUG: max_holding_days={max_holding_days}, type={type(max_holding_days)}")
    print(f"DEBUG: max_loss_rate={max_loss_rate}, type={type(max_loss_rate)}")
    
    # 檢查參數類型
    if isinstance(max_holding_days, dict):
        print(f"ERROR: max_holding_days 是字典: {max_holding_days}")
        return False, {"reason": "參數類型錯誤"}
    
    current_row = stock_data.row(current_index, named=True)
    entry_price = position["entry_price"]
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    # 檢查出場條件
    if holding_days >= max_holding_days:
        return True, {"reason": f"持有{holding_days}天，超過{max_holding_days}天限制"}
    
    if loss_rate <= -max_loss_rate:
        return True, {"reason": f"虧損{loss_rate:.2f}%，超過{max_loss_rate}%限制"}
    
    # 不出場，系統會自動增加 holding_days
    return False, {}

# 動態參數配置
custom_parameters = {
    "holding_days": {
        "type": "dynamic",
        "label": "持有天數",
        "default": 0,
        "increment": 1,
        "description": "動態追蹤持有天數"
    },
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 5,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數限制"
    },
    "max_loss_rate": {
        "type": "number",
        "label": "最大虧損率",
        "default": 5.0,
        "min": 1.0,
        "max": 20.0,
        "step": 0.5,
        "description": "最大虧損率百分比"
    }
}
'''
    
    # 測試案例1：參數是簡單數值
    print("\n=== 測試案例1：參數是簡單數值 ===")
    strategy1 = DynamicStrategy(
        parameters={
            "max_holding_days": 3,
            "max_loss_rate": 3.0
        },
        strategy_code=test_code,
        strategy_name="測試策略1"
    )
    
    # 測試參數值提取
    max_holding_days = strategy1.get_parameter_value('max_holding_days')
    max_loss_rate = strategy1.get_parameter_value('max_loss_rate')
    
    print(f"max_holding_days: {max_holding_days}, type: {type(max_holding_days)}")
    print(f"max_loss_rate: {max_loss_rate}, type: {type(max_loss_rate)}")
    
    # 測試案例2：參數是字典配置
    print("\n=== 測試案例2：參數是字典配置 ===")
    strategy2 = DynamicStrategy(
        parameters={
            "max_holding_days": {
                "type": "number",
                "default": 7,
                "min": 1,
                "max": 30
            },
            "max_loss_rate": {
                "type": "number", 
                "default": 4.0,
                "min": 1.0,
                "max": 20.0
            }
        },
        strategy_code=test_code,
        strategy_name="測試策略2"
    )
    
    # 測試參數值提取
    max_holding_days = strategy2.get_parameter_value('max_holding_days')
    max_loss_rate = strategy2.get_parameter_value('max_loss_rate')
    
    print(f"max_holding_days: {max_holding_days}, type: {type(max_holding_days)}")
    print(f"max_loss_rate: {max_loss_rate}, type: {type(max_loss_rate)}")
    
    # 測試案例3：參數不存在，使用預設值
    print("\n=== 測試案例3：參數不存在，使用預設值 ===")
    strategy3 = DynamicStrategy(
        parameters={},
        strategy_code=test_code,
        strategy_name="測試策略3"
    )
    
    # 測試參數值提取
    max_holding_days = strategy3.get_parameter_value('max_holding_days')
    max_loss_rate = strategy3.get_parameter_value('max_loss_rate')
    
    print(f"max_holding_days: {max_holding_days}, type: {type(max_holding_days)}")
    print(f"max_loss_rate: {max_loss_rate}, type: {type(max_loss_rate)}")
    
    print("\n🎉 參數值提取測試完成！")

if __name__ == "__main__":
    try:
        test_parameter_value_extraction()
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc() 