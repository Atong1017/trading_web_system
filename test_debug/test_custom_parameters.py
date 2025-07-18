#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試自定義參數解析
"""

import ast
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.dynamic_strategy import DynamicStrategy

def test_custom_parameters_parsing():
    """測試自定義參數解析"""
    print("=== 測試自定義參數解析 ===")
    
    # 您的策略程式碼
    strategy_code = '''# 自定義策略模板
# 請實作以下函數來定義您的策略邏輯

def breaking_high(stock_data, current_index):
    """
    判斷是否為20日新高
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        excel_pl_excel:Excel股票列表 (polars DataFrame)
        
    Returns:
        bool:True(進場)
    """
    prev_close_list = stock_data['close'][current_index - 20:current_index - 1].to_list()
    if stock_data['close'][current_index - 1] > max(prev_close_list):
        return True
    
def should_entry(stock_data, current_index, excel_pl_df):
    """
    判斷是否應該進場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        excel_pl_excel:Excel股票列表 (polars DataFrame)
        
    Returns:
        tuple: (是否進場, 進場資訊)
    """
    # 範例：當收盤價大於開盤價時進場
    current_row = stock_data.row(current_index)
    excel_date = excel_pl_df['date'][0]  # excel中股票的日期
    breaking_high_close = False
    
    if excel_date <= current_row['date']:        
        breaking_high_close = breaking_high(stock_data, current_index)
    
    if breaking_high_close:
        return True, {"reason": "突破20日新高"}
    
    return False, {}

def should_exit(stock_data, current_index, position):
    """
    判斷是否應該出場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        position: 當前持倉資訊
        
    Returns:
        tuple: (是否出場, 出場資訊)
    """
    # 範例：持有超過5天或虧損超過5%時出場
    current_row = stock_data.row(current_index)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    # 計算持有天數
    entry_row = stock_data.row(entry_index)
    holding_days = (current_row["date"] - entry_row["date"]).days
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 5 or loss_rate <= -5:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    
    return False, {}

# 可選：自定義參數配置
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


# 可選：自定義參數處理函數
def process_parameters(parameters):
    """
    處理策略參數
    
    Args:
        parameters: 輸入參數
        
    Returns:
        dict: 處理後的參數
    """
    # 在這裡處理參數邏輯
    return parameters

# 可選：自定義驗證函數
def validate_parameters(parameters):
    """
    驗證策略參數
    
    Args:
        parameters: 策略參數
        
    Raises:
        ValueError: 當參數無效時
    """
    # 在這裡驗證參數
    pass
'''
    
    try:
        # 檢查語法
        print("1. 檢查語法...")
        ast.parse(strategy_code)
        print("   ✓ 語法正確")
        
        # 建立策略實例
        print("2. 建立策略實例...")
        strategy = DynamicStrategy({}, strategy_code, "測試策略")
        print("   ✓ 策略實例建立成功")
        
        # 檢查自定義參數
        print("3. 檢查自定義參數...")
        if hasattr(strategy, 'custom_parameters'):
            print(f"   ✓ 找到 custom_parameters: {strategy.custom_parameters}")
        else:
            print("   ✗ 未找到 custom_parameters")
        
        # 檢查策略參數
        print("4. 檢查策略參數...")
        strategy_params = strategy.strategy_parameters
        print(f"   ✓ 策略參數: {list(strategy_params.keys())}")
        
        # 檢查是否有自定義參數
        custom_param_keys = [k for k in strategy_params.keys() if k not in ['commission_rate', 'commission_discount', 'securities_tax_rate', 'shares_per_trade']]
        if custom_param_keys:
            print(f"   ✓ 自定義參數: {custom_param_keys}")
        else:
            print("   ✗ 未找到自定義參數")
        
        # 測試參數值取得
        print("5. 測試參數值取得...")
        max_holding_days = strategy.get_parameter_value("max_holding_days")
        max_loss_rate = strategy.get_parameter_value("max_loss_rate")
        print(f"   ✓ max_holding_days: {max_holding_days}")
        print(f"   ✓ max_loss_rate: {max_loss_rate}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_extraction():
    """測試參數提取"""
    print("\n=== 測試參數提取 ===")
    
    # 模擬從策略程式碼中提取 custom_parameters
    strategy_code = '''# 測試策略
custom_parameters = {
    "test_param": {
        "type": "number",
        "label": "測試參數",
        "default": 10,
        "min": 1,
        "max": 100,
        "step": 1,
        "description": "測試參數描述"
    }
}

def should_entry(stock_data, current_index):
    return False, {}
'''
    
    try:
        # 建立執行環境
        exec_globals = {}
        exec(strategy_code, exec_globals)
        
        # 檢查是否有 custom_parameters
        if 'custom_parameters' in exec_globals:
            custom_params = exec_globals['custom_parameters']
            print(f"✓ 成功提取 custom_parameters: {custom_params}")
            return True
        else:
            print("✗ 未找到 custom_parameters")
            return False
            
    except Exception as e:
        print(f"✗ 提取失敗: {e}")
        return False

if __name__ == "__main__":
    print("開始測試自定義參數解析...")
    
    success1 = test_custom_parameters_parsing()
    success2 = test_parameter_extraction()
    
    if success1 and success2:
        print("\n✓ 所有測試通過")
    else:
        print("\n✗ 部分測試失敗") 