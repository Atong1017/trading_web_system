# 資料預覽系統功能說明

## 概述

本系統新增了類似 Jupyter 的資料預覽功能，讓用戶在策略編輯器中可以：
1. 載入各種預設的範例資料
2. 以表格形式預覽資料內容
3. 管理自定義資料類型
4. 快速測試策略邏輯

## 主要功能

### 1. 資料預覽功能

#### 1.1 資料預覽區域
- 在策略編輯器中新增了資料預覽區域
- 支援顯示最多 100 筆資料（避免頁面過載）
- 自動格式化數值和日期顯示
- 提供資料統計資訊（筆數、欄位數）

#### 1.2 資料載入控制
- **載入範例資料**：開啟資料選擇對話框
- **清除**：清除當前預覽的資料
- **資料資訊**：顯示資料筆數和欄位數

### 2. 預設資料類型

系統提供以下預設資料類型：

#### 2.1 每日股價 (daily_price)
- **描述**：股票每日開盤、收盤、最高、最低價等基本資訊
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
- **資料欄位**：date, symbol, open, high, low, close, volume, change, change_pct

#### 2.2 分K股價 (minute_price)
- **描述**：股票分K線圖資料，包含開盤、收盤、最高、最低價
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `interval`：時間間隔（1, 5, 15, 30, 60分鐘）
  - `date`：日期
- **資料欄位**：datetime, symbol, open, high, low, close, volume, interval

#### 2.3 除權息資料 (dividend)
- **描述**：股票除權息相關資訊，包含除權息日期、金額等
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
- **資料欄位**：date, symbol, dividend_type, cash_dividend, stock_dividend, ex_dividend_date, payment_date, total_dividend

#### 2.4 每日股價合併除權息 (daily_price_with_dividend)
- **描述**：每日股價資料並包含除權息調整資訊
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
  - `adjust_type`：調整類型（all, dividend, none）
- **資料欄位**：包含每日股價所有欄位 + dividend_type, cash_dividend, stock_dividend, total_dividend, adjusted_close

#### 2.5 技術指標 (technical_indicators)
- **描述**：包含各種技術指標的股價資料
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
  - `indicators`：技術指標（all, ma, rsi, macd, bollinger）
- **資料欄位**：包含每日股價欄位 + ma5, ma10, ma20, rsi, macd, macd_signal, macd_histogram, bb_upper, bb_middle, bb_lower

### 3. 資料類型管理

#### 3.1 新增自定義資料類型
```json
{
    "id": "custom_data_type",
    "name": "自定義資料類型",
    "description": "描述",
    "category": "分類",
    "parameters": {
        "param_name": {
            "type": "text|number|select|date",
            "label": "參數標籤",
            "default": "預設值",
            "placeholder": "提示文字",
            "options": [{"value": "v1", "label": "選項1"}]
        }
    }
}
```

#### 3.2 參數類型支援
- **text**：文字輸入
- **number**：數字輸入（支援 min, max, step）
- **select**：下拉選單（需要提供 options）
- **date**：日期選擇器

### 4. API 端點

#### 4.1 取得資料類型列表
```
GET /api/sample-data/types
```

#### 4.2 載入範例資料
```
POST /api/sample-data/load
Content-Type: application/json

{
    "data_type": "daily_price",
    "parameters": {
        "symbol": "2330",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
}
```

#### 4.3 取得特定資料類型
```
GET /api/sample-data/types/{data_type_id}
```

#### 4.4 新增資料類型
```
POST /api/sample-data/types
Content-Type: application/json

{
    "id": "custom_type",
    "name": "自定義類型",
    "description": "描述",
    "category": "分類",
    "parameters": {}
}
```

#### 4.5 移除資料類型
```
DELETE /api/sample-data/types/{data_type_id}
```

## 使用方式

### 1. 在策略編輯器中使用

1. 開啟策略編輯器頁面
2. 點擊「載入範例資料」按鈕
3. 在對話框中選擇資料類型
4. 設定相關參數
5. 點擊「載入資料」
6. 資料將以表格形式顯示在預覽區域

### 2. 在策略程式碼中使用

載入的資料可以透過 `currentPreviewData` 變數在策略程式碼中存取：

```python
def execute_strategy(data, parameters):
    # 使用預覽資料進行策略測試
    if currentPreviewData:
        # 轉換為 Polars DataFrame
        df = pl.DataFrame(currentPreviewData)
        
        # 進行策略分析
        result = analyze_data(df)
        
        return result
    else:
        return "請先載入資料"
```

### 3. 新增自定義資料類型

1. 準備資料類型定義 JSON
2. 使用 API 新增資料類型
3. 重新載入策略編輯器頁面
4. 新的資料類型將出現在選擇列表中

## 技術實作

### 1. 資料提供器 (DataProvider)

- 位置：`core/data_provider.py`
- 功能：管理資料類型定義和資料生成
- 支援：模擬資料生成、資料類型管理、檔案儲存

### 2. 前端整合

- 策略編輯器頁面：`web/templates/strategy_editor.html`
- JavaScript 功能：資料載入、預覽顯示、參數處理
- 響應式設計：支援不同螢幕尺寸

### 3. 後端 API

- 路由定義：`main.py`
- 資料處理：非同步處理、錯誤處理
- 快取整合：可與現有快取系統整合

## 注意事項

### 1. 資料限制
- 預覽最多顯示 100 筆資料
- 大量資料建議分批處理
- 資料為模擬資料，僅供測試使用

### 2. 效能考量
- 資料載入為非同步處理
- 大量資料可能影響頁面響應速度
- 建議定期清理不需要的資料

### 3. 安全性
- 資料類型定義需要驗證
- 防止惡意程式碼注入
- 參數值需要進行類型檢查

## 未來擴展

### 1. 資料來源擴展
- 整合真實股票 API
- 支援更多資料格式
- 新增歷史資料查詢

### 2. 功能增強
- 資料匯出功能
- 圖表視覺化
- 資料篩選和排序

### 3. 使用者體驗
- 拖拽式資料載入
- 資料預覽快照
- 批次資料處理

## 測試

使用提供的測試腳本驗證功能：

```bash
python test_data_preview_system.py
```

測試包含：
- 資料類型載入
- 各種資料類型測試
- 資料類型管理
- 策略編輯器整合

## 總結

資料預覽系統為策略編輯器提供了強大的資料處理能力，讓用戶可以：
- 快速載入和預覽各種資料
- 測試策略邏輯
- 管理自定義資料類型
- 提升開發效率

這個功能讓系統更接近專業的量化交易平台，提供類似 Jupyter 的互動式資料分析體驗。 