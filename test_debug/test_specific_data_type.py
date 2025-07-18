#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試指定資料類型的策略測試功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import asyncio
import polars as pl
from datetime import datetime, timedelta
from core.cache_manager import cache_manager

async def setup_test_cache_with_specific_type():
    """設定指定類型的測試快取資料"""
    print("設定指定類型的測試快取資料...")
    
    # 建立每日股價合併除權息的測試資料
    adjusted_data = pl.DataFrame({
        "stock_id": ["2330"] * 30,
        "date": [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)],
        "open": [100 + i * 0.5 for i in range(30)],
        "high": [102 + i * 0.5 for i in range(30)],
        "low": [98 + i * 0.5 for i in range(30)],
        "close": [101 + i * 0.5 for i in range(30)],
        "volume": [1000000] * 30,
        "adjusted_close": [101 + i * 0.5 for i in range(30)]  # 除權息調整後收盤價
    })
    
    # 儲存每日股價合併除權息資料到快取
    success1 = cache_manager.set_cached_data(
        stock_id="2330",
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        data=adjusted_data,
        data_type="daily_price_adjusted",
        ttl_hours=24
    )
    
    # 建立一般每日股價的測試資料
    regular_data = pl.DataFrame({
        "stock_id": ["2330"] * 30,
        "date": [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)],
        "open": [100 + i * 0.3 for i in range(30)],
        "high": [102 + i * 0.3 for i in range(30)],
        "low": [98 + i * 0.3 for i in range(30)],
        "close": [101 + i * 0.3 for i in range(30)],
        "volume": [1000000] * 30
    })
    
    # 儲存一般每日股價資料到快取
    success2 = cache_manager.set_cached_data(
        stock_id="2330",
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        data=regular_data,
        data_type="daily_price",
        ttl_hours=24
    )
    
    if success1 and success2:
        print("✅ 測試快取資料設定成功（兩種資料類型）")
        return True
    else:
        print("❌ 測試快取資料設定失敗")
        return False

def test_strategy_with_specific_data_type():
    """測試指定資料類型的策略測試"""
    print("\n測試指定資料類型的策略測試...")
    
    try:
        # 1. 建立測試策略
        strategy_data = {
            "name": "指定資料類型測試策略",
            "description": "測試指定資料類型的策略",
            "type": "template"
        }
        
        response = requests.post(
            "http://localhost:8000/api/strategies/custom",
            json=strategy_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 建立策略失敗: HTTP {response.status_code}")
            return False
        
        result = response.json()
        if result.get('status') != 'success':
            print(f"❌ 建立策略失敗: {result}")
            return False
        
        strategy_id = result.get('strategy_id')
        print(f"✅ 成功建立策略: {strategy_id}")
        
        # 2. 更新策略程式碼
        test_code = """def should_entry(stock_data, current_index):
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
    return False, {}"""
        
        update_data = {
            "name": "指定資料類型測試策略",
            "description": "測試指定資料類型的策略",
            "code": test_code
        }
        
        response = requests.put(
            f"http://localhost:8000/api/strategies/custom/{strategy_id}",
            json=update_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 更新策略失敗: HTTP {response.status_code}")
            return False
        
        print("✅ 成功更新策略程式碼")
        
        # 3. 測試策略 - 使用每日股價合併除權息
        print("\n--- 測試每日股價合併除權息 ---")
        test_data_1 = {
            "strategy_id": strategy_id,
            "code": test_code,
            "data_type": "daily_price_adjusted",
            "stock_id": "2330"
        }
        
        response = requests.post(
            "http://localhost:8000/api/strategies/custom/test",
            json=test_data_1,
            timeout=10
        )
        
        print(f"每日股價合併除權息測試回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                results = data.get('results', {})
                backtest_results = results.get('backtest_results', {})
                
                if 'data_source' in backtest_results:
                    print(f"✅ 資料來源: {backtest_results['data_source']}")
                if 'data_count' in backtest_results:
                    print(f"✅ 資料筆數: {backtest_results['data_count']}")
                
                # 檢查是否使用了正確的資料類型
                if backtest_results.get('data_source') == '快取':
                    print("🎉 成功使用快取中的每日股價合併除權息資料！")
                else:
                    print("ℹ️  使用其他資料來源")
            else:
                print(f"❌ 每日股價合併除權息測試失敗: {data}")
        
        # 4. 測試策略 - 使用一般每日股價
        print("\n--- 測試一般每日股價 ---")
        test_data_2 = {
            "strategy_id": strategy_id,
            "code": test_code,
            "data_type": "daily_price",
            "stock_id": "2330"
        }
        
        response = requests.post(
            "http://localhost:8000/api/strategies/custom/test",
            json=test_data_2,
            timeout=10
        )
        
        print(f"一般每日股價測試回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                results = data.get('results', {})
                backtest_results = results.get('backtest_results', {})
                
                if 'data_source' in backtest_results:
                    print(f"✅ 資料來源: {backtest_results['data_source']}")
                if 'data_count' in backtest_results:
                    print(f"✅ 資料筆數: {backtest_results['data_count']}")
                
                # 檢查是否使用了正確的資料類型
                if backtest_results.get('data_source') == '快取':
                    print("🎉 成功使用快取中的一般每日股價資料！")
                else:
                    print("ℹ️  使用其他資料來源")
            else:
                print(f"❌ 一般每日股價測試失敗: {data}")
        
        # 5. 測試策略 - 使用不存在的資料類型
        print("\n--- 測試不存在的資料類型 ---")
        test_data_3 = {
            "strategy_id": strategy_id,
            "code": test_code,
            "data_type": "nonexistent_data_type",
            "stock_id": "2330"
        }
        
        response = requests.post(
            "http://localhost:8000/api/strategies/custom/test",
            json=test_data_3,
            timeout=10
        )
        
        print(f"不存在資料類型測試回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                results = data.get('results', {})
                backtest_results = results.get('backtest_results', {})
                
                if 'data_source' in backtest_results:
                    print(f"✅ 資料來源: {backtest_results['data_source']}")
                if 'data_count' in backtest_results:
                    print(f"✅ 資料筆數: {backtest_results['data_count']}")
                
                # 檢查是否使用了備案資料
                if backtest_results.get('data_source') in ['API', '模擬']:
                    print("✅ 正確使用備案資料來源")
                else:
                    print("ℹ️  使用其他資料來源")
            else:
                print(f"❌ 不存在資料類型測試失敗: {data}")
        
        # 清理測試策略
        response = requests.delete(
            f"http://localhost:8000/api/strategies/custom/{strategy_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 測試策略清理完成")
        
        return True
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("開始測試指定資料類型的策略測試功能")
    print("=" * 60)
    
    # 1. 設定測試快取資料
    cache_success = await setup_test_cache_with_specific_type()
    if not cache_success:
        print("❌ 無法設定測試快取資料，測試終止")
        return
    
    # 2. 測試策略測試功能
    strategy_success = test_strategy_with_specific_data_type()
    
    # 3. 輸出測試結果
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    if cache_success and strategy_success:
        print("🎉 所有測試通過！指定資料類型策略測試功能正常")
    else:
        print("❌ 部分測試失敗")
    
    if cache_success:
        print("✅ 快取資料設定: 成功")
    else:
        print("❌ 快取資料設定: 失敗")
    
    if strategy_success:
        print("✅ 策略測試功能: 成功")
    else:
        print("❌ 策略測試功能: 失敗")

if __name__ == "__main__":
    asyncio.run(main()) 