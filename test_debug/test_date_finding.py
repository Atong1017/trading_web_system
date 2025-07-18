#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試日期查找邏輯
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from datetime import datetime, timedelta

def test_date_finding_logic():
    """測試日期查找邏輯"""
    print("=== 測試日期查找邏輯 ===")
    
    # 模擬股票資料（假設只有週一到週五的資料）
    test_data = {
        "date": [
            "2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18", "2024-01-19",
            "2024-01-22", "2024-01-23", "2024-01-24", "2024-01-25", "2024-01-26"
        ],
        "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    }
    
    df = pl.DataFrame(test_data)
    df_with_row_nums = df.with_row_count()
    
    print("測試資料:")
    print(df_with_row_nums)
    print()
    
    # 測試案例
    test_cases = [
        {
            "target_date": "2024-01-19",
            "description": "完全匹配的日期"
        },
        {
            "target_date": "2024-01-20",  # 週末，應該找不到
            "description": "不存在的日期（週末）"
        },
        {
            "target_date": "2024-01-21",  # 週末，應該找不到
            "description": "不存在的日期（週末）"
        },
        {
            "target_date": "2024-01-25",
            "description": "存在的日期"
        },
        {
            "target_date": "2024-01-30",  # 超出範圍
            "description": "超出資料範圍的日期"
        }
    ]
    
    for test_case in test_cases:
        print(f"--- {test_case['description']} ---")
        target_date = test_case['target_date']
        
        try:
            # 先嘗試找完全匹配的日期
            target_row = df_with_row_nums.filter(pl.col('date') == target_date).select('row_nr')
            if target_row.height > 0:
                target_index = target_row.row(0)[0]
                print(f"✅ 找到完全匹配的日期 {target_date}, index: {target_index}")
            else:
                # 如果找不到完全匹配，往後找最近的有效日期
                print(f"⚠️  找不到日期 {target_date}，往後尋找最近的有效日期")
                
                # 將日期轉為datetime物件進行比較
                target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
                
                # 找到所有大於等於目標日期的行
                valid_rows = df_with_row_nums.filter(pl.col('date') >= target_datetime).select('row_nr')
                
                if valid_rows.height > 0:
                    # 取第一行（最近的日期）
                    target_index = valid_rows.row(0)[0]
                    actual_date = df_with_row_nums.filter(pl.col('row_nr') == target_index).select('date').row(0)[0]
                    print(f"✅ 找到最近的有效日期 {actual_date}, index: {target_index}")
                else:
                    # 如果還是找不到，使用最後一行
                    target_index = df_with_row_nums.select('row_nr').row(-1)[0]
                    actual_date = df_with_row_nums.filter(pl.col('row_nr') == target_index).select('date').row(0)[0]
                    print(f"✅ 使用最後一行日期 {actual_date}, index: {target_index}")
        
        except Exception as e:
            print(f"❌ 日期查找失敗: {e}")
            # 如果出現錯誤，使用第一行
            target_index = 0
            print(f"✅ 使用預設index: {target_index}")
        
        print()

def test_strategy_scenario():
    """測試策略場景"""
    print("=== 測試策略場景 ===")
    
    # 模擬策略中的情況
    start_date = "2023-11-30"  # 往前推50天後的日期
    
    # 模擬股票資料（從2024年開始）
    test_data = {
        "date": [
            "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-08",
            "2024-01-09", "2024-01-10", "2024-01-11", "2024-01-12", "2024-01-15"
        ],
        "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    }
    
    df = pl.DataFrame(test_data)
    df_with_row_nums = df.with_row_count()
    
    print(f"目標開始日期: {start_date}")
    print("可用資料日期範圍:")
    print(f"  最早: {df_with_row_nums.select('date').row(0)[0]}")
    print(f"  最晚: {df_with_row_nums.select('date').row(-1)[0]}")
    print()
    
    try:
        # 尋找目標日期
        target_row = df_with_row_nums.filter(pl.col('date') == start_date).select('row_nr')
        if target_row.height > 0:
            target_index = target_row.row(0)[0]
            print(f"✅ 找到完全匹配的日期 {start_date}, index: {target_index}")
        else:
            print(f"⚠️  找不到日期 {start_date}，往後尋找最近的有效日期")
            
            target_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            valid_rows = df_with_row_nums.filter(pl.col('date') >= target_datetime).select('row_nr')
            
            if valid_rows.height > 0:
                target_index = valid_rows.row(0)[0]
                actual_date = df_with_row_nums.filter(pl.col('row_nr') == target_index).select('date').row(0)[0]
                print(f"✅ 找到最近的有效日期 {actual_date}, index: {target_index}")
            else:
                target_index = df_with_row_nums.select('row_nr').row(-1)[0]
                actual_date = df_with_row_nums.filter(pl.col('row_nr') == target_index).select('date').row(0)[0]
                print(f"✅ 使用最後一行日期 {actual_date}, index: {target_index}")
    
    except Exception as e:
        print(f"❌ 策略場景測試失敗: {e}")

if __name__ == "__main__":
    test_date_finding_logic()
    test_strategy_scenario() 