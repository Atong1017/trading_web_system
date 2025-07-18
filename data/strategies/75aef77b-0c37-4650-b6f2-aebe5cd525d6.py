# 狀態機策略模板
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
