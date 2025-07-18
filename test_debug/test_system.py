#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統測試檔案
用於測試回測系統的各項功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import polars as pl
from datetime import datetime, timedelta
import tempfile
import os

# 導入系統模組
from config.trading_config import TradingConfig
from strategies.day_trading import DayTradingStrategy
from strategies.swing_trading import SwingTradingStrategy
from strategies.bookbuilding import BookbuildingStrategy
from core.utils import Utils
from core.price_utils import PriceUtils

def test_strategy_configs():
    """測試策略配置"""
    print("=== 測試策略配置 ===")
    
    strategies = TradingConfig.get_available_strategies()
    print(f"可用策略: {strategies}")
    
    for strategy in strategies:
        config = TradingConfig.get_strategy_config(strategy)
        print(f"\n策略: {strategy}")
        print(f"  名稱: {config.get('name', 'N/A')}")
        print(f"  描述: {config.get('description', 'N/A')}")
        print(f"  資料來源: {config.get('data_source', 'N/A')}")
        print(f"  股票來源: {config.get('stock_source', 'N/A')}")
        print(f"  需要日期範圍: {config.get('need_date_range', False)}")

def create_test_data():
    """創建測試資料"""
    print("\n=== 創建測試資料 ===")
    
    # 創建模擬股票資料
    dates = []
    prices = []
    
    base_price = 100.0
    current_date = datetime(2024, 1, 1)
    
    for i in range(30):  # 30天的資料
        dates.append(current_date)
        
        # 模擬價格變化
        change = (i % 7 - 3) * 2  # 週期性變化
        price = base_price + change
        
        prices.append({
            'date': current_date,
            'open': price,
            'high': price + 3,
            'low': price - 2,
            'close': price + 1,
            'volume': 1000000 + i * 10000
        })
        
        current_date += timedelta(days=1)
    
    # 創建DataFrame
    df = pl.DataFrame(prices)
    print(f"測試資料創建完成，共 {len(df)} 筆記錄")
    print(f"資料欄位: {df.columns}")
    
    return df

def test_day_trading_strategy():
    """測試當沖策略"""
    print("\n=== 測試當沖策略 ===")
    
    # 創建測試資料
    test_data = create_test_data()
    
    # 創建策略實例
    parameters = {
        "use_limit_orders": True,
        "max_holding_time": 1,
        "force_exit": True
    }
    
    strategy = DayTradingStrategy(parameters)
    
    # 執行回測
    initial_capital = 1000000
    strategy.run_backtest(test_data, initial_capital, "2330", "台積電")
    
    # 取得結果
    result = strategy.get_strategy_result(initial_capital)
    
    print(f"總交易次數: {result.total_trades}")
    print(f"獲利交易: {result.winning_trades}")
    print(f"虧損交易: {result.losing_trades}")
    print(f"勝率: {result.win_rate:.2f}%")
    print(f"總損益: {result.total_profit_loss:,.0f}")
    print(f"總損益率: {result.total_profit_loss_rate:.2f}%")

def test_swing_trading_strategy():
    """測試波段策略"""
    print("\n=== 測試波段策略 ===")
    
    # 創建測試資料
    test_data = create_test_data()
    
    # 創建策略實例
    parameters = {
        "take_profit": 0.1,  # 10%停利
        "stop_loss": -0.05,  # -5%停損
        "max_holding_days": 20,
        "force_exit": True,
        "high_period": 10
    }
    
    strategy = SwingTradingStrategy(parameters)
    
    # 執行回測
    initial_capital = 1000000
    strategy.run_backtest(test_data, initial_capital, "2330", "台積電")
    
    # 取得結果
    result = strategy.get_strategy_result(initial_capital)
    
    print(f"總交易次數: {result.total_trades}")
    print(f"獲利交易: {result.winning_trades}")
    print(f"虧損交易: {result.losing_trades}")
    print(f"勝率: {result.win_rate:.2f}%")
    print(f"總損益: {result.total_profit_loss:,.0f}")
    print(f"總損益率: {result.total_profit_loss_rate:.2f}%")

def test_bookbuilding_strategy():
    """測試詢圈公告策略"""
    print("\n=== 測試詢圈公告策略 ===")
    
    # 創建測試資料
    test_data = create_test_data()
    
    # 創建策略實例
    parameters = {
        "announcement_delay": 1,
        "position_size": 0.1,
        "max_holding_days": 15
    }
    
    strategy = BookbuildingStrategy(parameters)
    
    # 執行回測
    initial_capital = 1000000
    strategy.run_backtest(test_data, initial_capital, "2330", "台積電")
    
    # 取得結果
    result = strategy.get_strategy_result(initial_capital)
    
    print(f"總交易次數: {result.total_trades}")
    print(f"獲利交易: {result.winning_trades}")
    print(f"虧損交易: {result.losing_trades}")
    print(f"勝率: {result.win_rate:.2f}%")
    print(f"總損益: {result.total_profit_loss:,.0f}")
    print(f"總損益率: {result.total_profit_loss_rate:.2f}%")

