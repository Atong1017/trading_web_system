# 動態參數策略範例
# 展示如何使用動態參數來追蹤持有天數

def breaking_20_days_high(stock_data, current_index, excel_pl_df, **kwargs):
    """
    判斷是否突破20日新高
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 額外參數
        
    Returns:
        tuple: (是否突破20日新高, 突破20日新高資訊)
    """
    current_row = stock_data.row(current_index, named=True)  # 當前欄位資料
    excel_date = excel_pl_df['date'][0]  # 股票列表日期
    stock_ids = [s.split(' ')[0].strip() for s in excel_pl_df['stock_id'].to_list()]  # 股票列表股票代碼列表
    if excel_date <= current_row['date'] and current_row['stock_id'] in stock_ids:  # 如果股票列表日期小於等於當前日期，且當前股票代碼在股票列表中
        prev_close_list = stock_data['close'][current_index - 20:current_index - 1].to_list()  # 前19天收盤價
        prev_close = stock_data.row(current_index - 1, named=True)['close']  # 前一天收盤價
        trade_direction = kwargs.get('trade_direction', None)  # 交易方向
        # 如果前一天收盤價大於前19天收盤價的最大值，且交易方向為多頭
        if prev_close > max(prev_close_list) and trade_direction == 'long':  
            return True, {"reason": "突破20日新高"}
        # 如果前一天收盤價小於前19天收盤價的最小值，且交易方向為空頭
        elif prev_close < min(prev_close_list) and trade_direction == 'short':  
            return True, {"reason": "突破20日新低"}
            
    return False, {}

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
    # 突破20日新高時進場
    if breaking_20_days_high(stock_data, current_index, excel_pl_df, **kwargs)[0]:
        return True, {"reason": "突破20日新高"}
    
    return False, {}

