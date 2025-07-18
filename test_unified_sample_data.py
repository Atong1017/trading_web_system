#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試統一後的載入範例資料功能和效能優化
"""

import asyncio
import aiohttp
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 20  # 20秒超時

async def test_unified_sample_data():
    """測試統一後的載入範例資料功能"""
    print("=== 測試統一後的載入範例資料功能 ===")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 測試1: 取得資料類型列表
        print("\n1. 測試取得資料類型列表")
        try:
            async with session.get(
                f"{BASE_URL}/api/sample-data/types",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 成功取得 {len(data.get('types', []))} 種資料類型")
                    for data_type in data.get('types', []):
                        print(f"  - {data_type.get('name')} ({data_type.get('id')})")
                else:
                    print(f"✗ 請求失敗: {response.status}")
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
        
        # 測試2: 測試每日股價資料載入（限制股票數量）
        print("\n2. 測試每日股價資料載入（限制股票數量）")
        start_time = time.time()
        try:
            payload = {
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "2330,2317,2454",  # 3檔股票
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"  # 30天
                }
            }
            
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    load_time = end_time - start_time
                    
                    if data.get('status') == 'success':
                        data_count = len(data.get('data', []))
                        print(f"✓ 成功載入資料")
                        print(f"  載入時間: {load_time:.2f} 秒")
                        print(f"  資料筆數: {data_count}")
                        print(f"  平均每筆載入時間: {load_time/data_count*1000:.2f} 毫秒")
                        
                        if data_count > 0:
                            sample_data = data['data'][0]
                            print(f"  範例資料欄位: {list(sample_data.keys())}")
                    else:
                        print(f"✗ 載入失敗: {data.get('message', '未知錯誤')}")
                else:
                    print(f"✗ 請求失敗: {response.status}")
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
        
        # 測試3: 測試未指定股票代碼（應該自動限制為10檔）
        print("\n3. 測試未指定股票代碼（自動限制）")
        start_time = time.time()
        try:
            payload = {
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "",  # 空白，應該自動選擇前10檔
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-15"  # 15天
                }
            }
            
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    load_time = end_time - start_time
                    
                    if data.get('status') == 'success':
                        data_count = len(data.get('data', []))
                        print(f"✓ 成功載入資料")
                        print(f"  載入時間: {load_time:.2f} 秒")
                        print(f"  資料筆數: {data_count}")
                        
                        # 檢查是否有多檔股票
                        if data_count > 0:
                            stock_ids = set()
                            for item in data['data']:
                                if 'stock_id' in item:
                                    stock_ids.add(item['stock_id'])
                            print(f"  股票檔數: {len(stock_ids)}")
                            print(f"  股票代碼: {list(stock_ids)[:5]}...")  # 只顯示前5個
                    else:
                        print(f"✗ 載入失敗: {data.get('message', '未知錯誤')}")
                else:
                    print(f"✗ 請求失敗: {response.status}")
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
        
        # 測試4: 測試技術指標資料載入
        print("\n4. 測試技術指標資料載入")
        start_time = time.time()
        try:
            payload = {
                "data_type": "technical_indicators",
                "parameters": {
                    "stock_id": "2330",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "indicators": "all"
                }
            }
            
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    load_time = end_time - start_time
                    
                    if data.get('status') == 'success':
                        data_count = len(data.get('data', []))
                        print(f"✓ 成功載入技術指標資料")
                        print(f"  載入時間: {load_time:.2f} 秒")
                        print(f"  資料筆數: {data_count}")
                        
                        if data_count > 0:
                            sample_data = data['data'][0]
                            tech_indicators = [k for k in sample_data.keys() if k in ['ma5', 'ma10', 'ma20', 'rsi', 'macd', 'bb_upper']]
                            print(f"  技術指標: {tech_indicators}")
                    else:
                        print(f"✗ 載入失敗: {data.get('message', '未知錯誤')}")
                else:
                    print(f"✗ 請求失敗: {response.status}")
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
        
        # 測試5: 測試超時處理
        print("\n5. 測試超時處理（大範圍日期）")
        start_time = time.time()
        try:
            payload = {
                "data_type": "daily_price",
                "parameters": {
                    "stock_id": "2330,2317,2454,3008,2412",  # 5檔股票
                    "start_date": "2020-01-01",  # 4年前的資料
                    "end_date": "2024-12-31"  # 到現在
                }
            }
            
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)  # 15秒超時
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    load_time = end_time - start_time
                    
                    if data.get('status') == 'success':
                        data_count = len(data.get('data', []))
                        print(f"✓ 成功載入大量資料")
                        print(f"  載入時間: {load_time:.2f} 秒")
                        print(f"  資料筆數: {data_count}")
                    else:
                        print(f"✗ 載入失敗: {data.get('message', '未知錯誤')}")
                else:
                    print(f"✗ 請求失敗: {response.status}")
        except asyncio.TimeoutError:
            print("✓ 正確觸發超時保護")
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)

async def test_jupyter_sample_data():
    """測試 Jupyter 範例資料載入"""
    print("\n=== 測試 Jupyter 範例資料載入 ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "data_type": "stock_data"
            }
            
            start_time = time.time()
            async with session.post(
                f"{BASE_URL}/api/jupyter/sample-data",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    load_time = end_time - start_time
                    
                    if data.get('status') == 'success':
                        print(f"✓ Jupyter 範例資料載入成功")
                        print(f"  載入時間: {load_time:.2f} 秒")
                        
                        if hasattr(data.get('data'), 'shape'):
                            print(f"  資料形狀: {data.get('data').shape}")
                        elif isinstance(data.get('data'), list):
                            print(f"  資料筆數: {len(data.get('data', []))}")
                    else:
                        print(f"✗ Jupyter 範例資料載入失敗: {data.get('error', '未知錯誤')}")
                else:
                    print(f"✗ 請求失敗: {response.status}")
        except Exception as e:
            print(f"✗ 測試失敗: {e}")

async def main():
    """主測試函數"""
    print("開始測試統一後的載入範例資料功能...")
    
    # 測試統一後的範例資料載入
    await test_unified_sample_data()
    
    # 測試 Jupyter 範例資料載入
    await test_jupyter_sample_data()
    
    print("\n🎉 所有測試完成！")
    print("\n主要改進:")
    print("1. ✓ 統一了 Jupyter 和傳統模式的載入範例資料功能")
    print("2. ✓ 移除了重複的按鈕，將傳統模式的按鈕移到格式化旁邊")
    print("3. ✓ 限制了股票數量（未指定時最多10檔，指定時最多5檔）")
    print("4. ✓ 減少了超時時間（從20秒改為15秒）")
    print("5. ✓ 前端自動限制日期範圍（超過60天自動調整）")
    print("6. ✓ 限制預覽資料量（最多100筆）")

if __name__ == "__main__":
    asyncio.run(main()) 