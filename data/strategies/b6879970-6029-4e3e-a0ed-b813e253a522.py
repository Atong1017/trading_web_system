df = df.with_columns([
    pl.lit(0).alias("matched_stock_id"),
    pl.arange(0, df.height).alias("row_index")
])

# 準備右側匹配來源（只保留 stock_id, date）
match_keys = stock_df.select(["date", "stock_id"])

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

up_limit_rate = parameters['up_limit_rate']
down_limit_rate = parameters['down_limit_rate']

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
        PriceUtils.calculate_shares(1000000, p, parameters['share_type']) if p is not None else None
        for p in df["entry_price"]
    ])
])

df = df.with_columns([
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

df = df.filter((pl.col("should_entry") == 1) | (pl.col("should_exit") == 1))