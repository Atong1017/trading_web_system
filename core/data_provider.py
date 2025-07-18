import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os
import polars as pl
from config.api_config import APIConfig
from api.stock_api import StockAPI

def print_log(message: str):
    print(f"********** data_provider.py - {message}")

class DataProvider:
    """資料提供器，用於提供各種範例資料類型"""
    
    def __init__(self):
        self.data_types = self._initialize_data_types()
    
    def _initialize_data_types(self) -> Dict[str, Dict]:
        """初始化資料類型定義"""
        return {
            'daily_price': {
                'id': 'daily_price',
                'name': '每日股價',
                'description': '股票每日開盤、收盤、最高、最低價等基本資訊',
                'category': '股價資料',
                'parameters': {
                    'stock_id': {
                        'type': 'text',
                        'label': '股票代碼',
                        'default': '',
                        'placeholder': '請輸入股票代碼（空白表示全部股票）'
                    },
                    'start_date': {
                        'type': 'date',
                        'label': '開始日期',
                        'default': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    },
                    'end_date': {
                        'type': 'date',
                        'label': '結束日期',
                        'default': datetime.now().strftime('%Y-%m-%d')
                    }
                }
            },
            'minute_price': {
                'id': 'minute_price',
                'name': '分K股價',
                'description': '股票分K線圖資料，包含開盤、收盤、最高、最低價',
                'category': '股價資料',
                'parameters': {
                    'stock_id': {
                        'type': 'text',
                        'label': '股票代碼',
                        'default': '',
                        'placeholder': '請輸入股票代碼（空白表示全部股票）'
                    },
                    'interval': {
                        'type': 'select',
                        'label': '時間間隔',
                        'default': '1',
                        'options': [
                            {'value': '1', 'label': '1分鐘'},
                            {'value': '5', 'label': '5分鐘'},
                            {'value': '15', 'label': '15分鐘'},
                            {'value': '30', 'label': '30分鐘'},
                            {'value': '60', 'label': '1小時'}
                        ]
                    },
                    'date': {
                        'type': 'date',
                        'label': '日期',
                        'default': datetime.now().strftime('%Y-%m-%d')
                    }
                }
            },
            'dividend': {
                'id': 'dividend',
                'name': '除權息資料',
                'description': '股票除權息相關資訊，包含除權息日期、金額等',
                'category': '財務資料',
                'parameters': {
                    'stock_id': {
                        'type': 'text',
                        'label': '股票代碼',
                        'default': '',
                        'placeholder': '請輸入股票代碼（空白表示全部股票）'
                    },
                    'start_date': {
                        'type': 'date',
                        'label': '開始日期',
                        'default': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                    },
                    'end_date': {
                        'type': 'date',
                        'label': '結束日期',
                        'default': datetime.now().strftime('%Y-%m-%d')
                    }
                }
            },
            'daily_price_with_dividend': {
                'id': 'daily_price_with_dividend',
                'name': '每日股價合併除權息',
                'description': '每日股價資料並包含除權息調整資訊',
                'category': '股價資料',
                'parameters': {
                    'stock_id': {
                        'type': 'text',
                        'label': '股票代碼',
                        'default': '',
                        'placeholder': '請輸入股票代碼（空白表示全部股票）'
                    },
                    'start_date': {
                        'type': 'date',
                        'label': '開始日期',
                        'default': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    },
                    'end_date': {
                        'type': 'date',
                        'label': '結束日期',
                        'default': datetime.now().strftime('%Y-%m-%d')
                    },
                    'adjust_type': {
                        'type': 'select',
                        'label': '調整類型',
                        'default': 'all',
                        'options': [
                            {'value': 'all', 'label': '全部調整'},
                            {'value': 'dividend', 'label': '僅除權息'},
                            {'value': 'none', 'label': '不調整'}
                        ]
                    }
                }
            },
            'technical_indicators': {
                'id': 'technical_indicators',
                'name': '技術指標',
                'description': '包含各種技術指標的股價資料',
                'category': '技術分析',
                'parameters': {
                    'stock_id': {
                        'type': 'text',
                        'label': '股票代碼',
                        'default': '',
                        'placeholder': '請輸入股票代碼（空白表示全部股票）'
                    },
                    'start_date': {
                        'type': 'date',
                        'label': '開始日期',
                        'default': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
                    },
                    'end_date': {
                        'type': 'date',
                        'label': '結束日期',
                        'default': datetime.now().strftime('%Y-%m-%d')
                    },
                    'indicators': {
                        'type': 'select',
                        'label': '技術指標',
                        'default': 'all',
                        'options': [
                            {'value': 'all', 'label': '全部指標'},
                            {'value': 'ma', 'label': '移動平均線'},
                            {'value': 'rsi', 'label': 'RSI'},
                            {'value': 'macd', 'label': 'MACD'},
                            {'value': 'bollinger', 'label': '布林通道'}
                        ]
                    }
                }
            }
        }
    
    def get_data_types(self) -> List[Dict]:
        """取得所有資料類型"""
        return list(self.data_types.values())
    
    def get_data_type(self, data_type_id: str) -> Optional[Dict]:
        """取得特定資料類型"""
        return self.data_types.get(data_type_id)
    
    async def load_data(self, data_type_id: str, parameters: Dict[str, Any]) -> List[Dict]:
        """載入指定類型的資料"""
        if data_type_id not in self.data_types:
            raise ValueError(f"不支援的資料類型: {data_type_id}")
        
        # 根據資料類型載入對應的資料
        if data_type_id == 'daily_price':
            return await self._generate_daily_price_data(parameters)
        elif data_type_id == 'minute_price':
            return self._generate_minute_price_data(parameters)
        elif data_type_id == 'dividend':
            return await self._generate_dividend_data(parameters)
        elif data_type_id == 'daily_price_with_dividend':
            return await self._generate_daily_price_with_dividend_data(parameters)
        elif data_type_id == 'technical_indicators':
            return await self._generate_technical_indicators_data(parameters)
        else:
            raise ValueError(f"未實作的資料類型: {data_type_id}")
    
    async def _generate_daily_price_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """直接請求 GET_TAIWAN_STOCK_PRICE API 並回傳 list of dict"""
        stock_id = parameters.get('stock_id', '')
        startDate = parameters.get('start_date', '2024-01-01')
        startDate = datetime.strptime(startDate, '%Y-%m-%d') + timedelta(days=-50)
        startDate = startDate.strftime('%Y-%m-%d')
        endDate = parameters.get('end_date', '2024-12-31')
        
        # 初始化 stock_info_df
        stock_info_df = None
        
        # 如果股票代碼為空白，使用預設股票列表
        if not stock_id or stock_id.strip() == '':
            async with StockAPI() as stock_api:
                stock_info_df = await stock_api.get_stock_info()
            stockIds = stock_info_df['stock_id'].to_list()
        else:
            stockIds = stock_id.split(',')
            # 如果指定了股票代碼，也需要取得股票資訊
            async with StockAPI() as stock_api:
                stock_info_df = await stock_api.get_stock_info()

        async with StockAPI() as stock_api:
            df = await stock_api.get_stock_price(stockIds, startDate, endDate, stock_info_df=stock_info_df)

        return df.to_dicts()
    
    def _generate_minute_price_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """生成分K股價資料"""
        stock_id = parameters.get('stock_id', '2330')
        interval = int(parameters.get('interval', '1'))
        date_str = parameters.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 生成模擬資料
        data = []
        base_price = 500.0
        
        # 交易時間 9:00-13:30
        start_time = datetime.strptime(f"{date_str} 09:00:00", "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(f"{date_str} 13:30:00", "%Y-%m-%d %H:%M:%S")
        
        current_time = start_time
        while current_time <= end_time:
            # 模擬股價變動
            change = np.random.normal(0, 0.005)  # 0.5% 標準差
            base_price *= (1 + change)
            
            open_price = base_price * (1 + np.random.normal(0, 0.002))
            high_price = max(open_price, base_price) * (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, base_price) * (1 - abs(np.random.normal(0, 0.005)))
            close_price = base_price
            volume = int(np.random.normal(50000, 10000))
            
            data.append({
                'datetime': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'stock_id': stock_id,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'interval': f"{interval}分鐘"
            })
            
            current_time += timedelta(minutes=interval)
        
        return data
    
    async def _generate_dividend_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """生成除權息資料"""
        stockIds = parameters.get('stock_id', '2330').split(',')
        startDate = parameters.get('start_date', '2024-01-01')
        endDate = parameters.get('end_date', '2024-12-31')
        
        async with StockAPI() as stock_api:
            df = await stock_api.get_stock_dividend(stockIds, startDate, endDate)
        return df.to_dicts()    
    
    async def _generate_daily_price_with_dividend_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """生成每日股價合併除權息資料"""
        # 先取得每日股價資料
        daily_data = await self._generate_daily_price_data(parameters)
        daily_data = pl.DataFrame(daily_data)
        # 取得除權息資料
        dividend_data = await self._generate_dividend_data(parameters)
        dividend_data = pl.DataFrame(dividend_data)
        
        # 建立除權息日期對照表
        async with StockAPI() as stock_api:
            dividend_dates = await stock_api.adjust_price_for_dividend(daily_data, dividend_data)
        
        return dividend_dates.to_dicts()
    
    async def _generate_technical_indicators_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """生成技術指標資料"""
        # 先取得每日股價資料
        daily_data = await self._generate_daily_price_data(parameters)
        
        # 轉換為 DataFrame 進行技術指標計算
        df = pd.DataFrame(daily_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 計算移動平均線
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        # 計算 RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 計算 MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # 計算布林通道
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # 轉換回字典格式
        result = []
        for _, row in df.iterrows():
            item = {
                'date': row['date'].strftime('%Y-%m-%d'),
                'stock_id': row['stock_id'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume'],
                'ma5': round(row['ma5'], 2) if pd.notna(row['ma5']) else None,
                'ma10': round(row['ma10'], 2) if pd.notna(row['ma10']) else None,
                'ma20': round(row['ma20'], 2) if pd.notna(row['ma20']) else None,
                'rsi': round(row['rsi'], 2) if pd.notna(row['rsi']) else None,
                'macd': round(row['macd'], 4) if pd.notna(row['macd']) else None,
                'macd_signal': round(row['macd_signal'], 4) if pd.notna(row['macd_signal']) else None,
                'macd_histogram': round(row['macd_histogram'], 4) if pd.notna(row['macd_histogram']) else None,
                'bb_upper': round(row['bb_upper'], 2) if pd.notna(row['bb_upper']) else None,
                'bb_middle': round(row['bb_middle'], 2) if pd.notna(row['bb_middle']) else None,
                'bb_lower': round(row['bb_lower'], 2) if pd.notna(row['bb_lower']) else None
            }
            result.append(item)
        
        return result
    
    def add_data_type(self, data_type: Dict[str, Any]) -> bool:
        """新增資料類型"""
        if 'id' not in data_type:
            return False
        
        self.data_types[data_type['id']] = data_type
        return True
    
    def remove_data_type(self, data_type_id: str) -> bool:
        """移除資料類型"""
        if data_type_id in self.data_types:
            del self.data_types[data_type_id]
            return True
        return False
    
    def save_data_types(self, file_path: str = None) -> bool:
        """儲存資料類型到檔案"""
        if file_path is None:
            file_path = 'data/sample_data_types.json'
        
        try:
            # 確保路徑使用正斜線
            file_path = file_path.replace('\\', '/')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_types, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"儲存資料類型失敗: {e}")
            return False
    
    def load_data_types(self, file_path: str = None) -> bool:
        """從檔案載入資料類型"""
        if file_path is None:
            file_path = 'data/sample_data_types.json'
        
        try:
            # 確保路徑使用正斜線
            file_path = file_path.replace('\\', '/')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_types = json.load(f)
                self.data_types.update(loaded_types)
                return True
        except Exception as e:
            print(f"載入資料類型失敗: {e}")
        
        return False 