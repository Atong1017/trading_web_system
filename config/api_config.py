# API設定檔
import os
from typing import Dict, Any

class APIConfig:
    """API設定類別"""
    
    # 回測API設定
    BACKTEST_API_TOKEN = "853DDFEB-44BF-45CF-8533-8597698D2307"
    BACKTEST_BASE_URL = "https://quant-trade-api.bridgefi.tech"
    
    # 台股價格API
    GET_TAIWAN_STOCK_PRICE = "/api/Stock/GetTaiwanStockPrice"
    GET_TAIWAN_STOCK_PRICE_PARAMS = {
        "stockIds": "2330,6462,4541",  # 股票代號:最多可100支
        "startDate": "2025-01-01",
        "endDate": "2025-06-28"
    }
    
    # 台股除權息API
    GET_TAIWAN_STOCK_DIVIDEND = "/api/Stock/GetTaiwanStockDividend"
    GET_TAIWAN_STOCK_DIVIDEND_PARAMS = {
        "stockIds": "2330,6462,4541",  # 股票代號:最多可100支
        "startDate": "2025-01-01",
        "endDate": "2025-06-28"
    }
    
    # 詢圈公告API
    GET_BOOKBUILDING_ANNOUNCEMENT = "/api/Stock/GetBookBuildingAnnouncement"
    GET_BOOKBUILDING_ANNOUNCEMENT_PARAMS = {
        "twYear": "114"  # 民國年
    }
    
    # 台股總覽API
    GET_STOCK_INFO = "/api/Stock/GetTaiwanStockInfo"
    GET_STOCK_INFO_PARAMS = {
        "page": 1,
        "pageSize": 100,
        "type": "",  # 非必要填
        "industry_category": "",  # 非必要填
        "stock_id": ""  # 非必要填
    }
    
    # 台股總覽(含權證)API
    GET_STOCK_INFO_WITH_WARRANT = "/api/Stock/GetTaiwanStockInfoWithWarrant"
    GET_STOCK_INFO_WITH_WARRANT_PARAMS = {
        "page": 1,
        "pageSize": 100,
        "type": "type",  # 非必要填
        "industry_category": "industry_category",  # 非必要填
        "stock_id": "2330"  # 非必要填
    }
    
    # 券商API設定
    BROKER_APIS = {
        "華南": {
            "name": "華南證券",
            "api_url": "https://api.hncb.com.tw",
            "api_key": os.getenv("HNCB_API_KEY", ""),
            "api_secret": os.getenv("HNCB_API_SECRET", ""),
            "account": os.getenv("HNCB_ACCOUNT", ""),
            "password": os.getenv("HNCB_PASSWORD", "")
        },
        "凱基": {
            "name": "凱基證券",
            "api_url": "https://api.kgi.com.tw",
            "api_key": os.getenv("KGI_API_KEY", ""),
            "api_secret": os.getenv("KGI_API_SECRET", ""),
            "account": os.getenv("KGI_ACCOUNT", ""),
            "password": os.getenv("KGI_PASSWORD", "")
        },
        "元大": {
            "name": "元大證券",
            "api_url": "https://api.yuanta.com.tw",
            "api_key": os.getenv("YUANTA_API_KEY", ""),
            "api_secret": os.getenv("YUANTA_API_SECRET", ""),
            "account": os.getenv("YUANTA_ACCOUNT", ""),
            "password": os.getenv("YUANTA_PASSWORD", "")
        }
    }
    
    @classmethod
    def get_backtest_headers(cls) -> Dict[str, str]:
        """取得回測API的請求標頭"""
        return {
            "Authorization": f"Bearer {cls.BACKTEST_API_TOKEN}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def get_broker_config(cls, broker_name: str) -> Dict[str, Any]:
        """取得指定券商的API設定"""
        return cls.BROKER_APIS.get(broker_name, {})
    
    @classmethod
    def get_available_brokers(cls) -> list:
        """取得可用的券商列表"""
        return list(cls.BROKER_APIS.keys()) 