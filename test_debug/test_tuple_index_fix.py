#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試 tuple index 錯誤修正
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from datetime import datetime, timedelta
from strategies.dynamic_strategy import DynamicStrategy

def create_test_data():
    """建立測試資料"""
    dates = []
    prices = []
    
    # 建立 30 天的測試資料
    start_date = datetime(2024, 1, 1)
    for i in range(30):
        date = start_date + timedelta(days=i)
        dates.append(date)
        
        # 模擬股價波動
        base_price = 100 + i * 0.5
        open_price = base_price + (i % 3 - 1) * 2
        high_price = open_price + 3
        low_price = open_price - 2
        close_price = open_price + (i % 5 - 2) * 1.5
        
        prices.append({
            'date': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000000 + i * 10000
        })
    
    return pl.DataFrame(prices)

def test_dynamic_strategy():
    """測試動態策略"""
    print("=== 測試動態策略 tuple index 修正 ===")
    
    # 建立測試資料
    test_data = create_test_data()
    print(f"測試資料行數: {len(test_data)}")
    print(f"測試資料欄位: {test_data.columns}")
    
    # 建立簡單的策略程式碼
    strategy_code = """
def should_entry(stock_data, current_index):
    # 簡單的進場邏輯：每5天進場一次
    return current_index % 5 == 0, {"entry_price": stock_data.row(current_index, named=True)["open"]}

def should_exit(stock_data, current_index, position):
    # 簡單的出場邏輯：持有3天後出場
    holding_days = current_index - position["entry_index"]
    return holding_days >= 3, {"reason": "持有期滿"}
"""
    
    # 建立策略實例
    parameters = {
        "commission_rate": 0.001425,
        "commission_discount": 0.3,
        "securities_tax_rate": 0.0015,
        "shares_per_trade": 1000
    }
    
    try:
        strategy = DynamicStrategy(parameters, strategy_code, "測試策略")
        print("✓ 策略實例建立成功")
        
        # 執行回測
        initial_capital = 1000000
        print("開始執行回測...")
        
        strategy.run_backtest(test_data, initial_capital, "TEST", "測試股票")
        print("✓ 回測執行成功")
        
        # 取得結果
        result = strategy.get_strategy_result(initial_capital)
        print("✓ 結果取得成功")
        
        print(f"總交易次數: {result['total_trades']}")
        print(f"勝率: {result['win_rate']:.2f}%")
        print(f"總損益: {result['total_profit_loss']:,.0f}")
        print(f"總損益率: {result['total_profit_loss_rate']:.2f}%")
        
        print("\n=== 測試完成 ===")
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dynamic_strategy()
    if success:
        print("所有測試通過！")
    else:
        print("測試失敗！") 