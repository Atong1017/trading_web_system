# Jupyter 風格策略編輯器功能說明

## 概述

策略編輯器現在支援 Jupyter 風格的互動式程式碼編輯，提供即時程式碼執行、圖表顯示和資料分析功能。

## 主要功能

### 1. 切換編輯模式
- **傳統模式**: 原有的程式碼編輯器，適合編寫完整的策略程式碼
- **Jupyter 模式**: 互動式單元格編輯器，適合探索性資料分析和策略開發

### 2. Jupyter 單元格功能
- **新增單元格**: 點擊「新增單元格」按鈕或使用 Ctrl+Enter
- **執行單元格**: 點擊執行按鈕或使用 Shift+Enter
- **刪除單元格**: 點擊刪除按鈕
- **重新編號**: 自動重新編號單元格

### 3. 程式碼執行
- **即時執行**: 程式碼立即在後端執行
- **輸出捕獲**: 自動捕獲 print 輸出、錯誤訊息和圖表
- **狀態指示**: 單元格會顯示執行狀態（執行中、成功、錯誤）

### 4. 支援的輸出類型
- **文字輸出**: print 語句的輸出
- **錯誤訊息**: 語法錯誤和執行錯誤
- **DataFrame 顯示**: Pandas 和 Polars DataFrame 的表格顯示
- **圖表顯示**: Matplotlib 和 Seaborn 圖表
- **數值結果**: 計算結果的顯示

## 可用模組

### 基本 Python 模組
- `np` - NumPy 數值計算
- `pd` - Pandas 資料處理
- `pl` - Polars 高效能資料處理
- `plt` - Matplotlib 繪圖
- `sns` - Seaborn 統計繪圖
- `go` - Plotly 互動圖表

### 策略工具模組
- `PriceUtils` - 價格計算工具
- `Utils` - 通用工具類別
- `TradeRecord` - 交易記錄資料類別
- `HoldingPosition` - 持有部位資料類別

## 快捷鍵

- **Shift+Enter**: 執行當前單元格
- **Ctrl+Enter**: 執行當前單元格並新增新單元格
- **Tab**: 自動縮排

## 範例程式碼

### 基本資料分析
```python
# 載入範例資料
import pandas as pd
import numpy as np

# 生成股票資料
dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
close_prices = 100 + np.cumsum(np.random.normal(0, 0.5, len(dates)))
df = pd.DataFrame({
    'date': dates,
    'close': close_prices,
    'volume': np.random.uniform(1000000, 5000000, len(dates))
})

print(f"載入 {len(df)} 筆股票資料")
df.head()
```

### 技術指標計算
```python
# 計算移動平均線
df['ma5'] = df['close'].rolling(5).mean()
df['ma20'] = df['close'].rolling(20).mean()
df['ma60'] = df['close'].rolling(60).mean()

# 計算日報酬率
df['daily_return'] = df['close'].pct_change()

print("技術指標計算完成")
df.tail()
```

### 圖表繪製
```python
# 繪製股價和移動平均線圖
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['close'], label='收盤價', linewidth=2)
plt.plot(df['date'], df['ma5'], label='5日均線', alpha=0.7)
plt.plot(df['date'], df['ma20'], label='20日均線', alpha=0.7)
plt.plot(df['date'], df['ma60'], label='60日均線', alpha=0.7)

plt.title('股票價格與移動平均線', fontsize=14)
plt.xlabel('日期')
plt.ylabel('價格')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### 策略邏輯測試
```python
# 測試策略邏輯
def should_buy(price, ma_short, ma_long):
    return price > ma_short and ma_short > ma_long

def should_sell(price, ma_short, ma_long):
    return price < ma_short and ma_short < ma_long

# 應用策略
df['buy_signal'] = should_buy(df['close'], df['ma5'], df['ma20'])
df['sell_signal'] = should_sell(df['close'], df['ma5'], df['ma20'])

# 統計信號
buy_count = df['buy_signal'].sum()
sell_count = df['sell_signal'].sum()

print(f"買入信號: {buy_count} 次")
print(f"賣出信號: {sell_count} 次")
```

## 筆記本管理

### 儲存筆記本
- 點擊「儲存筆記本」按鈕將筆記本儲存到本地瀏覽器
- 支援離線儲存和恢復

### 匯出筆記本
- 點擊「匯出」按鈕下載 JSON 格式的筆記本檔案
- 可以與其他用戶分享筆記本

### 載入筆記本
- 支援載入之前儲存的筆記本檔案
- 自動恢復程式碼和輸出

## 注意事項

1. **執行環境**: 程式碼在後端安全環境中執行
2. **記憶體管理**: 大型資料集會自動清理
3. **錯誤處理**: 語法錯誤和執行錯誤會清楚顯示
4. **圖表顯示**: 支援 Matplotlib 和 Seaborn 圖表
5. **資料持久性**: 單元格之間的變數會保持

## 最佳實踐

1. **模組化開發**: 將複雜邏輯分解為多個單元格
2. **逐步測試**: 逐個單元格測試程式碼
3. **圖表驗證**: 使用圖表驗證策略邏輯
4. **註解說明**: 在程式碼中添加清楚的註解
5. **定期儲存**: 定期儲存筆記本避免資料遺失

## 故障排除

### 常見問題
1. **單元格無法執行**: 檢查程式碼語法是否正確
2. **圖表不顯示**: 確保使用 `plt.show()` 顯示圖表
3. **模組找不到**: 確認使用的模組在支援列表中
4. **執行超時**: 避免執行過於複雜的程式碼

### 效能優化
1. **分批處理**: 大型資料集分批處理
2. **記憶體清理**: 及時清理不需要的變數
3. **圖表優化**: 設定適當的圖表大小和解析度 