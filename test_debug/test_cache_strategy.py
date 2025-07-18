#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試使用快取資料的策略測試功能
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
from api.stock_api import StockAPI

async def setup_test_cache():
    """設定測試快取資料"""
    print("設定測試快取資料...")
    
    # 建立測試資料
    test_data = pl.DataFrame({
        "stock_id": ["2330"] * 30,
        "date": [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)],
        "open": [100 + i * 0.5 for i in range(30)],
        "high": [102 + i * 0.5 for i in range(30)],
        "low": [98 + i * 0.5 for i in range(30)],
        "close": [101 + i * 0.5 for i in range(30)],
        "volume": [1000000] * 30
    })
    
    # 儲存到快取
    success = cache_manager.set_cached_data(
        stock_id="2330",
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        data=test_data,
        data_type="price",
        ttl_hours=24
    )
    
    if success:
        print("✅ 測試快取資料設定成功")
        return True
    else:
        print("❌ 測試快取資料設定失敗")
        return False

def test_strategy_with_cache():
    """測試使用快取資料的策略測試"""
    print("\n測試使用快取資料的策略測試...")
    
    try:
        # 1. 建立測試策略
        strategy_data = {
            "name": "快取測試策略",
            "description": "測試使用快取資料的策略",
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
            "name": "快取測試策略",
            "description": "測試使用快取資料的策略",
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
        
        # 3. 測試策略
        test_data = {
            "strategy_id": strategy_id,
            "code": test_code
        }
        
        response = requests.post(
            "http://localhost:8000/api/strategies/custom/test",
            json=test_data,
            timeout=10
        )
        
        print(f"測試策略回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"測試策略回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('status') == 'success':
                results = data.get('results', {})
                
                # 檢查語法驗證
                if results.get('validation'):
                    print("✅ 語法驗證通過")
                else:
                    print("❌ 語法驗證失敗")
                
                # 檢查函數檢測
                functions = results.get('functions', [])
                if functions:
                    print(f"✅ 檢測到函數: {functions}")
                else:
                    print("⚠️  未檢測到函數")
                
                # 檢查回測結果
                backtest_results = results.get('backtest_results')
                if backtest_results:
                    if 'message' in backtest_results:
                        print(f"ℹ️  回測訊息: {backtest_results['message']}")
                    else:
                        print("✅ 回測結果:")
                        for key, value in backtest_results.items():
                            print(f"  {key}: {value}")
                        
                        # 檢查資料來源
                        data_source = backtest_results.get('data_source')
                        if data_source == '快取':
                            print("🎉 成功使用快取資料進行回測！")
                        elif data_source == 'API':
                            print("ℹ️  使用API資料進行回測")
                        else:
                            print("⚠️  使用模擬資料進行回測")
                else:
                    print("⚠️  沒有回測結果")
                
                # 清理測試策略
                response = requests.delete(
                    f"http://localhost:8000/api/strategies/custom/{strategy_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("✅ 測試策略清理完成")
                
                return True
            else:
                print(f"❌ 策略測試失敗: {data}")
                return False
        else:
            print(f"❌ 策略測試 HTTP 錯誤: {response.status_code}")
            print(f"錯誤內容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("開始測試使用快取資料的策略測試功能")
    print("=" * 60)
    
    # 1. 設定測試快取資料
    cache_success = await setup_test_cache()
    if not cache_success:
        print("❌ 無法設定測試快取資料，測試終止")
        return
    
    # 2. 測試策略測試功能
    strategy_success = test_strategy_with_cache()
    
    # 3. 輸出測試結果
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    if cache_success and strategy_success:
        print("🎉 所有測試通過！快取策略測試功能正常")
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