#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖表相關API模組
包含回測圖表生成等功能
"""

import os
from typing import Dict, List, Any
from datetime import datetime

import polars as pl
from fastapi import HTTPException, Request
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.utils import Utils

def print_log(message: str):
    """日誌輸出"""
    print(f"********** chart_api.py - {message}")

class ChartAPI:
    """圖表API類別"""
    
    @staticmethod
    async def generate_charts(request: Request):
        """生成回測圖表"""
        try:
            data = await request.json()
            chart_type = data.get("chart_type", "")
            trade_records = data.get("trade_records", [])
            
            if not trade_records:
                raise HTTPException(status_code=400, detail="沒有交易記錄可生成圖表")
            
            # 轉換為DataFrame並標準化欄位名稱
            df = pl.DataFrame(trade_records)
            
            # 標準化欄位名稱 - 避免重複欄位名稱
            column_mapping = {
                'entry_date': '年月日',
                'exit_date': '出場日期',
                'stock_id': '證券代碼',
                'stock_name': '證券名稱',
                'profit_loss': '報酬',
                'net_profit_loss': '淨損益',
                'profit': '損益',
                'shares': '股數',
                'entry_price': '進場價',
                'exit_price': '出場價',
                'buy_amount': '買入金額',
                'sell_amount': '賣出金額',
                'commission': '手續費',
                'securities_tax': '證交稅',
                'holding_days': '持有天數',
                'exit_reason': '出場原因',
                'exit_status': '出場狀態',
                'trade_direction': '交易方向',
                'current_price': '當前價格',
                'unrealized_profit_loss': '未實現損益',
                'unrealized_profit_loss_rate': '未實現損益率',
                'current_date': '當前日期',
                'exit_price_type': '出場價類型',
                'current_entry_price': '當前進場價',
                'current_exit_price': '當前出場價',
                'current_profit_loss': '當前損益',
                'current_profit_loss_rate': '當前損益率',
                'take_profit_price': '停利價',
                'stop_loss_price': '停損價',
                'open_price': '開盤價',
                'high_price': '最高價',
                'low_price': '最低價',
                'close_price': '收盤價',
                '明日開盤': '明日開盤價'
            }
            
            # 重命名欄位
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns:
                    df = df.rename({old_name: new_name})
            
            # 統一損益欄位名稱 - 優先使用 '報酬'，如果沒有則使用其他損益欄位
            if '報酬' not in df.columns:
                if '淨損益' in df.columns:
                    df = df.rename({'淨損益': '報酬'})
                elif '損益' in df.columns:
                    df = df.rename({'損益': '報酬'})
                elif 'profit_loss' in df.columns:
                    df = df.rename({'profit_loss': '報酬'})
                elif 'net_profit_loss' in df.columns:
                    df = df.rename({'net_profit_loss': '報酬'})
                elif 'profit' in df.columns:
                    df = df.rename({'profit': '報酬'})
            
            # 確保有報酬欄位
            if '報酬' not in df.columns:
                raise HTTPException(status_code=400, detail="找不到損益欄位，請確保資料包含 profit_loss、net_profit_loss 或 profit 欄位")
            
            # 根據圖表類型生成不同的圖表
            if chart_type == "drawdown":
                chart_html = ChartAPI._create_drawdown_chart(df)
            elif chart_type == "drawdown_merge":
                chart_html = ChartAPI._create_drawdown_chart_merge(df)
            elif chart_type == "heatmap":
                chart_html = ChartAPI._create_heatmap(df)
            elif chart_type == "monthly_return_heatmap":
                chart_html = ChartAPI._create_monthly_return_heatmap(df)
            elif chart_type == "yearly_return_heatmap":
                chart_html = ChartAPI._create_yearly_return_heatmap(df)
            elif chart_type == "trading_days_heatmap":
                chart_html = ChartAPI._create_trading_days_heatmap(df)
            elif chart_type == "trading_stocks_heatmap":
                chart_html = ChartAPI._create_trading_stocks_heatmap(df)
            elif chart_type == "win_rate_heatmap":
                chart_html = ChartAPI._create_win_rate_heatmap(df)
            elif chart_type == "weekday_analysis_charts":
                chart_html = ChartAPI._create_weekday_analysis_charts(df)
            else:
                raise HTTPException(status_code=400, detail=f"不支援的圖表類型: {chart_type}")
            
            return {
                "success": True,
                "chart_html": chart_html
            }
            
        except Exception as e:
            print_log(f"generate_charts error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def _create_drawdown_chart(df: pl.DataFrame) -> str:
        """創建回落圖（每檔股票分開）"""
        try:
            if df.is_empty():
                return "<p>沒有可顯示的結果資料。</p>"
            
            # 處理日期與報酬欄
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date),
                pl.col("報酬").cast(pl.Float64)
            ]).sort(["證券代碼", "年月日"])
            
            # 取得所有股票代碼
            stock_ids = df["證券代碼"].unique().to_list()
            
            fig = make_subplots(rows=len(stock_ids), cols=1, shared_xaxes=True, vertical_spacing=0.04,
                                subplot_titles=[f"{sid} 回落圖" for sid in stock_ids],
                                row_heights=[1/len(stock_ids)]*len(stock_ids))
            
            for idx, sid in enumerate(stock_ids):
                sdf = df.filter(pl.col("證券代碼") == sid)
                daily_returns = (
                    sdf.group_by("年月日")
                    .agg(pl.col("報酬").sum().alias("日報酬"))
                    .sort("年月日")
                )
                daily_returns = daily_returns.with_columns([
                    pl.col("日報酬").cum_sum().alias("累積報酬")
                ])
                cum_profit = daily_returns["累積報酬"].to_list()
                max_so_far = []
                drawdown = []
                high_marks = []
                max_val = float('-inf')
                for val in cum_profit:
                    max_val = max(max_val, val)
                    max_so_far.append(max_val)
                    drawdown.append(val - max_val)
                    high_marks.append(val == max_val)
                daily_returns = daily_returns.with_columns([
                    pl.Series("高點", max_so_far),
                    pl.Series("回落", drawdown),
                    pl.Series("新高點", high_marks)
                ])
                # 畫累積損益
                fig.add_trace(go.Scatter(
                    x=daily_returns["年月日"].to_list(),
                    y=daily_returns["累積報酬"].to_list(),
                    mode='lines+markers', name=f'{sid} 累積損益',
                    line=dict(color='blue')
                ), row=idx+1, col=1)
                # 畫最大回落
                fig.add_trace(go.Bar(
                    x=daily_returns["年月日"].to_list(),
                    y=daily_returns["回落"].to_list(),
                    name=f'{sid} 最大回落', marker_color='red', opacity=0.5
                ), row=idx+1, col=1)
            
            fig.update_layout(
                height=350*len(stock_ids),
                title='各股績效與回落圖',
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(orientation='h', yanchor='top', y=1.02, xanchor='center', x=0.5),
                font=dict(color='black'),
                margin=dict(t=60, b=40, l=40, r=40)
            )
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建回落圖時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_drawdown_chart_merge(df: pl.DataFrame) -> str:
        """合併所有股票的回落圖（組合績效）"""
        try:
            if df.is_empty():
                return "<p>沒有可顯示的結果資料。</p>"
            
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date),
                pl.col("報酬").cast(pl.Float64)
            ]).sort("年月日")
            
            # 合併所有股票的每日報酬
            daily_returns = (
                df.group_by("年月日")
                .agg(pl.col("報酬").sum().alias("日報酬"))
                .sort("年月日")
            )
            daily_returns = daily_returns.with_columns([
                pl.col("日報酬").cum_sum().alias("累積報酬")
            ])
            cum_profit = daily_returns["累積報酬"].to_list()
            max_so_far = []
            drawdown = []
            high_marks = []
            max_val = float('-inf')
            for val in cum_profit:
                max_val = max(max_val, val)
                max_so_far.append(max_val)
                drawdown.append(val - max_val)
                high_marks.append(val == max_val)
            daily_returns = daily_returns.with_columns([
                pl.Series("高點", max_so_far),
                pl.Series("回落", drawdown),
                pl.Series("新高點", high_marks)
            ])
            
            # 畫圖
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                                row_heights=[0.7, 0.3], subplot_titles=["累積損益", "最大回落"])
            fig.add_trace(go.Scatter(
                x=daily_returns["年月日"].to_list(),
                y=daily_returns["累積報酬"].to_list(),
                mode='lines+markers', name='累積損益', line=dict(color='blue')
            ), row=1, col=1)
            fig.add_trace(go.Bar(
                x=daily_returns["年月日"].to_list(),
                y=daily_returns["回落"].to_list(),
                name='最大回落', marker_color='red'
            ), row=2, col=1)
            fig.update_layout(
                height=700, title='組合績效與回落圖', plot_bgcolor='white', paper_bgcolor='white',
                legend=dict(orientation='h', yanchor='top', y=1.02, xanchor='center', x=0.5),
                font=dict(color='black'), margin=dict(t=60, b=40, l=40, r=40)
            )
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建合併回落圖時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_heatmap(df: pl.DataFrame) -> str:
        """月實際損益熱力圖（萬元）"""
        try:
            if df.is_empty():
                return "<p>沒有資料產生熱力圖。</p>"
            
            # 確保年月日欄位是日期類型
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date).alias("年月日")
            ])
            
            # 提取年份和月份
            df = df.with_columns([
                pl.col("年月日").dt.year().alias("年"),
                pl.col("年月日").dt.month().alias("月")
            ])
            
            pivot_table = df.group_by(["年", "月"]).agg([
                pl.col("報酬").sum().alias("報酬")
            ]).pivot(values="報酬", index="年", columns="月").fill_nan(0)
            
            month_cols = sorted([col for col in pivot_table.columns if isinstance(col, int) or (isinstance(col, str) and col.isdigit())], key=int)
            # 按年份降序排序（新到舊）
            pivot_table = pivot_table.sort("年", descending=True)
            years = pivot_table["年"].to_list()
            z = pivot_table.select(month_cols).to_numpy() / 10000  # 單位：萬元
            text = [[f"{v:.2f}" if v != 0 else "" for v in row] for row in z]
            
            min_value = z.min()
            max_value = z.max()
            if min_value == max_value:
                colorscale = [[0, '#FFEE9C'], [1, 'green']] if min_value >= 0 else [[0, 'red'], [1, '#FFEE9C']]
            else:
                middle_point = (0 - min_value) / (max_value - min_value)
                middle_point = max(0, min(1, middle_point))
                colorscale = [[0, 'red'], [middle_point, '#FFEE9C'], [1, 'green']]
            
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=[str(m) for m in month_cols],
                y=[str(y) for y in years],
                colorscale=colorscale,
                showscale=False,
                text=text,
                texttemplate="%{text}",
                textfont={"size": 14, "color": "black"}
            ))
            
            plot_height = 50 * len(years)
            fig.update_layout(
                title={
                    'text': '月累積平均損益 (萬元)',
                    'font': {'size': 15},
                    'y': 0.94,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis=dict(title='月'),
                yaxis=dict(title='年'),
                height=plot_height + 100,
                width=700,
                margin=dict(t=60, l=40, r=40, b=40),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建熱力圖時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_monthly_return_heatmap(df: pl.DataFrame) -> str:
        """月平均收益率熱力圖（bp）— 使用單筆損益計算"""
        try:
            if df.is_empty():
                return "<p>沒有資料產生熱力圖。</p>"
            
            # 確保年月日欄位是日期類型
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date).alias("年月日")
            ])
            
            # 提取年份和月份
            df = df.with_columns([
                pl.col("年月日").dt.year().alias("年"),
                pl.col("年月日").dt.month().alias("月"),
                ((pl.col("報酬") / pl.col("進場價")) * 10000).alias("單筆收益率bp")
            ])
            
            # 過濾有效交易
            if "明日開盤價" in df.columns:
                df = df.filter(pl.col("明日開盤價").is_not_null() & (pl.col("股數") > 0))
            else:
                df = df.filter(pl.col("出場價").is_not_null() & (pl.col("股數") > 0))
                
            grouped = df.group_by(["年", "月"]).agg([
                pl.col("單筆收益率bp").mean().alias("月平均bp"),
                pl.count().alias("交易筆數")
            ]).filter(pl.col("交易筆數") > 0)
            
            pivot_table = grouped.pivot(
                values="月平均bp", index="年", columns="月"
            ).fill_nan(0)
            
            month_cols = sorted([col for col in pivot_table.columns if col != "年"], key=int)
            # 按年份降序排序（新到舊）
            pivot_table = pivot_table.sort("年", descending=True)
            years = pivot_table["年"].to_list()
            z = pivot_table.select(month_cols).to_numpy()
            text = [[f"{v:.0f}" if v != 0 else "" for v in row] for row in z]
            
            min_value, max_value = float(z.min()), float(z.max())
            if min_value == max_value:
                colorscale = [[0, '#FFEE9C'], [1, 'green']] if min_value >= 0 else [[0, 'red'], [1, '#FFEE9C']]
            else:
                mid = (0 - min_value) / (max_value - min_value)
                mid = max(0, min(1, mid))
                colorscale = [[0, 'red'], [mid, '#FFEE9C'], [1, 'green']]
            
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=[str(m) for m in month_cols],
                y=[str(y) for y in years],
                colorscale=colorscale,
                showscale=False,
                text=text,
                texttemplate="%{text}",
                textfont={"size": 12, "color": "black"}
            ))
            
            plot_height = 50 * len(years)
            fig.update_layout(
                title={
                    'text': '月平均收益率 (bp)',
                    'font': {'size': 15},
                    'y': 0.94,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis=dict(title='月'),
                yaxis=dict(title='年'),
                height=plot_height + 100,
                width=700,
                margin=dict(t=60, l=40, r=40, b=40),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建月收益率熱力圖時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_yearly_return_heatmap(df: pl.DataFrame) -> str:
        """年平均收益率熱力圖（bp）"""
        try:
            if df.is_empty():
                return "<p>沒有資料產生圖表。</p>"
            
            # 確保年月日欄位是日期類型
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date).alias("年月日")
            ])
            
            # 提取年份
            df = df.with_columns([
                pl.col("年月日").dt.year().alias("年"),
            ])
            
            # 按年加總損益，按年份降序排序
            df_yearly = df.group_by("年").agg(
                pl.col("報酬").sum().alias("總損益")
            ).sort("年", descending=True)
            
            years = df_yearly["年"].to_list()
            profits = (df_yearly["總損益"] / 10000).to_numpy()  # 單位轉成萬元
            
            # 創建柱狀圖
            fig = go.Figure(data=[
                go.Bar(
                    x=years,
                    y=profits,
                    text=[f"{v:.1f}萬" for v in profits],
                    textposition='auto',
                    marker_color='green',  # 設置柱狀圖顏色為綠色
                )
            ])
            
            plot_width = 100 * len(years)
            # 更新布局
            fig.update_layout(
                title={
                    'text': '年度總損益 (萬元)',
                    'font': {'size': 18},
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis=dict(
                    title='年份',
                    tickmode='array',
                    ticktext=years,
                    tickvals=years,
                ),
                yaxis=dict(
                    title='損益 (萬元)',
                    gridcolor='lightgray',  # 添加網格線
                ),
                height=300,
                width=plot_width + 100,
                margin=dict(t=60, l=50, r=30, b=40),
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=False,
                # 添加網格線
                yaxis_gridwidth=1,
                yaxis_gridcolor='rgba(211,211,211,0.3)',
            )
            
            # 添加水平參考線（零線）
            fig.add_hline(
                y=0, 
                line_dash="solid",
                line_color="gray",
                line_width=1
            )
            
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建年度損益圖表時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_trading_days_heatmap(df: pl.DataFrame) -> str:
        """月交易次數(天)熱力圖"""
        try:
            if df.is_empty():
                return "<p>沒有資料產生熱力圖。</p>"
            
            # 確保年月日欄位是日期類型
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date).alias("年月日")
            ])
            
            # 添加年份和月份列
            df = df.with_columns([
                pl.col("年月日").dt.year().alias("年"),
                pl.col("年月日").dt.month().alias("月")
            ])
            
            # 計算每個月的交易天數
            trading_days = df.group_by(["年", "月"]).agg(
                pl.n_unique("年月日").alias("交易天數")
            ).sort(["年", "月"])
            
            # 創建樞紐表
            pivot_table = trading_days.pivot(
                values="交易天數",
                index="年",
                columns="月"
            ).fill_null(0)
            
            # 獲取年份和月份
            # 按年份降序排序（新到舊）
            pivot_table = pivot_table.sort("年", descending=True)
            years = pivot_table["年"].to_list()
            month_cols = sorted([col for col in pivot_table.columns if isinstance(col, int) or (isinstance(col, str) and str(col).isdigit())], key=int)
            
            # 準備熱力圖數據
            z = pivot_table.select(month_cols).to_numpy()
            text = [[f"{int(v)}" if v != 0 else "0" for v in row] for row in z]
            
            # 創建熱力圖
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=[str(m) for m in month_cols],
                y=[str(y) for y in years],
                colorscale='Greens',  # 使用綠色色階
                text=text,
                texttemplate="%{text}",
                textfont={"size": 16, "color": "black"},
                showscale=False  # 不顯示顏色刻度
            ))
            
            plot_height = 50 * len(years)
            fig.update_layout(
                title={
                    'text': '月交易筆數(天)',  # 更新標題以反映實際顯示的內容
                    'font': {'size': 18},
                    'y': 0.98,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis=dict(
                    title='月',
                    ticktext=[str(i) for i in range(1, 13)],
                    tickvals=list(range(1, 13))
                ),
                yaxis=dict(
                    title='年'
                ),
                height=plot_height + 100,
                width=700,
                margin=dict(t=50, l=80, r=20, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建月交易次數熱力圖時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_trading_stocks_heatmap(df: pl.DataFrame) -> str:
        """月交易次數(隻)熱力圖"""
        try:
            if df.is_empty():
                return "<p>沒有資料產生熱力圖。</p>"
            
            # 確保年月日欄位是日期類型
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date).alias("年月日")
            ])
            
            # 添加年份和月份列
            df = df.with_columns([
                pl.col("年月日").dt.year().alias("年"),
                pl.col("年月日").dt.month().alias("月")
            ])
            
            # 計算每個年月的交易總筆數
            trading_days = df.group_by(["年", "月"]).agg(
                pl.col("證券代碼").n_unique().alias("交易股票數")
            ).sort(["年", "月"])  # 按年和月排序
            
            # 創建透視表
            pivot_table = trading_days.pivot(
                values="交易股票數",
                index="年",
                columns="月"
            ).fill_null(0)
            
            # 按年份降序排序（新到舊）
            pivot_table = pivot_table.sort("年", descending=True)
            years = pivot_table["年"].to_list()
            month_cols = sorted([col for col in pivot_table.columns if isinstance(col, int) or (isinstance(col, str) and str(col).isdigit())], key=int)
            
            z = pivot_table.select(month_cols).to_numpy()
            text = [[f"{int(v)}" if v != 0 else "0" for v in row] for row in z]
            
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=[str(m) for m in month_cols],
                y=[str(y) for y in years],
                colorscale='Greens',
                text=text,
                texttemplate="%{text}",
                textfont={"size": 16, "color": "black"},
                showscale=False
            ))
            
            plot_height = 50 * len(years)
            fig.update_layout(
                title={
                    'text': '月交易筆數(隻)',  # 更新標題以反映實際顯示的內容
                    'font': {'size': 18},
                    'y': 0.98,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis=dict(
                    title='月',
                    ticktext=[str(i) for i in range(1, 13)],
                    tickvals=list(range(1, 13))
                ),
                yaxis=dict(
                    title='年'
                ),
                height=plot_height + 100,
                width=700,
                margin=dict(t=50, l=80, r=20, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建月交易次數熱力圖時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_win_rate_heatmap(df: pl.DataFrame) -> str:
        """月勝率熱力圖"""
        try:
            if df.is_empty():
                return "<p>沒有資料產生熱力圖。</p>"
            
            # 確保年月日欄位是日期類型
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date).alias("年月日")
            ])
            
            # 添加年份和月份列
            df = df.with_columns([
                pl.col("年月日").dt.year().alias("年"),
                pl.col("年月日").dt.month().alias("月"),
                (pl.col("報酬") > 0).cast(pl.Int64).alias("是否獲利")  # 計算是否獲利
            ])
            
            # 計算每月的勝率
            win_rates = df.group_by(["年", "月"]).agg([
                (pl.col("是否獲利").mean() * 100).round(0).alias("勝率"),  # 計算勝率並轉換為百分比
                pl.col("年月日").count().alias("交易次數")  # 計算交易次數
            ]).filter(
                pl.col("交易次數") > 0  # 只保留有交易的月份
            ).sort(["年", "月"])
            
            # 創建樞紐表
            pivot_table = win_rates.pivot(
                values="勝率",
                index="年",
                columns="月"
            ).fill_null(0)
            
            # 獲取年份和月份
            # 按年份降序排序（新到舊）
            pivot_table = pivot_table.sort("年", descending=True)
            years = pivot_table["年"].to_list()
            month_cols = sorted([col for col in pivot_table.columns if isinstance(col, int) or (isinstance(col, str) and str(col).isdigit())], key=int)
            
            # 準備熱力圖數據
            z = pivot_table.select(month_cols).to_numpy()
            text = [[f"{int(v)}%" if v != 0 else "0%" for v in row] for row in z]
            
            # 創建熱力圖
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=[str(m) for m in month_cols],
                y=[str(y) for y in years],
                colorscale='RdYlGn',  # 使用紅黃綠色階，紅色表示低勝率，綠色表示高勝率
                text=text,
                texttemplate="%{text}",
                textfont={"size": 13, "color": "black"},
                showscale=False
            ))
            
            plot_height = 50 * len(years)
            # 更新布局
            fig.update_layout(
                title={
                    'text': '月度勝率 (%)',
                    'font': {'size': 15},
                    'y': 0.94,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis=dict(
                    title='月',
                    ticktext=[str(i) for i in range(1, 13)],
                    tickvals=list(range(1, 13))
                ),
                yaxis=dict(
                    title='年'
                ),
                height=plot_height + 100,
                width=700,
                margin=dict(t=50, l=80, r=20, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建月度勝率熱力圖時發生錯誤: {str(e)}</p>"
    
    @staticmethod
    def _create_weekday_analysis_charts(df: pl.DataFrame) -> str:
        """月週期收益率圖：分析各星期交易次數、平均收益(bp)、勝率(%)"""
        try:
            if df.is_empty():
                return "<p>沒有資料產生圖表。</p>"
            
            # 確保年月日欄位是日期類型
            df = df.with_columns([
                pl.col("年月日").cast(pl.Date).alias("年月日")
            ])
            
            # 資料預處理
            df = df.with_columns([
                pl.col("年月日").dt.weekday().alias("星期"),  # 0=星期一
                (pl.col("報酬") > 0).cast(pl.Int64).alias("是否獲利")
            ])
            
            df = df.filter(pl.col("星期") <= 5)  # 保留星期一至五
            
            # 統計每星期績效
            if "明日開盤價" in df.columns:
                # Day Trading 使用明日開盤價
                weekday_df = df.group_by("星期").agg([
                    pl.col("年月日").count().alias("交易次數"),
                    pl.when((pl.col("明日開盤價") > 0) & (pl.col("股數") > 0))
                    .then((pl.col("報酬") / (pl.col("明日開盤價") * pl.col("股數"))) * 10000)
                    .otherwise(None).mean().fill_nan(None).round(0).alias("收益率bp"),
                    (pl.col("是否獲利").mean() * 100).round(2).alias("勝率")
                ]).sort("星期")
            else:
                # Swing Trading 和 BookBuilding Announcement 使用出場價
                weekday_df = df.group_by("星期").agg([
                    pl.col("年月日").count().alias("交易次數"),
                    pl.when((pl.col("出場價") > 0) & (pl.col("股數") > 0))
                    .then((pl.col("報酬") / (pl.col("出場價") * pl.col("股數"))) * 10000)
                    .otherwise(None).mean().fill_nan(None).round(0).alias("收益率bp"),
                    (pl.col("是否獲利").mean() * 100).round(2).alias("勝率")
                ]).sort("星期")
            
            if weekday_df.is_empty():
                return "<p>資料不足以繪製星期分析圖。</p>"
            
            avg_win_rate = df.select((pl.col("是否獲利").mean() * 100).round(2)).item()
            
            # 對應星期中文名
            day_names = ['星期一', '星期二', '星期三', '星期四', '星期五']
            trades = weekday_df["交易次數"].to_list()
            returns = weekday_df["收益率bp"].to_list()
            win_rates = weekday_df["勝率"].to_list()
            
            # 建立圖表
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                subplot_titles=['每個星期的交易次數', '每個星期的平均收益 (bp)', '每個星期的勝率 (%)'],
                vertical_spacing=0.12,
                row_heights=[0.25, 0.35, 0.4]
            )
            
            # 子圖 1：交易次數
            fig.add_trace(go.Bar(x=day_names, y=trades, marker_color='blue', name='交易次數'), row=1, col=1)
            
            # 子圖 2：平均收益率
            fig.add_trace(go.Bar(
                x=day_names, y=returns,
                marker_color=['green' if x >= 0 else 'red' for x in returns],
                name='平均收益 (bp)',
                text=[f"{int(x)}bp" for x in returns],
                textposition='outside'
            ), row=2, col=1)
            
            # 子圖 3：勝率
            fig.add_trace(go.Bar(
                x=day_names, y=win_rates,
                marker_color='orange',
                name='勝率 (%)',
                text=[f"{x:.1f}%" for x in win_rates],
                textposition='outside'
            ), row=3, col=1)
            
            # 加上平均勝率參考線
            fig.add_trace(go.Scatter(
                x=day_names,
                y=[avg_win_rate] * 5,
                mode='lines',
                line=dict(color='red', width=2, dash='dash'),
                name=f'平均勝率 ({avg_win_rate:.1f}%)'
            ), row=3, col=1)
            
            # 調整 Y 軸範圍
            fig.update_yaxes(range=[0, max(trades) * 1.2], row=1, col=1)
            
            min_ret, max_ret = min(returns), max(returns)
            if min_ret < 0:
                fig.update_yaxes(range=[min_ret * 1.8, max_ret * 1.3], row=2, col=1)
            else:
                fig.update_yaxes(range=[0, max_ret * 1.3], row=2, col=1)
            
            fig.update_yaxes(range=[0, max(win_rates) * 1.2], row=3, col=1)
            
            # 設定背景與格線
            for i in range(1, 4):
                fig.update_xaxes(showgrid=True, gridcolor='lightgray', row=i, col=1)
                fig.update_yaxes(showgrid=True, gridcolor='lightgray', row=i, col=1)
            
            # 圖表外觀設定
            fig.update_layout(
                height=900,
                width=500,
                title={
                    'text': '按星期分析交易 (工作日)',
                    'font': {'size': 18},
                    'y': 0.98,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.08,
                    xanchor="center",
                    x=0.5
                ),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            return fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            return f"<p>創建星期分析圖表時發生錯誤: {str(e)}</p>" 