#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試增強的資料載入和快取功能
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

async def test_enhanced_features():
    """測試增強的資料載入和快取功能"""
    print("開始測試增強的資料載入和快取功能")
    print("=" * 60)
    
    try:
        # 1. 測試空白股票代碼的資料載入
        print("\n1. 測試空白股票代碼的資料載入")
        
        response = requests.post(
            "http://localhost:8000/api/sample-data/load",
            json={
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "",  # 空白股票代碼
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-03"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                result_data = data.get('data', [])
                print(f"✅ 成功載入 {len(result_data)} 筆資料")
                
                # 檢查是否包含多支股票
                stock_ids = set()
                for row in result_data:
                    if 'stock_id' in row:
                        stock_ids.add(row['stock_id'])
                
                print(f"✅ 包含 {len(stock_ids)} 支股票: {list(stock_ids)}")
            else:
                print(f"❌ 載入資料失敗: {data}")
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
        
        # 2. 測試指定股票代碼的資料載入
        print("\n2. 測試指定股票代碼的資料載入")
        
        response = requests.post(
            "http://localhost:8000/api/sample-data/load",
            json={
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "2330",  # 指定股票代碼
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-03"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                result_data = data.get('data', [])
                print(f"✅ 成功載入 {len(result_data)} 筆資料")
                
                # 檢查是否只包含指定股票
                stock_ids = set()
                for row in result_data:
                    if 'stock_id' in row:
                        stock_ids.add(row['stock_id'])
                
                print(f"✅ 包含股票: {list(stock_ids)}")
            else:
                print(f"❌ 載入資料失敗: {data}")
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
        
        # 3. 測試策略表格選擇功能
        print("\n3. 測試策略表格選擇功能")
        
        # 建立測試策略
        strategy_data = {
            "name": "表格選擇測試策略",
            "description": "測試策略表格選擇功能",
            "type": "template"
        }
        
        response = requests.post(
            "http://localhost:8000/api/strategies/custom",
            json=strategy_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 建立策略失敗: HTTP {response.status_code}")
            return
        
        result = response.json()
        if result.get('status') != 'success':
            print(f"❌ 建立策略失敗: {result}")
            return
        
        strategy_id = result.get('strategy_id')
        print(f"✅ 成功建立策略: {strategy_id}")
        
        # 更新策略程式碼
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
            "name": "表格選擇測試策略",
            "description": "測試策略表格選擇功能",
            "code": test_code
        }
        
        response = requests.put(
            f"http://localhost:8000/api/strategies/custom/{strategy_id}",
            json=update_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 更新策略失敗: HTTP {response.status_code}")
            return
        
        print("✅ 成功更新策略程式碼")
        
        # 測試不同的策略表格選擇
        test_cases = [
            {
                "name": "自動選擇表格",
                "data_type": "daily_price",
                "stock_id": "2330",
                "strategy_table": "auto"
            },
            {
                "name": "指定技術指標表格",
                "data_type": "daily_price",
                "stock_id": "2330",
                "strategy_table": "technical_indicators"
            },
            {
                "name": "空白股票代碼",
                "data_type": "daily_price",
                "stock_id": "",
                "strategy_table": "auto"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- 測試案例 {i}: {test_case['name']} ---")
            
            test_data = {
                "strategy_id": strategy_id,
                "code": test_code,
                "data_type": test_case["data_type"],
                "stock_id": test_case["stock_id"],
                "strategy_table": test_case["strategy_table"]
            }
            
            response = requests.post(
                "http://localhost:8000/api/strategies/custom/test",
                json=test_data,
                timeout=10
            )
            
            print(f"回應狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    results = data.get('results', {})
                    backtest_results = results.get('backtest_results', {})
                    
                    print(f"✅ 語法驗證: {'通過' if results.get('validation') else '失敗'}")
                    
                    if 'data_source' in backtest_results:
                        print(f"✅ 資料來源: {backtest_results['data_source']}")
                    if 'data_count' in backtest_results:
                        print(f"✅ 資料筆數: {backtest_results['data_count']}")
                    if 'strategy_table' in backtest_results:
                        print(f"✅ 策略表格: {backtest_results['strategy_table']}")
                    
                    if backtest_results.get('total_trades') is not None:
                        print(f"✅ 總交易次數: {backtest_results['total_trades']}")
                else:
                    print(f"❌ 測試失敗: {data}")
            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")
        
        # 清理測試策略
        response = requests.delete(
            f"http://localhost:8000/api/strategies/custom/{strategy_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 測試策略清理完成")
        
        print("\n" + "=" * 60)
        print("測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_features()) 