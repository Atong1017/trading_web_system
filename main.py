#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI主程式 - 簡化版本
重構後的模組化版本
"""

import os
import traceback
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 導入自定義模組
from config.trading_config import TradingConfig
from config.api_config import APIConfig
from core.utils import Utils
from core.cache_manager import cache_manager
from strategies.strategy_manager import StrategyManager
from core.data_provider import DataProvider
from core.stock_list_manager import StockListManager

# 導入路由模組
from routes.pages import router as pages_router
from routes.api_routes import router as api_router

def print_log(message: str):
    """日誌輸出"""
    print(f"********** main.py - {message}")

# 建立FastAPI應用
app = FastAPI(
    title="台灣股票回測+自動下單系統",
    description="完整的台灣股票回測和自動下單系統",
    version="1.0.0"
)

# 設定CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定靜態檔案
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 確保目錄存在
Utils.ensure_directory("data/uploads".replace('\\', '/'))
Utils.ensure_directory("data/exports".replace('\\', '/'))

# FastAPI 啟動事件 - 初始化所有管理器
@app.on_event("startup")
async def startup_event():
    try:
        app.state.strategy_manager = StrategyManager()
        app.state.data_provider = DataProvider()
        app.state.stock_list_manager = StockListManager()
        app.state.cache_manager = cache_manager
        
        print_log("FastAPI 啟動事件：所有管理器初始化成功")
        
    except Exception as e:
        print_log(f"FastAPI 啟動事件初始化失敗: {e}")
        print_log(f"錯誤詳情: {traceback.format_exc()}")
        raise

# 註冊路由
app.include_router(pages_router)
app.include_router(api_router)

# 錯誤處理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="web/templates")
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="web/templates")
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(
        "main_simplified:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 