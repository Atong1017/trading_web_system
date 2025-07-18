#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快取系統測試腳本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import polars as pl
from datetime import datetime, timedelta
from core.cache_manager import cache_manager
from api.stock_api import StockAPI

async def test_cache_system():
    """測試快取系統"""
    print("=== 快取系統測試 ===")
    
    # 1. 測試基本快取功能
    print("\n1. 測試基本快取功能")
    
    # 建立測試資料
    test_data = pl.DataFrame({
        "stock_id": ["2330", "2330", "2330"],
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "open": [100.0, 101.0, 102.0],
        "high": [105.0, 106.0, 107.0],
        "low": [98.0, 99.0, 100.0],
        "close": [103.0, 104.0, 105.0],
        "volume": [1000000, 1100000, 1200000]
    })
    
    # 儲存到快取
    success = cache_manager.set_cached_data(
        stock_id="2330",
        start_date="2024-01-01",
        end_date="2024-01-03",
        data=test_data,
        data_type="price",
        ttl_hours=1
    )
    
    print(f"儲存快取: {'成功' if success else '失敗'}")
    
    # 從快取讀取
    cached_data = cache_manager.get_cached_data(
        stock_id="2330",
        start_date="2024-01-01",
        end_date="2024-01-03",
        data_type="price"
    )
    
    if cached_data is not None:
        print(f"讀取快取: 成功，資料筆數: {len(cached_data)}")
        print(f"快取資料前3筆:\n{cached_data.head(3)}")
    else:
        print("讀取快取: 失敗")
    
    # 2. 測試快取資訊
    print("\n2. 測試快取資訊")
    cache_info = cache_manager.get_cache_info()
    print(f"記憶體使用量: {cache_info['memory_usage_mb']} MB")
    print(f"記憶體項目數: {cache_info['memory_items']}")
    print(f"檔案快取大小: {cache_info['file_cache_size_mb']} MB")
    print(f"總項目數: {cache_info['total_items']}")
    print(f"股票代碼: {cache_info['stock_ids']}")
    
    # 3. 測試快取檢查
    print("\n3. 測試快取檢查")
    is_cached = cache_manager.is_cached(
        stock_id="2330",
        start_date="2024-01-01",
        end_date="2024-01-03",
        data_type="price"
    )
    print(f"資料是否已快取: {is_cached}")
    
    # 4. 測試預載入功能
    print("\n4. 測試預載入功能")
    preload_results = cache_manager.preload_cache(
        stock_ids=["2330"],
        start_date="2024-01-01",
        end_date="2024-01-03",
        data_type="price"
    )
    print(f"預載入結果: {preload_results}")
    
    # 5. 測試清理功能
    print("\n5. 測試清理功能")
    
    # 清理過期快取
    success = cache_manager.clear_cache("expired")
    print(f"清理過期快取: {'成功' if success else '失敗'}")
    
    # 6. 測試與 StockAPI 整合
    print("\n6. 測試與 StockAPI 整合")
    
    # 建立 StockAPI 實例
    async with StockAPI() as stock_api:
        try:
            # 第一次請求（會從 API 取得並快取）
            print("第一次請求（從 API 取得）...")
            data1 = await stock_api.get_stock_price(
                stock_ids=["2330"],
                start_date="2024-01-01",
                end_date="2024-01-03",
                use_cache=True
            )
            print(f"第一次請求結果: {len(data1)} 筆資料")
            
            # 第二次請求（應該從快取取得）
            print("第二次請求（從快取取得）...")
            data2 = await stock_api.get_stock_price(
                stock_ids=["2330"],
                start_date="2024-01-01",
                end_date="2024-01-03",
                use_cache=True
            )
            print(f"第二次請求結果: {len(data2)} 筆資料")
            
            # 比較兩次請求的資料是否相同
            if len(data1) > 0 and len(data2) > 0:
                is_same = data1.equals(data2)
                print(f"兩次請求資料是否相同: {is_same}")
            
        except Exception as e:
            print(f"API 測試失敗: {e}")
    
    # 7. 最終快取資訊
    print("\n7. 最終快取資訊")
    final_cache_info = cache_manager.get_cache_info()
    print(f"記憶體使用量: {final_cache_info['memory_usage_mb']} MB")
    print(f"記憶體項目數: {final_cache_info['memory_items']}")
    print(f"檔案快取大小: {final_cache_info['file_cache_size_mb']} MB")
    print(f"總項目數: {final_cache_info['total_items']}")
    
    print("\n=== 測試完成 ===")

def test_strategy_manager():
    """測試策略管理器"""
    print("\n=== 策略管理器測試 ===")
    
    from strategies.strategy_manager import StrategyManager
    
    # 建立策略管理器
    manager = StrategyManager()
    
    # 1. 測試建立策略
    print("\n1. 測試建立策略")
    
    test_code = """
def should_entry(stock_data, current_index):
    current_row = stock_data[current_index]
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    return False, {}

def should_exit(stock_data, current_index, position):
    current_row = stock_data[current_index]
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    holding_days = (current_row["date"] - stock_data[entry_index]["date"]).days
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 5 or loss_rate <= -5:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    return False, {}
"""
    
    try:
        strategy_id = manager.create_strategy(
            name="測試策略",
            description="這是一個測試策略",
            code=test_code
        )
        print(f"建立策略成功，ID: {strategy_id}")
        
        # 2. 測試取得策略
        print("\n2. 測試取得策略")
        strategy = manager.get_strategy(strategy_id)
        if strategy:
            print(f"策略名稱: {strategy['name']}")
            print(f"策略描述: {strategy['description']}")
            print(f"程式碼長度: {len(strategy['code'])} 字元")
        
        # 3. 測試取得所有策略
        print("\n3. 測試取得所有策略")
        all_strategies = manager.get_all_strategies()
        print(f"總策略數: {len(all_strategies)}")
        
        # 4. 測試更新策略
        print("\n4. 測試更新策略")
        success = manager.update_strategy(
            strategy_id,
            name="更新後的測試策略",
            description="這是更新後的描述"
        )
        print(f"更新策略: {'成功' if success else '失敗'}")
        
        # 5. 測試驗證程式碼
        print("\n5. 測試驗證程式碼")
        is_valid = manager.validate_strategy_code(test_code)
        print(f"程式碼驗證: {'通過' if is_valid else '失敗'}")
        
        # 6. 測試建立策略實例
        print("\n6. 測試建立策略實例")
        strategy_instance = manager.create_strategy_instance(strategy_id)
        print(f"策略實例建立: {'成功' if strategy_instance else '失敗'}")
        if strategy_instance:
            print(f"策略名稱: {strategy_instance.strategy_name}")
        
        # 7. 測試刪除策略
        print("\n7. 測試刪除策略")
        success = manager.delete_strategy(strategy_id)
        print(f"刪除策略: {'成功' if success else '失敗'}")
        
    except Exception as e:
        print(f"策略管理器測試失敗: {e}")

if __name__ == "__main__":
    # 執行快取系統測試
    asyncio.run(test_cache_system())
    
    # 執行策略管理器測試
    test_strategy_manager() 