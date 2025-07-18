# 向量化 vs 狀態機模式示範策略
# 展示如何使用 use_vectorized 參數來選擇不同的計算模式

import polars as pl
from core.technical_indicators import generate_indicators
from core.price_utils import PriceUtils
from core.utils import Utils
from strategies.base_strategy import TradeRecord, HoldingPosition

# ===== 向量化模式（推薦，效能最佳） =====
def calculate_entry_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算進場信號（推薦）
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        polars.DataFrame: 包含 should_entry 和 entry_reason 欄位的 DataFrame
    """
    # 生成技術指標
    df = generate_indicators(stock_data, ['break_20_day_high', 'ma_5', 'ma_20'])
    
    # 範例：當日突破20日高點且5日均線大於20日均線時進場
    df = df.with_columns([
        pl.when(
            (pl.col("break_20_day_high").shift(1) == 1) & 
            (pl.col("ma_5") > pl.col("ma_20"))
        )
        .then(1)
        .otherwise(0)
        .alias("should_entry"),
        
        pl.when(
            (pl.col("break_20_day_high").shift(1) == 1) & 
            (pl.col("ma_5") > pl.col("ma_20"))
        )
        .then("突破20日新高且均線多頭排列")
        .otherwise("")
        .alias("entry_reason")
    ])
    
    return df

def calculate_exit_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算出場信號（推薦）
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        polars.DataFrame: 包含 should_exit 和 exit_reason 欄位的 DataFrame
    """
    max_holding_days = kwargs.get("max_holding_days", 5)
    max_loss_rate = kwargs.get("max_loss_rate", 5.0)
    
    # 範例：持有超過指定天數或虧損超過指定比例時出場
    df = stock_data.with_columns([
        pl.when(
            (pl.col("holding_days") >= max_holding_days) | 
            (pl.col("profit_loss_rate") <= -max_loss_rate)
        )
        .then(1)
        .otherwise(0)
        .alias("should_exit"),
        
        pl.when(pl.col("holding_days") >= max_holding_days)
        .then(f"持有{max_holding_days}天")
        .when(pl.col("profit_loss_rate") <= -max_loss_rate)
        .then(f"虧損超過{max_loss_rate}%")
        .otherwise("")
        .alias("exit_reason")
    ])
    
    return df

# ===== 狀態機模式（適用於複雜邏輯） =====
def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    """
    判斷是否應該進場（狀態機模式，適用於複雜邏輯）
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        tuple: (是否進場, 進場資訊)
    """
    # 複雜邏輯範例：連續3天收盤價上漲且成交量放大時進場
    if current_index < 3:
        return False, {}
    
    current_row = stock_data.row(current_index, named=True)
    
    # 檢查連續3天收盤價上漲
    consecutive_up = True
    for i in range(current_index - 2, current_index + 1):
        if i > 0:
            prev_row = stock_data.row(i - 1, named=True)
            curr_row = stock_data.row(i, named=True)
            if curr_row["close"] <= prev_row["close"]:
                consecutive_up = False
                break
    
    # 檢查成交量放大（當日成交量大於前3日平均）
    if current_index >= 3:
        volume_sum = 0
        for i in range(current_index - 3, current_index):
            volume_sum += stock_data.row(i, named=True)["volume"]
        avg_volume = volume_sum / 3
        volume_surge = current_row["volume"] > avg_volume * 1.2
    else:
        volume_surge = False
    
    if consecutive_up and volume_surge:
        return True, {"reason": "連續3天上漲且成交量放大"}
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df, **kwargs):
    """
    判斷是否應該出場（狀態機模式，適用於複雜邏輯）
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        position: 當前持倉資訊
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 策略參數
        
    Returns:
        tuple: (是否出場, 出場資訊)
    """
    # 複雜邏輯範例：動態調整出場條件
    current_row = stock_data.row(current_index, named=True)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    # 計算持有天數
    entry_row = stock_data.row(entry_index, named=True)
    holding_days = (current_row["date"] - entry_row["date"]).days
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    # 動態調整出場條件：持有越久，容忍度越高
    max_holding_days = kwargs.get("max_holding_days", 5)
    base_loss_rate = kwargs.get("max_loss_rate", 5.0)
    
    # 根據持有天數調整虧損容忍度
    adjusted_loss_rate = base_loss_rate + (holding_days * 0.5)  # 每多持有一天，容忍度增加0.5%
    
    # 檢查出場條件
    if holding_days >= max_holding_days:
        return True, {"reason": f"持有{holding_days}天"}
    
    if loss_rate <= -adjusted_loss_rate:
        return True, {"reason": f"虧損{loss_rate:.2f}%（調整後容忍度：{adjusted_loss_rate:.1f}%）"}
    
    # 檢查連續下跌
    if current_index >= 2:
        prev_row = stock_data.row(current_index - 1, named=True)
        prev_prev_row = stock_data.row(current_index - 2, named=True)
        
        if (current_row["close"] < prev_row["close"] and 
            prev_row["close"] < prev_prev_row["close"]):
            return True, {"reason": "連續兩天下跌"}
    
    return False, {}

# ===== 策略參數配置 =====
custom_parameters = {
    "use_vectorized": {
        "type": "boolean",
        "label": "使用向量化模式",
        "default": True,
        "description": "啟用向量化計算（推薦，效能最佳）。關閉時使用狀態機模式（適用於複雜邏輯）"
    },
    "use_fully_vectorized": {
        "type": "boolean",
        "label": "使用完全向量化模式",
        "default": False,
        "description": "啟用完全向量化回測（實驗性，適用於簡單策略）"
    },
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 5,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數"
    },
    "max_loss_rate": {
        "type": "number",
        "label": "最大虧損率",
        "default": 5.0,
        "min": 1.0,
        "max": 20.0,
        "step": 0.5,
        "description": "最大虧損率百分比"
    }
}

# ===== 使用說明 =====
# 這個策略展示了兩種不同的計算模式：
#
# 1. 向量化模式（use_vectorized = True）：
#    - 使用 calculate_entry_signals 和 calculate_exit_signals 函數
#    - 適用於簡單邏輯：突破20日新高且均線多頭排列
#    - 效能最佳，適合大量數據處理
#
# 2. 狀態機模式（use_vectorized = False）：
#    - 使用 should_entry 和 should_exit 函數
#    - 適用於複雜邏輯：連續3天上漲、成交量放大、動態調整出場條件
#    - 支援複雜的狀態追蹤和條件組合
#
# 3. 測試方法：
#    - 在策略編輯器中設定 use_vectorized = True 測試向量化模式
#    - 設定 use_vectorized = False 測試狀態機模式
#    - 比較兩種模式的效能和結果差異 