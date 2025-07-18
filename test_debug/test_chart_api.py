#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試圖表API功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.chart_api import ChartAPI
import polars as pl

async def test_chart_api():
    """測試圖表API功能"""
    print("開始測試圖表API...")
    
    # 創建模擬的交易記錄資料
    trade_records = [
        {
            "entry_date": "2024-01-01",
            "exit_date": "2024-01-02",
            "stock_id": "2330",
            "stock_name": "台積電",
            "profit_loss": 1000,
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
            "shares": 500,
            "entry_price": 50,
            "exit_price": 49,
            "commission": 10,
            "securities_tax": 1.5,
            "holding_days": 1,
            "exit_reason": "停損"
        }
    ]
    
    # 測試不同的圖表類型
    chart_types = [
        "drawdown",
        "drawdown_merge", 
        "heatmap",
        "monthly_return_heatmap",
        "yearly_return_heatmap",
        "trading_days_heatmap",
        "trading_stocks_heatmap",
        "win_rate_heatmap",
        "weekday_analysis_charts"
    ]
    
    for chart_type in chart_types:
        print(f"測試圖表類型: {chart_type}")
        try:
            # 創建模擬請求
            class MockRequest:
                async def json(self):
                    return {
                        "chart_type": chart_type,
                        "trade_records": trade_records
                    }
            
            # 測試圖表生成
            result = await ChartAPI.generate_charts(MockRequest())
            
            if result.get("success"):
                print(f"  ✓ {chart_type} 圖表生成成功")
                print(f"    圖表HTML長度: {len(result.get('chart_html', ''))}")
            else:
                print(f"  ✗ {chart_type} 圖表生成失敗")
                
        except Exception as e:
            print(f"  ✗ {chart_type} 圖表生成錯誤: {e}")
    
    print("圖表API測試完成！")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chart_api()) 