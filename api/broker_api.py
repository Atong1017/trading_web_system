# 券商API模組
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
from config.api_config import APIConfig
from core.utils import Utils

def print_log(message: str):
    """日誌輸出"""
    print(f"********** broker_api.py - {message}")

class BrokerAPI:
    """券商API類別"""
    
    def __init__(self, broker_name: str):
        """
        初始化券商API
        
        Args:
            broker_name (str): 券商名稱
        """
        self.broker_name = broker_name
        self.config = APIConfig.get_broker_config(broker_name)
        
        if not self.config:
            raise ValueError(f"不支援的券商: {broker_name}")
        
        self.api_url = self.config["api_url"]
        self.api_key = self.config["api_key"]
        self.api_secret = self.config["api_secret"]
        self.account = self.config["account"]
        self.password = self.config["password"]
        
        self.session = None
        self.access_token = None
    
    async def __aenter__(self):
        """非同步上下文管理器進入"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def login(self) -> bool:
        """
        登入券商系統
        
        Returns:
            bool: 登入是否成功
        """
        try:
            login_data = {
                "account": self.account,
                "password": self.password,
                "api_key": self.api_key
            }
            
            async with self.session.post(f"{self.api_url}/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        self.access_token = result.get("access_token")
                        return True
                    else:
                        print(f"登入失敗: {result.get('message', '未知錯誤')}")
                        return False
                else:
                    print(f"登入請求失敗: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"登入錯誤: {str(e)}")
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        取得帳戶資訊
        
        Returns:
            Dict[str, Any]: 帳戶資訊
        """
        if not self.access_token:
            if not await self.login():
                return {}
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.get(f"{self.api_url}/account/info", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        return result.get("data", {})
                    else:
                        print(f"取得帳戶資訊失敗: {result.get('message', '未知錯誤')}")
                        return {}
                else:
                    print(f"取得帳戶資訊請求失敗: {response.status}")
                    return {}
                    
        except Exception as e:
            print(f"取得帳戶資訊錯誤: {str(e)}")
            return {}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        取得持倉資訊
        
        Returns:
            List[Dict[str, Any]]: 持倉列表
        """
        if not self.access_token:
            if not await self.login():
                return []
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.get(f"{self.api_url}/positions", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        return result.get("data", [])
                    else:
                        print(f"取得持倉資訊失敗: {result.get('message', '未知錯誤')}")
                        return []
                else:
                    print(f"取得持倉資訊請求失敗: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"取得持倉資訊錯誤: {str(e)}")
            return []
    
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        下單
        
        Args:
            order_data (Dict[str, Any]): 訂單資料
            
        Returns:
            Dict[str, Any]: 下單結果
        """
        if not self.access_token:
            if not await self.login():
                return {"status": "error", "message": "登入失敗"}
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # 準備訂單資料
            order_payload = {
                "stock_id": order_data["stock_id"],
                "order_type": order_data["order_type"],  # "buy" or "sell"
                "quantity": order_data["quantity"],
                "price": order_data["price"],
                "order_method": order_data.get("order_method", "limit"),  # "limit" or "market"
                "time_in_force": order_data.get("time_in_force", "day"),  # "day" or "ioc"
                "strategy_name": order_data.get("strategy_name", ""),
                "remark": order_data.get("remark", "")
            }
            
            async with self.session.post(f"{self.api_url}/orders", 
                                        json=order_payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    return {
                        "status": "error", 
                        "message": f"下單請求失敗: {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "error", 
                "message": f"下單錯誤: {str(e)}"
            }
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        取消訂單
        
        Args:
            order_id (str): 訂單ID
            
        Returns:
            Dict[str, Any]: 取消結果
        """
        if not self.access_token:
            if not await self.login():
                return {"status": "error", "message": "登入失敗"}
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.delete(f"{self.api_url}/orders/{order_id}", 
                                          headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    return {
                        "status": "error", 
                        "message": f"取消訂單請求失敗: {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "error", 
                "message": f"取消訂單錯誤: {str(e)}"
            }
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        取得訂單狀態
        
        Args:
            order_id (str): 訂單ID
            
        Returns:
            Dict[str, Any]: 訂單狀態
        """
        if not self.access_token:
            if not await self.login():
                return {}
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.get(f"{self.api_url}/orders/{order_id}", 
                                       headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        return result.get("data", {})
                    else:
                        print(f"取得訂單狀態失敗: {result.get('message', '未知錯誤')}")
                        return {}
                else:
                    print(f"取得訂單狀態請求失敗: {response.status}")
                    return {}
                    
        except Exception as e:
            print(f"取得訂單狀態錯誤: {str(e)}")
            return {}
    
    async def get_trade_history(self, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        取得交易歷史
        
        Args:
            start_date (Optional[str]): 開始日期
            end_date (Optional[str]): 結束日期
            
        Returns:
            List[Dict[str, Any]]: 交易歷史
        """
        if not self.access_token:
            if not await self.login():
                return []
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            async with self.session.get(f"{self.api_url}/trades", 
                                       params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        return result.get("data", [])
                    else:
                        print(f"取得交易歷史失敗: {result.get('message', '未知錯誤')}")
                        return []
                else:
                    print(f"取得交易歷史請求失敗: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"取得交易歷史錯誤: {str(e)}")
            return []
    
    def create_order_data(self, stock_id: str, order_type: str, quantity: int, 
                         price: float, strategy_name: str = "", remark: str = "") -> Dict[str, Any]:
        """
        建立訂單資料
        
        Args:
            stock_id (str): 股票代碼
            order_type (str): 訂單類型 ("buy" or "sell")
            quantity (int): 數量
            price (float): 價格
            strategy_name (str): 策略名稱
            remark (str): 備註
            
        Returns:
            Dict[str, Any]: 訂單資料
        """
        return {
            "stock_id": stock_id,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "order_method": "limit",
            "time_in_force": "day",
            "strategy_name": strategy_name,
            "remark": remark
        }
    
    async def execute_strategy_order(self, strategy_result: Dict[str, Any], 
                                   capital: float) -> Dict[str, Any]:
        """
        執行策略訂單
        
        Args:
            strategy_result (Dict[str, Any]): 策略結果
            capital (float): 可用資金
            
        Returns:
            Dict[str, Any]: 執行結果
        """
        try:
            # 取得策略資訊
            stock_id = strategy_result.get("stock_id")
            entry_price = strategy_result.get("entry_price")
            strategy_name = strategy_result.get("strategy_name", "")
            
            if not stock_id or not entry_price:
                return {
                    "status": "error",
                    "message": "缺少必要參數"
                }
            
            # 計算股數
            from core.price_utils import PriceUtils
            shares = PriceUtils.calculate_shares(capital, entry_price, "整股")
            
            if shares <= 0:
                return {
                    "status": "error",
                    "message": "資金不足"
                }
            
            # 建立訂單資料
            order_data = self.create_order_data(
                stock_id=stock_id,
                order_type="buy",
                quantity=shares,
                price=entry_price,
                strategy_name=strategy_name,
                remark=f"自動下單 - {strategy_name}"
            )
            
            # 執行下單
            result = await self.place_order(order_data)
            
            return {
                "status": "success",
                "order_result": result,
                "order_data": order_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"執行策略訂單錯誤: {str(e)}"
            } 