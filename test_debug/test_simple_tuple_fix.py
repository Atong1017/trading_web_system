#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡單測試 tuple index 錯誤修正
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import polars as pl
from datetime import datetime, timedelta

def test_polars_row_access():
    """測試 polars row 存取"""
    print("=== 測試 Polars Row 存取 ===")
    
    # 建立測試資料
    data = [
        {'date': datetime(2024, 1, 1), 'open': 100, 'close': 105},
        {'date': datetime(2024, 1, 2), 'open': 105, 'close': 110},
        {'date': datetime(2024, 1, 3), 'open': 110, 'close': 108}
    ]
    
    df = pl.DataFrame(data)
    print(f"資料框架: {df}")
    
    # 測試 row() 方法
    try:
        # 錯誤的方式（會導致 tuple index 錯誤）
        row = df.row(0)
        print(f"Row 0 (tuple): {row}")
        print(f"Row 0 type: {type(row)}")
        
        # 正確的方式（使用 named=True）
        named_row = df.row(0, named=True)
        print(f"Named Row 0: {named_row}")
        print(f"Named Row 0 type: {type(named_row)}")
        
        # 測試存取欄位
        print(f"Date from named row: {named_row['date']}")
        print(f"Open from named row: {named_row['open']}")
        
        print("✓ 測試通過！")
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_polars_row_access()
    if success:
        print("所有測試通過！")
    else:
        print("測試失敗！") 