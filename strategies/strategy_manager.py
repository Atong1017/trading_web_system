# 策略管理器
import json
import os
import uuid
import ast
from typing import Dict, List, Any, Optional
from datetime import datetime
from core.utils import Utils
import polars as pl

def print_log(message: str):
    print(f"********** strategy_manager.py - {message}")
    
class StrategyManager:
    """策略管理器，用於管理用戶自定義的策略"""
    
    def __init__(self, storage_dir: str = "data/strategies"):
        """
        初始化策略管理器
        
        Args:
            storage_dir (str): 策略儲存目錄
        """
        # 確保路徑使用正斜線，避免 Windows 路徑問題
        self.storage_dir = storage_dir.replace('\\', '/')
        self.strategies_file = os.path.join(self.storage_dir, "strategies.json").replace('\\', '/')
        self.strategies: Dict[str, Dict[str, Any]] = {}
        
        # 確保目錄存在
        Utils.ensure_directory(storage_dir)
        
        # 載入現有策略
        self._load_strategies()
    
    def _load_strategies(self):
        """載入策略列表"""
        # 確保使用正確的路徑分隔符號
        strategies_file = self.strategies_file.replace('\\', '/')
        
        if os.path.exists(strategies_file):
            try:
                print(f"正在載入策略檔案: {strategies_file}")
                with open(strategies_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"檔案內容長度: {len(content)}")
                    self.strategies = json.loads(content)
                    print(f"成功載入 {len(self.strategies)} 個策略")
            except Exception as e:
                import traceback
                print(f"載入策略列表失敗: {e}")
                print(f"錯誤詳情: {traceback.format_exc()}")
                self.strategies = {}
        else:
            print(f"策略檔案不存在: {strategies_file}")
            self.strategies = {}
    
    def _save_strategies(self):
        """儲存策略列表"""
        try:
            # 確保使用正確的路徑分隔符號
            strategies_file = self.strategies_file.replace('\\', '/')
            with open(strategies_file, 'w', encoding='utf-8') as f:
                json.dump(self.strategies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存策略列表失敗: {e}")
    
    def _extract_custom_parameters(self, code: str) -> Dict[str, Any]:
        """
        從策略程式碼中提取自定義參數
        
        Args:
            code (str): 策略程式碼
            
        Returns:
            Dict[str, Any]: 提取的參數配置
        """
        try:
            # 建立執行環境
            exec_globals = {}
            exec(code, exec_globals)
            
            # 檢查是否有 custom_parameters
            if 'custom_parameters' in exec_globals:
                return exec_globals['custom_parameters']
            
            return {}
        except Exception as e:
            print(f"提取自定義參數失敗: {e}")
            return {}
    
    def create_strategy(self, name: str, description: str, code: str, parameters: Dict[str, Any] = None, 
                       is_confirmed: bool = False, editor_mode: str = "jupyter", 
                       jupyter_strategy_type: str = "analysis") -> str:
        """
        建立新策略
        
        Args:
            name (str): 策略名稱
            description (str): 策略描述
            code (str): 策略程式碼
            parameters (Dict[str, Any]): 策略參數配置
            is_confirmed (bool): 是否為確認版策略
            editor_mode (str): 編輯模式 ("traditional" 或 "jupyter")
            jupyter_strategy_type (str): Jupyter 策略類型
            
        Returns:
            str: 策略ID
        """
        # 生成唯一ID
        strategy_id = str(uuid.uuid4())
        
        # 驗證策略程式碼語法
        try:
            ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"策略程式碼語法錯誤: {str(e)}")
        
        # 從程式碼中提取自定義參數
        extracted_parameters = self._extract_custom_parameters(code)
        
        # 合併參數（程式碼中的參數優先）
        final_parameters = {}
        if parameters:
            final_parameters.update(parameters)
        if extracted_parameters:
            final_parameters.update(extracted_parameters)
        
        # 建立策略檔案
        strategy_file = os.path.join(self.storage_dir, f"{strategy_id}.py").replace('\\', '/')
        try:
            with open(strategy_file, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            raise ValueError(f"儲存策略檔案失敗: {str(e)}")
        
        # 儲存策略資訊
        strategy_info = {
            "id": strategy_id,
            "name": name,
            "description": description,
            "code": code,
            "parameters": final_parameters,
            "is_confirmed": is_confirmed,  # 新增確認狀態
            "editor_mode": editor_mode,  # 新增編輯模式
            "jupyter_strategy_type": jupyter_strategy_type,  # 新增 Jupyter 策略類型
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "file_path": strategy_file  # 已經統一使用正斜線
        }
        
        self.strategies[strategy_id] = strategy_info
        self._save_strategies()
        
        return strategy_id
    
    def update_strategy(self, strategy_id: str, name: str = None, description: str = None, 
                       code: str = None, parameters: Dict[str, Any] = None, is_confirmed: bool = None) -> bool:
        """
        更新策略
        
        Args:
            strategy_id (str): 策略ID
            name (str): 新策略名稱
            description (str): 新策略描述
            code (str): 新策略程式碼
            parameters (Dict[str, Any]): 新策略參數配置
            is_confirmed (bool): 是否為確認版策略
            
        Returns:
            bool: 是否更新成功
        """
        if strategy_id not in self.strategies:
            raise ValueError(f"策略不存在: {strategy_id}")
        
        strategy_info = self.strategies[strategy_id]
        
        # 更新欄位
        if name is not None:
            strategy_info["name"] = name
        if description is not None:
            strategy_info["description"] = description
        if is_confirmed is not None:
            strategy_info["is_confirmed"] = is_confirmed
        
        # 如果更新程式碼，需要重新驗證並提取參數
        if code is not None:
            try:
                # 驗證新程式碼語法
                ast.parse(code)
                
                # 從程式碼中提取自定義參數
                extracted_parameters = self._extract_custom_parameters(code)
                
                # 合併參數（程式碼中的參數優先）
                final_parameters = {}
                if parameters:
                    final_parameters.update(parameters)
                if extracted_parameters:
                    final_parameters.update(extracted_parameters)
                
                strategy_info["parameters"] = final_parameters
                
                # 更新程式碼檔案
                strategy_file = strategy_info["file_path"].replace('\\', '/')
                with open(strategy_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                strategy_info["code"] = code
            except SyntaxError as e:
                raise ValueError(f"策略程式碼語法錯誤: {str(e)}")
        elif parameters is not None:
            # 如果只更新參數，不更新程式碼
            strategy_info["parameters"] = parameters
        
        # 更新時間戳
        strategy_info["updated_at"] = datetime.now().isoformat()
        
        # 儲存更新
        self._save_strategies()
        
        return True
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """
        刪除策略
        
        Args:
            strategy_id (str): 策略ID
            
        Returns:
            bool: 是否刪除成功
        """
        if strategy_id not in self.strategies:
            raise ValueError(f"策略不存在: {strategy_id}")
        
        strategy_info = self.strategies[strategy_id]
        
        # 刪除策略檔案
        try:
            strategy_file = strategy_info["file_path"].replace('\\', '/')
            if os.path.exists(strategy_file):
                os.remove(strategy_file)
        except Exception as e:
            print(f"刪除策略檔案失敗: {e}")
        
        # 從列表中移除
        del self.strategies[strategy_id]
        self._save_strategies()
        
        return True
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        取得策略資訊
        
        Args:
            strategy_id (str): 策略ID
            
        Returns:
            Optional[Dict[str, Any]]: 策略資訊
        """
        return self.strategies.get(strategy_id)
    
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """
        取得所有策略列表
        
        Returns:
            List[Dict[str, Any]]: 策略列表
        """
        return list(self.strategies.values())
    
    def get_confirmed_strategies(self) -> List[Dict[str, Any]]:
        """
        取得所有確認版策略列表
        
        Returns:
            List[Dict[str, Any]]: 確認版策略列表
        """
        return [strategy for strategy in self.strategies.values() if strategy.get("is_confirmed", False)]
    
    def get_editing_strategies(self) -> List[Dict[str, Any]]:
        """
        取得所有編輯中的策略列表
        
        Returns:
            List[Dict[str, Any]]: 編輯中的策略列表
        """
        return [strategy for strategy in self.strategies.values() if not strategy.get("is_confirmed", False)]
    
    def create_strategy_instance(self, strategy_id: str, parameters: Dict[str, Any] = None):
        """
        建立策略實例
        
        Args:
            strategy_id (str): 策略ID
            parameters (Dict[str, Any]): 策略參數
            
        Returns:
            DynamicStrategy: 策略實例
        """
        # 延遲導入避免循環導入
        from strategies.dynamic_strategy import DynamicStrategy
        
        if strategy_id not in self.strategies:
            raise ValueError(f"策略不存在: {strategy_id}")
        
        strategy_info = self.strategies[strategy_id]
        
        # 合併參數
        merged_parameters = strategy_info.get("parameters", {}).copy()
        if parameters:
            merged_parameters.update(parameters)
        
        # 建立策略實例
        return DynamicStrategy(
            parameters=merged_parameters,
            strategy_code=strategy_info["code"],
            strategy_name=strategy_info["name"]
        )
    
    def validate_strategy_code(self, code: str) -> bool:
        """
        驗證策略程式碼
        
        Args:
            code (str): 策略程式碼
            
        Returns:
            bool: 是否有效
        """
        try:
            # 延遲導入避免循環導入
            from strategies.dynamic_strategy import DynamicStrategy
            
            # 嘗試建立臨時策略實例
            temp_strategy = DynamicStrategy({}, code, "temp")
            return True
        except Exception:
            return False
    
    def get_strategy_template(self) -> str:
        """
        取得策略模板（混合模式，包含向量化和狀態機）
        
        Returns:
            str: 策略模板程式碼
        """
        template = '''# 自定義策略模板（混合模式）
# 請實作以下函數來定義您的策略邏輯
# 
# 可用的工具類別：
# - PriceUtils: 價格計算工具，包含最小變動單位、漲跌停計算等
# - Utils: 通用工具類別
# - TradeRecord: 交易記錄資料類別
# - generate_indicators: 生成技術指標

# ===== 向量化模式（推薦，效能最佳） =====
def calculate_entry_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算進場信號
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        polars.DataFrame: 包含 should_entry 和 entry_reason 欄位的 DataFrame
    """
    # 生成技術指標
    df = generate_indicators(stock_data, ['break_20_day_high'])
    
    # 範例：當日突破20日高點，則下一日進場
    df = df.with_columns([
        pl.when(pl.col("break_20_day_high").shift(1) == 1)
        .then(1)
        .otherwise(0)
        .alias("should_entry"),
        
        pl.when(pl.col("break_20_day_high").shift(1) == 1)
        .then(pl.lit("突破20日新高"))
        .otherwise(pl.lit(""))
        .alias("entry_reason")
    ])
    
    return df

def calculate_exit_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算出場信號
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        polars.DataFrame: 包含 should_exit 和 exit_reason 欄位的 DataFrame
    """    
    # 範例：持有超過指定天數或虧損超過指定比例時出場
    df = stock_data.with_columns([
        pl.when(pl.col("should_entry").shift(1) == 1)
        .then(1)
        .otherwise(0)
        .alias("should_exit"),
        
        pl.when(pl.col("should_entry").shift(1) == 1)
        .then(pl.lit("隔日出場"))
        .otherwise(pl.lit(""))
        .alias("entry_reason")
    ])
    
    return df

# ===== 狀態機模式（適用於複雜邏輯） =====
def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    """
    判斷是否應該進場（狀態機模式）
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        tuple: (是否進場, 進場資訊)
    """
    # 範例：當收盤價大於開盤價時進場
    current_row = stock_data.row(current_index, named=True)
    
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df, **kwargs):
    """
    判斷是否應該出場（狀態機模式）
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        position: 當前持倉資訊
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        tuple: (是否出場, 出場資訊)
    """
    # 範例：持有超過5天或虧損超過5%時出場
    current_row = stock_data.row(current_index, named=True)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    # 計算持有天數
    entry_row = stock_data.row(entry_index, named=True)
    holding_days = (current_row["date"] - entry_row["date"]).days
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 5 or loss_rate <= -5:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    
    return False, {}

# ===== 策略參數配置範例 =====
# 固定自定義參數
custom_parameters = {
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 5,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數"
    },
    'record_holdings': {
        'type': 'boolean', 
        'label': '完整記錄', 
        'description': '是否記錄未出場', 
        'default': True
    }
}

# ===== 處理策略參數 =====
def process_parameters(parameters):
    """
    處理策略參數
    
    Args:
        parameters: 輸入參數
        
    Returns:
        dict: 處理後的參數
    """
    # 在這裡處理參數邏輯
    return parameters

def validate_parameters(parameters):
    """
    驗證策略參數
    
    Args:
        parameters: 策略參數
        
    Raises:
        ValueError: 當參數無效時
    """
    # 在這裡驗證參數
    pass

# ===== 使用說明 =====
# 1. 向量化模式（推薦，預設啟用）：
#    - "需"定義 calculate_entry_signals 和 calculate_exit_signals 函數
#    - 使用 Polars 向量化操作，效能最佳
#    - 適用於大量數據處理和簡單邏輯
#    - 可使用 generate_indicators() 生成技術指標
#    - 如果向量化失敗，會自動回退到狀態機模式
#
# 2. 狀態機模式（適用於複雜邏輯）：
#    - "需"定義 should_entry 和 should_exit 函數
#    - 逐行判斷，適用於複雜邏輯和跨列狀態追蹤
#    - 支援複雜的進出場條件和狀態管理
#    - 向後相容，適合複雜策略
#
# 3. 混合模式(適用於複雜策略)：
#    - 可以同時定義向量化和傳統函數
#    - 系統會優先使用向量化函數
#    - 如果向量化信號不足，會使用傳統函數作為備用
#
# 4. 模式選擇建議：
#    - 簡單邏輯（如：突破、均線交叉）：使用向量化模式
#    - 複雜邏輯（如：多條件組合、狀態追蹤）：使用狀態機模式
#    - 不確定時：先嘗試向量化，失敗會自動回退
#
# 5. 可用的技術指標：
#    - break_20_day_high: 突破20日新高
#    - break_10_day_high: 突破10日新高
#    - ma_5, ma_10, ma_20: 移動平均線
#    - volume_ma_20: 成交量移動平均
#
# 6. 策略參數配置範例:
#    - custom_parameters: 要固定顯示在回測頁面的參數
#    - 新增/刪除/修改參數: 新增/刪除/修改參數，會修改回測頁面
'''
        return template
    
    def get_vectorized_template(self) -> str:
        """
        取得向量化策略模板
        
        Returns:
            str: 向量化策略模板程式碼
        """
        template = '''# 向量化策略模板（推薦）
# 使用 Polars 向量化操作，效能最佳
# 適用於大量數據處理和簡單邏輯
# 
# 可用的工具類別：
# - PriceUtils: 價格計算工具，包含最小變動單位、漲跌停計算等
# - Utils: 通用工具類別
# - TradeRecord: 交易記錄資料類別
# - generate_indicators: 生成技術指標

def calculate_entry_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算進場信號
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        polars.DataFrame: 包含 should_entry 和 entry_reason 欄位的 DataFrame
    """
    # 生成技術指標
    df = generate_indicators(stock_data, ['break_20_day_high'])
    
    # 範例：當日突破20日高點，則下一日進場
    df = df.with_columns([
        pl.when(pl.col("break_20_day_high").shift(1) == 1)
        .then(1)
        .otherwise(0)
        .alias("should_entry"),
        
        pl.when(pl.col("break_20_day_high").shift(1) == 1)
        .then(pl.lit("突破20日新高"))
        .otherwise(pl.lit(""))
        .alias("entry_reason")
    ])
    
    return df

def calculate_exit_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算出場信號
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        polars.DataFrame: 包含 should_exit 和 exit_reason 欄位的 DataFrame
    """    
    # 範例：持有超過指定天數或虧損超過指定比例時出場
    df = stock_data.with_columns([
        pl.when(pl.col("should_entry").shift(1) == 1)
        .then(1)
        .otherwise(0)
        .alias("should_exit"),
        
        pl.when(pl.col("should_entry").shift(1) == 1)
        .then(pl.lit("隔日出場"))
        .otherwise(pl.lit(""))
        .alias("entry_reason")
    ])
    
    return df
    
# ===== 策略參數配置範例 =====
# 固定自定義參數
custom_parameters = {
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 5,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數"
    },
    'record_holdings': {
        'type': 'boolean', 
        'label': '完整記錄', 
        'description': '是否記錄未出場', 
        'default': True
    }
}

# ===== 自定義函數 =====
def process_parameters(parameters):
    """
    處理策略參數
    
    Args:
        parameters: 輸入參數
        
    Returns:
        dict: 處理後的參數
    """
    # 在這裡處理參數邏輯
    return parameters

def validate_parameters(parameters):
    """
    驗證策略參數
    
    Args:
        parameters: 策略參數
        
    Raises:
        ValueError: 當參數無效時
    """
    # 在這裡驗證參數
    pass

# ===== 使用說明 =====
# 1. 向量化模式特點：
#    - 使用 Polars 向量化操作，效能最佳
#    - 適用於大量數據處理和簡單邏輯
#    - 可使用 generate_indicators() 生成技術指標
#    - 支援複雜的條件組合
#
# 2. 必須實作的函數：
#    - calculate_entry_signals: 計算進場信號
#    - calculate_exit_signals: 計算出場信號
#
# 3. 可用的技術指標：
#    - break_20_day_high: 突破20日新高
#    - break_10_day_high: 突破10日新高
#    - ma_5, ma_10, ma_20: 移動平均線
#    - volume_ma_20: 成交量移動平均
#    - 更多指標請參考 core/technical_indicators.py
#
# 4. 範例邏輯：
#    - 突破策略：使用 break_20_day_high 等指標
#    - 均線策略：使用 ma_5, ma_10, ma_20 等指標
#    - 成交量策略：使用 volume_ma_20 等指標
#
# 5. 策略參數配置範例:
#    - custom_parameters: 要固定顯示在回測頁面的參數
#    - 新增/刪除/修改參數: 新增/刪除/修改參數，會修改回測頁面

'''
        return template
    
    def get_state_machine_template(self) -> str:
        """
        取得狀態機策略模板
        
        Returns:
            str: 狀態機策略模板程式碼
        """
        template = '''# 狀態機策略模板
# 使用逐行判斷，適用於複雜邏輯和跨列狀態追蹤
# 支援複雜的進出場條件和狀態管理
# 
# 可用的工具類別：
# - PriceUtils: 價格計算工具，包含最小變動單位、漲跌停計算等
# - Utils: 通用工具類別
# - TradeRecord: 交易記錄資料類別
# - generate_indicators: 生成技術指標

def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    """
    判斷是否應該進場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        tuple: (是否進場, 進場資訊)
    """
    # 取得當前資料行
    current_row = stock_data.row(current_index, named=True)
    
    # 範例：當收盤價大於開盤價時進場
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    
    # 範例：檢查前幾天的資料（適用於複雜邏輯）
    if current_index >= 5:
        # 檢查前5天的收盤價是否都上漲
        all_rising = True
        for i in range(current_index - 4, current_index + 1):
            prev_row = stock_data.row(i - 1, named=True)
            curr_row = stock_data.row(i, named=True)
            if curr_row["close"] <= prev_row["close"]:
                all_rising = False
                break
        
        if all_rising:
            return True, {"reason": "連續5天上漲"}
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df, **kwargs):
    """
    判斷是否應該出場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        position: 當前持倉資訊
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        tuple: (是否出場, 出場資訊)
    """
    # 取得當前資料行
    current_row = stock_data.row(current_index, named=True)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    # 計算持有天數
    entry_row = stock_data.row(entry_index, named=True)
    holding_days = (current_row["date"] - entry_row["date"]).days
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    # 範例：持有超過指定天數或虧損超過指定比例時出場
    max_holding_days = kwargs.get("max_holding_days", 5)
    max_loss_rate = kwargs.get("max_loss_rate", 5.0)
    
    if holding_days >= max_holding_days:
        return True, {"reason": f"持有{holding_days}天"}
    
    if loss_rate <= -max_loss_rate:
        return True, {"reason": f"虧損{loss_rate:.2f}%"}
    
    # 範例：檢查連續下跌（適用於複雜邏輯）
    if current_index >= 3:
        # 檢查前3天是否連續下跌
        all_falling = True
        for i in range(current_index - 2, current_index + 1):
            prev_row = stock_data.row(i - 1, named=True)
            curr_row = stock_data.row(i, named=True)
            if curr_row["close"] >= prev_row["close"]:
                all_falling = False
                break
        
        if all_falling:
            return True, {"reason": "連續3天下跌"}
    
    return False, {}

# ===== 策略參數配置範例 =====
# 固定自定義參數
custom_parameters = {
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 5,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數"
    },
    'record_holdings': {
        'type': 'boolean', 
        'label': '完整記錄', 
        'description': '是否記錄未出場', 
        'default': True
    }
}

# ===== 自定義函數 =====
def process_parameters(parameters):
    """
    處理策略參數
    
    Args:
        parameters: 輸入參數
        
    Returns:
        dict: 處理後的參數
    """
    # 在這裡處理參數邏輯
    return parameters

def validate_parameters(parameters):
    """
    驗證策略參數
    
    Args:
        parameters: 策略參數
        
    Raises:
        ValueError: 當參數無效時
    """
    # 在這裡驗證參數
    pass

# ===== 使用說明 =====
# 1. 狀態機模式特點：
#    - 逐行判斷，適用於複雜邏輯和跨列狀態追蹤
#    - 支援複雜的進出場條件和狀態管理
#    - 可以檢查歷史資料和未來資料
#    - 適合複雜的技術分析邏輯
#
# 2. 必須實作的函數：
#    - should_entry: 判斷是否進場
#    - should_exit: 判斷是否出場
#
# 3. 函數參數說明：
#    - stock_data: 股價資料 DataFrame
#    - current_index: 當前資料索引
#    - position: 當前持倉資訊（僅 should_exit 函數）
#    - excel_pl_df: Excel股票列表
#    - **kwargs: 策略參數
#
# 4. 返回值格式：
#    - should_entry: (bool, dict) - (是否進場, 進場資訊)
#    - should_exit: (bool, dict) - (是否出場, 出場資訊)
#
# 5. 範例邏輯：
#    - 連續上漲/下跌檢測
#    - 複雜的技術指標組合
#    - 基於歷史資料的條件判斷
#    - 動態止損止盈
#
# 6. 策略參數配置範例:
#    - custom_parameters: 要固定顯示在回測頁面的參數
#    - 新增/刪除/修改參數: 新增/刪除/修改參數，會修改回測頁面
'''
        return template
    
    def search_strategies(self, keyword: str = None, category: str = None) -> List[Dict[str, Any]]:
        """
        搜尋策略
        
        Args:
            keyword (str): 關鍵字
            category (str): 分類
            
        Returns:
            List[Dict[str, Any]]: 搜尋結果
        """
        results = []
        
        for strategy in self.strategies.values():
            # 關鍵字搜尋
            if keyword:
                if (keyword.lower() in strategy["name"].lower() or 
                    keyword.lower() in strategy["description"].lower() or
                    keyword.lower() in strategy["code"].lower()):
                    results.append(strategy)
            else:
                results.append(strategy)
        
        return results
    
    def export_strategy(self, strategy_id: str, export_path: str) -> bool:
        """
        匯出策略
        
        Args:
            strategy_id (str): 策略ID
            export_path (str): 匯出路徑
            
        Returns:
            bool: 是否匯出成功
        """
        if strategy_id not in self.strategies:
            raise ValueError(f"策略不存在: {strategy_id}")
        
        strategy_info = self.strategies[strategy_id]
        
        try:
            export_data = {
                "strategy_info": strategy_info,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"匯出策略失敗: {e}")
            return False
    
    def import_strategy(self, import_path: str) -> str:
        """
        匯入策略
        
        Args:
            import_path (str): 匯入檔案路徑
            
        Returns:
            str: 新策略ID
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            strategy_info = import_data["strategy_info"]
            
            # 建立新策略
            strategy_id = self.create_strategy(
                name=strategy_info["name"],
                description=strategy_info["description"],
                code=strategy_info["code"],
                parameters=strategy_info.get("parameters", {})
            )
            
            return strategy_id
        except Exception as e:
            raise ValueError(f"匯入策略失敗: {str(e)}") 