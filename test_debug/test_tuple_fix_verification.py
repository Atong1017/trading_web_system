#!/usr/bin/env python3
"""
驗證 tuple 索引錯誤修復
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import polars as pl
from datetime import datetime, timedelta
from strategies.dynamic_strategy import DynamicStrategy

def create_test_data():
    """創建測試資料"""
    # 創建測試股價資料
    dates = [datetime.now() + timedelta(days=i) for i in range(10)]
    data = {
        "date": dates,
        "open": [100 + i for i in range(10)],
        "high": [105 + i for i in range(10)],
        "low": [95 + i for i in range(10)],
        "close": [102 + i for i in range(10)],
        "volume": [1000000 + i * 100000 for i in range(10)]
    }
    
    return pl.DataFrame(data)

def test_strategy_code():
    """測試策略程式碼"""
    # 創建測試策略程式碼
    strategy_code = """
def should_entry(stock_data, current_index):
    current_row = stock_data.row(current_index, named=True)
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    return False, {}

def should_exit(stock_data, current_index, position):
    current_row = stock_data.row(current_index, named=True)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    entry_row = stock_data.row(entry_index, named=True)
    holding_days = (current_row["date"] - entry_row["date"]).days
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 3 or loss_rate <= -3:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    return False, {}
"""
    
    return strategy_code

def test_dynamic_strategy():
    """測試動態策略"""
    print("測試動態策略...")
    
    try:
        # 創建測試資料
        stock_data = create_test_data()
        print(f"✅ 創建測試資料成功，共 {len(stock_data)} 筆")
        
        # 創建策略程式碼
        strategy_code = test_strategy_code()
        print("✅ 創建策略程式碼成功")
        
        # 創建動態策略實例
        parameters = {
            "commission_rate": 0.001425,
            "commission_discount": 0.3,
            "securities_tax_rate": 0.0015,
            "shares_per_trade": 1000
        }
        
        strategy = DynamicStrategy(parameters, strategy_code, "測試策略")
        print("✅ 創建動態策略實例成功")
        
        # 測試策略函數
        print("\n測試策略函數...")
        
        # 測試 should_entry
        should_entry, entry_info = strategy.should_entry(stock_data, 0)
        print(f"should_entry(0): {should_entry}, {entry_info}")
        
        # 測試 should_exit
        position = {
            "entry_index": 0,
            "entry_price": 100.0,
            "entry_date": stock_data.row(0, named=True)["date"]
        }
        should_exit, exit_info = strategy.should_exit(stock_data, 5, position)
        print(f"should_exit(5): {should_exit}, {exit_info}")
        
        # 測試回測
        print("\n測試回測...")
        strategy.run_backtest(stock_data, 100000, "2330", "台積電")
        
        # 取得回測結果
        results = strategy.get_strategy_result(100000)
        print(f"✅ 回測成功完成")
        print(f"總交易次數: {results['total_trades']}")
        print(f"總損益: {results['total_profit_loss']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("開始驗證 tuple 索引錯誤修復")
    print("=" * 50)
    
    success = test_dynamic_strategy()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 驗證成功！tuple 索引錯誤已修復")
    else:
        print("❌ 驗證失敗！仍有問題需要解決")

if __name__ == "__main__":
    main() 