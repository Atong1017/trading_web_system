# 快取管理器
import os
import json
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import polars as pl
from threading import Lock
import logging

def print_log(message: str):
    """日誌輸出"""
    print(f"********** cache_manager.py - {message}")

class CacheManager:
    """快取管理器，用於管理股價資料的記憶體快取"""
    
    def __init__(self, cache_dir: str = "data/cache", max_memory_mb: int = 1024):
        """
        初始化快取管理器
        
        Args:
            cache_dir (str): 快取檔案目錄
            max_memory_mb (int): 最大記憶體使用量 (MB)
        """
        # 確保路徑使用正斜線，避免 Windows 路徑問題
        self.cache_dir = cache_dir.replace('\\', '/')
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.memory_cache: Dict[str, Any] = {}
        self.cache_metadata: Dict[str, Dict[str, Any]] = {}
        self.cache_lock = Lock()
        
        # 確保快取目錄存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 載入快取元資料
        self._load_cache_metadata()
        
        # 設定日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_cache_metadata(self):
        """載入快取元資料"""
        metadata_file = os.path.join(self.cache_dir, "cache_metadata.json").replace('\\', '/')
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.cache_metadata = json.load(f)
            except Exception as e:
                self.logger.error(f"載入快取元資料失敗: {e}")
                self.cache_metadata = {}
    
    def _save_cache_metadata(self):
        """儲存快取元資料"""
        metadata_file = os.path.join(self.cache_dir, "cache_metadata.json").replace('\\', '/')
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"儲存快取元資料失敗: {e}")
    
    def _generate_cache_key(self, stock_id: str, start_date: str, end_date: str, 
                           data_type: str = "price") -> str:
        """
        生成快取鍵值
        
        Args:
            stock_id (str): 股票代碼
            start_date (str): 開始日期
            end_date (str): 結束日期
            data_type (str): 資料類型
            
        Returns:
            str: 快取鍵值
        """
        # 新的快取名稱格式：data_type:表格類型、stock_id:股票代碼(空白就是all)、start_date_end_date:開始結束日期合併
        stock_code = stock_id if stock_id else "all"
        date_range = f"{start_date.replace('-', '')}{end_date.replace('-', '')}"
        key_string = f"{data_type}_{stock_code}_{date_range}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """取得快取檔案路徑"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl").replace('\\', '/')
    
    def _parse_cache_key(self, cache_key: str) -> Dict[str, str]:
        """解析快取鍵值，提取資料類型、股票代碼和日期範圍"""
        try:
            # 新的快取名稱格式：data_type_stock_id_date_range
            parts = cache_key.split('_')
            
            if len(parts) >= 3:
                # 最後一部分是日期範圍（數字）
                date_range = parts[-1]
                # 倒數第二部分是股票代碼
                stock_id = parts[-2]
                # 其餘部分是資料類型
                data_type = '_'.join(parts[:-2])
                
                # 生成顯示名稱
                display_name = f"{data_type} - {stock_id} - {date_range}"
                
                return {
                    'data_type': data_type,
                    'stock_id': stock_id,
                    'date_range': date_range,
                    'display_name': display_name
                }
            else:
                return {
                    'data_type': 'unknown',
                    'stock_id': 'unknown',
                    'date_range': 'unknown',
                    'display_name': cache_key
                }
        except Exception as e:
            self.logger.error(f"解析快取鍵值失敗: {e}")
            return {
                'data_type': 'unknown',
                'stock_id': 'unknown',
                'date_range': 'unknown',
                'display_name': cache_key
            }
    
    def _generate_friendly_display_name(self, cache_key: str, metadata: Dict[str, Any]) -> str:
        """生成友好的顯示名稱，使用 data_type + created_at + expires_at"""
        try:
            # 直接從元資料取得資料類型，而不是解析快取鍵值
            data_type = metadata.get('data_type', 'unknown')
            stock_id = metadata.get('stock_id', 'unknown')
            start_date = metadata.get('start_date', '')
            end_date = metadata.get('end_date', '')
            
            # 從元資料取得時間資訊
            created_at = metadata.get('created_at', '')
            expires_at = metadata.get('expires_at', '')
            
            # 格式化時間
            if created_at:
                try:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_str = created_dt.strftime('%Y%m%d')
                except:
                    created_str = 'unknown'
            else:
                created_str = 'unknown'
            
            if expires_at:
                try:
                    expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    expires_str = expires_dt.strftime('%Y%m%d')
                except:
                    expires_str = 'unknown'
            else:
                expires_str = 'unknown'
            
            # 生成友好顯示名稱
            if created_str != 'unknown' and expires_str != 'unknown':
                # 如果有股票代碼和日期範圍資訊，加入這些資訊來區分不同的快取
                if stock_id != 'unknown' and start_date and end_date:
                    # 簡化日期格式，只取年月日
                    start_simple = start_date.replace('-', '')[:8]
                    end_simple = end_date.replace('-', '')[:8]
                    display_name = f"{data_type}_{stock_id}_{start_simple}_{end_simple}"
                else:
                    display_name = f"{data_type}_{created_str}_{expires_str}"
            else:
                # 如果時間資訊不完整，使用元資料中的描述
                display_name = metadata.get('description', cache_key)
            
            return display_name
            
        except Exception as e:
            self.logger.error(f"生成友好顯示名稱失敗: {e}")
            return cache_key
    
    def _calculate_memory_usage(self) -> int:
        """計算當前記憶體使用量"""
        total_size = 0
        for key, value in self.memory_cache.items():
            if isinstance(value, pl.DataFrame):
                # 估算 DataFrame 大小
                total_size += value.estimated_size()
            else:
                # 其他物件的大小估算
                total_size += len(str(value).encode())
        return total_size
    
    def _cleanup_memory_cache(self):
        """清理記憶體快取，移除最舊的資料"""
        if self._calculate_memory_usage() <= self.max_memory_bytes:
            return
        
        # 按最後存取時間排序
        sorted_items = sorted(
            self.cache_metadata.items(),
            key=lambda x: x[1].get('last_accessed', 0)
        )
        
        # 移除最舊的項目直到記憶體使用量低於限制
        for cache_key, metadata in sorted_items:
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                self.logger.info(f"從記憶體快取中移除: {metadata.get('description', cache_key)}")
                
                if self._calculate_memory_usage() <= self.max_memory_bytes * 0.8:
                    break
    
    def get_cached_data(self, stock_id: str, start_date: str, end_date: str, 
                       data_type: str = "price") -> Optional[pl.DataFrame]:
        """
        取得快取資料
        
        Args:
            stock_id (str): 股票代碼
            start_date (str): 開始日期
            end_date (str): 結束日期
            data_type (str): 資料類型
            
        Returns:
            Optional[pl.DataFrame]: 快取資料，如果不存在則返回 None
        """
        cache_key = self._generate_cache_key(stock_id, start_date, end_date, data_type)
        
        with self.cache_lock:
            # 檢查記憶體快取
            if cache_key in self.memory_cache:
                # 更新最後存取時間
                if cache_key in self.cache_metadata:
                    self.cache_metadata[cache_key]['last_accessed'] = datetime.now().isoformat()
                    self._save_cache_metadata()
                
                self.logger.info(f"從記憶體快取取得: {stock_id} ({start_date} ~ {end_date})")
                return self.memory_cache[cache_key]
            
            # 檢查檔案快取
            cache_file = self._get_cache_file_path(cache_key)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    # 載入到記憶體快取
                    self._cleanup_memory_cache()
                    self.memory_cache[cache_key] = data
                    
                    # 更新元資料
                    if cache_key in self.cache_metadata:
                        self.cache_metadata[cache_key]['last_accessed'] = datetime.now().isoformat()
                        self._save_cache_metadata()
                    
                    self.logger.info(f"從檔案快取載入到記憶體: {stock_id} ({start_date} ~ {end_date})")
                    return data
                    
                except Exception as e:
                    self.logger.error(f"載入快取檔案失敗: {e}")
                    # 刪除損壞的快取檔案
                    try:
                        os.remove(cache_file)
                    except:
                        pass
        
        return None
    
    def set_cached_data(self, stock_id: str, start_date: str, end_date: str, 
                       data: pl.DataFrame, data_type: str = "price", 
                       ttl_hours: int = 24) -> bool:
        """
        設定快取資料
        
        Args:
            stock_id (str): 股票代碼
            start_date (str): 開始日期
            end_date (str): 結束日期
            data (pl.DataFrame): 要快取的資料
            data_type (str): 資料類型
            ttl_hours (int): 快取存活時間（小時）
            
        Returns:
            bool: 是否成功設定快取
        """
        cache_key = self._generate_cache_key(stock_id, start_date, end_date, data_type)
        cache_file = self._get_cache_file_path(cache_key)
        
        with self.cache_lock:
            try:
                # 清理記憶體快取
                self._cleanup_memory_cache()
                
                # 儲存到記憶體快取
                self.memory_cache[cache_key] = data
                
                # 儲存到檔案快取
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
                
                # 更新元資料
                self.cache_metadata[cache_key] = {
                    'stock_id': stock_id,
                    'start_date': start_date,
                    'end_date': end_date,
                    'data_type': data_type,
                    'description': f"{stock_id} ({start_date} ~ {end_date})",
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
                    'size_bytes': data.estimated_size() if hasattr(data, 'estimated_size') else 0,
                    'rows': len(data) if hasattr(data, '__len__') else 0
                }
                self._save_cache_metadata()
                
                self.logger.info(f"快取資料: {stock_id} ({start_date} ~ {end_date}) - {len(data)} 筆資料")
                return True
                
            except Exception as e:
                self.logger.error(f"設定快取失敗: {e}")
                return False
    
    def clear_cache(self, cache_type: str = "all") -> bool:
        """
        清理快取
        
        Args:
            cache_type (str): 清理類型 ("all", "memory", "file", "expired")
            
        Returns:
            bool: 是否成功清理
        """
        with self.cache_lock:
            try:
                if cache_type in ["all", "memory"]:
                    self.memory_cache.clear()
                    self.logger.info("記憶體快取已清理")
                
                if cache_type in ["all", "file"]:
                    # 清理檔案快取
                    for filename in os.listdir(self.cache_dir):
                        if filename.endswith('.pkl'):
                            file_path = os.path.join(self.cache_dir, filename).replace('\\', '/')
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                self.logger.error(f"刪除快取檔案失敗 {filename}: {e}")
                    
                    # 清理元資料
                    self.cache_metadata.clear()
                    self._save_cache_metadata()
                    self.logger.info("檔案快取已清理")
                
                if cache_type == "expired":
                    # 清理過期的快取
                    current_time = datetime.now()
                    expired_keys = []
                    
                    for cache_key, metadata in self.cache_metadata.items():
                        expires_at = datetime.fromisoformat(metadata.get('expires_at', '1970-01-01'))
                        if current_time > expires_at:
                            expired_keys.append(cache_key)
                    
                    for cache_key in expired_keys:
                        # 從記憶體移除
                        if cache_key in self.memory_cache:
                            del self.memory_cache[cache_key]
                        
                        # 從檔案移除
                        cache_file = self._get_cache_file_path(cache_key)
                        if os.path.exists(cache_file):
                            try:
                                os.remove(cache_file)
                            except Exception as e:
                                self.logger.error(f"刪除過期快取檔案失敗: {e}")
                        
                        # 從元資料移除
                        del self.cache_metadata[cache_key]
                    
                    self._save_cache_metadata()
                    self.logger.info(f"已清理 {len(expired_keys)} 個過期快取")
                
                return True
                
            except Exception as e:
                self.logger.error(f"清理快取失敗: {e}")
                return False
    
    def remove_cache_item(self, cache_key: str) -> bool:
        """
        移除特定的快取項目
        
        Args:
            cache_key (str): 快取鍵值
            
        Returns:
            bool: 是否成功移除
        """
        with self.cache_lock:
            try:
                # 從記憶體快取移除
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    self.logger.info(f"從記憶體快取移除: {cache_key}")
                
                # 從檔案快取移除
                cache_file = self._get_cache_file_path(cache_key)
                if os.path.exists(cache_file):
                    try:
                        os.remove(cache_file)
                        self.logger.info(f"刪除快取檔案: {cache_file}")
                    except Exception as e:
                        self.logger.error(f"刪除快取檔案失敗: {e}")
                        return False
                
                # 從元資料移除
                if cache_key in self.cache_metadata:
                    del self.cache_metadata[cache_key]
                    self._save_cache_metadata()
                    self.logger.info(f"從元資料移除: {cache_key}")
                
                return True
                
            except Exception as e:
                self.logger.error(f"移除快取項目失敗: {e}")
                return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        取得快取資訊
        
        Returns:
            Dict[str, Any]: 快取統計資訊
        """
        with self.cache_lock:
            # 計算記憶體使用量
            memory_usage = self._calculate_memory_usage()
            
            # 計算檔案快取大小並收集詳細資訊
            file_cache_size = 0
            file_cache_count = 0
            cache_files = []
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    file_path = os.path.join(self.cache_dir, filename).replace('\\', '/')
                    try:
                        file_size = os.path.getsize(file_path)
                        file_cache_size += file_size
                        file_cache_count += 1
                        
                        # 解析快取檔案名稱以取得更多資訊
                        cache_key = filename.replace('.pkl', '')
                        cache_info = self._parse_cache_key(cache_key)
                        
                        # 取得檔案修改時間
                        file_mtime = os.path.getmtime(file_path)
                        modified_time = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 取得快取元資料
                        metadata = self.cache_metadata.get(cache_key, {})
                        
                        # 生成友好的顯示名稱
                        friendly_display_name = self._generate_friendly_display_name(cache_key, metadata)
                        
                        cache_files.append({
                            'filename': filename,
                            'cache_key': cache_key,
                            'size_bytes': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'modified_time': modified_time,
                            'data_type': cache_info.get('data_type', 'unknown'),
                            'stock_id': cache_info.get('stock_id', 'unknown'),
                            'date_range': cache_info.get('date_range', 'unknown'),
                            'display_name': cache_info.get('display_name', filename),
                            'friendly_display_name': friendly_display_name,
                            'full_path': file_path,
                            'metadata': metadata
                        })
                    except Exception as e:
                        self.logger.error(f"處理快取檔案失敗 {filename}: {e}")
            
            # 統計快取項目
            total_items = len(self.cache_metadata)
            memory_items = len(self.memory_cache)
            
            # 統計股票代碼
            stock_ids = set()
            for metadata in self.cache_metadata.values():
                stock_ids.add(metadata.get('stock_id', ''))
            
            return {
                'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                'memory_usage_bytes': memory_usage,
                'max_memory_mb': round(self.max_memory_bytes / (1024 * 1024), 2),
                'memory_items': memory_items,
                'file_cache_size_mb': round(file_cache_size / (1024 * 1024), 2),
                'file_cache_count': file_cache_count,
                'total_items': total_items,
                'unique_stocks': len(stock_ids),
                'stock_ids': list(stock_ids),
                'cache_metadata': self.cache_metadata,
                'cache_files': cache_files
            }
    
    def is_cached(self, stock_id: str, start_date: str, end_date: str, 
                  data_type: str = "price") -> bool:
        """
        檢查資料是否已快取
        
        Args:
            stock_id (str): 股票代碼
            start_date (str): 開始日期
            end_date (str): 結束日期
            data_type (str): 資料類型
            
        Returns:
            bool: 是否已快取
        """
        cache_key = self._generate_cache_key(stock_id, start_date, end_date, data_type)
        
        # 檢查記憶體快取
        if cache_key in self.memory_cache:
            return True
        
        # 檢查檔案快取
        cache_file = self._get_cache_file_path(cache_key)
        if os.path.exists(cache_file):
            # 檢查是否過期
            if cache_key in self.cache_metadata:
                expires_at = datetime.fromisoformat(self.cache_metadata[cache_key].get('expires_at', '1970-01-01'))
                if datetime.now() <= expires_at:
                    return True
        
        return False
    
    def preload_cache(self, stock_ids: List[str], start_date: str, end_date: str, 
                     data_type: str = "price") -> Dict[str, bool]:
        """
        預載入快取
        
        Args:
            stock_ids (List[str]): 股票代碼列表
            start_date (str): 開始日期
            end_date (str): 結束日期
            data_type (str): 資料類型
            
        Returns:
            Dict[str, bool]: 預載入結果
        """
        results = {}
        
        for stock_id in stock_ids:
            cache_key = self._generate_cache_key(stock_id, start_date, end_date, data_type)
            cache_file = self._get_cache_file_path(cache_key)
            
            if os.path.exists(cache_file) and cache_key not in self.memory_cache:
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    self._cleanup_memory_cache()
                    self.memory_cache[cache_key] = data
                    results[stock_id] = True
                    
                except Exception as e:
                    self.logger.error(f"預載入快取失敗 {stock_id}: {e}")
                    results[stock_id] = False
            else:
                results[stock_id] = False
        
        return results

# 全域快取管理器實例
cache_manager = CacheManager() 