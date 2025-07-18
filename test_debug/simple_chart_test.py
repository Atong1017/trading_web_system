#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單圖表測試
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("開始測試...")

try:
    from api.chart_api import ChartAPI
    print("ChartAPI 導入成功")
    
    # 測試資料
    trade_records = [
        {
            "entry_date": "2024-01-01",
            "exit_date": "2024-01-02",
            "stock_id": "2330",
            "stock_name": "台積電",
            "profit_loss": 1000,
            "net_profit_loss": 950,
            "profit": 1000,
            "shares": 1000,
            "entry_price": 100,
            "exit_price": 101,
            "commission": 20,
            "securities_tax": 3,
            "holding_days": 1,
            "exit_reason": "獲利了結"
        }
    ]
    
    print(f"測試資料包含 {len(trade_records)} 筆記錄")
    print(f"第一筆記錄的欄位: {list(trade_records[0].keys())}")
    
    # 檢查是否有重複的欄位名稱
    import polars as pl
    df = pl.DataFrame(trade_records)
    print(f"DataFrame 欄位: {df.columns}")
    
    # 檢查欄位映射
    column_mapping = {
        'profit_loss': '報酬',
        'net_profit_loss': '淨損益',
        'profit': '損益',
    }
    
    print("欄位映射:")
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            print(f"  {old_name} -> {new_name}")
    
    # 重命名欄位
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            df = df.rename({old_name: new_name})
    
    print(f"重命名後的欄位: {df.columns}")
    
    # 統一損益欄位
    if '報酬' not in df.columns:
        if '淨損益' in df.columns:
            df = df.rename({'淨損益': '報酬'})
            print("將 '淨損益' 重命名為 '報酬'")
        elif '損益' in df.columns:
            df = df.rename({'損益': '報酬'})
            print("將 '損益' 重命名為 '報酬'")
    
    print(f"最終欄位: {df.columns}")
    
    if '報酬' in df.columns:
        print("✓ 成功統一損益欄位為 '報酬'")
    else:
        print("✗ 未能統一損益欄位")
    
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

print("測試完成") 