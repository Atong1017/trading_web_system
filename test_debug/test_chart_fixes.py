#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試圖表API修正
驗證日期欄位類型錯誤修正和排序方式
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import polars as pl
from datetime import datetime, timedelta
import random

def create_test_data():
    """創建測試資料"""
    # 創建測試日期範圍
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # 生成測試資料
    test_records = []
    current_date = start_date
    
    while current_date <= end_date:
        # 跳過週末
        if current_date.weekday() < 5:  # 0-4 是週一到週五
            # 每天隨機生成1-3筆交易
            num_trades = random.randint(1, 3)
            
            for _ in range(num_trades):
                stock_id = f"00{random.randint(1000, 9999)}"
                stock_name = f"測試股票{stock_id}"
                
                # 隨機生成交易資料
                entry_price = random.uniform(10, 100)
                exit_price = entry_price * random.uniform(0.9, 1.1)  # ±10%波動
                shares = random.randint(1000, 10000)
                
                profit_loss = (exit_price - entry_price) * shares
                
                record = {
                    "entry_date": current_date.strftime("%Y-%m-%d"),
                    "exit_date": (current_date + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "stock_id": stock_id,
                    "stock_name": stock_name,
                    "profit_loss": profit_loss,
                    "net_profit_loss": profit_loss * 0.997,  # 扣除手續費
                    "profit": profit_loss,
                    "shares": shares,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "buy_amount": entry_price * shares,
                    "sell_amount": exit_price * shares,
                    "commission": abs(profit_loss) * 0.001425,
                    "securities_tax": abs(profit_loss) * 0.003,
                    "holding_days": random.randint(1, 30),
                    "exit_reason": "停利" if profit_loss > 0 else "停損",
                    "exit_status": "已平倉",
                    "trade_direction": "買入",
                    "current_price": exit_price,
                    "unrealized_profit_loss": 0,
                    "unrealized_profit_loss_rate": 0,
                    "current_date": current_date.strftime("%Y-%m-%d"),
                    "exit_price_type": "收盤價",
                    "current_entry_price": entry_price,
                    "current_exit_price": exit_price,
                    "current_profit_loss": profit_loss,
                    "current_profit_loss_rate": (profit_loss / (entry_price * shares)) * 100,
                    "take_profit_price": entry_price * 1.05,
                    "stop_loss_price": entry_price * 0.95,
                    "open_price": entry_price * random.uniform(0.98, 1.02),
                    "high_price": max(entry_price, exit_price) * random.uniform(1.0, 1.05),
                    "low_price": min(entry_price, exit_price) * random.uniform(0.95, 1.0),
                    "close_price": exit_price,
                    "明日開盤": exit_price * random.uniform(0.98, 1.02)
                }
                test_records.append(record)
        
        current_date += timedelta(days=1)
    
    return test_records

async def test_chart_api():
    """測試圖表API"""
    from api.chart_api import ChartAPI
    from fastapi import Request
    import json
    
    print("********** 開始測試圖表API修正 **********")
    
    # 創建測試資料
    test_records = create_test_data()
    print(f"創建了 {len(test_records)} 筆測試交易記錄")
    
    # 測試所有圖表類型
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
        print(f"\n--- 測試圖表類型: {chart_type} ---")
        
        try:
            # 創建模擬請求
            request_data = {
                "chart_type": chart_type,
                "trade_records": test_records
            }
            
            # 創建模擬Request物件
            class MockRequest:
                async def json(self):
                    return request_data
            
            mock_request = MockRequest()
            
            # 調用圖表生成函數
            result = await ChartAPI.generate_charts(mock_request)
            
            if result.get("success"):
                print(f"✅ {chart_type} 圖表生成成功")
                print(f"   圖表HTML長度: {len(result['chart_html'])} 字元")
            else:
                print(f"❌ {chart_type} 圖表生成失敗")
                print(f"   錯誤: {result}")
                
        except Exception as e:
            print(f"❌ {chart_type} 測試失敗")
            print(f"   錯誤: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 運行測試
    import asyncio
    asyncio.run(test_chart_api())
    
    print("\n********** 測試完成 **********") 