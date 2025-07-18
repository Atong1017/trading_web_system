#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
範例資料API模組
包含範例資料類型管理和載入功能
"""

from typing import Dict, List, Any
from fastapi import HTTPException, Request

from core.data_provider import DataProvider

def print_log(message: str):
    """日誌輸出"""
    print(f"********** sample_data_api.py - {message}")

class SampleDataAPI:
    """範例資料API類別"""
    
    @staticmethod
    async def get_sample_data_types(request: Request):
        """取得可用的範例資料類型"""
        try:
            data_provider = request.app.state.data_provider
            types = data_provider.get_data_types()
            return {"status": "success", "types": types}
        except Exception as e:
            print_log(f"get_sample_data_types error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def load_sample_data(request: Request):
        """載入範例資料"""
        try:
            data = await request.json()
            data_type_id = data.get('data_type')
            parameters = data.get('parameters', {})
            
            if not data_type_id:
                raise HTTPException(status_code=400, detail="缺少資料類型參數")
            
            # 載入資料
            data_provider = request.app.state.data_provider
            result_data = await data_provider.load_data(data_type_id, parameters)
            
            return {"status": "success", "data": result_data}
        except Exception as e:
            print_log(f"load_sample_data error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_sample_data_type(data_type_id: str, request: Request):
        """取得特定資料類型資訊"""
        print(1111111111111)
        try:
            data_provider = request.app.state.data_provider
            data_type = data_provider.get_data_type(data_type_id)
            if not data_type:
                raise HTTPException(status_code=404, detail="資料類型不存在")
            
            return {"status": "success", "data_type": data_type}
        except Exception as e:
            print_log(f"get_sample_data_type error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def add_sample_data_type(request: Request):
        """新增範例資料類型"""
        try:
            data = await request.json()
            
            if not data.get('id'):
                raise HTTPException(status_code=400, detail="缺少資料類型ID")
            
            data_provider = request.app.state.data_provider
            success = data_provider.add_data_type(data)
            if not success:
                raise HTTPException(status_code=400, detail="新增資料類型失敗")
            
            # 儲存到檔案
            data_provider.save_data_types()
            
            return {"status": "success", "message": "資料類型新增成功"}
        except Exception as e:
            print_log(f"add_sample_data_type error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def remove_sample_data_type(data_type_id: str, request: Request):
        """移除範例資料類型"""
        try:
            data_provider = request.app.state.data_provider
            success = data_provider.remove_data_type(data_type_id)
            if not success:
                raise HTTPException(status_code=404, detail="資料類型不存在")
            
            # 儲存到檔案
            data_provider.save_data_types()
            
            return {"status": "success", "message": "資料類型移除成功"}
        except Exception as e:
            print_log(f"remove_sample_data_type error: {e}")
            raise HTTPException(status_code=500, detail=str(e)) 