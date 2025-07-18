#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試動態參數系統
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.dynamic_strategy import DynamicStrategy

def test_dynamic_parameters():
    """測試動態參數系統"""
    print("=== 測試動態參數系統 ===")
    
    # 測試策略程式碼
    test_code = '''
def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    """判斷是否應該進場"""
    current_row = stock_data.row(current_index, named=True)
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    return False, {}

def should_exit(stock_data, current_index, position, **kwargs):
    """判斷是否應該出場"""
    # 從動態參數中取得持有天數
    holding_days = kwargs.get('holding_days', 0)
    max_holding_days = kwargs.get('max_holding_days', 5)
    max_loss_rate = kwargs.get('max_loss_rate', 5.0)
    
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
        "type": "dynamic",  # 動態參數類型
        "label": "持有天數",
        "default": 0,       # 初始值
        "increment": 1,     # 每次不出場時增加的值
        "description": "動態追蹤持有天數，出場時重置為0"
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
    
    # 建立策略實例
    strategy = DynamicStrategy(
        parameters={
            "max_holding_days": 3,
            "max_loss_rate": 3.0
        },
        strategy_code=test_code,
        strategy_name="動態參數測試策略"
    )
    
    print("✅ 策略建立成功")
    print(f"動態參數: {strategy.dynamic_parameters}")
    
    # 測試動態參數操作
    print("\n=== 測試動態參數操作 ===")
    
    # 初始值
    holding_days = strategy.get_dynamic_parameter('holding_days')
    print(f"初始持有天數: {holding_days}")
    
    # 模擬不出場的情況（增加持有天數）
    print("\n模擬不出場的情況:")
    for i in range(3):
        strategy.increment_dynamic_parameter('holding_days')
        current_days = strategy.get_dynamic_parameter('holding_days')
        print(f"第{i+1}次不出場後，持有天數: {current_days}")
    
    # 模擬出場的情況（重置持有天數）
    print("\n模擬出場的情況:")
    strategy.reset_dynamic_parameter('holding_days')
    current_days = strategy.get_dynamic_parameter('holding_days')
    print(f"出場後，持有天數重置為: {current_days}")
    
    # 測試參數歷史
    print("\n=== 測試參數歷史 ===")
    history = strategy.get_parameter_history('holding_days')
    print(f"參數變更歷史: {len(history)} 次變更")
    for i, record in enumerate(history):
        print(f"  變更{i+1}: {record['old_value']} -> {record['new_value']}")
    
    print("\n🎉 動態參數系統測試完成！")

if __name__ == "__main__":
    try:
        test_dynamic_parameters()
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc() 