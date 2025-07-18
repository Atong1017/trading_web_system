#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
頁面路由模組
包含所有頁面的路由定義
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

def print_log(message: str):
    """日誌輸出"""
    print(f"********** pages.py - {message}")

# 設定模板
templates = Jinja2Templates(directory="web/templates")

# 建立路由器
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/backtest", response_class=HTMLResponse)
async def backtest_page(request: Request):
    """回測頁面"""
    return templates.TemplateResponse("backtest.html", {"request": request})

@router.get("/auto-trading", response_class=HTMLResponse)
async def auto_trading_page(request: Request):
    """自動下單頁面"""
    return templates.TemplateResponse("auto_trading.html", {"request": request})

@router.get("/trading-records", response_class=HTMLResponse)
async def trading_records_page(request: Request):
    """交易記錄頁面"""
    return templates.TemplateResponse("trading_records.html", {"request": request})

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """設定頁面"""
    return templates.TemplateResponse("settings.html", {"request": request})

@router.get("/strategy-editor", response_class=HTMLResponse)
async def strategy_editor_page(request: Request):
    """策略編輯器頁面"""
    return templates.TemplateResponse("strategy_editor.html", {"request": request})

@router.get("/cache-manager", response_class=HTMLResponse)
async def cache_manager_page(request: Request):
    """快取管理頁面"""
    return templates.TemplateResponse("cache_manager.html", {"request": request})

@router.get("/stock-selector", response_class=HTMLResponse)
async def stock_selector_page(request: Request):
    """選股編輯器頁面"""
    return templates.TemplateResponse("stock_selector.html", {"request": request}) 