#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試範例資料載入功能修復
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

async def test_sample_data_types():
    """測試取得範例資料類型"""
    print("=== 測試取得範例資料類型 ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/sample-data/types", timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 成功取得資料類型")
                    print(f"  狀態: {data.get('status')}")
                    print(f"  資料類型數量: {len(data.get('types', []))}")
                    
                    for i, data_type in enumerate(data.get('types', [])[:3]):  # 只顯示前3個
                        print(f"  {i+1}. {data_type.get('name')} ({data_type.get('id')})")
                        print(f"     描述: {data_type.get('description')}")
                        print(f"     分類: {data_type.get('category')}")
                    
                    return data.get('types', [])
                else:
                    print(f"✗ 請求失敗: {response.status}")
                    return []
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
            return []

async def test_load_sample_data(data_type_id, parameters):
    """測試載入範例資料"""
    print(f"\n=== 測試載入範例資料: {data_type_id} ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "data_type": data_type_id,
                "parameters": parameters
            }
            
            async with session.post(
                f"{BASE_URL}/api/sample-data/load",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 成功載入資料")
                    print(f"  狀態: {data.get('status')}")
                    print(f"  資料筆數: {len(data.get('data', []))}")
                    
                    if data.get('data'):
                        sample_data = data['data'][0] if data['data'] else {}
                        print(f"  範例資料欄位: {list(sample_data.keys())}")
                        print(f"  範例資料: {sample_data}")
                    
                    return data.get('data', [])
                else:
                    error_text = await response.text()
                    print(f"✗ 請求失敗: {response.status}")
                    print(f"  錯誤訊息: {error_text}")
                    return []
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
            return []

async def test_jupyter_sample_data():
    """測試 Jupyter 範例資料"""
    print(f"\n=== 測試 Jupyter 範例資料 ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "data_type": "stock_data"
            }
            
            async with session.post(
                f"{BASE_URL}/api/jupyter/sample-data",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 成功載入 Jupyter 範例資料")
                    print(f"  狀態: {data.get('status')}")
                    print(f"  資料類型: {type(data.get('data'))}")
                    
                    if hasattr(data.get('data'), 'shape'):
                        print(f"  資料形狀: {data.get('data').shape}")
                    elif isinstance(data.get('data'), list):
                        print(f"  資料筆數: {len(data.get('data', []))}")
                    
                    return data.get('data')
                else:
                    error_text = await response.text()
                    print(f"✗ 請求失敗: {response.status}")
                    print(f"  錯誤訊息: {error_text}")
                    return None
        except Exception as e:
            print(f"✗ 測試失敗: {e}")
            return None

async def main():
    """主測試函數"""
    print("開始測試範例資料載入功能...")
    print("=" * 50)
    
    # 測試1: 取得資料類型
    data_types = await test_sample_data_types()
    
    if not data_types:
        print("無法取得資料類型，停止測試")
        return
    
    # 測試2: 載入每日股價資料
    daily_params = {
        "stock_id": "2330",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
    daily_data = await test_load_sample_data("daily_price", daily_params)
    
    # 測試3: 載入分K資料
    minute_params = {
        "stock_id": "2330",
        "interval": "5",
        "date": "2024-01-15"
    }
    minute_data = await test_load_sample_data("minute_price", minute_params)
    
    # 測試4: 載入技術指標資料
    tech_params = {
        "stock_id": "2330",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "indicators": "all"
    }
    tech_data = await test_load_sample_data("technical_indicators", tech_params)
    
    # 測試5: Jupyter 範例資料
    jupyter_data = await test_jupyter_sample_data()
    
    # 總結
    print("\n" + "=" * 50)
    print("測試總結:")
    print(f"✓ 資料類型數量: {len(data_types)}")
    print(f"✓ 每日股價資料: {'成功' if daily_data else '失敗'}")
    print(f"✓ 分K資料: {'成功' if minute_data else '失敗'}")
    print(f"✓ 技術指標資料: {'成功' if tech_data else '失敗'}")
    print(f"✓ Jupyter 範例資料: {'成功' if jupyter_data is not None else '失敗'}")
    
    if daily_data and minute_data and tech_data and jupyter_data is not None:
        print("\n🎉 所有測試通過！範例資料載入功能正常")
    else:
        print("\n⚠️  部分測試失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    asyncio.run(main()) 