def should_exit(stock_data, current_index, position, excel_pl_df, **kwargs):
    """
    判斷是否應該出場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        position: 當前持倉資訊
        excel_pl_df: Excel股票列表 (polars DataFrame)
        **kwargs: 額外參數，包含動態參數
        
    Returns:
        tuple: (是否出場, 出場資訊)
    """    
    # 當前欄位資料
    current_row = stock_data.row(current_index, named=True)  
    open_price = current_row['open']  # 開盤價
    close_price = current_row['close']  # 收盤價
    high_price = current_row['high']  # 最高價
    low_price = current_row['low']  # 最低價
    prev_row = stock_data.row(current_index - 1, named=True)  # 前一天欄位資料
    prev_close_price = prev_row['close']  # 前一天收盤價
    
    entry_price = position["entry_price"]  # 進場價格
    # 交易方向
    trade_direction = kwargs.get('trade_direction', 'long')
    # 出場類型
    exit_type = kwargs.get('exit_type', 'open')
    # 停利/損、漲/跌停利率
    max_profit_rate = float(kwargs.get('max_profit_rate', 20))
    max_loss_rate = float(kwargs.get('max_loss_rate', -20))
    up_limit_rate = float(kwargs.get('up_limit_rate', 9))
    down_limit_rate = float(kwargs.get('down_limit_rate', -9))
    # 停利/損價、漲/跌停價
    profit_price = PriceUtils.calculate_limit_price(entry_price, max_profit_rate)
    loss_price = PriceUtils.calculate_limit_price(entry_price, max_loss_rate)    
    if trade_direction == 'short':
        profit_price = PriceUtils.calculate_limit_price(entry_price, -max_profit_rate)
        loss_price = PriceUtils.calculate_limit_price(entry_price, -max_loss_rate)
    up_limit_price = PriceUtils.calculate_limit_price(prev_close_price, up_limit_rate)
    down_limit_price = PriceUtils.calculate_limit_price(prev_close_price, down_limit_rate)
    if trade_direction == 'short':
        up_limit_price = PriceUtils.calculate_limit_price(prev_close_price, -up_limit_rate)
        down_limit_price = PriceUtils.calculate_limit_price(prev_close_price, -down_limit_rate)
        
    # 出場條件
    profit_enable = kwargs.get('profit_enable', '1')
    loss_enable = kwargs.get('loss_enable', '1')
    up_limit_enable = kwargs.get('up_limit_enable', '1')
    down_limit_enable = kwargs.get('down_limit_enable', '1')
    max_holding_days = kwargs.get('max_holding_days', 20)

    # 強制出場條件
    forced_profit_enable = kwargs.get('forced_profit_enable', '1')
    forced_loss_enable = kwargs.get('forced_loss_enable', '1')
    forced_up_limit_enable = kwargs.get('forced_up_limit_enable', '1')
    forced_down_limit_enable = kwargs.get('forced_down_limit_enable', '1')    
    forced_holding_days_enable = kwargs.get('forced_holding_days_enable', '1')
    # 突破20日新高
    break_20_days_high = breaking_20_days_high(stock_data, current_index, excel_pl_df)[0]
    
    # 檢查一字跌停
    is_limit_down_result = PriceUtils.is_limit_down(
        current_row['open'], 
        current_row['high'], 
        current_row['low'], 
        current_row['close'],
        prev_close_price,
        10, 
        -10, 
        'long'
        )
    
    if is_limit_down_result == 1:
        return False, {"reason": f"一字跌停不出場"}
    
    # 停利條件
    elif profit_enable and (
        (open_price >= profit_price and trade_direction == 'long') or 
        (open_price <= profit_price and trade_direction == 'short')
        ):
        if forced_profit_enable != '1' and break_20_days_high:
            return False, {}
        else:
            return True, {"exit_price": open_price, "reason": f"停利出場(開盤價)"}
        
        
    # 停利條件
    elif profit_enable and (
        (high_price >= profit_price and trade_direction == 'long') or 
        (low_price <= profit_price and trade_direction == 'short')
        ):
        # print(88888888888, current_row, forced_profit_enable, break_20_days_high, kwargs, self.parameters['holding_days'])
        if forced_profit_enable != '1' and break_20_days_high:
            return False, {}
        else:            
            return True, {"exit_price": profit_price, "reason": f"停利出場(最高價)"}
    
    # 停損條件
    elif loss_enable and (
        (open_price <= loss_price and trade_direction == 'long') or 
        (open_price >= loss_price and trade_direction == 'short')
        ):
        if forced_loss_enable != '1' and break_20_days_high:
            return False, {}
        else:
            return True, {"exit_price": open_price, "reason": f"停損出場(開盤價)"}
    
    # 停損條件
    elif loss_enable and (
        (low_price <= loss_price and trade_direction == 'long') or 
        (high_price >= loss_price and trade_direction == 'short')
        ):
        if forced_loss_enable != '1' and break_20_days_high:
            return False, {}
        else:
            return True, {"exit_price": loss_price, "reason": f"停損出場(最低價)"}
    
    # 漲停出場
    elif up_limit_enable and (
        (high_price >= up_limit_price and trade_direction == 'long') or 
        (low_price <= up_limit_price and trade_direction == 'short')
        ):
        if forced_up_limit_enable != '1' and break_20_days_high:
            return False, {}
        else:
            return True, {
            "exit_price": up_limit_price, 
            "reason": f"漲停出場", 
            "prev_close_price": prev_close_price,
            "up_limit_price": up_limit_price}
    
    # 跌停出場
    elif down_limit_enable and (
        (low_price <= down_limit_price and trade_direction == 'long') or 
        (high_price >= down_limit_price and trade_direction == 'short')
        ):
        if forced_down_limit_enable != '1' and break_20_days_high:
            return False, {}
        else:
            return True, {
            "exit_price": down_limit_price, 
            "reason": f"跌停出場", 
            "prev_close_price": prev_close_price,
            "down_limit_price": down_limit_price}
    
    # 天數出場
    elif self.parameters['holding_days'] >= max_holding_days:
        if forced_holding_days_enable and break_20_days_high:
            return False, {}
        else:
            exit_price = open_price if exit_type == 'open' else close_price
            exit_reason = f"天數出場(開盤價)" if exit_type == 'open' else f"天數出場(收盤價)"
            
            return True, {"exit_price": exit_price, "reason": exit_reason}
    
    # 不出場，系統會自動增加 holding_days
    return False, {}    

# 處理策略參數
def process_parameters(parameters=None):
    """
    處理策略參數
    
    Args:
        parameters: 輸入參數
        
    Returns:
        dict: 處理後的參數
    """
    # 在這裡處理參數邏輯
    return parameters
    
# 驗證策略參數
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