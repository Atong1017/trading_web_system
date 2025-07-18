# 選股編輯器功能說明

## 概述

選股編輯器是一個強大的股票篩選和管理工具，允許用戶建立、編輯和管理選股列表，並與策略編輯器整合使用。系統支援多種股票來源，包括手動新增、Excel匯入、條件篩選等。

## 主要功能

### 1. 選股列表管理

#### 建立選股列表
- 支援自定義名稱和描述
- 自動生成唯一ID
- 記錄建立和更新時間

#### 編輯選股列表
- 修改列表名稱和描述
- 新增/移除股票
- 批量操作支援

#### 刪除選股列表
- 安全刪除確認
- 自動清理相關資料

### 2. 股票來源支援

#### Excel檔案匯入
- 支援 `.xlsx` 格式
- 必要欄位：`stock_id`, `startdate`, `enddate`
- 自動驗證資料格式
- 錯誤處理和提示

#### 手動新增股票
- 單筆新增股票
- 支援股票代碼和名稱
- 可設定交易日期範圍

#### 條件篩選
- 多條件組合篩選
- 支援股票代碼和名稱篩選
- 可擴展的篩選邏輯

### 3. 策略整合

#### 匯出到策略
- 將選股列表匯出到策略編輯器
- 自動更新策略的股票來源設定
- 支援策略回測和自動交易

#### 股票來源選擇
- 策略編輯器中可選擇股票來源
- Excel檔案或選股列表
- 動態切換來源類型

## 技術架構

### 後端架構

#### StockListManager 類別
```python
class StockListManager:
    def __init__(self, data_dir: str = "data/stock_lists")
    def create_stock_list(self, name: str, description: str = "") -> str
    def get_stock_list(self, stock_list_id: str) -> Optional[Dict]
    def update_stock_list(self, stock_list_id: str, **kwargs) -> bool
    def delete_stock_list(self, stock_list_id: str) -> bool
    def import_stocks_from_excel(self, excel_file_path: str) -> List[Dict]
    def apply_stock_conditions(self, conditions: List[Dict]) -> List[Dict]
```

#### 資料儲存
- JSON格式儲存選股列表
- 檔案路徑：`data/stock_lists/stock_lists.json`
- 支援資料備份和恢復

### 前端架構

#### 選股編輯器頁面 (`/stock-selector`)
- 響應式設計
- 直觀的操作介面
- 即時資料更新

#### 策略編輯器整合
- 股票來源選擇介面
- 動態載入選股列表
- 無縫整合體驗

## API 端點

### 選股列表管理

#### 取得所有選股列表
```
GET /api/stock-lists
Response: {"status": "success", "stock_lists": [...]}
```

#### 取得特定選股列表
```
GET /api/stock-lists/{stock_list_id}
Response: {"status": "success", "stock_list": {...}}
```

#### 建立選股列表
```
POST /api/stock-lists
Body: {"name": "列表名稱", "description": "描述"}
Response: {"status": "success", "stock_list_id": "uuid"}
```

#### 更新選股列表
```
PUT /api/stock-lists/{stock_list_id}
Body: {"name": "新名稱", "stocks": [...]}
Response: {"status": "success", "message": "更新成功"}
```

#### 刪除選股列表
```
DELETE /api/stock-lists/{stock_list_id}
Response: {"status": "success", "message": "刪除成功"}
```

### Excel 操作

#### 匯入Excel檔案
```
POST /api/stock-lists/import-excel
Body: multipart/form-data with Excel file
Response: {"status": "success", "stocks": [...]}
```

### 選股條件

#### 套用選股條件
```
POST /api/stock-lists/apply-conditions
Body: {"conditions": [{"field": "stock_id", "operator": "contains", "value": "23"}]}
Response: {"status": "success", "stocks": [...]}
```

### 策略整合

#### 匯出到策略
```
POST /api/stock-lists/export-to-strategy
Body: {"stock_list_id": "uuid", "strategy_id": "uuid", "stocks": [...]}
Response: {"status": "success", "message": "匯出成功"}
```

## 使用方式

### 1. 建立選股列表

1. 進入選股編輯器頁面 (`/stock-selector`)
2. 點擊「新建選股列表」按鈕
3. 輸入列表名稱和描述
4. 選擇股票來源方式

### 2. Excel匯入股票

1. 準備Excel檔案，包含必要欄位
2. 點擊「匯入Excel」按鈕
3. 選擇檔案並上傳
4. 系統自動解析並顯示股票列表

### 3. 條件篩選股票

1. 點擊「條件篩選」按鈕
2. 設定篩選條件
3. 點擊「套用條件」
4. 查看篩選結果

### 4. 匯出到策略

1. 在選股編輯器中選擇要匯出的股票
2. 點擊「匯出到策略」按鈕
3. 選擇目標策略
4. 確認匯出

### 5. 在策略中使用

1. 進入策略編輯器
2. 選擇股票來源為「選股列表」
3. 選擇已建立的選股列表
4. 儲存策略設定

## 資料格式

### Excel檔案格式

| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| stock_id | 股票代碼 | 2330 |
| stock_name | 股票名稱 | 台積電 |
| start_date | 開始日期 | 2024-01-01 |
| end_date | 結束日期 | 2024-12-31 |

### 選股條件格式

```json
{
  "field": "stock_id",
  "operator": "contains",
  "value": "23"
}
```

支援的欄位：
- `stock_id`: 股票代碼
- `stock_name`: 股票名稱

支援的運算子：
- `contains`: 包含
- `equals`: 等於
- `starts_with`: 開頭為
- `ends_with`: 結尾為

## 注意事項

### 1. 資料驗證
- Excel檔案必須包含必要欄位
- 股票代碼格式驗證
- 日期格式驗證

### 2. 效能考量
- 大量股票資料處理
- 記憶體使用優化
- 檔案上傳大小限制

### 3. 錯誤處理
- 網路連線錯誤
- 檔案格式錯誤
- 資料驗證錯誤

### 4. 安全性
- 檔案上傳安全檢查
- 資料輸入驗證
- 權限控制

## 測試

### 執行測試腳本
```bash
python test_stock_selector_system.py
```

### 測試項目
1. 選股列表管理功能
2. 選股條件功能
3. Excel匯入匯出功能
4. 策略整合功能
5. 選股編輯器頁面
6. 策略編輯器整合

### 測試結果
- 所有測試通過表示功能正常
- 失敗的測試會顯示詳細錯誤訊息
- 測試報告包含通過率和詳細結果

## 未來擴展

### 1. 進階篩選條件
- 技術指標篩選
- 基本面篩選
- 自定義指標篩選

### 2. 資料來源整合
- 即時股價資料
- 財務報表資料
- 新聞資料

### 3. 自動化功能
- 定期更新選股列表
- 自動篩選條件
- 智能推薦股票

### 4. 協作功能
- 分享選股列表
- 評論和評分
- 社群功能

## 技術支援

如有問題或建議，請參考：
1. 系統日誌檔案
2. API錯誤訊息
3. 測試腳本輸出
4. 開發文件

---

*最後更新：2024年12月* 