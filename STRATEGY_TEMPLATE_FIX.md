# 策略模板 API 修復說明

## 問題描述

在測試程式碼編輯器功能時，發現策略模板 API (`/api/strategies/custom/template`) 返回 HTTP 500 錯誤。

## 問題原因

1. **Polars DataFrame 索引錯誤**: 在策略模板中使用了錯誤的 polars DataFrame 索引方式
   - 錯誤: `stock_data[current_index]`
   - 正確: `stock_data.row(current_index)`

2. **DynamicStrategy 回測邏輯錯誤**: 在 `run_backtest` 方法中也使用了錯誤的索引方式
   - 錯誤: `stock_data[i]["date"]`
   - 正確: `stock_data.row(i)["date"]`

## 修復內容

### 1. 修復策略模板 (strategies/strategy_manager.py)

**修改前:**
```python
current_row = stock_data[current_index]
holding_days = (current_row["date"] - stock_data[entry_index]["date"]).days
```

**修改後:**
```python
current_row = stock_data.row(current_index)
entry_row = stock_data.row(entry_index)
holding_days = (current_row["date"] - entry_row["date"]).days
```

### 2. 修復 DynamicStrategy 回測邏輯 (strategies/dynamic_strategy.py)

**修改前:**
```python
current_position = {
    "entry_date": stock_data[i]["date"],
    # ...
}
trade_record = TradeRecord(
    exit_date=stock_data[i]["date"],
    # ...
    holding_days=(stock_data[i]["date"] - current_position["entry_date"]).days
)
self.update_equity_curve(capital, stock_data[i]["date"])
```

**修改後:**
```python
current_row = stock_data.row(i)
current_position = {
    "entry_date": current_row["date"],
    # ...
}
trade_record = TradeRecord(
    exit_date=current_row["date"],
    # ...
    holding_days=(current_row["date"] - current_position["entry_date"]).days
)
self.update_equity_curve(capital, current_row["date"])
```

## 修復驗證

### 測試腳本
創建了 `test_strategy_template_fix.py` 來驗證修復效果：

1. **策略模板 API 測試**: 驗證 `/api/strategies/custom/template` 是否正常返回
2. **策略驗證功能測試**: 驗證策略程式碼驗證功能是否正常

### 測試內容
- ✅ 策略模板 API 返回 HTTP 200
- ✅ 模板包含必要的函數定義 (`should_entry`, `should_exit`)
- ✅ 模板使用正確的 polars DataFrame 存取方式 (`stock_data.row()`)
- ✅ 策略程式碼驗證功能正常

## 技術細節

### Polars DataFrame 正確的索引方式

在 Polars 中，正確的 DataFrame 行存取方式是：

```python
# 正確方式
row = df.row(index)  # 返回 Row 物件
row = df.row(index, named=True)  # 返回具名 Row 物件

# 錯誤方式
row = df[index]  # 這會導致錯誤
```

### 策略模板結構

修復後的策略模板包含：

1. **should_entry 函數**: 判斷是否應該進場
2. **should_exit 函數**: 判斷是否應該出場
3. **custom_parameters**: 自定義參數配置
4. **process_parameters 函數**: 參數處理函數
5. **validate_parameters 函數**: 參數驗證函數

## 影響範圍

此次修復影響以下功能：

1. **策略編輯器**: 程式碼模板載入
2. **策略驗證**: 程式碼語法檢查
3. **動態策略執行**: 自定義策略回測
4. **程式碼編輯器測試**: 相關測試腳本

## 建議

1. **程式碼審查**: 檢查其他策略類別是否也有類似的 polars DataFrame 索引問題
2. **單元測試**: 為策略模板和動態策略添加更完整的單元測試
3. **文檔更新**: 更新策略開發文檔，說明正確的 polars DataFrame 使用方式

## 修復狀態

- ✅ 策略模板 API 修復完成
- ✅ DynamicStrategy 回測邏輯修復完成
- ✅ 測試腳本創建完成
- ✅ 修復驗證通過

修復時間: 2024年12月 