#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試圖表API欄位重複問題修正
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.chart_api import ChartAPI
import polars as pl

async def test_chart_fix():
    """測試圖表API欄位重複問題修正"""
    print("開始測試圖表API欄位重複問題修正...")
    
    # 測試案例1：包含多個損益欄位的資料
    trade_records_with_duplicates = [
        {
            "entry_date": "2024-01-01",
            "exit_date": "2024-01-02",
            "stock_id": "2330",
            "stock_name": "台積電",
            "profit_loss": 1000,      # 這個會被映射為 '報酬'
            "net_profit_loss": 950,   # 這個會被映射為 '淨損益'
            "profit": 1000,           # 這個會被映射為 '損益'
            "shares": 1000,
            "entry_price": 100,
            "exit_price": 101,
            "commission": 20,
            "securities_tax": 3,
            "holding_days": 1,
            "exit_reason": "獲利了結"
        },
        {
            "entry_date": "2024-01-03",
            "exit_date": "2024-01-04",
            "stock_id": "2317",
            "stock_name": "鴻海",
            "profit_loss": -500,
            "net_profit_loss": -510,
            "profit": -500,
            "shares": 500,
            "entry_price": 50,
            "exit_price": 49,
            "commission": 10,
            "securities_tax": 1.5,
            "holding_days": 1,
            "exit_reason": "停損"
        }
    ]
    
    # 測試案例2：只有一個損益欄位的資料
    trade_records_single = [
        {
            "entry_date": "2024-01-01",
            "exit_date": "2024-01-02",
            "stock_id": "2330",
            "stock_name": "台積電",
            "profit_loss": 1000,      # 只有這一個損益欄位
            "shares": 1000,
            "entry_price": 100,
            "exit_price": 101,
            "commission": 20,
            "securities_tax": 3,
            "holding_days": 1,
            "exit_reason": "獲利了結"
        }
    ]
    
    # 測試案例3：使用不同欄位名稱的資料
    trade_records_different = [
        {
            "entry_date": "2024-01-01",
            "exit_date": "2024-01-02",
            "stock_id": "2330",
            "stock_name": "台積電",
            "net_profit_loss": 950,   # 使用 net_profit_loss
            "shares": 1000,
            "entry_price": 100,
            "exit_price": 101,
            "commission": 20,
            "securities_tax": 3,
            "holding_days": 1,
            "exit_reason": "獲利了結"
        }
    ]
    
    test_cases = [
        ("多個損益欄位", trade_records_with_duplicates),
        ("單一損益欄位", trade_records_single),
        ("不同欄位名稱", trade_records_different)
    ]
    
    for test_name, trade_records in test_cases:
        print(f"\n測試案例: {test_name}")
        try:
            # 創建模擬請求
            class MockRequest:
                async def json(self):
                    return {
                        "chart_type": "heatmap",
                        "trade_records": trade_records
                    }
            
            # 測試圖表生成
            result = await ChartAPI.generate_charts(MockRequest())
            
            if result.get("success"):
                print(f"  ✓ {test_name} 圖表生成成功")
                print(f"    圖表HTML長度: {len(result.get('chart_html', ''))}")
                
                # 檢查是否有重複欄位錯誤
                if "column with name" in result.get('chart_html', ''):
                    print(f"  ✗ {test_name} 仍有欄位重複問題")
                else:
                    print(f"  ✓ {test_name} 欄位重複問題已解決")
            else:
                print(f"  ✗ {test_name} 圖表生成失敗")
                
        except Exception as e:
            error_msg = str(e)
            if "column with name" in error_msg:
                print(f"  ✗ {test_name} 欄位重複錯誤: {error_msg}")
            else:
                print(f"  ✗ {test_name} 其他錯誤: {error_msg}")
    
    print("\n圖表API欄位重複問題修正測試完成！")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chart_fix()) 