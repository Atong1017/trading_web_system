#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的參數管理系統
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.strategy_manager import StrategyManager

def test_parameter_extraction():
    """測試參數提取功能"""
    print("=== 測試參數提取功能 ===")
    
    # 測試策略程式碼
    test_code = '''
# 自定義策略模板
def should_entry(stock_data, current_index, excel_pl_df):
    return True, {"reason": "測試"}

def should_exit(stock_data, current_index, position):
    return False, {}

# 自定義參數配置
custom_parameters = {
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 5,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數"
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
    
    # 建立策略管理器
    strategy_manager = StrategyManager()
    
    # 測試參數提取
    extracted_params = strategy_manager._extract_custom_parameters(test_code)
    print(f"提取的參數: {extracted_params}")
    
    assert "max_holding_days" in extracted_params
    assert "max_loss_rate" in extracted_params
    assert extracted_params["max_holding_days"]["type"] == "number"
    assert extracted_params["max_loss_rate"]["default"] == 5.0
    
    print("✅ 參數提取測試通過")

def test_strategy_creation_with_parameters():
    """測試帶參數的策略建立"""
    print("\n=== 測試帶參數的策略建立 ===")
    
    strategy_manager = StrategyManager()
    
    # 測試策略程式碼
    test_code = '''
def should_entry(stock_data, current_index, excel_pl_df):
    return True, {"reason": "測試"}

def should_exit(stock_data, current_index, position):
    return False, {}

custom_parameters = {
    "test_param": {
        "type": "number",
        "label": "測試參數",
        "default": 10,
        "min": 0,
        "max": 100,
        "step": 1,
        "description": "這是一個測試參數"
    }
}
'''
    
    # 建立策略
    strategy_id = strategy_manager.create_strategy(
        name="測試策略",
        description="這是一個測試策略",
        code=test_code
    )
    
    print(f"建立的策略ID: {strategy_id}")
    
    # 取得策略資訊
    strategy_info = strategy_manager.get_strategy(strategy_id)
    print(f"策略參數: {strategy_info['parameters']}")
    
    assert "test_param" in strategy_info["parameters"]
    assert strategy_info["parameters"]["test_param"]["default"] == 10
    
    print("✅ 策略建立測試通過")
    
    # 清理測試資料
    strategy_manager.delete_strategy(strategy_id)

def test_strategy_update_with_parameters():
    """測試帶參數的策略更新"""
    print("\n=== 測試帶參數的策略更新 ===")
    
    strategy_manager = StrategyManager()
    
    # 建立初始策略
    initial_code = '''
def should_entry(stock_data, current_index, excel_pl_df):
    return True, {"reason": "測試"}

def should_exit(stock_data, current_index, position):
    return False, {}
'''
    
    strategy_id = strategy_manager.create_strategy(
        name="更新測試策略",
        description="這是一個更新測試策略",
        code=initial_code
    )
    
    # 更新策略，加入參數
    updated_code = '''
def should_entry(stock_data, current_index, excel_pl_df):
    return True, {"reason": "測試"}

def should_exit(stock_data, current_index, position):
    return False, {}

custom_parameters = {
    "updated_param": {
        "type": "number",
        "label": "更新參數",
        "default": 20,
        "min": 0,
        "max": 50,
        "step": 1,
        "description": "這是一個更新後的參數"
    }
}
'''
    
    # 更新策略
    success = strategy_manager.update_strategy(
        strategy_id=strategy_id,
        code=updated_code
    )
    
    assert success
    
    # 檢查更新結果
    strategy_info = strategy_manager.get_strategy(strategy_id)
    print(f"更新後的策略參數: {strategy_info['parameters']}")
    
    assert "updated_param" in strategy_info["parameters"]
    assert strategy_info["parameters"]["updated_param"]["default"] == 20
    
    print("✅ 策略更新測試通過")
    
    # 清理測試資料
    strategy_manager.delete_strategy(strategy_id)

def test_parameter_priority():
    """測試參數優先級"""
    print("\n=== 測試參數優先級 ===")
    
    strategy_manager = StrategyManager()
    
    # 程式碼中的參數
    code_with_params = '''
def should_entry(stock_data, current_index, excel_pl_df):
    return True, {"reason": "測試"}

def should_exit(stock_data, current_index, position):
    return False, {}

custom_parameters = {
    "code_param": {
        "type": "number",
        "label": "程式碼參數",
        "default": 100,
        "description": "來自程式碼的參數"
    }
}
'''
    
    # 外部傳入的參數
    external_params = {
        "external_param": {
            "type": "number",
            "label": "外部參數",
            "default": 200,
            "description": "來自外部的參數"
        },
        "code_param": {  # 同名參數，應該被程式碼中的覆蓋
            "type": "number",
            "label": "外部程式碼參數",
            "default": 300,
            "description": "來自外部的同名參數"
        }
    }
    
    # 建立策略
    strategy_id = strategy_manager.create_strategy(
        name="優先級測試策略",
        description="測試參數優先級",
        code=code_with_params,
        parameters=external_params
    )
    
    # 檢查結果
    strategy_info = strategy_manager.get_strategy(strategy_id)
    final_params = strategy_info["parameters"]
    
    print(f"最終參數: {final_params}")
    
    # 程式碼中的參數應該優先
    assert final_params["code_param"]["default"] == 100  # 程式碼中的值
    assert final_params["external_param"]["default"] == 200  # 外部參數
    
    print("✅ 參數優先級測試通過")
    
    # 清理測試資料
    strategy_manager.delete_strategy(strategy_id)

if __name__ == "__main__":
    try:
        test_parameter_extraction()
        test_strategy_creation_with_parameters()
        test_strategy_update_with_parameters()
        test_parameter_priority()
        
        print("\n🎉 所有測試通過！新的參數管理系統運作正常。")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc() 