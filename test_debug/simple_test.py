#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試腳本
"""

print("開始測試...")

try:
    from api.chart_api import ChartAPI
    print("ChartAPI 導入成功")
except Exception as e:
    print(f"ChartAPI 導入失敗: {e}")

try:
    import plotly.graph_objects as go
    print("plotly 導入成功")
except Exception as e:
    print(f"plotly 導入失敗: {e}")

try:
    import polars as pl
    print("polars 導入成功")
except Exception as e:
    print(f"polars 導入失敗: {e}")

print("測試完成") 