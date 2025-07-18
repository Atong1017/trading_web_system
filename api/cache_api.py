#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快取管理API模組
包含快取資訊查詢、清理等功能
"""

import os
import pickle
from typing import Dict, List, Any
from fastapi import HTTPException, Request

from core.cache_manager import cache_manager

def print_log(message: str):
    """日誌輸出"""
    print(f"********** cache_api.py - {message}")

class CacheAPI:
    """快取API類別"""
    
    @staticmethod
    async def get_cache_info():
        """取得快取資訊"""
        try:
            info = cache_manager.get_cache_info()
            return {"status": "success", "info": info}
        except Exception as e:
            print_log(f"get_cache_info error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_cache_files():
        """取得快取檔案列表，用於策略表格選擇"""
        try:
            info = cache_manager.get_cache_info()
            
            # 只返回快取檔案資訊，用於前端選擇
            cache_files = info.get('cache_files', [])
            
            # 按資料類型分組
            grouped_files = {}
            for file_info in cache_files:
                data_type = file_info.get('data_type', 'unknown')
                if data_type not in grouped_files:
                    grouped_files[data_type] = []
                grouped_files[data_type].append(file_info)
            
            return {
                "status": "success", 
                "data": {
                    "files": cache_files,
                    "grouped_files": grouped_files
                }
            }
        except Exception as e:
            print_log(f"get_cache_files error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def clear_cache(request: Request):
        """清理快取"""
        try:
            data = await request.json()
            cache_type = data.get("cache_type", "all")
            
            success = cache_manager.clear_cache(cache_type)
            
            if success:
                return {"status": "success", "message": f"快取清理成功 ({cache_type})"}
            else:
                raise HTTPException(status_code=500, detail="快取清理失敗")
        except Exception as e:
            print_log(f"clear_cache error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def remove_cache_item(cache_key: str):
        """移除特定快取項目"""
        try:
            print_log(f"嘗試移除快取項目: {cache_key}")
            
            # 調用快取管理器的移除方法
            success = cache_manager.remove_cache_item(cache_key)
            
            if success:
                print_log(f"快取項目移除成功: {cache_key}")
                return {"status": "success", "message": "快取項目移除成功"}
            else:
                print_log(f"快取項目移除失敗: {cache_key}")
                raise HTTPException(status_code=500, detail="快取項目移除失敗")
        except Exception as e:
            print_log(f"remove_cache_item error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_cache_data(cache_file: str):
        """根據快取檔案名稱取得快取資料"""
        try:
            # 從快取檔案名稱解析出快取鍵值
            # 快取檔案名稱格式：{cache_key}.pkl
            if not cache_file.endswith('.pkl'):
                cache_file = f"{cache_file}.pkl"
            
            cache_key = cache_file.replace('.pkl', '')
            
            # 從快取管理器的元資料中找到對應的快取資訊
            info = cache_manager.get_cache_info()
            cache_files = info.get('cache_files', [])
            
            # 找到對應的快取檔案資訊
            target_cache = None
            for cache_info in cache_files:
                if cache_info.get('cache_key') == cache_key:
                    target_cache = cache_info
                    break
            
            if not target_cache:
                raise HTTPException(status_code=404, detail="快取檔案不存在")
            
            # 從快取檔案載入資料
            cache_file_path = os.path.join(cache_manager.cache_dir, cache_file).replace('\\', '/')
            
            if not os.path.exists(cache_file_path):
                raise HTTPException(status_code=404, detail="快取檔案不存在")
            
            # 載入快取資料
            with open(cache_file_path, 'rb') as f:
                import pickle
                data = pickle.load(f)
            
            return data
            
        except Exception as e:
            print_log(f"get_cache_data error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_cache_data_api(request: Request):
        """API 端點：根據快取檔案名稱取得快取資料，返回 JSON 格式"""
        try:
            data = await request.json()
            cache_file = data.get("cache_file")
            
            if not cache_file:
                raise HTTPException(status_code=400, detail="缺少快取檔案參數")
            
            # 使用現有的 get_cache_data 方法取得資料
            cache_data = await CacheAPI.get_cache_data(cache_file)
            
            # 將 Polars DataFrame 轉換為字典格式（JSON 可序列化）
            if hasattr(cache_data, 'to_dicts'):
                # 如果是 Polars DataFrame
                data_dict = cache_data.to_dicts()
            elif hasattr(cache_data, 'to_dict'):
                # 如果是 Pandas DataFrame
                data_dict = cache_data.to_dict('records')
            else:
                # 其他格式，嘗試直接轉換
                data_dict = cache_data
            
            return {
                "status": "success",
                "data": data_dict,
                "cache_file": cache_file
            }
            
        except Exception as e:
            print_log(f"get_cache_data_api error: {e}")
            return {
                "status": "error",
                "message": str(e)
            } 