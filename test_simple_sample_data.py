#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試範例資料載入功能
"""

import asyncio
from core.data_provider import DataProvider

async def test_data_provider():
    """測試 DataProvider"""
    print("=== 測試 DataProvider ===")
    
    try:
        # 建立 DataProvider 實例
        data_provider = DataProvider()
        
        # 測試取得資料類型
        data_types = data_provider.get_data_types()
        print(f"✓ 資料類型數量: {len(data_types)}")
        
        # 測試載入分K資料（不需要 API 調用）
        minute_params = {
            "stock_id": "2330",
            "interval": "5",
            "date": "2024-01-15"
        }
        
        minute_data = data_provider._generate_minute_price_data(minute_params)
        print(f"✓ 分K資料載入成功: {len(minute_data)} 筆")
        
        if minute_data:
            print(f"  範例資料: {minute_data[0]}")
        
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("開始簡單測試...")
    
    success = await test_data_provider()
    
    if success:
        print("\n🎉 測試通過！DataProvider 基本功能正常")
    else:
        print("\n⚠️ 測試失敗")

if __name__ == "__main__":
    asyncio.run(main()) 