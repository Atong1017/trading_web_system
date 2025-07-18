# 測試狀態機模式功能
import polars as pl
from datetime import datetime, timedelta
import uuid
from strategies.dynamic_strategy import DynamicStrategy
from strategies.base_strategy import TradeRecord, HoldingPosition

def test_state_machine_mode():
    """測試狀態機模式"""
    print("=== 測試狀態機模式 ===")
    
    # 創建測試數據
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(30)]
    test_data = {
        "date": dates,
        "stock_id": ["2330"] * 30,
        "open": [100 + i * 0.5 for i in range(30)],
        "high": [102 + i * 0.5 for i in range(30)],
        "low": [98 + i * 0.5 for i in range(30)],
        "close": [101 + i * 0.5 for i in range(30)],
        "volume": [1000000 + i * 10000 for i in range(30)]
    }
    
    stock_data = pl.DataFrame(test_data)
    
    # 創建測試策略（狀態機模式）
    strategy_code = '''
# 狀態機模式測試策略
import polars as pl
from core.technical_indicators import generate_indicators
from core.price_utils import PriceUtils
from core.utils import Utils
from strategies.base_strategy import TradeRecord, HoldingPosition

def should_entry(stock_data, current_index, excel_pl_df, **kwargs):
    """複雜的進場邏輯：連續3天收盤價上漲且成交量放大"""
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
    """複雜的出場邏輯：動態調整出場條件"""
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
    adjusted_loss_rate = base_loss_rate + (holding_days * 0.5)
    
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

# 策略參數配置
custom_parameters = {
    "use_vectorized": {
        "type": "boolean",
        "label": "使用向量化模式",
        "default": False,  # 關閉向量化，使用狀態機
        "description": "使用狀態機模式（適用於複雜邏輯）"
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
'''
    
    # 創建策略實例
    parameters = {
        "use_vectorized": False,  # 使用狀態機模式
        "max_holding_days": 5,
        "max_loss_rate": 5.0,
        "commission_rate": 0.001425,
        "commission_discount": 0.3,
        "securities_tax_rate": 0.003,
        "shares_per_trade": 1000
    }
    
    strategy = DynamicStrategy(parameters, strategy_code, "狀態機測試策略")
    
    # 測試信號計算
    print("1. 測試信號計算...")
    signals_df = strategy._calculate_signals_state_machine(stock_data, None)
    
    # 檢查結果
    entry_signals = signals_df.filter(pl.col("should_entry") == 1)
    exit_signals = signals_df.filter(pl.col("should_exit") == 1)
    
    print(f"   進場信號數量: {len(entry_signals)}")
    print(f"   出場信號數量: {len(exit_signals)}")
    
    if len(entry_signals) > 0:
        print("   進場信號範例:")
        for i in range(min(3, len(entry_signals))):
            row = entry_signals.row(i, named=True)
            print(f"     - 日期: {row['date']}, 原因: {row['entry_reason']}")
    
    if len(exit_signals) > 0:
        print("   出場信號範例:")
        for i in range(min(3, len(exit_signals))):
            row = exit_signals.row(i, named=True)
            print(f"     - 日期: {row['date']}, 原因: {row['exit_reason']}")
    
    # 測試完整回測
    print("\n2. 測試完整回測...")
    try:
        strategy.run_backtest(stock_data, None, 1000000, "2330", "台積電")
        result = strategy.get_strategy_result(1000000)
        
        print(f"   總交易次數: {result['total_trades']}")
        print(f"   獲利交易: {result['winning_trades']}")
        print(f"   虧損交易: {result['losing_trades']}")
        print(f"   勝率: {result['win_rate']:.2f}%")
        print(f"   總損益: {result['total_profit_loss']:.2f}")
        print(f"   總損益率: {result['total_profit_loss_rate']:.2f}%")
        
        if result['trade_records']:
            print("   交易記錄範例:")
            for i, trade in enumerate(result['trade_records'][:3]):
                print(f"     - 進場: {trade['entry_date']}, 出場: {trade['exit_date']}, 損益: {trade['net_profit_loss']:.2f}")
        
    except Exception as e:
        print(f"   回測失敗: {e}")
    
    print("\n=== 測試完成 ===")

def test_vectorized_vs_state_machine():
    """比較向量化模式和狀態機模式"""
    print("=== 比較向量化模式和狀態機模式 ===")
    
    # 創建測試數據
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(30)]
    test_data = {
        "date": dates,
        "stock_id": ["2330"] * 30,
        "open": [100 + i * 0.5 for i in range(30)],
        "high": [102 + i * 0.5 for i in range(30)],
        "low": [98 + i * 0.5 for i in range(30)],
        "close": [101 + i * 0.5 for i in range(30)],
        "volume": [1000000 + i * 10000 for i in range(30)]
    }
    
    stock_data = pl.DataFrame(test_data)
    
    # 測試向量化模式
    print("1. 測試向量化模式...")
    vectorized_strategy = DynamicStrategy(
        {"use_vectorized": True}, 
        "", 
        "向量化測試策略"
    )
    
    start_time = datetime.now()
    vectorized_signals = vectorized_strategy._calculate_entry_exit_signals(stock_data, None)
    vectorized_time = (datetime.now() - start_time).total_seconds()
    
    # 測試狀態機模式
    print("2. 測試狀態機模式...")
    state_machine_strategy = DynamicStrategy(
        {"use_vectorized": False}, 
        "", 
        "狀態機測試策略"
    )
    
    start_time = datetime.now()
    state_machine_signals = state_machine_strategy._calculate_entry_exit_signals(stock_data, None)
    state_machine_time = (datetime.now() - start_time).total_seconds()
    
    # 比較結果
    print("\n3. 效能比較:")
    print(f"   向量化模式執行時間: {vectorized_time:.4f} 秒")
    print(f"   狀態機模式執行時間: {state_machine_time:.4f} 秒")
    print(f"   效能比率: {state_machine_time/vectorized_time:.2f}x")
    
    # 比較信號數量
    vectorized_entries = len(vectorized_signals.filter(pl.col("should_entry") == 1))
    vectorized_exits = len(vectorized_signals.filter(pl.col("should_exit") == 1))
    state_machine_entries = len(state_machine_signals.filter(pl.col("should_entry") == 1))
    state_machine_exits = len(state_machine_signals.filter(pl.col("should_exit") == 1))
    
    print(f"\n4. 信號比較:")
    print(f"   向量化模式 - 進場: {vectorized_entries}, 出場: {vectorized_exits}")
    print(f"   狀態機模式 - 進場: {state_machine_entries}, 出場: {state_machine_exits}")
    
    print("\n=== 比較完成 ===")

if __name__ == "__main__":
    print("開始測試狀態機模式...")
    try:
        test_state_machine_mode()
        print("\n" + "="*50 + "\n")
        test_vectorized_vs_state_machine()
        print("所有測試完成！")
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc() 