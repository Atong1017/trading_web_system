# 向量化策略模板（推薦）
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
    # 加入 row_index 以便追蹤
    df = stock_data.with_columns([
        pl.lit(0).alias("matched_stock_id"),
        pl.arange(0, stock_data.height).alias("row_index")
    ])

    # 準備右側匹配來源（只保留 stock_id, date）
    match_keys = excel_pl_df.select(["stock_id", "date"])
    
    # inner join 找出匹配的 row_index
    matched = df.join(match_keys, on=["stock_id", "date"], how="inner")
    matched_indices = matched.select("row_index")["row_index"].to_list()
    
    # 將 matched row_index 設為 1
    df = df.with_columns([
        pl.when(pl.col("row_index").is_in(matched_indices))
          .then(1)
          .otherwise(0)
          .alias("matched_stock_id")
    ])    
    up_limit_rate = self.parameters['up_limit_rate']
    down_limit_rate = self.parameters['down_limit_rate']
    
    # 範例：當日突破20日高點，則下一日進場
    df = df.with_columns([
        pl.when(pl.col("matched_stock_id").shift(1) == 1)
        .then(1)
        .otherwise(0)
        .alias("should_entry"),
        
        pl.when(pl.col("matched_stock_id").shift(1) == 1)
        .then(pl.lit("當沖進場"))
        .otherwise(pl.lit(""))
        .alias("entry_reason"),
        
        pl.when(pl.col("matched_stock_id").shift(1) == 1)
        .then(pl.col("open"))
        .alias("entry_price"),
        
        pl.when(pl.col("matched_stock_id").shift(1) == 1)
        .then(pl.col("date"))
        .otherwise(0)
        .alias("entry_date"),
        
        # 下一列的 base_price = 本列的 close（前一列 matched=1 時）
        pl.when(pl.col("matched_stock_id").shift(1) == 1)
          .then(pl.col("close").shift(1))   # 將當列 close 指定給下一列
          .otherwise(0)
          .alias("base_price")
    ])
    df = df.with_columns([
        pl.Series("up_limit_price", [
            PriceUtils.calculate_limit_price(p, up_limit_rate) if p is not None else None
            for p in df["base_price"]
        ]),
        pl.Series("down_limit_price", [
            PriceUtils.calculate_limit_price(p, down_limit_rate) if p is not None else None
            for p in df["base_price"]
        ]),
        pl.Series("shares", [
            PriceUtils.calculate_shares(self.parameters['initial_capital'], p, self.parameters['share_type']) if p is not None else None
            for p in df["entry_price"]
        ])
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
        pl.when(pl.col("should_entry") == 1)
        .then(1)
        .otherwise(0)
        .alias("should_exit"),
        
        pl.when(pl.col("should_entry") == 1)
        .then(pl.col('date'))
        .otherwise(pl.lit(""))
        .alias("exit_date"),
        
        pl.when(pl.col("should_entry") == 1)
          .then(
              pl.when(pl.col("high") >= pl.col("up_limit_price"))
                .then(pl.col("up_limit_price"))
                .when(pl.col("low") <= pl.col("down_limit_price"))
                .then(pl.col("down_limit_price"))
                .otherwise(pl.col("close"))
          )
          .otherwise(None)
          .alias("exit_price"),
        
        pl.when(pl.col("should_entry") == 1)
        .then(pl.lit("當沖出場"))
        .otherwise(pl.lit(""))
        .alias("exit_reason")
    ])
    
    return df
    
# ===== 可選：自定義函數 =====
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