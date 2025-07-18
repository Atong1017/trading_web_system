import re
import polars as pl

def generate_indicators(df: pl.DataFrame, indicators: list[str]) -> pl.DataFrame:
    if isinstance(indicators, str):
        raise ValueError("請傳入 list，例如 ['break_20_day_high']")

    # 轉日期欄位格式並排序
    # if df["date"].dtype != pl.Date:
    #     df = df.with_columns([
    #         pl.col("date").str.strptime(pl.Date, format="%Y/%m/%d").alias("date")
    #     ])
    df = df.sort("date")
    
    # 擴展依賴關係
    indicator_dependencies = {
        "rolling_max_{n}": [],
        "rolling_min_{n}": [],
        "ma_{n}": [],
        "is_{n}_day_high": ["rolling_max_{n}"],
        "break_{n}_day_high": ["rolling_max_{n}", "is_{n}_day_high"],
        "volume_ma_{n}": [],
        "volume_surge": ["volume_ma_20"],  # 暫定只支援 20 日
        "ma_bullish": ["ma_5", "ma_10", "ma_20"],
        "ma_bearish": ["ma_5", "ma_10", "ma_20"],
    }

    def parse_indicator_pattern(indicator: str):
        """
        將例如 break_20_day_high 拆成 base = 'break_{n}_day_high', n = 20
        """
        for base in indicator_dependencies:
            pattern = base.replace("{n}", r"(\d+)")
            match = re.fullmatch(pattern, indicator)
            if match:
                return base, int(match.group(1))
        return indicator, None  # 若無參數化的版本，回傳原名與 None
    
    # 收集所有依賴欄位，含展開 {n}
    required = set()
    def collect_dependencies(indicator_list):
        for indicator in indicator_list:
            base, n = parse_indicator_pattern(indicator)
            key = base.format(n=n) if n is not None else base
            if key not in required:
                required.add(key)
                deps = indicator_dependencies.get(base, [])
                collect_dependencies([d.format(n=n) if "{n}" in d else d for d in deps])
         
        return required
    
    required = collect_dependencies(indicators)
    
    # 建立對應欄位
    with_cols = []

    for col in required:
        if match := re.fullmatch(r"rolling_max_(\d+)", col):
            n = int(match.group(1))
            with_cols.append(pl.col("close").rolling_max(n, min_periods=1).over("stock_id").alias(col))

        elif match := re.fullmatch(r"rolling_min_(\d+)", col):
            n = int(match.group(1))
            with_cols.append(pl.col("close").rolling_min(n, min_periods=1).over("stock_id").alias(col))

        elif match := re.fullmatch(r"ma_(\d+)", col):
            n = int(match.group(1))
            with_cols.append(pl.col("close").rolling_mean(n, min_periods=1).over("stock_id").alias(col))

        elif match := re.fullmatch(r"volume_ma_(\d+)", col):
            n = int(match.group(1))
            with_cols.append(pl.col("trading_volume").rolling_mean(n, min_periods=1).over("stock_id").alias(col))
    
    df = df.with_columns(with_cols)

    # === 推導欄位 ===
    derived_cols = []

    for col in required:
        if match := re.fullmatch(r"is_(\d+)_day_high", col):
            n = int(match.group(1))
            derived_cols.append((pl.col("close") == pl.col(f"rolling_max_{n}")).cast(pl.Int8).alias(col))

        elif match := re.fullmatch(r"break_(\d+)_day_high", col):
            n = int(match.group(1))
            derived_cols.append(((pl.col("close") > pl.col(f"rolling_max_{n}").shift(1)) &
                                 pl.col(f"rolling_max_{n}").shift(1).is_not_null()).cast(pl.Int8).alias(col))

        elif col == "volume_surge":
            derived_cols.append((pl.col("trading_volume") > pl.col("volume_ma_20") * 1.5)
                                 .cast(pl.Int8).alias(col))

        elif col == "ma_bullish":
            derived_cols.append(((pl.col("ma_5") > pl.col("ma_10")) & (pl.col("ma_10") > pl.col("ma_20")))
                                 .cast(pl.Int8).alias(col))

        elif col == "ma_bearish":
            derived_cols.append(((pl.col("ma_5") < pl.col("ma_10")) & (pl.col("ma_10") < pl.col("ma_20")))
                                 .cast(pl.Int8).alias(col))
            
    return df.with_columns(derived_cols)
