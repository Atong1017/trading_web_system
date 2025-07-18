"""
測試下載每日股價資料
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from api.stock_api import StockAPI

params={'stockIds': '2330', 'startDate': '20250415', 'endDate': '2025-07-04'}
async def test_price():
    """測試下載每日股價資料"""
    print("測試下載每日股價資料")
    print("=" * 60)
    stockIds = params['stockIds'].split(',')
    startDate = params['startDate']
    endDate = params['endDate']
    print(f"stockIds={stockIds}, startDate={startDate}, endDate={endDate}")
    try:
        # 1. 測試空白股票代碼的資料載入
        print("\n1. 測試空白股票代碼的資料載入")
        async with StockAPI() as stock_api:
            df = await stock_api.get_stock_price(['2330', '2317', '2454', '3008', '1301'], startDate, endDate)
            print(df)
    except Exception as e:
        print(f"測試失敗: {e}")

async def test_stock_info():
    """測試取得股票基本資訊"""
    print("測試取得股票基本資訊")
    print("=" * 60)
    
    try:
        async with StockAPI() as stock_api:
            df = await stock_api.get_stock_info()
            print(df)
    except Exception as e:
        print(f"測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_price())