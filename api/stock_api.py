# 股票API模組
import requests
import polars as pl
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from config.api_config import APIConfig
from core.utils import Utils
from core.cache_manager import cache_manager

def print_log(message: str):
    print(f"********** stock_api.py - {message}")

class StockAPI:
    """股票API類別"""
    
    def __init__(self):
        """初始化股票API"""
        self.base_url = APIConfig.BACKTEST_BASE_URL
        self.headers = APIConfig.get_backtest_headers()
        self.session = None
    
    async def __aenter__(self):
        """非同步上下文管理器進入"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        發送API請求
        
        Args:
            endpoint (str): API端點
            params (Dict[str, Any]): 請求參數
            
        Returns:
            Dict[str, Any]: API回應
        """
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.get(url, params=params) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API請求失敗: {response.status} - {await response.text()}")
        except Exception as e:
            raise Exception(f"API請求錯誤: {str(e)}")
        
    async def get_stock_price(self, stock_ids: List[str], start_date: str, end_date: str, stock_info_df: pl.DataFrame = None,
                             use_cache: bool = True) -> pl.DataFrame:
        """
        取得股票價格資料
        
        Args:
            stock_ids (List[str]): 股票代碼列表
            start_date (str): 開始日期
            end_date (str): 結束日期
            stock_info_df (pl.DataFrame): 股票基本資訊DataFrame
            use_cache (bool): 是否使用快取
            
        Returns:
            pl.DataFrame: 股票價格資料
        """
        # 檢查快取
        if use_cache:
            cached_data = cache_manager.get_cached_data(
                stock_ids[0] if len(stock_ids) == 1 else "multiple", 
                start_date, end_date, "price"
            )
            if cached_data is not None:
                return cached_data
        
        # 將股票代碼列表分割成每100支一批
        stock_chunks = Utils.chunk_list(stock_ids, 100)
        all_data = []
        
        for chunk in stock_chunks:
            stock_ids_str = ",".join(chunk)
            params = {
                "stockIds": stock_ids_str,
                "startDate": start_date,
                "endDate": end_date
            }
            try:
                response = await self._make_request(APIConfig.GET_TAIWAN_STOCK_PRICE, params)
                if response.get("data", []):                    
                    data = response.get("data", [])
                    all_data.extend(data)
                else:
                    raise Exception(f"API回應錯誤: {response.get('message', '未知錯誤')}")
                    
            except Exception as e:
                print(f"取得股票價格資料失敗: {str(e)}")
                continue

        # 轉換為DataFrame
        if all_data:
            df = pl.DataFrame(all_data)
            
            # 標準化欄位名稱
            column_mapping = {
                "stock_id": "stock_id",
                "date": "date",
                "open": "open",
                "max": "high",
                "min": "low",
                "close": "close",
                "volume": "volume",
                "amount": "amount"
            }
            # 重新命名欄位
            df = df.rename(column_mapping)  # max=>high, min=>low
            # 合併股票基本資訊
            df = df.join(stock_info_df, on="stock_id", how="left")
            
            # 確保必要欄位存在
            required_columns = ["stock_id", "date", "open", "high", "low", "close"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"缺少必要欄位: {missing_columns}")
            
            # 轉換資料類型
            numeric_columns = ["open", "high", "low", "close", "spread"]
            for col in numeric_columns:
                if col in df.columns:
                    df = df.with_columns(pl.col(col).cast(pl.Float64, strict=False))

            # # 轉換日期格式
            # if "date" in df.columns:
            #     df = df.with_columns(pl.col("date").str.strptime(pl.Datetime, format="%Y-%m-%d"))

            # 儲存到快取
            if use_cache and len(df) > 0:
                cache_key = stock_ids[0] if len(stock_ids) == 1 else "multiple"
                cache_manager.set_cached_data(cache_key, start_date, end_date, df, "price")
            
            return df
        else:
            return pl.DataFrame()
    
    async def get_stock_dividend(self, stock_ids: List[str], start_date: str, end_date: str) -> pl.DataFrame:
        """
        取得股票除權息資料
        
        Args:
            stock_ids (List[str]): 股票代碼列表
            start_date (str): 開始日期
            end_date (str): 結束日期
            
        Returns:
            pl.DataFrame: 除權息資料
        """
        if len(stock_ids) > 0 and stock_ids[0] == "":   
            stock_ids_info = await self.get_stock_info()         
            stock_ids = stock_ids_info.select("stock_id").unique().to_series().to_list()

        # 將股票代碼列表分割成每100支一批
        stock_chunks = Utils.chunk_list(stock_ids, 100)
        all_data = []

        for chunk in stock_chunks:
            stock_ids_str = ",".join(chunk)
            params = {
                "stockIds": stock_ids_str,
                "startDate": start_date,
                "endDate": end_date
            }
            
            try:
                response = await self._make_request(APIConfig.GET_TAIWAN_STOCK_DIVIDEND, params)
                
                if response.get("data", []):
                    data = response.get("data", [])
                    all_data.extend(data)
                else:
                    raise Exception(f"API回應錯誤: {response.get('message', '未知錯誤')}")
                    
            except Exception as e:
                print(f"取得除權息資料失敗: {str(e)}")
                continue
        
        # 轉換為DataFrame
        if all_data:
            df = pl.DataFrame(all_data)
            
            # 標準化欄位名稱
            column_mapping = {
                "stock_id": "stock_id",
                "date": "date",
                "stock_and_cache_dividend": "dividend",
                "reference_price": "reference_price"
            }
            # 重新命名欄位
            df = df.rename(column_mapping)
            
            # # 轉換日期格式
            # if "date" in df.columns:
            #     df = df.with_columns(pl.col("date").str.strptime(pl.Datetime, fmt="%Y-%m-%d"))
            
            # # 轉換數值欄位
            # if "dividend" in df.columns:
            #     df = df.with_columns(pl.col("dividend").cast(pl.Float64, strict=False))

            return df
        else:
            return pl.DataFrame()
    
    async def get_bookbuilding_announcement(self, tw_year: str) -> pl.DataFrame:
        """
        取得詢圈公告資料
        
        Args:
            tw_year (str): 民國年
            
        Returns:
            pl.DataFrame: 詢圈公告資料
        """
        params = {
            "twYear": tw_year
        }
        
        try:
            response = await self._make_request(APIConfig.GET_BOOKBUILDING_ANNOUNCEMENT, params)
            
            if response.get("status") == "success":
                data = response.get("data", [])
                
                if data:
                    df = pl.DataFrame(data)
                    
                    # 標準化欄位名稱
                    column_mapping = {
                        "stock_id": "stock_id",
                        "date": "date",
                        "announcement_type": "announcement_type",
                        "details": "details"
                    }
                    
                    # 重新命名欄位
                    df = df.rename(column_mapping)
                    
                    # 轉換日期格式
                    if "date" in df.columns:
                        df = df.with_columns(pl.col("date").str.strptime(pl.Datetime, fmt="%Y-%m-%d"))
                    
                    return df
                else:
                    return pl.DataFrame()
            else:
                raise Exception(f"API回應錯誤: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            print(f"取得詢圈公告資料失敗: {str(e)}")
            return pl.DataFrame()
    
    async def get_stock_info(self, page: int = 1, page_size: int = 10000, 
                           stock_id: Optional[str] = None) -> pl.DataFrame:
        """
        取得股票基本資訊
        
        Args:
            page (int): 頁碼
            page_size (int): 每頁筆數
            stock_id (Optional[str]): 股票代碼（可選）
            
        Returns:
            pl.DataFrame: 股票基本資訊
        """
        params = APIConfig.GET_STOCK_INFO_PARAMS
        params["page"] = page
        params["pageSize"] = page_size
        
        if stock_id:
            params["stockId"] = stock_id
        
        try:
            response = await self._make_request(APIConfig.GET_STOCK_INFO, params)
            data = response.get("data", [])
                
            if data:
                df = pl.DataFrame(data)
                
                # 標準化欄位名稱
                column_mapping = {
                    "stock_id": "stock_id",
                    "stock_name": "stock_name",
                    "industry": "industry",
                    "market": "market"
                }
                
                # 重新命名欄位
                df = df.rename(column_mapping)
                df = df.unique(subset=["stock_id"], keep="first")  # 去重
                
                return df                 
            else:                
                raise Exception(f"API回應錯誤: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            print(f"取得股票基本資訊失敗: {str(e)}")
            return pl.DataFrame()
    
    async def adjust_price_for_dividend(self, price_data: pl.DataFrame, dividend_data: pl.DataFrame) -> pl.DataFrame:
        """
        根據除權息調整股價
        
        Args:
            price_data (pl.DataFrame): 股價資料
            dividend_data (pl.DataFrame): 除權息資料
            
        Returns:
            pl.DataFrame: 調整後的股價資料
        """
        if dividend_data.is_empty():
            return price_data
        
        # 合併股價和除權息資料
        merged_df = price_data.join(
            dividend_data.select(["stock_id", "date", "dividend", "stock_or_cache_dividend", "reference_price"]),
            on=["stock_id", "date"],
            how="left"
        )
        
        # # 調整股價（簡化版，實際應根據除權息類型進行更複雜的調整）
        # adjusted_df = merged_df.with_columns([
        #     pl.when(pl.col("dividend").is_not_null())
        #     .then(pl.col("close") - pl.col("dividend"))
        #     .otherwise(pl.col("close"))
        #     .alias("adjusted_close")
        # ])
        
        # # 更新其他價格欄位
        # adjusted_df = adjusted_df.with_columns([
        #     pl.when(pl.col("dividend").is_not_null())
        #     .then(pl.col("open") - pl.col("dividend"))
        #     .otherwise(pl.col("open"))
        #     .alias("adjusted_open"),
        #     pl.when(pl.col("dividend").is_not_null())
        #     .then(pl.col("high") - pl.col("dividend"))
        #     .otherwise(pl.col("high"))
        #     .alias("adjusted_high"),
        #     pl.when(pl.col("dividend").is_not_null())
        #     .then(pl.col("low") - pl.col("dividend"))
        #     .otherwise(pl.col("low"))
        #     .alias("adjusted_low")
        # ])
        
        return merged_df
    
    def process_stock_list(self, stock_list_df: pl.DataFrame) -> Dict[str, Any]:
        """
        處理股票清單
        
        Args:
            stock_list_df (pl.DataFrame): 股票清單DataFrame
            
        Returns:
            Dict[str, Any]: 處理結果
        """
        if stock_list_df.is_empty():
            raise ValueError("股票清單為空")
        
        # 取得股票代碼列表
        stock_ids = stock_list_df.select("stock_id").unique().to_series().to_list()
        
        # 取得日期範圍
        date_range = stock_list_df.select("date").unique().sort("date")
        start_date = date_range.head(1).item(0, 0).strftime("%Y-%m-%d")
        end_date = date_range.tail(1).item(0, 0).strftime("%Y-%m-%d")
        
        return {
            "stock_ids": stock_ids,
            "start_date": start_date,
            "end_date": end_date,
            "total_stocks": len(stock_ids)
        } 