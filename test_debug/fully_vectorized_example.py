# 完全向量化策略範例
# 這個範例展示如何完全避免 for 迴圈，使用純 Polars 向量化操作

import polars as pl
from datetime import datetime

# 自定義參數配置
custom_parameters = {
    "use_fully_vectorized": {
        "type": "boolean",
        "label": "使用完全向量化模式",
        "default": True,
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
    },
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 10,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數限制"
    }
}

def calculate_entry_signals(stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame) -> pl.DataFrame:
    """
    完全向量化的進場信號計算
    使用 Polars 的向量化操作，避免任何 Python 迴圈
    """
    entry_threshold = self.get_parameter_value("entry_threshold", 1.0)
    
    # 一次性計算所有技術指標
    df = stock_data.with_columns([
        # 價格變化率
        ((pl.col("close") - pl.col("open")) / pl.col("open")).alias("price_change_rate"),
        
        # 成交量變化率
        ((pl.col("volume") - pl.col("volume").shift(1)) / pl.col("volume").shift(1)).alias("volume_change_rate"),
        
        # 移動平均
        pl.col("close").rolling_mean(window_size=5, min_periods=1).alias("ma_5"),
        pl.col("close").rolling_mean(window_size=20, min_periods=1).alias("ma_20"),
        
        # 布林通道
        pl.col("close").rolling_mean(window_size=20, min_periods=1).alias("bb_middle"),
        (pl.col("close").rolling_std(window_size=20, min_periods=1) * 2).alias("bb_std")
    ])
    
    # 計算布林通道上下軌
    df = df.with_columns([
        (pl.col("bb_middle") + pl.col("bb_std")).alias("bb_upper"),
        (pl.col("bb_middle") - pl.col("bb_std")).alias("bb_lower")
    ])
    
    # 使用向量化操作計算所有進場條件
    df = df.with_columns([
        # 條件1: 突破20日新高
        pl.when(pl.col("break_20_day_high") == 1)
        .then(1)
        .otherwise(0)
        .alias("condition_1"),
        
        # 條件2: 價格變化率大於閾值
        pl.when(pl.col("price_change_rate") > entry_threshold)
        .then(1)
        .otherwise(0)
        .alias("condition_2"),
        
        # 條件3: 成交量放大
        pl.when(pl.col("volume_change_rate") > 0.5)
        .then(1)
        .otherwise(0)
        .alias("condition_3"),
        
        # 條件4: 均線多頭排列
        pl.when((pl.col("ma_5") > pl.col("ma_20")) & (pl.col("close") > pl.col("ma_5")))
        .then(1)
        .otherwise(0)
        .alias("condition_4"),
        
        # 條件5: 突破布林通道上軌
        pl.when(pl.col("close") > pl.col("bb_upper"))
        .then(1)
        .otherwise(0)
        .alias("condition_5")
    ])
    
    # 綜合判斷：至少滿足3個條件才進場
    df = df.with_columns([
        pl.when(
            (pl.col("condition_1") + pl.col("condition_2") + pl.col("condition_3") + 
             pl.col("condition_4") + pl.col("condition_5")) >= 3
        )
        .then(1)
        .otherwise(0)
        .alias("should_entry"),
        
        # 進場原因
        pl.when(
            (pl.col("condition_1") + pl.col("condition_2") + pl.col("condition_3") + 
             pl.col("condition_4") + pl.col("condition_5")) >= 3
        )
        .then("多重技術指標確認")
        .otherwise("")
        .alias("entry_reason")
    ])
    
    return df

def calculate_exit_signals(stock_data: pl.DataFrame, excel_pl_df: pl.DataFrame) -> pl.DataFrame:
    """
    完全向量化的出場信號計算
    使用 Polars 的向量化操作，避免任何 Python 迴圈
    """
    exit_threshold = self.get_parameter_value("exit_threshold", -0.05)
    max_holding_days = self.get_parameter_value("max_holding_days", 10)
    
    # 一次性計算所有技術指標
    df = stock_data.with_columns([
        # 價格變化率
        ((pl.col("close") - pl.col("open")) / pl.col("open")).alias("price_change_rate"),
        
        # 移動平均
        pl.col("close").rolling_mean(window_size=5, min_periods=1).alias("ma_5"),
        pl.col("close").rolling_mean(window_size=20, min_periods=1).alias("ma_20"),
        
        # 布林通道
        pl.col("close").rolling_mean(window_size=20, min_periods=1).alias("bb_middle"),
        (pl.col("close").rolling_std(window_size=20, min_periods=1) * 2).alias("bb_std")
    ])
    
    # 計算布林通道上下軌
    df = df.with_columns([
        (pl.col("bb_middle") + pl.col("bb_std")).alias("bb_upper"),
        (pl.col("bb_middle") - pl.col("bb_std")).alias("bb_lower")
    ])
    
    # 使用向量化操作計算所有出場條件
    df = df.with_columns([
        # 條件1: 價格變化率小於閾值（虧損）
        pl.when(pl.col("price_change_rate") < exit_threshold)
        .then(1)
        .otherwise(0)
        .alias("exit_condition_1"),
        
        # 條件2: 跌破20日均線
        pl.when(pl.col("close") < pl.col("ma_20"))
        .then(1)
        .otherwise(0)
        .alias("exit_condition_2"),
        
        # 條件3: 跌破布林通道下軌
        pl.when(pl.col("close") < pl.col("bb_lower"))
        .then(1)
        .otherwise(0)
        .alias("exit_condition_3"),
        
        # 條件4: 均線空頭排列
        pl.when((pl.col("ma_5") < pl.col("ma_20")) & (pl.col("close") < pl.col("ma_5")))
        .then(1)
        .otherwise(0)
        .alias("exit_condition_4")
    ])
    
    # 綜合判斷：滿足任一條件就出場
    df = df.with_columns([
        pl.when(
            (pl.col("exit_condition_1") + pl.col("exit_condition_2") + 
             pl.col("exit_condition_3") + pl.col("exit_condition_4")) >= 1
        )
        .then(1)
        .otherwise(0)
        .alias("should_exit"),
        
        # 出場原因
        pl.when(pl.col("exit_condition_1") == 1)
        .then("虧損達到閾值")
        .when(pl.col("exit_condition_2") == 1)
        .then("跌破20日均線")
        .when(pl.col("exit_condition_3") == 1)
        .then("跌破布林通道下軌")
        .when(pl.col("exit_condition_4") == 1)
        .then("均線空頭排列")
        .otherwise("")
        .alias("exit_reason")
    ])
    
    return df

# 使用說明：
# 1. 將此策略程式碼複製到策略編輯器中
# 2. 設定 use_fully_vectorized = True 來啟用完全向量化模式
# 3. 系統會使用 _execute_fully_vectorized_backtest 方法
# 4. 完全避免 for 迴圈，使用純 Polars 向量化操作
# 5. 適用於簡單的進出場邏輯，複雜策略可能需要混合模式

# 效能比較：
# - 傳統逐行判斷：O(n) 時間複雜度，每個數據點都要調用 Python 函數
# - 混合向量化：O(n) 時間複雜度，但減少了函數調用次數
# - 完全向量化：O(1) 時間複雜度，一次性計算所有信號

# 注意事項：
# 1. 完全向量化模式適用於簡單的進出場邏輯
# 2. 複雜的狀態管理（如動態參數）可能需要混合模式
# 3. 如果完全向量化失敗，系統會自動回退到混合模式
# 4. 建議先用混合模式測試策略邏輯，再嘗試完全向量化 