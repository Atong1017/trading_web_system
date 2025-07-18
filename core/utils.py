# 通用工具函數模組
import os
import polars as pl
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiofiles
import json

def print_log(message: str):
    """日誌輸出"""
    print(f"********** utils.py - {message}")

class Utils:
    """通用工具類別"""
    
    @staticmethod
    def ensure_directory(directory: str) -> None:
        """確保目錄存在，不存在則建立"""
        # 確保路徑使用正斜線
        directory = directory.replace('\\', '/')
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """取得檔案副檔名"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def is_valid_excel_file(filename: str) -> bool:
        """檢查是否為有效的Excel檔案"""
        valid_extensions = ['.xlsx', '.xls', '.csv']
        return Utils.get_file_extension(filename) in valid_extensions
    
    @staticmethod
    def read_excel_file(file_path: str) -> pl.DataFrame:
        """讀取Excel檔案"""
        try:
            # 確保路徑使用正斜線
            file_path = file_path.replace('\\', '/')
            if file_path.endswith('.csv'):
                data = pl.read_csv(file_path)
            else:
                # 嘗試讀取Excel檔案
                data = pl.read_excel(file_path)
            
            return data
            
        except Exception as e:
            print(f"讀取檔案失敗: {file_path}, 錯誤: {str(e)}")
            raise ValueError(f"無法讀取檔案 {file_path}: {str(e)}")
    
    @staticmethod
    def save_excel_file(df: pl.DataFrame, file_path: str, sheet_name: str = "Sheet1") -> None:
        """儲存Excel檔案"""
        try:
            # 確保路徑使用正斜線
            file_path = file_path.replace('\\', '/')
            if file_path.endswith('.csv'):
                df.write_csv(file_path)
            else:
                df.write_excel(file_path, worksheet=sheet_name)
        except Exception as e:
            raise ValueError(f"無法儲存檔案 {file_path}: {str(e)}")
    
    @staticmethod
    def validate_stock_data(data: pl.DataFrame, required_columns: List[str]) -> Dict[str, str]:
        """
        驗證股票資料的欄位並返回欄位映射
        
        Args:
            data (pl.DataFrame): 股票資料
            required_columns (List[str]): 必要欄位列表
            
        Returns:
            Dict[str, str]: 標準欄位名稱到實際欄位名稱的映射
            
        Raises:
            ValueError: 當缺少必要欄位時
        """
        if data.is_empty():
            raise ValueError("資料為空")
        
        # 欄位名稱映射表，支援多種常見的欄位名稱
        column_mapping = {
            "stock_id": ["stock_id", "證券代碼", "股票代碼", "代碼", "code", "symbol"],
            "date": ["date", "年月日", "日期", "開始日期", "交易日期", "time", "datetime"],
            "open": ["open", "開盤價", "開盤", "open_price"],
            "high": ["high", "最高價", "最高", "high_price", "max"],
            "low": ["low", "最低價", "最低", "low_price", "min"],
            "close": ["close", "收盤價", "收盤", "close_price"],
            "volume": ["volume", "成交量", "vol", "volume_amount", "trading_volume", "交易量"]
        }
        
        # 檢查必要欄位
        missing_columns = []
        found_columns = {}
        
        for required_col in required_columns:
            found = False
            # 檢查原始欄位名稱
            if required_col in data.columns:
                found_columns[required_col] = required_col
                found = True
            else:
                # 檢查映射的欄位名稱
                if required_col in column_mapping:
                    for mapped_col in column_mapping[required_col]:
                        if mapped_col in data.columns:
                            found_columns[required_col] = mapped_col
                            found = True
                            break
            
            if not found:
                missing_columns.append(required_col)
        
        if missing_columns:
            raise ValueError(f"缺少必要欄位: {', '.join(missing_columns)}")
        
        # 檢查是否有空值
        for required_col, actual_col in found_columns.items():
            if data.select(actual_col).null_count().item() > 0:
                raise ValueError(f"欄位 {actual_col} (對應 {required_col}) 包含空值")
            
        return found_columns
    
    @staticmethod
    def standardize_columns(data: pl.DataFrame, required_columns: List[str]) -> pl.DataFrame:
        """
        標準化欄位名稱
        
        Args:
            data (pl.DataFrame): 原始資料
            required_columns (List[str]): 必要欄位列表
            
        Returns:
            pl.DataFrame: 標準化欄位名稱後的資料
        """
        # 取得欄位映射
        column_mapping = Utils.validate_stock_data(data, required_columns)
        # 標準化欄位名稱
        standardized_data = data.clone()  # 複製資料        
        
        # 重新命名欄位為標準名稱
        rename_dict = {}
        for standard_col, actual_col in column_mapping.items():
            if actual_col != standard_col:
                rename_dict[actual_col] = standard_col
        if rename_dict:
            standardized_data = standardized_data.rename(rename_dict)

        standardized_data = Utils.standardize_date_column(standardized_data, "date")
        # 將股票代碼轉換為字串
        standardized_data = standardized_data.with_columns([
            pl.col("stock_id")
            .cast(pl.Utf8)  # 確保是字串
            .str.strip_chars()              # 去除前後空白（含全形空白）
            .str.replace_all(r"\D", "")  # \D 代表非數字，全部替換為空字串
            .alias("stock_id"),
            pl.col("date").cast(pl.Date)  # 確保日期欄位為日期類型
        ])
        
        return standardized_data
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """解析日期字串"""
        try:
            # 嘗試多種日期格式
            formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"無法解析日期格式: {date_str}")
        except Exception as e:
            raise ValueError(f"日期解析錯誤: {str(e)}")
    
    @staticmethod
    def format_date(date: datetime) -> str:
        """格式化日期為字串"""
        return date.strftime('%Y-%m-%d')
    
    @staticmethod
    def get_trading_days(start_date: datetime, end_date: datetime) -> List[datetime]:
        """取得交易日列表（簡化版，實際應使用交易日曆）"""
        trading_days = []
        current_date = start_date
        while current_date <= end_date:
            # 排除週末
            if current_date.weekday() < 5:  # 0-4 為週一到週五
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        return trading_days
    
    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """將列表分割成指定大小的塊"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    async def async_read_file(file_path: str) -> str:
        """非同步讀取檔案"""
        # 確保路徑使用正斜線
        file_path = file_path.replace('\\', '/')
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    @staticmethod
    async def async_write_file(file_path: str, content: str) -> None:
        """非同步寫入檔案"""
        # 確保路徑使用正斜線
        file_path = file_path.replace('\\', '/')
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, float]:
        """計算統計資料"""
        if not data:
            return {}
        
        return {
            'mean': np.mean(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'median': np.median(data),
            'count': len(data)
        }
    
    @staticmethod
    def calculate_drawdown(equity_curve: List[float]) -> Dict[str, float]:
        """計算回撤"""
        if not equity_curve:
            return {}
        
        peak = equity_curve[0]
        max_drawdown = 0
        max_drawdown_pct = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            
            drawdown = peak - value
            drawdown_pct = drawdown / peak if peak > 0 else 0
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_pct = drawdown_pct
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct
        }
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """計算夏普比率"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate / 252  # 日化無風險利率
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    @staticmethod
    def format_number(number: float, decimal_places: int = 2) -> str:
        """格式化數字"""
        return f"{number:.{decimal_places}f}"
    
    @staticmethod
    def format_percentage(number: float, decimal_places: int = 2) -> str:
        """格式化百分比"""
        return f"{number * 100:.{decimal_places}f}%"
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """安全除法"""
        if denominator == 0:
            return default
        return numerator / denominator
    
    @staticmethod
    def generate_unique_filename(prefix: str, extension: str) -> str:
        """產生唯一檔案名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """清理檔案名，移除不合法字元"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """取得檔案大小（MB）"""
        # 確保路徑使用正斜線
        file_path = file_path.replace('\\', '/')
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
        return 0.0
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: float = 10.0) -> bool:
        """驗證檔案大小"""
        # 確保路徑使用正斜線
        file_path = file_path.replace('\\', '/')
        file_size = Utils.get_file_size_mb(file_path)
        return file_size <= max_size_mb
    
    @staticmethod
    def parse_date_string(date_str: str) -> datetime:
        """
        解析日期字串，支援多種日期格式
        
        Args:
            date_str (str): 日期字串
            
        Returns:
            datetime: 解析後的datetime物件
            
        Raises:
            ValueError: 當無法解析日期時
        """
        if not date_str or date_str.strip() == '':
            raise ValueError(f"日期字串為空: {date_str}")
        
        if not isinstance(date_str, str):
            raise ValueError(f"日期必須是字串格式: {date_str}")
        
        date_str = date_str.strip()
        
        try:
            # 嘗試多種日期格式
            formats = [
                '%Y-%m-%d',      # 2023-01-19
                '%Y/%m/%d',      # 2023/01/19
                '%Y%m%d',        # 20230119
                '%m-%d-%y',      # 01-19-23
                '%m/%d/%y',      # 01/19/23
                '%m-%d-%Y',      # 01-19-2023
                '%m/%d/%Y',      # 01/19/2023
                '%d-%m-%y',      # 19-01-23
                '%d/%m/%y',      # 19/01/23
                '%d-%m-%Y',      # 19-01-2023
                '%d/%m/%Y',      # 19/01/2023
            ]
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date
                except ValueError:
                    continue
            
            # 如果所有格式都失敗，嘗試處理特殊情況
            # 處理只有數字的情況（如：20230119）
            if date_str.isdigit():
                if len(date_str) == 8:
                    try:
                        return datetime.strptime(date_str, '%Y%m%d')
                    except ValueError:
                        pass
                elif len(date_str) == 6:
                    try:
                        return datetime.strptime(date_str, '%y%m%d')
                    except ValueError:
                        pass
            
            raise ValueError(f"無法解析日期格式: {date_str}")
            
        except Exception as e:
            raise ValueError(f"日期解析錯誤 '{date_str}': {str(e)}")
    
    @staticmethod
    def parse_date_list(date_strings: str) -> datetime:
        """
        解析日期字串列表
        
        Args:
            date_strings (str): 日期字串列表
            
        Returns:
            List[datetime]: 解析後的datetime物件列表
        """
        parsed_dates = []
        for date_str in date_strings:
            try:
                parsed_date = Utils.parse_date_string(date_str)
                parsed_dates.append(parsed_date)
            except Exception as e:
                print(f"跳過無效日期: {date_strings}, 錯誤: {e}")        
        return parsed_dates
    
    @staticmethod
    def get_date_range_from_list(date_strings: List[str], days_before: int = 0) -> Tuple[str, str]:
        """
        從日期字串列表取得日期範圍
        
        Args:
            date_strings (List[str]): 日期字串列表
            days_before (int): 開始日期要往前推的天數
            
        Returns:
            Tuple[str, str]: (開始日期, 結束日期) 格式為 YYYY-MM-DD
        """
        if not date_strings:
            raise ValueError("日期列表為空")
        
        parsed_dates = Utils.parse_date_list(date_strings)
        if not parsed_dates:
            raise ValueError("沒有有效的日期資料")
        
        dates = []
        for date in parsed_dates:
            parse_date = date + timedelta(days=days_before)
            dates.append(date.strftime('%Y-%m-%d'))
            dates.append(parse_date.strftime('%Y-%m-%d'))

        start_date = min(dates)
        end_date = max(dates)
        
        return start_date, end_date
    
    @staticmethod
    def convert_date_format(date_str: str, days_offset: int = 0) -> str:
        """
        轉換日期格式並可選擇往前或往後偏移天數
        
        Args:
            date_str (str): 日期字串
            days_offset (int): 天數偏移，正數往後，負數往前
            
        Returns:
            str: 轉換後的日期字串，格式為 YYYY-MM-DD
        """
        try:
            # 解析日期字串
            if '-' in date_str:
                if len(date_str.split('-')[0]) == 2:  # MM-DD-YY 格式
                    parsed_date = datetime.strptime(date_str, '%m-%d-%y')
                else:  # YYYY-MM-DD 格式
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            elif '/' in date_str:
                if len(date_str.split('/')[0]) == 2:  # MM/DD/YY 格式
                    parsed_date = datetime.strptime(date_str, '%m/%d/%y')
                else:  # YYYY/MM/DD 格式
                    parsed_date = datetime.strptime(date_str, '%Y/%m/%d')
            else:
                # 嘗試其他格式
                parsed_date = datetime.strptime(date_str, '%Y%m%d')
            
            # 加上偏移天數
            if days_offset != 0:
                parsed_date = parsed_date + timedelta(days=days_offset)
            
            # 返回標準格式字串
            return parsed_date.strftime('%Y-%m-%d')
            
        except Exception as e:
            raise ValueError(f"無法轉換日期格式 '{date_str}': {str(e)}")
    
    @staticmethod
    def standardize_date_column(data: pl.DataFrame, date_column: str) -> pl.DataFrame:
        """
        標準化 DataFrame 中的日期欄位為 datetime 類型
        
        Args:
            data (pl.DataFrame): 要處理的 DataFrame
            date_column (str): 日期欄位名稱
            
        Returns:
            pl.DataFrame: 處理後的 DataFrame
        """
        if date_column not in data.columns:
            return data
        
        if data[date_column].dtype == pl.Datetime:
            # 將日期欄位轉換為日期類型
            data = data.with_columns([
                pl.col(date_column).cast(pl.Date)
            ])
            
            return data
        
        try:
            # 嘗試不同的日期格式，包括美式日期格式
            date_formats = [
                "%m-%d-%y",      # 01-31-24 (美式)
                "%Y-%m-%d",      # 2024-01-31
                "%Y/%m/%d",      # 2024/01/31
                "%Y%m%d",        # 20240131
                "%Y-%m-%d %H:%M:%S",  # 2024-01-31 10:30:00
                "%m-%d-%Y",      # 01-31-2024 (美式)
                "%m/%d/%Y"       # 01/31/2024 (美式)
            ]
            
            for date_format in date_formats:
                try:
                    data = data.with_columns([
                        pl.col(date_column).str.strptime(pl.Datetime, date_format)
                    ])
                    # 將日期欄位轉換為日期類型
                    data = data.with_columns([
                        pl.col(date_column).cast(pl.Date)
                    ])
                    
                    return data
                except Exception:
                    continue
            
            # 如果所有格式都失敗，嘗試自動解析
            try:
                data = data.with_columns([
                    pl.col(date_column).str.to_datetime()
                ])
            except Exception as e:
                print(f"日期欄位轉換失敗: {e}")
                # 如果轉換失敗，保持原始格式
            
            return data
            
        except Exception as e:
            print(f"標準化日期欄位失敗: {e}")
            return data