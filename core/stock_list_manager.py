import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

def print_log(message: str):
    """日誌輸出"""
    print(f"********** stock_list_manager.py - {message}")

class StockListManager:
    """選股列表管理器"""
    
    def __init__(self, data_dir: str = "data/stock_lists"):
        # 確保路徑使用正斜線，避免 Windows 路徑問題
        self.data_dir = data_dir.replace('\\', '/')
        self.stock_lists_file = os.path.join(self.data_dir, "stock_lists.json").replace('\\', '/')
        self.ensure_directory()
        self.stock_lists = self.load_stock_lists()
    
    def ensure_directory(self):
        """確保目錄存在"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_stock_lists(self) -> Dict[str, Dict]:
        """載入選股列表"""
        stock_lists_file = self.stock_lists_file.replace('\\', '/')
        if os.path.exists(stock_lists_file):
            try:
                with open(stock_lists_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入選股列表失敗: {e}")
                return {}
        return {}
    
    def save_stock_lists(self):
        """儲存選股列表"""
        try:
            stock_lists_file = self.stock_lists_file.replace('\\', '/')
            with open(stock_lists_file, 'w', encoding='utf-8') as f:
                json.dump(self.stock_lists, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"儲存選股列表失敗: {e}")
            return False
    
    def create_stock_list(self, name: str, description: str = "") -> str:
        """建立新的選股列表"""
        stock_list_id = str(uuid.uuid4())
        
        stock_list = {
            "id": stock_list_id,
            "name": name,
            "description": description,
            "stocks": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.stock_lists[stock_list_id] = stock_list
        self.save_stock_lists()
        
        return stock_list_id
    
    def get_stock_list(self, stock_list_id: str) -> Optional[Dict]:
        """取得選股列表"""
        return self.stock_lists.get(stock_list_id)
    
    def get_all_stock_lists(self) -> List[Dict]:
        """取得所有選股列表"""
        stock_lists = []
        for stock_list in self.stock_lists.values():
            stock_list_copy = stock_list.copy()
            stock_list_copy['stock_count'] = len(stock_list.get('stocks', []))
            stock_lists.append(stock_list_copy)
        return stock_lists
    
    def update_stock_list(self, stock_list_id: str, name: str = None, 
                         description: str = None, stocks: List[Dict] = None) -> bool:
        """更新選股列表"""
        if stock_list_id not in self.stock_lists:
            return False
        
        stock_list = self.stock_lists[stock_list_id]
        
        if name is not None:
            stock_list['name'] = name
        if description is not None:
            stock_list['description'] = description
        if stocks is not None:
            stock_list['stocks'] = stocks
        
        stock_list['updated_at'] = datetime.now().isoformat()
        
        return self.save_stock_lists()
    
    def delete_stock_list(self, stock_list_id: str) -> bool:
        """刪除選股列表"""
        if stock_list_id in self.stock_lists:
            del self.stock_lists[stock_list_id]
            return self.save_stock_lists()
        return False
    
    def add_stock_to_list(self, stock_list_id: str, stock: Dict) -> bool:
        """新增股票到列表"""
        if stock_list_id not in self.stock_lists:
            return False
        
        stock_list = self.stock_lists[stock_list_id]
        
        # 檢查是否已存在
        existing_stock = next((s for s in stock_list['stocks'] 
                             if s['stock_id'] == stock['stock_id']), None)
        
        if existing_stock:
            # 更新現有股票
            existing_stock.update(stock)
        else:
            # 新增新股票
            stock_list['stocks'].append(stock)
        
        stock_list['updated_at'] = datetime.now().isoformat()
        
        return self.save_stock_lists()
    
    def remove_stock_from_list(self, stock_list_id: str, stock_id: str) -> bool:
        """從列表中移除股票"""
        if stock_list_id not in self.stock_lists:
            return False
        
        stock_list = self.stock_lists[stock_list_id]
        stock_list['stocks'] = [s for s in stock_list['stocks'] 
                               if s['stock_id'] != stock_id]
        stock_list['updated_at'] = datetime.now().isoformat()
        
        return self.save_stock_lists()
    
    def import_stocks_from_excel(self, excel_file_path: str) -> List[Dict]:
        """從Excel檔案匯入股票"""
        try:
            # 確保路徑使用正斜線
            excel_file_path = excel_file_path.replace('\\', '/')
            df = pd.read_excel(excel_file_path)
            
            stocks = []
            for _, row in df.iterrows():
                stock = {
                    'stock_id': str(row.get('stock_id', '')).strip(),
                    'stock_name': str(row.get('stock_name', '')).strip(),
                    'start_date': str(row.get('start_date', '')).strip(),
                    'end_date': str(row.get('end_date', '')).strip()
                }
                
                # 驗證股票代碼
                if stock['stock_id'] and stock['stock_id'] != 'nan':
                    stocks.append(stock)
            
            return stocks
        except Exception as e:
            print(f"匯入Excel失敗: {e}")
            return []
    
    def export_stocks_to_excel(self, stocks: List[Dict], file_path: str) -> bool:
        """匯出股票到Excel檔案"""
        try:
            # 確保路徑使用正斜線
            file_path = file_path.replace('\\', '/')
            df = pd.DataFrame(stocks)
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"匯出Excel失敗: {e}")
            return False
    
    def apply_stock_conditions(self, conditions: List[Dict]) -> List[Dict]:
        """套用選股條件（模擬功能）"""
        # 這裡可以實作真實的選股邏輯
        # 目前返回模擬資料
        sample_stocks = [
            {'stock_id': '2330', 'stock_name': '台積電', 'start_date': '', 'end_date': ''},
            {'stock_id': '2317', 'stock_name': '鴻海', 'start_date': '', 'end_date': ''},
            {'stock_id': '2454', 'stock_name': '聯發科', 'start_date': '', 'end_date': ''},
            {'stock_id': '2412', 'stock_name': '中華電', 'start_date': '', 'end_date': ''},
            {'stock_id': '1301', 'stock_name': '台塑', 'start_date': '', 'end_date': ''},
            {'stock_id': '1303', 'stock_name': '南亞', 'start_date': '', 'end_date': ''},
            {'stock_id': '2002', 'stock_name': '中鋼', 'start_date': '', 'end_date': ''},
            {'stock_id': '2881', 'stock_name': '富邦金', 'start_date': '', 'end_date': ''},
            {'stock_id': '2882', 'stock_name': '國泰金', 'start_date': '', 'end_date': ''},
            {'stock_id': '1216', 'stock_name': '統一', 'start_date': '', 'end_date': ''}
        ]
        
        # 根據條件篩選（簡化版本）
        filtered_stocks = sample_stocks
        
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field == 'stock_id' and operator == 'contains':
                filtered_stocks = [s for s in filtered_stocks 
                                 if value.lower() in s['stock_id'].lower()]
            elif field == 'stock_name' and operator == 'contains':
                filtered_stocks = [s for s in filtered_stocks 
                                 if value.lower() in s['stock_name'].lower()]
        
        return filtered_stocks
    
    def get_stock_list_statistics(self, stock_list_id: str) -> Dict:
        """取得選股列表統計資訊"""
        stock_list = self.get_stock_list(stock_list_id)
        if not stock_list:
            return {}
        
        stocks = stock_list.get('stocks', [])
        
        return {
            'total_stocks': len(stocks),
            'created_at': stock_list.get('created_at'),
            'updated_at': stock_list.get('updated_at'),
            'name': stock_list.get('name'),
            'description': stock_list.get('description')
        } 