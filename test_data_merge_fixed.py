import polars as pl
import os
import sys
import tempfile
from datetime import datetime
import json

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.cache_manager import CacheManager
from core.stock_list_manager import StockListManager

def print_log(message):
    print(f"********** test_data_merge_fixed.py - {message}")

def test_data_merge():
    """測試上傳Excel和使用快取的功能，並合併兩個資料來源"""
    
    print_log("開始測試資料合併功能")
    
    try:
        # 1. 初始化快取管理器
        print_log("初始化快取管理器")
        cache_manager = CacheManager()
        
        # 2. 初始化股票清單管理器
        print_log("初始化股票清單管理器")
        stock_list_manager = StockListManager()
        
        # 3. 建立測試Excel檔案
        print_log("建立測試Excel檔案")
        test_excel_data = {
            "stock_id": ["2330", "2317", "2454", "3008", "2412"],
            "date": ["2024-01-01", "2024-01-01", "2024-01-01", "2024-01-01", "2024-01-01"],
            "price": [500.0, 120.5, 85.2, 45.8, 78.9],
            "volume": [1000000, 500000, 300000, 200000, 400000]
        }
        
        # 建立臨時Excel檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as f:
            temp_excel_path = f.name
        
        # 將測試資料寫入Excel檔案
        test_df = pl.DataFrame(test_excel_data)
        
        # 5. 建立快取資料
        print_log("建立快取資料")
        cache_data = {
            "stock_id": ["2330", "2317", "2454", "3008", "2412"],
            "date": ["2024-01-01", "2024-01-01", "2024-01-01", "2024-01-01", "2024-01-01"],
            "open": [498.0, 119.0, 84.5, 45.2, 78.0],
            "high": [502.0, 122.0, 86.0, 46.5, 79.5],
            "low": [497.0, 118.5, 84.0, 44.8, 77.5],
            "close": [500.0, 120.5, 85.2, 45.8, 78.9],
            "volume": [1000000, 500000, 300000, 200000, 400000]
        }
        
        cache_df = pl.DataFrame(cache_data)
        print_log(f"快取資料內容:\n{cache_df}")
        test_df = test_df.with_columns(pl.col("date").cast(pl.Utf8))
        cache_df = cache_df.with_columns(pl.col("date").cast(pl.Utf8))
        
        print(131313133131)
        # 合併資料（使用stock_id和date作為合併鍵）
        merged_df = test_df.join(
            cache_df,
            on=["stock_id", "date"],
            how="inner"
        )
        
        print_log(f"22222222合併後的資料:\n{merged_df}")
        print_log(f"合併後資料欄位: {merged_df.columns}")
        print_log(f"合併後資料行數: {len(merged_df)}")
        
        # 9. 驗證合併結果
        print_log("驗證合併結果")
        
        # 檢查是否有重複的stock_id和date組合
        duplicate_check = merged_df.group_by(["stock_id", "date"]).count()
        print_log(f"重複檢查結果:\n{duplicate_check}")
        
        # 檢查資料完整性
        null_check = merged_df.null_count()
        print_log(f"空值檢查結果:\n{null_check}")
        
        # 10. 儲存合併結果
        print_log("儲存合併結果")
        output_path = "data/exports/merged_data.xlsx"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        merged_df.write_excel(output_path)
        print_log(f"合併結果已儲存至: {output_path}")
        
        # 11. 清理臨時檔案
        print_log("清理臨時檔案")
        os.unlink(temp_excel_path)
        
        print_log("測試完成！")
        
        return {
            "success": True,
            "excel_data": excel_df,
            "cache_data": loaded_cache_df,
            "merged_data": merged_df,
            "output_path": output_path
        }
        
    except Exception as e:
        print_log(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

def test_cache_operations():
    """測試快取操作功能"""
    
    print_log("開始測試快取操作功能")
    
    try:
        cache_manager = CacheManager()
        
        # 建立測試資料
        test_data = {
            "stock_id": ["2330", "2317"],
            "date": ["2024-01-01", "2024-01-01"],
            "price": [500.0, 120.5]
        }
        
        test_df = pl.DataFrame(test_data)
        
        # 測試儲存快取
        cache_key = "test_cache_operations"
        cache_manager.save_cache(cache_key, test_df)
        print_log("快取儲存成功")
        
        # 測試載入快取
        loaded_df = cache_manager.load_cache(cache_key)
        print_log(f"快取載入成功:\n{loaded_df}")
        
        # 測試快取是否存在
        exists = cache_manager.cache_exists(cache_key)
        print_log(f"快取存在檢查: {exists}")
        
        # 測試刪除快取
        cache_manager.delete_cache(cache_key)
        print_log("快取刪除成功")
        
        # 驗證刪除
        exists_after_delete = cache_manager.cache_exists(cache_key)
        print_log(f"刪除後快取存在檢查: {exists_after_delete}")
        
        print_log("快取操作測試完成！")
        
        return True
        
    except Exception as e:
        print_log(f"快取操作測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_list_operations():
    """測試股票清單操作功能"""
    
    print_log("開始測試股票清單操作功能")
    
    try:
        stock_list_manager = StockListManager()
        
        # 建立測試股票清單
        test_stocks = [
            {"stock_id": "2330", "stock_name": "台積電"},
            {"stock_id": "2317", "stock_name": "鴻海"},
            {"stock_id": "2454", "stock_name": "聯發科"}
        ]
        
        # 測試儲存股票清單
        list_name = "test_stock_list"
        stock_list_manager.save_stock_list(list_name, test_stocks)
        print_log("股票清單儲存成功")
        
        # 測試載入股票清單
        loaded_stocks = stock_list_manager.load_stock_list(list_name)
        print_log(f"股票清單載入成功: {loaded_stocks}")
        
        # 測試取得所有股票清單
        all_lists = stock_list_manager.get_all_stock_lists()
        print_log(f"所有股票清單: {all_lists}")
        
        # 測試刪除股票清單
        stock_list_manager.delete_stock_list(list_name)
        print_log("股票清單刪除成功")
        
        print_log("股票清單操作測試完成！")
        
        return True
        
    except Exception as e:
        print_log(f"股票清單操作測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("開始執行資料合併測試")
    print("=" * 50)
    
    # 執行主要測試
    result = test_data_merge()
    
    if result["success"]:
        print("\n" + "=" * 50)
        print("主要測試成功！")
        print("=" * 50)
        
        # 執行額外測試
        print("\n執行快取操作測試...")
        cache_result = test_cache_operations()
        
        print("\n執行股票清單操作測試...")
        stock_list_result = test_stock_list_operations()
        
        print("\n" + "=" * 50)
        print("所有測試完成！")
        print(f"主要測試: {'成功' if result['success'] else '失敗'}")
        print(f"快取操作測試: {'成功' if cache_result else '失敗'}")
        print(f"股票清單測試: {'成功' if stock_list_result else '失敗'}")
        print("=" * 50)
        
    else:
        print(f"\n主要測試失敗: {result['error']}") 