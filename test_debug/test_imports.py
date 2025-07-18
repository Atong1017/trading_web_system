#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試所有導入是否正常
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """測試所有導入"""
    print("開始測試導入...")
    
    try:
        print("1. 測試基本模組...")
        import os
        import asyncio
        import polars as pl
        from typing import Dict, List, Any, Optional
        from datetime import datetime
        print("✅ 基本模組導入成功")
        
        print("2. 測試 FastAPI 模組...")
        from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
        from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
        print("✅ FastAPI 模組導入成功")
        
        print("3. 測試其他模組...")
        import json
        import tempfile
        import shutil
        import concurrent.futures
        from functools import partial
        print("✅ 其他模組導入成功")
        
        print("4. 測試自定義模組...")
        from config.trading_config import TradingConfig
        from config.api_config import APIConfig
        from core.utils import Utils
        from core.price_utils import PriceUtils
        from core.cache_manager import cache_manager
        print("✅ 核心模組導入成功")
        
        print("5. 測試策略模組...")
        from strategies.day_trading import DayTradingStrategy
        from strategies.swing_trading import SwingTradingStrategy
        from strategies.bookbuilding import BookbuildingStrategy
        from strategies.dynamic_strategy import DynamicStrategy
        from strategies.strategy_manager import StrategyManager
        print("✅ 策略模組導入成功")
        
        print("6. 測試其他核心模組...")
        from core.data_provider import DataProvider
        from core.stock_list_manager import StockListManager
        from api.stock_api import StockAPI
        from api.broker_api import BrokerAPI
        print("✅ 其他核心模組導入成功")
        
        print("\n🎉 所有導入測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 導入測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports() 