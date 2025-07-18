#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
選股列表API模組
包含選股列表的CRUD操作和匯入匯出功能
"""

import os
import shutil
from typing import Dict, List, Any
from fastapi import HTTPException, Request, File, UploadFile

from core.stock_list_manager import StockListManager

def print_log(message: str):
    """日誌輸出"""
    print(f"********** stock_list_api.py - {message}")

class StockListAPI:
    """選股列表API類別"""
    
    @staticmethod
    async def get_stock_lists(request: Request):
        """取得所有選股列表"""
        try:
            stock_list_manager = request.app.state.stock_list_manager
            stock_lists = stock_list_manager.get_all_stock_lists()
            return {"status": "success", "stock_lists": stock_lists}
        except Exception as e:
            print_log(f"get_stock_lists error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_stock_list(stock_list_id: str, request: Request):
        """取得特定選股列表"""
        try:
            stock_list_manager = request.app.state.stock_list_manager
            stock_list = stock_list_manager.get_stock_list(stock_list_id)
            if not stock_list:
                raise HTTPException(status_code=404, detail="選股列表不存在")
            
            return {"status": "success", "stock_list": stock_list}
        except Exception as e:
            print_log(f"get_stock_list error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def create_stock_list(request: Request):
        """建立新的選股列表"""
        try:
            data = await request.json()
            name = data.get("name")
            description = data.get("description", "")
            
            if not name:
                raise HTTPException(status_code=400, detail="選股列表名稱不能為空")
            
            stock_list_manager = request.app.state.stock_list_manager
            stock_list_id = stock_list_manager.create_stock_list(name, description)
            
            return {"status": "success", "stock_list_id": stock_list_id}
        except Exception as e:
            print_log(f"create_stock_list error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def update_stock_list(stock_list_id: str, request: Request):
        """更新選股列表"""
        try:
            data = await request.json()
            name = data.get("name")
            description = data.get("description")
            stocks = data.get("stocks")
            
            stock_list_manager = request.app.state.stock_list_manager
            success = stock_list_manager.update_stock_list(
                stock_list_id, name, description, stocks
            )
            
            if success:
                return {"status": "success", "message": "選股列表更新成功"}
            else:
                raise HTTPException(status_code=404, detail="選股列表不存在")
        except Exception as e:
            print_log(f"update_stock_list error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def delete_stock_list(stock_list_id: str, request: Request):
        """刪除選股列表"""
        try:
            stock_list_manager = request.app.state.stock_list_manager
            success = stock_list_manager.delete_stock_list(stock_list_id)
            
            if success:
                return {"status": "success", "message": "選股列表刪除成功"}
            else:
                raise HTTPException(status_code=404, detail="選股列表不存在")
        except Exception as e:
            print_log(f"delete_stock_list error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def import_stocks_from_excel(file: UploadFile, request: Request):
        """從Excel檔案匯入股票"""
        try:
            # 儲存上傳的檔案
            temp_file_path = f"data/uploads/temp_{file.filename}".replace('\\', '/')
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 匯入股票
            stock_list_manager = request.app.state.stock_list_manager
            stocks = stock_list_manager.import_stocks_from_excel(temp_file_path)
            
            # 清理臨時檔案
            os.remove(temp_file_path)
            
            return {"status": "success", "stocks": stocks}
        except Exception as e:
            print_log(f"import_stocks_from_excel error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def apply_stock_conditions(request: Request):
        """套用選股條件"""
        try:
            data = await request.json()
            conditions = data.get("conditions", [])
            
            stock_list_manager = request.app.state.stock_list_manager
            stocks = stock_list_manager.apply_stock_conditions(conditions)
            
            return {"status": "success", "stocks": stocks}
        except Exception as e:
            print_log(f"apply_stock_conditions error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def export_stock_list_to_strategy(request: Request):
        """匯出選股列表到策略"""
        try:
            data = await request.json()
            stock_list_id = data.get("stock_list_id")
            strategy_id = data.get("strategy_id")
            stocks = data.get("stocks", [])
            
            if not stock_list_id or not strategy_id:
                raise HTTPException(status_code=400, detail="缺少必要參數")
            
            # 更新選股列表
            stock_list_manager = request.app.state.stock_list_manager
            stock_list_manager.update_stock_list(stock_list_id, stocks=stocks)
            
            # 更新策略的股票來源設定
            strategy_manager = request.app.state.strategy_manager
            strategy = strategy_manager.get_strategy(strategy_id)
            if strategy:
                strategy['stock_source'] = 'stock_list'
                strategy['stock_list_id'] = stock_list_id
                strategy_manager.update_strategy(strategy_id, strategy['name'], 
                                               strategy['description'], strategy['code'])
            
            return {"status": "success", "message": "匯出成功"}
        except Exception as e:
            print_log(f"export_stock_list_to_strategy error: {e}")
            raise HTTPException(status_code=500, detail=str(e)) 