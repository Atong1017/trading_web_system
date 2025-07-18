# 使用技術指標的策略範例
# 這個範例展示如何在策略編輯器中使用 generate_indicators

import polars as pl
from core.technical_indicators import generate_indicators
from core.price_utils import PriceUtils
from core.utils import Utils
from strategies.base_strategy import TradeRecord, HoldingPosition

# 自定義參數配置
custom_parameters = {
    "use_fully_vectorized": {
        "type": "boolean",
        "label": "使用完全向量化模式",
        "default": False,
        "description": "啟用完全向量化回測（實驗性）"
    },
    "entry_threshold": {
        "type": "number",
        "label": "進場閾值",
        "default": 1.0,
        "min": 0.1,
        "max": 5.0,
        "step": 0.1,
        "description": "進場信號的閾值"
    },
    "exit_threshold": {
        "type": "number", 
        "label": "出場閾值",
        "default": -0.05,
        "min": -0.2,
        "max": 0.0,
        "step": 0.01,
        "description": "出場信號的閾值"
    }
}

def calculate_entry_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算進場信號
    展示如何使用 generate_indicators 生成技術指標
    """
    # 生成技術指標
    df = generate_indicators(stock_data, ['break_20_day_high', 'ma_5', 'ma_20'])
    
    # 使用技術指標進行進場判斷
    df = df.with_columns([
        # 條件1: 突破20日新高
        pl.when(pl.col("break_20_day_high").shift(1) == 1)
        .then(1)
        .otherwise(0)
        .alias("condition_1"),
        
        # 條件2: 5日均線大於20日均線（多頭排列）
        pl.when(pl.col("ma_5") > pl.col("ma_20"))
        .then(1)
        .otherwise(0)
        .alias("condition_2"),
        
        # 條件3: 收盤價大於開盤價（上漲）
        pl.when(pl.col("close") > pl.col("open"))
        .then(1)
        .otherwise(0)
        .alias("condition_3")
    ])
    
    # 綜合判斷：至少滿足2個條件才進場
    df = df.with_columns([
        pl.when(
            (pl.col("condition_1") + pl.col("condition_2") + pl.col("condition_3")) >= 2
        )
        .then(1)
        .otherwise(0)
        .alias("should_entry"),
        
        # 進場原因
        pl.when(pl.col("condition_1") == 1)
        .then("突破20日新高")
        .when(pl.col("condition_2") == 1)
        .then("均線多頭排列")
        .when(pl.col("condition_3") == 1)
        .then("價格上漲")
        .otherwise("")
        .alias("entry_reason")
    ])
    
    return df

def calculate_exit_signals(stock_data, excel_pl_df, **kwargs):
    """
    使用向量化操作計算出場信號
    """
    exit_threshold = kwargs.get("exit_threshold", -0.05)
    
    # 生成技術指標
    df = generate_indicators(stock_data, ['ma_5', 'ma_20'])
    
    # 使用技術指標進行出場判斷
    df = df.with_columns([
        # 條件1: 5日均線跌破20日均線（空頭排列）
        pl.when(pl.col("ma_5") < pl.col("ma_20"))
        .then(1)
        .otherwise(0)
        .alias("exit_condition_1"),
        
        # 條件2: 收盤價小於開盤價（下跌）
        pl.when(pl.col("close") < pl.col("open"))
        .then(1)
        .otherwise(0)
        .alias("exit_condition_2")
    ])
    
    # 綜合判斷：滿足任一條件就出場
    df = df.with_columns([
        pl.when(
            (pl.col("exit_condition_1") + pl.col("exit_condition_2")) >= 1
        )
        .then(1)
        .otherwise(0)
        .alias("should_exit"),
        
        # 出場原因
        pl.when(pl.col("exit_condition_1") == 1)
        .then("均線空頭排列")
        .when(pl.col("exit_condition_2") == 1)
        .then("價格下跌")
        .otherwise("")
        .alias("exit_reason")
    ])
    
    return df

# 傳統模式函數（備用）
def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    """
    傳統的逐行進場判斷（備用）
    """
    current_row = stock_data.row(current_index, named=True)
    
    # 檢查是否有向量化進場信號
    if current_row.get("should_entry", 0) == 1:
        return True, {"reason": current_row.get("entry_reason", "向量化進場信號")}
    
    # 備用邏輯：簡單的價格判斷
    if current_row["close"] > current_row["open"] * 1.02:  # 上漲2%
        return True, {"reason": "價格上漲超過2%"}
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df, **kwargs):
    """
    傳統的逐行出場判斷（備用）
    """
    current_row = stock_data.row(current_index, named=True)
    entry_price = position["entry_price"]
    holding_days = kwargs.get("holding_days", 0)
    
    # 檢查是否有向量化出場信號
    if current_row.get("should_exit", 0) == 1:
        return True, {"reason": current_row.get("exit_reason", "向量化出場信號")}
    
    # 備用邏輯：持有天數或虧損限制
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 10:
        return True, {"reason": f"持有{holding_days}天達到限制"}
    
    if loss_rate <= -5:  # 虧損5%
        return True, {"reason": f"虧損{loss_rate:.2f}%達到限制"}
    
    return False, {}

# 使用說明：
# 1. 將此策略程式碼複製到策略編輯器中
# 2. 系統會自動導入 generate_indicators 函數
# 3. 可以使用以下技術指標：
#    - break_20_day_high: 突破20日新高
#    - break_10_day_high: 突破10日新高
#    - ma_5, ma_10, ma_20: 移動平均線
#    - volume_ma_20: 成交量移動平均
#    - 更多指標請參考 core/technical_indicators.py
#
# 4. 向量化模式優勢：
#    - 一次性計算所有技術指標
#    - 使用 Polars 向量化操作，效能最佳
#    - 適用於大量數據處理
#
# 5. 混合模式：
#    - 可以同時定義向量化和傳統函數
#    - 系統會優先使用向量化函數
#    - 如果向量化信號不足，會使用傳統函數作為備用 