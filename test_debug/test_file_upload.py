#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試檔案上傳和讀取功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import os
import shutil
import polars as pl
from core.utils import Utils

def create_test_excel():
    """建立測試Excel檔案"""
    # 建立測試資料
    test_data = {
        "stock_id": ["2330", "2317", "2330", "2317"],
        "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
        "open": [100.0, 50.0, 101.0, 51.0],
        "high": [105.0, 55.0, 106.0, 56.0],
        "low": [98.0, 48.0, 99.0, 49.0],
        "close": [103.0, 53.0, 104.0, 54.0]
    }
    
    df = pl.DataFrame(test_data)
    return df

def test_file_upload_simulation():
    """模擬檔案上傳過程"""
    print("=== 測試檔案上傳模擬 ===")
    
    # 建立測試資料
    test_df = create_test_excel()
    print(f"原始資料: {test_df.shape}, 欄位: {test_df.columns}")
    
    # 模擬檔案上傳過程
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    print(f"臨時檔案路徑: {temp_file.name}")
    
    try:
        # 儲存測試資料到臨時檔案
        test_df.write_excel(temp_file.name, worksheet="測試資料")
        temp_file.flush()
        temp_file.close()
        
        # 檢查檔案是否存在
        print(f"檔案存在: {os.path.exists(temp_file.name)}")
        print(f"檔案大小: {os.path.getsize(temp_file.name)} bytes")
        
        # 嘗試讀取檔案
        print("嘗試讀取檔案...")
        excel_data = Utils.read_excel_file(temp_file.name)
        print(f"讀取結果: {excel_data.shape}, 欄位: {excel_data.columns}")
        
        if not excel_data.is_empty():
            print("✅ 檔案讀取成功！")
            print(f"資料預覽:\n{excel_data.head()}")
        else:
            print("❌ 檔案讀取失敗：資料為空")
            
    except Exception as e:
        print(f"❌ 檔案處理失敗: {str(e)}")
        
    finally:
        # 清理臨時檔案
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
            print("臨時檔案已清理")

if __name__ == "__main__":
    test_file_upload_simulation() 