def test_excel_operations():
    """測試Excel操作"""
    print("\n=== 測試Excel操作 ===")
    
    # 創建測試資料
    test_data = create_test_data()
    
    # 添加股票代碼欄位
    test_data = test_data.with_columns(pl.lit("2330").alias("stock_id"))
    
    # 創建臨時檔案
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        # 儲存Excel檔案
        Utils.save_excel_file(test_data, temp_path, "測試資料")
        print(f"Excel檔案已儲存: {temp_path}")
        
        # 讀取Excel檔案
        loaded_data = Utils.read_excel_file(temp_path)
        print(f"Excel檔案已讀取，資料筆數: {len(loaded_data)}")
        
        # 驗證資料
        required_columns = ["stock_id", "date", "open", "high", "low", "close"]
        Utils.validate_stock_data(loaded_data, required_columns)
        print("資料驗證通過")
        
    finally:
        # 清理臨時檔案
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("臨時檔案已清理")

def test_price_utils():
    """測試價格工具"""
    print("\n=== 測試價格工具 ===")
    
    base_price = 100.0
    
    # 測試漲跌停價格計算
    up_limit, down_limit = PriceUtils.calculate_up_down_limit_prices(base_price)
    print(f"基準價格: {base_price}")
    print(f"漲停價格: {up_limit}")
    print(f"跌停價格: {down_limit}")
    
    # 測試股數計算
    capital = 100000
    shares = PriceUtils.calculate_shares(capital, base_price, "整股")
    print(f"資金: {capital:,}")
    print(f"可買股數: {shares:,}")
    
    # 測試損益計算
    entry_price = 100.0
    exit_price = 110.0
    profit = PriceUtils.calculate_profit_loss(entry_price, exit_price, shares, 1)
    profit_rate = PriceUtils.calculate_profit_loss_rate(entry_price, exit_price, 1)
    print(f"進場價格: {entry_price}")
    print(f"出場價格: {exit_price}")
    print(f"損益: {profit:,.0f}")
    print(f"損益率: {profit_rate:.2f}%")

def test_strategy_excel_processing():
    """測試策略參數處理功能"""
    print("\n=== 測試策略參數處理功能 ===")
    
    # 建立測試資料
    test_data = pl.DataFrame({
        "stock_id": ["2330", "2317", "2330", "2317"],
        "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"]
    })
    
    # 測試當沖策略
    print("測試當沖策略參數處理...")
    day_trading = DayTradingStrategy({
        "use_limit_orders": True,
        "max_holding_time": 1,
        "force_exit": False
    })
    
    try:
        parameters = {
            "excel_data": test_data,
            "strategy_params": {
                "use_limit_orders": True,
                "max_holding_time": 1,
                "force_exit": False
            }
        }
        result = day_trading.process_parameters(parameters)
        print(f"✓ 當沖策略處理成功")
        print(f"  股票代碼: {result['stock_ids']}")
        print(f"  開始日期: {result['start_date']}")
        print(f"  結束日期: {result['end_date']}")
    except Exception as e:
        print(f"✗ 當沖策略處理失敗: {e}")
    
    # 測試波段策略
    print("\n測試波段策略參數處理...")
    swing_trading = SwingTradingStrategy({
        "take_profit": 0.2,
        "stop_loss": -0.2,
        "max_holding_days": 30,
        "force_exit": True,
        "high_period": 20
    })
    
    try:
        parameters = {
            "excel_data": test_data,
            "strategy_params": {
                "take_profit": 0.2,
                "stop_loss": -0.2,
                "max_holding_days": 30,
                "force_exit": True,
                "high_period": 20
            }
        }
        result = swing_trading.process_parameters(parameters)
        print(f"✓ 波段策略處理成功")
        print(f"  股票代碼: {result['stock_ids']}")
        print(f"  開始日期: {result['start_date']}")
        print(f"  結束日期: {result['end_date']}")
    except Exception as e:
        print(f"✗ 波段策略處理失敗: {e}")
    
    # 測試詢圈公告策略
    print("\n測試詢圈公告策略參數處理...")
    bookbuilding = BookbuildingStrategy({
        "announcement_delay": 1,
        "position_size": 0.1,
        "max_holding_days": 30
    })
    
    try:
        parameters = {
            "excel_data": test_data,
            "strategy_params": {
                "announcement_delay": 1,
                "position_size": 0.1,
                "max_holding_days": 30
            },
            "start_year": "112",
            "end_year": "113"
        }
        result = bookbuilding.process_parameters(parameters)
        print(f"✓ 詢圈公告策略處理成功")
        print(f"  股票代碼: {result['stock_ids']}")
        print(f"  開始日期: {result['start_date']}")
        print(f"  結束日期: {result['end_date']}")
    except Exception as e:
        print(f"✗ 詢圈公告策略處理失敗: {e}")

def main():
    """主測試函數"""
    print("台灣股票回測系統測試")
    print("=" * 50)
    
    try:
        # 測試策略配置
        test_strategy_configs()
        
        # 測試價格工具
        test_price_utils()
        
        # 測試Excel操作
        test_excel_operations()
        
        # 測試策略Excel處理
        test_strategy_excel_processing()
        
        # 測試當沖策略
        test_day_trading_strategy()
        
        # 測試波段策略
        test_swing_trading_strategy()
        
        # 測試詢圈公告策略
        test_bookbuilding_strategy()
        
        print("\n" + "=" * 50)
        print("所有測試完成！")
        
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 