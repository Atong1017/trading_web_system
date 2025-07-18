#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立策略測試用的 Excel 範本檔案
"""

import pandas as pd
import os
from datetime import datetime, timedelta

def create_excel_template():
    """建立策略測試用的 Excel 範本檔案"""
    
    # 建立範例資料
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    # 模擬台積電股價資料
    base_price = 500.0
    data = []
    
    for i, date in enumerate(dates):
        # 模擬價格波動
        change = (i % 7 - 3) * 0.015  # 每週循環
        price = base_price * (1 + change)
        
        row = {
            'date': date.strftime('%Y-%m-%d'),
            'stock_id': '2330',
            'open': round(price * 0.99, 2),
            'high': round(price * 1.02, 2),
            'low': round(price * 0.98, 2),
            'close': round(price, 2),
            'volume': 1000000 + (i * 50000)
        }
        data.append(row)
    
    # 建立 DataFrame
    df = pd.DataFrame(data)
    
    # 確保目錄存在
    os.makedirs('data/exports', exist_ok=True)
    
    # 儲存 Excel 檔案
    template_path = 'data/exports/strategy_test_template.xlsx'
    df.to_excel(template_path, index=False, sheet_name='股票資料')
    
    print(f"✓ Excel 範本檔案已建立: {template_path}")
    print(f"  包含 {len(df)} 筆資料")
    print(f"  欄位: {', '.join(df.columns)}")
    print()
    print("檔案格式說明:")
    print("- date: 日期 (YYYY-MM-DD 格式)")
    print("- stock_id: 股票代碼 (可選)")
    print("- open: 開盤價")
    print("- high: 最高價") 
    print("- low: 最低價")
    print("- close: 收盤價")
    print("- volume: 成交量 (可選)")
    print()
    print("使用方式:")
    print("1. 在策略編輯器中選擇 'Excel 檔案上傳'")
    print("2. 點擊 '選擇檔案' 按鈕")
    print("3. 選擇此範本檔案或您自己的 Excel 檔案")
    print("4. 點擊 '測試策略' 進行回測")
    
    return template_path

if __name__ == "__main__":
    create_excel_template() 