# 動態參數策略範例
# 展示如何使用動態參數來追蹤持有天數

def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    """
    判斷是否應該進場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 額外參數
        
    Returns:
        tuple: (是否進場, 進場資訊)
    """
    # 範例：當收盤價大於開盤價時進場
    current_row = stock_data.row(current_index, named=True)
    
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    
    return False, {}

def should_exit(stock_data, current_index, position, **kwargs):
    """
    判斷是否應該出場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        position: 當前持倉資訊
        **kwargs: 額外參數，包含動態參數
        
    Returns:
        tuple: (是否出場, 出場資訊)
    """
    # 從動態參數中取得持有天數
    holding_days = kwargs.get('holding_days', 0)
    max_holding_days = kwargs.get('max_holding_days', 5)
    max_loss_rate = kwargs.get('max_loss_rate', 5.0)
    
    current_row = stock_data.row(current_index, named=True)
    entry_price = position["entry_price"]
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    # 檢查出場條件
    if holding_days >= max_holding_days:
        return True, {"reason": f"持有{holding_days}天，超過{max_holding_days}天限制"}
    
    if loss_rate <= -max_loss_rate:
        return True, {"reason": f"虧損{loss_rate:.2f}%，超過{max_loss_rate}%限制"}
    
    # 不出場，系統會自動增加 holding_days
    return False, {}

# 動態參數配置
custom_parameters = {
    "holding_days": {
        "type": "dynamic",  # 動態參數類型
        "label": "持有天數",
        "default": 0,       # 初始值
        "increment": 1,     # 每次不出場時增加的值
        "description": "動態追蹤持有天數，出場時重置為0"
    },
    "max_holding_days": {
        "type": "number",
        "label": "最大持有天數",
        "default": 5,
        "min": 1,
        "max": 30,
        "step": 1,
        "description": "最大持有天數限制"
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

# 可選：自定義參數處理函數
def process_parameters(parameters):
    """
    處理策略參數
    
    Args:
        parameters: 輸入參數
        
    Returns:
        dict: 處理後的參數
    """
    return parameters

# 可選：自定義驗證函數
def validate_parameters(parameters):
    """
    驗證策略參數
    
    Args:
        parameters: 策略參數
        
    Raises:
        ValueError: 當參數無效時
    """
    if parameters.get('max_holding_days', 0) <= 0:
        raise ValueError("最大持有天數必須大於0")
    
    if parameters.get('max_loss_rate', 0) <= 0:
        raise ValueError("最大虧損率必須大於0") 