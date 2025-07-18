#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試圖表功能
"""

import json
import requests
from datetime import datetime, timedelta
import random

def create_test_trade_data():
    """創建測試交易資料"""
    trade_records = []
    
    # 創建一些測試股票
    stock_ids = ['2330', '2317', '2454', '3008', '2412']
    stock_names = ['台積電', '鴻海', '聯發科', '大立光', '中華電']
    
    # 生成日期範圍
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for i in range(100):  # 生成100筆交易記錄
        # 隨機選擇股票
        stock_idx = random.randint(0, len(stock_ids) - 1)
        stock_id = stock_ids[stock_idx]
        stock_name = stock_names[stock_idx]
        
        # 隨機生成日期
        random_days = random.randint(0, (end_date - start_date).days)
        entry_date = start_date + timedelta(days=random_days)
        exit_date = entry_date + timedelta(days=random.randint(1, 30))
        
        # 隨機生成價格和報酬
        entry_price = random.uniform(50, 500)
        exit_price = entry_price * random.uniform(0.8, 1.3)  # 80% - 130%
        shares = random.randint(1000, 10000)
        
        # 計算報酬
        profit_loss = (exit_price - entry_price) * shares
        profit_loss_rate = (exit_price - entry_price) / entry_price * 100
        
        # 隨機生成其他欄位
        trade_record = {
            "entry_date": entry_date.strftime("%Y-%m-%d"),
            "exit_date": exit_date.strftime("%Y-%m-%d"),
            "stock_id": stock_id,
            "stock_name": stock_name,
            "entry_price": round(entry_price, 2),
            "exit_price": round(exit_price, 2),
            "shares": shares,
            "profit_loss": round(profit_loss, 2),
            "profit_loss_rate": round(profit_loss_rate, 2),
            "net_profit_loss": round(profit_loss * 0.997, 2),  # 扣除手續費
            "holding_days": (exit_date - entry_date).days,
            "exit_reason": random.choice(['停利', '停損', '到期出場', '手動出場']),
            "trade_direction": 1,  # 做多
            "commission": round(profit_loss * 0.001425, 2),
            "securities_tax": round(profit_loss * 0.003, 2),
            "current_price": round(exit_price, 2),
            "unrealized_profit_loss": 0,
            "unrealized_profit_loss_rate": 0,
            "current_date": exit_date.strftime("%Y-%m-%d"),
            "exit_price_type": "close",
            "current_entry_price": round(entry_price, 2),
            "current_exit_price": round(exit_price, 2),
            "current_profit_loss": round(profit_loss, 2),
            "current_profit_loss_rate": round(profit_loss_rate, 2),
            "take_profit_price": round(entry_price * 1.1, 2),
            "stop_loss_price": round(entry_price * 0.9, 2),
            "open_price": round(entry_price * random.uniform(0.98, 1.02), 2),
            "high_price": round(entry_price * random.uniform(1.0, 1.05), 2),
            "low_price": round(entry_price * random.uniform(0.95, 1.0), 2),
            "close_price": round(exit_price, 2),
            "明日開盤價": round(exit_price * random.uniform(0.98, 1.02), 2)
        }
        
        trade_records.append(trade_record)
    
    return trade_records

def test_chart_generation():
    """測試圖表生成功能"""
    base_url = "http://localhost:8000"
    
    # 創建測試資料
    trade_records = create_test_trade_data()
    print(f"創建了 {len(trade_records)} 筆測試交易記錄")
    
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
        print(f"\n測試圖表類型: {chart_type}")
        
        try:
            # 準備請求資料
            request_data = {
                "chart_type": chart_type,
                "trade_records": trade_records
            }
            
            # 發送請求
            response = requests.post(
                f"{base_url}/api/backtest/charts",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ {chart_type} 圖表生成成功")
                    # 檢查返回的HTML是否包含圖表內容
                    chart_html = result.get("chart_html", "")
                    if "plotly" in chart_html.lower() or "chart" in chart_html.lower():
                        print(f"   HTML內容長度: {len(chart_html)} 字符")
                    else:
                        print(f"   ⚠️  HTML內容可能不完整: {chart_html[:100]}...")
                else:
                    print(f"❌ {chart_type} 圖表生成失敗: {result.get('message', '未知錯誤')}")
            else:
                print(f"❌ {chart_type} 請求失敗: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ {chart_type} 測試時發生錯誤: {str(e)}")

def test_chart_with_real_data():
    """使用真實資料測試圖表"""
    print("\n=== 使用真實資料測試圖表 ===")
    
    # 這裡可以載入真實的交易記錄資料
    # 或者從檔案系統讀取之前保存的回測結果
    
    print("請先執行回測產生真實交易資料，然後再測試圖表功能")

if __name__ == "__main__":
    print("開始測試圖表功能...")
    
    # 測試圖表生成
    test_chart_generation()
    
    # 測試真實資料
    test_chart_with_real_data()
    
    print("\n圖表功能測試完成！") 