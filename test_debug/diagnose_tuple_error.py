#!/usr/bin/env python3
"""
診斷 tuple 索引錯誤的具體位置
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import polars as pl
from datetime import datetime, timedelta
from strategies.dynamic_strategy import DynamicStrategy

def create_test_data():
    """創建測試資料"""
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

def test_without_named_true():
    """測試沒有 named=True 的情況"""
    print("測試沒有 named=True 的情況...")
    
    stock_data = create_test_data()
    
    # 測試沒有 named=True 的 row() 調用
    try:
        row = stock_data.row(0)  # 沒有 named=True
        print(f"row 類型: {type(row)}")
        print(f"row 內容: {row}")
        
        # 嘗試用字串索引
        close_price = row["close"]
        print(f"close 價格: {close_price}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        print("這證明了沒有 named=True 會導致 tuple 索引錯誤")

def test_with_named_true():
    """測試有 named=True 的情況"""
    print("\n測試有 named=True 的情況...")
    
    stock_data = create_test_data()
    
    try:
        row = stock_data.row(0, named=True)  # 有 named=True
        print(f"row 類型: {type(row)}")
        print(f"row 內容: {row}")
        
        # 嘗試用字串索引
        close_price = row["close"]
        print(f"close 價格: {close_price}")
        print("✅ 成功使用字串索引")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")

def test_strategy_execution():
    """測試策略執行"""
    print("\n測試策略執行...")
    
    try:
        # 創建測試資料
        stock_data = create_test_data()
        print(f"✅ 創建測試資料成功，共 {len(stock_data)} 筆")
        
        # 創建策略程式碼 - 故意使用錯誤的寫法
        wrong_code = """
def should_entry(stock_data, current_index):
    current_row = stock_data.row(current_index)  # 沒有 named=True
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    return False, {}

def should_exit(stock_data, current_index, position):
    current_row = stock_data.row(current_index)  # 沒有 named=True
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    entry_row = stock_data.row(entry_index)  # 沒有 named=True
    holding_days = (current_row["date"] - entry_row["date"]).days
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 3 or loss_rate <= -3:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    return False, {}
"""
        
        # 創建動態策略實例
        parameters = {
            "commission_rate": 0.001425,
            "commission_discount": 0.3,
            "securities_tax_rate": 0.0015,
            "shares_per_trade": 1000
        }
        
        strategy = DynamicStrategy(parameters, wrong_code, "錯誤策略")
        print("✅ 創建動態策略實例成功")
        
        # 測試策略函數 - 這應該會出錯
        print("\n測試 should_entry 函數...")
        should_entry, entry_info = strategy.should_entry(stock_data, 0)
        print(f"should_entry(0): {should_entry}, {entry_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ 策略執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("開始診斷 tuple 索引錯誤")
    print("=" * 50)
    
    # 1. 測試沒有 named=True 的情況
    test_without_named_true()
    
    # 2. 測試有 named=True 的情況
    test_with_named_true()
    
    # 3. 測試策略執行
    test_strategy_execution()
    
    print("\n" + "=" * 50)
    print("診斷完成")

if __name__ == "__main__":
    main() 