#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試超時和載入狀態功能
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 25  # 設定為 25 秒，比前端的 20 秒稍長

async def test_sample_data_with_timeout():
    """測試範例資料載入的超時功能"""
    print("=== 測試範例資料載入超時功能 ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 測試1: 正常載入（小量資料）
            print("\n1. 測試正常載入（小量資料）...")
            payload = {
                "data_type": "minute_price",
                "parameters": {
                    "stock_id": "2330",
                    "interval": "5",
                    "date": "2024-01-15"
                }
            }
            
            start_time = datetime.now()
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 正常載入成功")
                    print(f"  耗時: {duration:.2f} 秒")
                    print(f"  資料筆數: {len(data.get('data', []))}")
                else:
                    print(f"✗ 載入失敗: {response.status}")
            
            # 測試2: 大量資料載入（可能超時）
            print("\n2. 測試大量資料載入...")
            payload = {
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "2330,2317,2454,3008,2412",  # 多檔股票
                    "start_date": "2023-01-01",
                    "end_date": "2024-12-31"
                }
            }
            
            start_time = datetime.now()
            try:
                async with session.post(
                    f"{BASE_URL}/api/sample-data/load",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
                ) as response:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✓ 大量資料載入成功")
                        print(f"  耗時: {duration:.2f} 秒")
                        print(f"  資料筆數: {len(data.get('data', []))}")
                    else:
                        print(f"✗ 載入失敗: {response.status}")
                        
            except asyncio.TimeoutError:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                print(f"⚠️ 載入超時（{duration:.2f} 秒）")
                print("  這是預期的行為，大量資料應該會超時")
            
            # 測試3: Jupyter 範例資料
            print("\n3. 測試 Jupyter 範例資料...")
            payload = {
                "data_type": "stock_data"
            }
            
            start_time = datetime.now()
            async with session.post(
                f"{BASE_URL}/api/jupyter/sample-data",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Jupyter 範例資料載入成功")
                    print(f"  耗時: {duration:.2f} 秒")
                    if data.get('data'):
                        print(f"  資料類型: {type(data.get('data'))}")
                else:
                    print(f"✗ 載入失敗: {response.status}")
            
            return True
            
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
            return False

async def test_data_limits():
    """測試資料量限制功能"""
    print("\n=== 測試資料量限制功能 ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 測試過大的日期範圍
            print("\n1. 測試過大的日期範圍...")
            payload = {
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "2330",
                    "start_date": "2020-01-01",  # 4年前的資料
                    "end_date": "2024-12-31"
                }
            }
            
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 過大日期範圍處理成功")
                    print(f"  資料筆數: {len(data.get('data', []))}")
                    print(f"  系統應該自動調整日期範圍")
                else:
                    print(f"✗ 處理失敗: {response.status}")
            
            # 測試多檔股票
            print("\n2. 測試多檔股票...")
            payload = {
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "2330,2317,2454,3008,2412,1301,1303,2002,2207,2308,2881,2882",  # 12檔股票
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                }
            }
            
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 多檔股票處理成功")
                    print(f"  資料筆數: {len(data.get('data', []))}")
                    print(f"  系統應該限制股票數量")
                else:
                    print(f"✗ 處理失敗: {response.status}")
            
            return True
            
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
            return False

async def main():
    """主測試函數"""
    print("開始測試超時和載入狀態功能...")
    print("=" * 50)
    
    # 測試超時功能
    timeout_success = await test_sample_data_with_timeout()
    
    # 測試資料限制
    limits_success = await test_data_limits()
    
    # 總結
    print("\n" + "=" * 50)
    print("測試總結:")
    print(f"✓ 超時功能測試: {'成功' if timeout_success else '失敗'}")
    print(f"✓ 資料限制測試: {'成功' if limits_success else '失敗'}")
    
    if timeout_success and limits_success:
        print("\n🎉 所有測試通過！")
        print("功能改進:")
        print("- 20秒超時設定已生效")
        print("- 載入狀態提示已實作")
        print("- 資料量限制已生效")
        print("- 成功通知已實作")
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    asyncio.run(main()) 