#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試友好顯示名稱功能
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

async def test_friendly_display_names():
    """測試友好顯示名稱功能"""
    print("開始測試友好顯示名稱功能")
    print("=" * 60)
    
    try:
        # 1. 測試取得快取檔案列表（包含友好顯示名稱）
        print("\n1. 測試取得快取檔案列表（包含友好顯示名稱）")
        
        response = requests.get(
            "http://localhost:8000/api/cache/files",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                cache_files = data.get('data', {}).get('files', [])
                grouped_files = data.get('data', {}).get('grouped_files', {})
                
                print(f"✅ 成功取得 {len(cache_files)} 個快取檔案")
                
                if cache_files:
                    print("\n快取檔案列表（包含友好顯示名稱）:")
                    for file_info in cache_files:
                        print(f"  - 友好名稱: {file_info.get('friendly_display_name', 'N/A')}")
                        print(f"    原始名稱: {file_info.get('display_name', 'N/A')}")
                        print(f"    檔案: {file_info.get('filename', 'N/A')}")
                        print(f"    類型: {file_info.get('data_type', 'N/A')}")
                        print(f"    股票: {file_info.get('stock_id', 'N/A')}")
                        print(f"    大小: {file_info.get('size_mb', 'N/A')}MB")
                        print(f"    修改時間: {file_info.get('modified_time', 'N/A')}")
                        
                        # 顯示元資料資訊
                        metadata = file_info.get('metadata', {})
                        if metadata:
                            print(f"    建立時間: {metadata.get('created_at', 'N/A')}")
                            print(f"    過期時間: {metadata.get('expires_at', 'N/A')}")
                        print()
                else:
                    print("⚠️  沒有找到快取檔案")
                
                print("分組資訊:")
                for data_type, files in grouped_files.items():
                    print(f"  {data_type}: {len(files)} 個檔案")
                
                return cache_files
            else:
                print(f"❌ 取得快取檔案失敗: {data}")
                return None
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return None

def test_strategy_with_friendly_names(cache_files):
    """測試使用友好顯示名稱的策略測試"""
    print("\n2. 測試使用友好顯示名稱的策略測試")
    
    if not cache_files:
        print("⚠️  沒有快取檔案可供測試")
        return
    
    try:
        # 建立測試策略
        strategy_data = {
            "name": "友好名稱測試策略",
            "description": "測試使用友好顯示名稱的策略",
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
            "name": "友好名稱測試策略",
            "description": "測試使用友好顯示名稱的策略",
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
        
        # 測試使用友好顯示名稱的快取檔案
        test_cases = []
        
        # 添加快取檔案測試案例
        for i, file_info in enumerate(cache_files[:2]):  # 只測試前2個檔案
            friendly_name = file_info.get('friendly_display_name', 'unknown')
            test_cases.append({
                "name": f"使用友好名稱: {friendly_name}",
                "data_type": "daily_price",
                "stock_id": "2330",
                "strategy_table": file_info['cache_key']
            })
        
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

async def main():
    """主測試函數"""
    # 1. 測試友好顯示名稱
    cache_files = await test_friendly_display_names()
    
    # 2. 測試使用友好顯示名稱的策略測試
    test_strategy_with_friendly_names(cache_files)

if __name__ == "__main__":
    asyncio.run(main()) 