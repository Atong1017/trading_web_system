#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由模組初始化檔案
"""

from .pages import router as pages_router
from .api_routes import router as api_router

__all__ = ['pages_router', 'api_router'] 