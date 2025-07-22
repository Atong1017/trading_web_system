# 台灣股票回測與自動下單系統

這是一個完整的台灣股票回測與自動下單系統，支援多策略、多資料來源、多股票並行處理，並提供完整的前後端介面。系統採用現代化的 Web 架構，支援 Jupyter 風格的互動式策略開發。

## 🚀 功能特色

### 📊 回測功能
- **策略支援**：自定義策略
- **多資料來源**：Excel上傳、API資料、手動輸入、範例資料
- **多股票並行處理**：使用多執行緒提升回測效能
- **智能欄位映射**：支援多種Excel欄位格式
- **完整前後端**：現代化Web介面，支援即時回測
- **詳細測試**：完整的單元測試和整合測試

### 🤖 自動下單功能
- **即時監控**：自動執行策略信號
- **風險控制**：停利停損、部位管理
- **多券商支援**：可擴展的券商API介面

### 🗄️ 快取系統
- **雙層快取**：記憶體快取 + 檔案快取
- **自動管理**：記憶體不足時自動清理最舊的資料
- **TTL 機制**：可設定快取存活時間
- **統計資訊**：提供詳細的快取使用統計
- **API 整合**：與 StockAPI 無縫整合

### 📈 自定義策略系統
### 傳統策略編輯器
- **視覺化編輯器**：網頁版策略編輯器
- **即時程式碼執行**：程式碼立即在後端執行並顯示結果
- **模板系統**：提供策略模板
### 💻 Jupyter 風格
- **互動式開發**：支援單元格編輯和即時執行
- **變數共享**：單元格間變數保持狀態
- **筆記本管理**：支援儲存、載入、匯出筆記本
- **即時驗證**：語法檢查和函數檢測

- **版本管理**：策略的建立、更新、刪除
- **動態載入**：程式碼字串動態編譯執行
- **圖表顯示**：支援 Matplotlib、Seaborn、Plotly 圖表
- **資料分析**：內建 Pandas、Polars、NumPy 等資料分析工具

### 📋 資料預覽系統
- **範例資料**：提供多種預設資料類型
- **表格預覽**：支援最多100筆資料的表格顯示
- **自定義資料類型**：可新增和管理自定義資料類型
- **快速測試**：快速載入資料測試策略邏輯

### 📊 交易記錄管理
- **多維度篩選**：支援日期、股票、策略、方向等多種篩選條件
- **統計分析**：提供勝率、報酬率、最大回撤等關鍵指標
- **詳細資訊**：包含進出場價格、損益計算、風險控制等完整資訊
- **匯出功能**：支援Excel匯出和分頁顯示

### 🎯 股票選擇器
- **多來源支援**：Excel匯入、手動新增、條件篩選
- **列表管理**：建立、編輯、刪除選股列表
- **策略整合**：與策略編輯器無縫整合
- **批量操作**：支援批量新增、移除股票

### 🛠️ 共同功能
- **價格計算工具**: 最小變動單位、漲跌停價格計算
- **交易成本計算**: 手續費、證交稅自動計算
- **除權息調整**: 自動處理除權息對股價的影響
- **模組化設計**: 易於擴展和維護

## 📁 專案結構

```
trading_web_system/
├── api/                    # API模組
│   ├── stock_api.py       # 股票資料API
│   ├── broker_api.py      # 券商API
│   ├── jupyter_api.py     # Jupyter編輯器API
│   ├── strategy_api.py    # 策略管理API
│   ├── backtest_api.py    # 回測API
│   ├── chart_api.py       # 圖表API
│   ├── cache_api.py       # 快取API
│   ├── excel_api.py       # Excel處理API
│   ├── sample_data_api.py # 範例資料API
│   └── stock_list_api.py  # 股票清單API
├── config/                # 配置檔案
│   ├── api_config.py      # API配置
│   └── trading_config.py  # 交易配置
├── core/                  # 核心功能
│   ├── cache_manager.py   # 快取管理器
│   ├── data_provider.py   # 資料提供器
│   ├── price_utils.py     # 價格計算工具
│   ├── stock_list_manager.py # 股票清單管理器
│   ├── technical_indicators.py # 技術指標
│   ├── trading_utils.py   # 交易工具
│   └── utils.py           # 通用工具函數
├── data/                  # 資料目錄
│   ├── cache/             # 快取檔案
│   ├── uploads/           # 上傳檔案
│   ├── exports/           # 匯出檔案
│   ├── strategies/        # 策略檔案
│   └── stock_lists/       # 股票清單
├── routes/                # 路由模組
│   ├── api_routes.py      # API路由
│   └── pages.py           # 頁面路由
├── strategies/            # 策略模組
│   ├── base_strategy.py   # 策略基礎類別
│   ├── dynamic_strategy.py # 動態策略
│   └── strategy_manager.py # 策略管理器
├── web/                   # 網頁介面
│   ├── static/            # 靜態檔案
│   │   ├── css/           # 樣式檔案
│   │   ├── js/            # JavaScript檔案
│   │   └── images/        # 圖片檔案
│   └── templates/         # HTML模板
│       ├── base.html      # 基礎模板
│       ├── index.html     # 首頁
│       ├── backtest.html  # 回測頁面
│       ├── strategy_editor.html # 策略編輯器
│       ├── stock_selector.html # 股票選擇器
│       ├── cache_manager.html # 快取管理
│       ├── auto_trading.html # 自動下單頁面
│       ├── trading_records.html # 交易記錄頁面
│       └── settings.html  # 設定頁面
├── main.py               # FastAPI主程式
├── run.py                # 啟動腳本
├── requirements.txt      # 依賴套件
└── README.md            # 說明文件
```

## 🛠️ 安裝與設定

### 1. 環境需求
- Python 3.8+
- Windows 10/11 或 Linux/macOS

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 啟動系統
```bash
python run.py
```

系統將在 `http://localhost:8000` 啟動

## 📖 使用說明

### 首頁功能
- **回測系統**: 進入股票策略回測功能
- **策略編輯器**: 進入 Jupyter 風格策略編輯器
- **股票選擇器**: 管理股票清單
- **快取管理**: 管理系統快取
- **自動下單**: 進入自動交易系統
- **交易記錄**: 查看歷史交易記錄
- **系統設定**: 配置API和系統參數

### 策略編輯器

#### 1. 編輯模式
- **傳統模式**: 原有的程式碼編輯器，適合編寫完整的策略程式碼
- **Jupyter 模式**: 互動式單元格編輯器，適合探索性資料分析和策略開發

#### 2. 單元格功能
- **新增單元格**: 點擊「新增單元格」按鈕或使用 Ctrl+Enter
- **執行單元格**: 點擊執行按鈕或使用 Shift+Enter
- **刪除單元格**: 點擊刪除按鈕
- **重新編號**: 自動重新編號單元格

#### 3. 支援的模組
- **基本 Python 模組**: np, pd, pl, plt, sns, go
- **策略工具模組**: PriceUtils, Utils, TradeRecord, HoldingPosition

#### 4. 範例程式碼
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

### 快取系統

#### 1. 快取管理頁面
訪問 `/cache-manager` 可以查看：
- 記憶體使用量統計
- 快取項目詳情
- 股票代碼列表
- 快取清理功能

#### 2. API 整合
```python
from api.stock_api import StockAPI

async with StockAPI() as stock_api:
    # 第一次請求會從 API 取得並快取
    data1 = await stock_api.get_stock_price(
        stock_ids=["2330"],
        start_date="2024-01-01",
        end_date="2024-01-03",
        use_cache=True  # 啟用快取
    )
```

### 自定義策略系統

#### 1. 策略編輯器
訪問 `/strategy-editor` 進入策略編輯器，可以：
- 建立新策略
- 編輯現有策略
- 載入策略模板
- 驗證策略程式碼
- 測試策略功能

#### 2. 策略程式碼格式
```python
def should_entry(stock_data, current_index):
    """判斷是否應該進場"""
    current_row = stock_data[current_index]
    
    # 範例：當收盤價大於開盤價時進場
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    
    return False, {}

def should_exit(stock_data, current_index, position):
    """判斷是否應該出場"""
    current_row = stock_data[current_index]
    entry_price = position["entry_price"]
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    # 範例：虧損超過5%時出場
    if loss_rate <= -5:
        return True, {"reason": f"虧損{loss_rate:.2f}%"}
    
    return False, {}
```

### 資料預覽系統

#### 1. 預設資料類型
- **每日股價**: 股票每日開盤、收盤、最高、最低價等基本資訊
- **分K股價**: 股票分K線圖資料
- **除權息資料**: 股票除權息相關資訊
- **每日股價合併除權息**: 每日股價資料並包含除權息調整資訊
- **技術指標**: 包含各種技術指標的股價資料

#### 2. 使用方式
1. 開啟策略編輯器頁面
2. 點擊「載入範例資料」按鈕
3. 在對話框中選擇資料類型
4. 設定相關參數
5. 點擊「載入資料」
6. 資料將以表格形式顯示在預覽區域

### 📊 交易記錄管理

#### 1. 篩選功能
- **日期範圍篩選**: 按進場/出場日期範圍篩選
- **股票代碼篩選**: 按特定股票代碼篩選
- **策略類型篩選**: 按使用的策略篩選
- **交易方向篩選**: 按買入/賣出方向篩選
- **損益範圍篩選**: 按損益金額範圍篩選

#### 2. 統計分析
- **總交易次數**: 顯示總交易筆數
- **勝率統計**: 計算獲利交易的比例
- **總報酬**: 顯示總體投資報酬率
- **平均報酬**: 計算平均每筆交易的報酬率
- **最大單筆獲利/虧損**: 顯示最大獲利和虧損金額
- **最大回撤分析**: 分析最大回撤期間和幅度

#### 3. 詳細交易資訊
- **進出場資訊**: 進場日期、出場日期、進場價格、出場價格
- **交易詳情**: 股票代碼、股票名稱、交易方向、股數
- **損益計算**: 損益金額、損益率、手續費、證交稅、淨損益
- **風險控制**: 停利價、停損價、出場原因
- **持有期間**: 持有天數、策略名稱

#### 4. 匯出功能
- **Excel匯出**: 將篩選結果匯出為Excel檔案
- **分頁顯示**: 支援大量資料的分頁顯示
- **即時更新**: 自動重新整理最新交易記錄

### 🎯 股票選擇器

#### 1. 選股列表管理
- **建立選股列表**: 支援自定義名稱和描述
- **編輯選股列表**: 修改列表名稱、描述和股票內容
- **刪除選股列表**: 安全刪除確認機制
- **列表匯出**: 將選股列表匯出到策略編輯器

#### 2. 股票來源支援
- **Excel檔案匯入**: 支援 `.xlsx` 格式，必要欄位：`stock_id`, `startdate`, `enddate`
- **手動新增股票**: 單筆新增股票代碼和名稱
- **條件篩選**: 多條件組合篩選股票
- **批量操作**: 支援批量新增、移除股票

#### 3. 策略整合
- **匯出到策略**: 將選股列表匯出到策略編輯器
- **股票來源選擇**: 策略編輯器中可選擇股票來源
- **動態切換**: 支援Excel檔案或選股列表的動態切換

#### 4. 資料格式
**Excel檔案格式**：
| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| stock_id | 股票代碼 | 2330 |
| stock_name | 股票名稱 | 台積電 |
| start_date | 開始日期 | 2024-01-01 |
| end_date | 結束日期 | 2024-12-31 |

#### 5. 使用方式
1. **建立選股列表**：
   - 進入選股編輯器頁面 (`/stock-selector`)
   - 點擊「新建選股列表」按鈕
   - 輸入列表名稱和描述
   - 選擇股票來源方式

2. **Excel匯入股票**：
   - 準備Excel檔案，包含必要欄位
   - 點擊「匯入Excel」按鈕
   - 選擇檔案並上傳
   - 系統自動解析並顯示股票列表

3. **條件篩選股票**：
   - 點擊「條件篩選」按鈕
   - 設定篩選條件
   - 點擊「套用條件」
   - 查看篩選結果

4. **匯出到策略**：
   - 在選股編輯器中選擇要匯出的股票
   - 點擊「匯出到策略」按鈕
   - 選擇目標策略
   - 確認匯出

### 回測功能使用

#### 1. 選擇策略
- **當沖策略**：當日沖銷，以漲跌停為依據
- **波段策略**：波段交易，以20日新高為依據
- **詢圈公告策略**：基於詢圈公告進行交易
- **自定義策略**：使用策略編輯器建立的自定義策略

#### 2. 設定資料來源
- **API模式**：上傳包含股票代碼和日期的Excel檔案，系統從API取得股價資料
- **Excel模式**：上傳包含完整K線資料的Excel檔案
- **範例資料**：使用系統提供的範例資料

#### 3. Excel檔案格式

**API模式格式**：
| stock_id | date |
|----------|------|
| 2330 | 2024-01-01 |
| 2330 | 2024-01-02 |

**Excel模式格式**：
| stock_id | date | open | high | low | close |
|----------|------|------|------|-----|-------|
| 2330 | 2024-01-01 | 100 | 105 | 98 | 103 |
| 2330 | 2024-01-02 | 103 | 108 | 102 | 106 |

#### 4. 策略參數

**當沖策略參數**：
- 使用漲跌停單：是否使用漲跌停單
- 最大持有天數：最大持有天數（1-7天）
- 強制出場：是否強制出場

**波段策略參數**：
- 停利比例：停利百分比（1%-100%）
- 停損比例：停損百分比（-100%--1%）
- 最大持有天數：最大持有天數（1-365天）
- 強制出場：是否強制出場
- 新高計算期間：新高計算期間（5-60天）

**詢圈公告策略參數**：
- 公告延遲天數：公告延遲天數（0-10天）
- 部位大小比例：部位大小比例（1%-100%）
- 最大持有天數：最大持有天數（1-365天）

### 自動下單功能使用

#### 1. 選擇策略和參數
與回測功能相同，選擇策略並設定參數。

#### 2. 選擇券商
選擇您使用的券商API。

#### 3. 設定資金
設定自動下單的初始資金。

#### 4. 啟動/停止
點擊啟動按鈕開始自動下單，點擊停止按鈕停止。

### 交易記錄管理

#### 1. 篩選功能
- **日期範圍篩選**: 按進場/出場日期範圍篩選
- **股票代碼篩選**: 按特定股票代碼篩選
- **策略類型篩選**: 按使用的策略篩選
- **交易方向篩選**: 按買入/賣出方向篩選
- **損益範圍篩選**: 按損益金額範圍篩選

#### 2. 統計分析
- **總交易次數**: 顯示總交易筆數
- **勝率統計**: 計算獲利交易的比例
- **總報酬**: 顯示總體投資報酬率
- **平均報酬**: 計算平均每筆交易的報酬率
- **最大單筆獲利/虧損**: 顯示最大獲利和虧損金額
- **最大回撤分析**: 分析最大回撤期間和幅度

#### 3. 詳細交易資訊
- **進出場資訊**: 進場日期、出場日期、進場價格、出場價格
- **交易詳情**: 股票代碼、股票名稱、交易方向、股數
- **損益計算**: 損益金額、損益率、手續費、證交稅、淨損益
- **風險控制**: 停利價、停損價、出場原因
- **持有期間**: 持有天數、策略名稱

#### 4. 匯出功能
- **Excel匯出**: 將篩選結果匯出為Excel檔案
- **分頁顯示**: 支援大量資料的分頁顯示
- **即時更新**: 自動重新整理最新交易記錄

### 股票選擇器使用

#### 1. 建立選股列表
1. 進入選股編輯器頁面 (`/stock-selector`)
2. 點擊「新建選股列表」按鈕
3. 輸入列表名稱和描述
4. 選擇股票來源方式

#### 2. Excel匯入股票
1. 準備Excel檔案，包含必要欄位
2. 點擊「匯入Excel」按鈕
3. 選擇檔案並上傳
4. 系統自動解析並顯示股票列表

#### 3. 條件篩選股票
1. 點擊「條件篩選」按鈕
2. 設定篩選條件
3. 點擊「套用條件」
4. 查看篩選結果

#### 4. 匯出到策略
1. 在選股編輯器中選擇要匯出的股票
2. 點擊「匯出到策略」按鈕
3. 選擇目標策略
4. 確認匯出

### 系統設定

#### 1. API設定
- **股票資料API**: 設定股價資料來源
- **券商API**: 設定自動下單券商

#### 2. 交易參數
- 手續費率和最低手續費
- 證交稅率
- 預設初始資金
- 風險控制參數

#### 3. 系統參數
- 日誌等級和檔案管理
- 會話超時設定
- 檔案上傳限制
- 自動清理設定

#### 4. 備份設定
- 自動備份頻率和時間
- 備份保留天數
- 手動備份和還原

## 策略開發

### 新增策略
1. 繼承 `BaseStrategy` 類別
2. 實作必要的方法：
   - `should_entry()`: 進場條件
   - `should_exit()`: 出場條件
   - `execute_trade()`: 執行交易
3. 在 `config/trading_config.py` 中新增配置
4. 在 `main.py` 中註冊策略

### 策略配置範例
```python
"new_strategy": {
    "name": "新策略",
    "description": "策略描述",
    "parameters": {
        "param1": {
            "type": "number",
            "label": "參數1",
            "default": 0.1,
            "min": 0,
            "max": 1,
            "description": "參數說明"
        }
    },
    "charts": ["equity_curve", "drawdown"],
    "data_source": "api",
    "stock_source": "excel"
}
```

## 📊 資料格式

### Excel檔案格式

#### 股價資料檔案
| 欄位 | 說明 | 範例 |
|------|------|------|
| stock_id | 股票代碼 | 2330 |
| date | 日期 | 2024-01-01 |
| open | 開盤價 | 100.0 |
| high | 最高價 | 101.0 |
| low | 最低價 | 99.0 |
| close | 收盤價 | 100.5 |
| volume | 成交量 | 1000000 |

#### 股票清單檔案
| 欄位 | 說明 | 範例 |
|------|------|------|
| stock_id | 股票代碼 | 2330 |
| date | 日期 | 2024-01-01 |

#### 選股列表檔案
| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| stock_id | 股票代碼 | 2330 |
| stock_name | 股票名稱 | 台積電 |
| start_date | 開始日期 | 2024-01-01 |
| end_date | 結束日期 | 2024-12-31 |

## 🔒 安全性

- API金鑰使用環境變數或加密儲存
- 檔案上傳有大小和格式限制
- 系統支援HTTPS加密傳輸
- 定期備份重要資料

## 🐛 故障排除

### 常見問題

#### 1. 模組導入錯誤
```bash
# 檢查Python版本
python --version

# 重新安裝依賴
pip install -r requirements.txt --force-reinstall
```

#### 2. 檔案上傳失敗
- 檢查檔案格式是否為Excel (.xlsx, .xls)
- 檢查檔案大小是否超過50MB
- 確認檔案包含必要欄位

#### 3. API連線失敗
- 檢查網路連線
- 確認API金鑰是否正確
- 檢查API服務是否正常

#### 4. 回測執行失敗
- 檢查資料格式是否正確
- 確認策略參數是否合理
- 查看系統日誌檔案

#### 5. Jupyter編輯器問題
- 檢查程式碼語法是否正確
- 確認使用的模組在支援列表中
- 避免執行過於複雜的程式碼

#### 6. 交易記錄問題
- 檢查篩選條件是否正確設定
- 確認交易記錄資料是否完整
- 檢查Excel匯出功能是否正常

#### 7. 選股功能問題
- 檢查Excel檔案格式是否符合要求
- 確認股票代碼是否正確
- 檢查選股列表是否成功建立

### 日誌檔案
系統日誌位於 `logs/` 目錄下，包含:
- `app.log`: 應用程式日誌
- `error.log`: 錯誤日誌
- `access.log`: 存取日誌

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 支援

如有問題或建議，請:
1. 查看 [Issues](../../issues) 頁面
2. 建立新的 Issue
3. 聯繫開發團隊

## 🔄 更新日誌

### v3.0.0 (最新)
- 新增 Jupyter 風格策略編輯器
- 新增快取系統
- 新增自定義策略系統
- 新增資料預覽系統
- 新增股票選擇器功能
- 改善策略編輯器使用者體驗
- 新增完整的參數設定系統
- 支援共用參數（手續費、證交稅、交易股數）
- 新增進場/出場條件選擇
- 新增停利/停損開關選項
- 新增漲跌停限制選項
- 改善參數顯示格式（使用百分比）
- 更新所有策略的參數配置
- 新增完整的參數測試

### v2.0.0
- 新增完整的參數設定系統
- 支援共用參數（手續費、證交稅、交易股數）
- 新增進場/出場條件選擇
- 新增停利/停損開關選項
- 新增漲跌停限制選項
- 改善參數顯示格式（使用百分比）
- 更新所有策略的參數配置
- 新增完整的參數測試

### v1.0.0
- 初始版本
- 支援基本回測功能
- 支援Excel檔案上傳
- 支援多執行緒處理

## 系統特色

### 🚀 高效能多執行緒處理
- **並行回測**: 支援多執行緒並行處理多股票回測，大幅提升處理速度
- **智能線程管理**: 自動調整線程數量，避免過度並行造成系統負載
- **容錯處理**: 單一股票處理失敗不影響其他股票的回測執行
- **效能提升**: 處理100支股票時，效能可提升5-10倍

### 📊 多策略支援
- **當沖策略**: 適合短線交易，日內進出
- **波段策略**: 適合中期持有，包含除權息調整
- **詢圈公告策略**: 專門處理詢圈公告相關交易
- **自定義策略**: 支援用戶自定義策略開發
- **策略擴展**: 基於 `BaseStrategy` 類別，易於新增自定義策略

### 📈 多資料來源
- **API資料**: 支援多種股票API資料來源
- **Excel上傳**: 支援Excel檔案上傳，自動識別欄位格式
- **範例資料**: 提供多種預設資料類型供測試使用
- **欄位映射**: 智能識別中文/英文欄位名稱
- **資料驗證**: 自動驗證資料完整性和格式正確性

### 💻 Jupyter 風格開發環境
- **互動式編輯**: 支援單元格編輯和即時執行
- **即時程式碼執行**: 程式碼立即在後端執行並顯示結果
- **圖表顯示**: 支援 Matplotlib、Seaborn、Plotly 圖表
- **資料分析**: 內建 Pandas、Polars、NumPy 等資料分析工具
- **變數共享**: 單元格間變數保持狀態
- **筆記本管理**: 支援儲存、載入、匯出筆記本

### 🗄️ 智能快取系統
- **雙層快取**: 記憶體快取 + 檔案快取
- **自動管理**: 記憶體不足時自動清理最舊的資料
- **TTL 機制**: 可設定快取存活時間
- **統計資訊**: 提供詳細的快取使用統計
- **API 整合**: 與 StockAPI 無縫整合

### 🎯 動態參數配置
- **參數來源**: 支援手動輸入、Excel上傳、API取得等多種參數來源
- **策略專用**: 不同策略顯示對應的參數設定
- **即時驗證**: 參數輸入時即時驗證格式和範圍
- **格式說明**: 提供詳細的Excel格式說明和範例

### 📊 完整交易記錄系統
- **多維度篩選**: 支援日期、股票、策略、方向等多種篩選條件
- **統計分析**: 提供勝率、報酬率、最大回撤等關鍵指標
- **詳細資訊**: 包含進出場價格、損益計算、風險控制等完整資訊
- **匯出功能**: 支援Excel匯出和分頁顯示

### 🎯 智能選股系統
- **多來源支援**: Excel匯入、手動新增、條件篩選
- **列表管理**: 建立、編輯、刪除選股列表
- **策略整合**: 與策略編輯器無縫整合
- **批量操作**: 支援批量新增、移除股票

---

**注意**: 本系統僅供學習和研究使用，實際交易請謹慎評估風險。

---

# 📚 詳細功能說明

## Jupyter 風格策略編輯器

### 概述

策略編輯器現在支援 Jupyter 風格的互動式程式碼編輯，提供即時程式碼執行、圖表顯示和資料分析功能。

### 主要功能

#### 1. 切換編輯模式
- **傳統模式**: 原有的程式碼編輯器，適合編寫完整的策略程式碼
- **Jupyter 模式**: 互動式單元格編輯器，適合探索性資料分析和策略開發

#### 2. Jupyter 單元格功能
- **新增單元格**: 點擊「新增單元格」按鈕或使用 Ctrl+Enter
- **執行單元格**: 點擊執行按鈕或使用 Shift+Enter
- **刪除單元格**: 點擊刪除按鈕
- **重新編號**: 自動重新編號單元格

#### 3. 程式碼執行
- **即時執行**: 程式碼立即在後端執行
- **輸出捕獲**: 自動捕獲 print 輸出、錯誤訊息和圖表
- **狀態指示**: 單元格會顯示執行狀態（執行中、成功、錯誤）

#### 4. 支援的輸出類型
- **文字輸出**: print 語句的輸出
- **錯誤訊息**: 語法錯誤和執行錯誤
- **DataFrame 顯示**: Pandas 和 Polars DataFrame 的表格顯示
- **圖表顯示**: Matplotlib 和 Seaborn 圖表
- **數值結果**: 計算結果的顯示

### 可用模組

#### 基本 Python 模組
- `np` - NumPy 數值計算
- `pd` - Pandas 資料處理
- `pl` - Polars 高效能資料處理
- `plt` - Matplotlib 繪圖
- `sns` - Seaborn 統計繪圖
- `go` - Plotly 互動圖表

#### 策略工具模組
- `PriceUtils` - 價格計算工具
- `Utils` - 通用工具類別
- `TradeRecord` - 交易記錄資料類別
- `HoldingPosition` - 持有部位資料類別

### 快捷鍵

- **Shift+Enter**: 執行當前單元格
- **Ctrl+Enter**: 執行當前單元格並新增新單元格
- **Tab**: 自動縮排

### 範例程式碼

#### 基本資料分析
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

#### 技術指標計算
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

#### 圖表繪製
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

### 筆記本管理

#### 儲存筆記本
- 點擊「儲存筆記本」按鈕將筆記本儲存到本地瀏覽器
- 支援離線儲存和恢復

#### 匯出筆記本
- 點擊「匯出」按鈕下載 JSON 格式的筆記本檔案
- 可以與其他用戶分享筆記本

#### 載入筆記本
- 支援載入之前儲存的筆記本檔案
- 自動恢復程式碼和輸出

### 注意事項

1. **執行環境**: 程式碼在後端安全環境中執行
2. **記憶體管理**: 大型資料集會自動清理
3. **錯誤處理**: 語法錯誤和執行錯誤會清楚顯示
4. **圖表顯示**: 支援 Matplotlib 和 Seaborn 圖表
5. **資料持久性**: 單元格之間的變數會保持

### 最佳實踐

1. **模組化開發**: 將複雜邏輯分解為多個單元格
2. **逐步測試**: 逐個單元格測試程式碼
3. **圖表驗證**: 使用圖表驗證策略邏輯
4. **註解說明**: 在程式碼中添加清楚的註解
5. **定期儲存**: 定期儲存筆記本避免資料遺失

### 故障排除

#### 常見問題
1. **單元格無法執行**: 檢查程式碼語法是否正確
2. **圖表不顯示**: 確保使用 `plt.show()` 顯示圖表
3. **模組找不到**: 確認使用的模組在支援列表中
4. **執行超時**: 避免執行過於複雜的程式碼

#### 效能優化
1. **分批處理**: 大型資料集分批處理
2. **記憶體清理**: 及時清理不需要的變數
3. **圖表優化**: 設定適當的圖表大小和解析度

## 程式碼編輯器功能

### 概述

策略編輯器現在整合了專業的程式碼編輯器功能，基於 CodeMirror 5.65.2 實現，提供類似 Python IDE 的開發體驗。編輯器支援語法高亮、自動縮排、程式碼提示、搜尋替換等專業功能。

### 主要功能

#### 1. 語法高亮
- **Python 語法支援**：完整的 Python 語法高亮
- **多主題選擇**：支援 Eclipse、Monokai、Dracula 等主題
- **即時高亮**：輸入時即時顯示語法高亮

#### 2. 自動縮排
- **智能縮排**：輸入 `:` 後按 Enter 自動增加縮排
- **Tab 鍵支援**：Tab 鍵插入 4 個空格
- **選區縮排**：選中多行可批量縮排
- **自動對齊**：括號、引號自動配對

#### 3. 程式碼提示
- **自動完成**：Ctrl+Space 觸發自動完成
- **函數提示**：顯示函數參數和說明
- **變數提示**：智能變數名稱建議

#### 4. 程式碼摺疊
- **區塊摺疊**：可摺疊函數、類別、註解區塊
- **行號顯示**：顯示行號便於定位
- **摺疊指示器**：視覺化摺疊狀態

#### 5. 搜尋與替換
- **快速搜尋**：Ctrl+F 開啟搜尋
- **替換功能**：Ctrl+H 開啟替換
- **跳轉行號**：快速跳轉到指定行

#### 6. 程式碼格式化
- **一鍵格式化**：自動調整縮排和空行
- **語法檢查**：檢查括號配對和基本語法
- **程式碼清理**：移除多餘空格和空行

#### 7. 全螢幕編輯
- **全螢幕模式**：專注程式碼編輯
- **快速切換**：一鍵進入/退出全螢幕
- **自適應大小**：自動調整編輯器大小

### 技術架構

#### 前端技術
- **CodeMirror 5.65.2**：專業程式碼編輯器
- **Python Mode**：Python 語法支援
- **多種 Addon**：功能擴展模組

#### 編輯器配置
```javascript
codeEditor = CodeMirror.fromTextArea(textarea, {
    mode: 'python',                    // Python 語法模式
    theme: 'eclipse',                  // 預設主題
    lineNumbers: true,                 // 顯示行號
    lineWrapping: true,                // 自動換行
    indentUnit: 4,                     // 縮排單位
    tabSize: 4,                        // Tab 大小
    indentWithTabs: false,             // 使用空格縮排
    autoCloseBrackets: true,           // 自動關閉括號
    matchBrackets: true,               // 括號配對高亮
    foldGutter: true,                  // 摺疊功能
    gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter']
});
```

#### 快捷鍵設定
- **Tab**：插入縮排或選區縮排
- **Enter**：智能換行和縮排
- **Ctrl+Space**：觸發自動完成
- **Ctrl+F**：開啟搜尋
- **Ctrl+H**：開啟替換
- **Ctrl+/**：註解/取消註解

### 使用方式

#### 1. 基本編輯
1. 進入策略編輯器頁面
2. 程式碼編輯器會自動載入預設模板
3. 開始輸入程式碼，享受語法高亮和自動縮排

#### 2. 自動縮排範例
```python
# 輸入以下程式碼時會自動縮排
if a == 1:  # 輸入 : 後按 Enter
    print("a is 1")  # 自動縮排 4 個空格
    if b == 2:  # 再次縮排
        print("b is 2")  # 再縮排 4 個空格
```

#### 3. 程式碼格式化
1. 點擊「格式化」按鈕
2. 系統自動調整縮排和空行
3. 檢查並修正基本語法問題

#### 4. 語法驗證
1. 點擊「驗證語法」按鈕
2. 系統檢查括號配對和縮排
3. 顯示驗證結果和錯誤訊息

#### 5. 全螢幕編輯
1. 點擊「全螢幕」按鈕
2. 編輯器進入全螢幕模式
3. 專注於程式碼編輯
4. 點擊「退出全螢幕」返回

### 程式碼模板

#### 預設策略模板
```python
class MyStrategy:
    def __init__(self, parameters):
        self.parameters = parameters
        self.strategy_name = "我的策略"
        self.strategy_description = "自定義交易策略"
    
    def execute(self, data):
        """
        策略執行邏輯
        data: 股票資料 (polars DataFrame)
        """
        # 在這裡實作您的策略邏輯
        result = data.clone()
        
        # 範例：簡單的移動平均策略
        if len(data) > 20:
            result = result.with_columns([
                pl.col('close').rolling_mean(window_size=20).alias('ma20'),
                pl.col('close').rolling_mean(window_size=5).alias('ma5')
            ])
            
            # 產生買賣訊號
            result = result.with_columns([
                pl.when(pl.col('ma5') > pl.col('ma20'))
                .then(1)  # 買入訊號
                .otherwise(0).alias('signal')
            ])
        
        return result
    
    def get_parameters(self):
        """取得策略參數"""
        return self.parameters
```

### 編輯器主題

#### 可用主題
1. **Eclipse**：淺色主題，適合日間使用
2. **Monokai**：深色主題，適合夜間使用
3. **Dracula**：深色主題，現代化設計

#### 主題切換
- 可在編輯器設定中切換主題
- 主題設定會自動保存
- 支援自定義主題

### 程式碼驗證

#### 驗證項目
1. **括號配對**：檢查 `()`, `[]`, `{}` 配對
2. **縮排檢查**：檢查 Python 縮排規則
3. **基本語法**：檢查常見語法錯誤
4. **程式碼結構**：檢查類別和函數定義

#### 錯誤提示
- 即時顯示錯誤位置
- 提供錯誤說明和建議
- 支援錯誤快速修復

### 效能優化

#### 編輯器效能
- **虛擬化渲染**：只渲染可見區域
- **延遲載入**：按需載入功能模組
- **記憶體管理**：自動清理未使用資源

#### 大型檔案支援
- **分頁載入**：支援大型程式碼檔案
- **增量更新**：只更新變更的部分
- **背景處理**：非阻塞式語法檢查

### 自定義設定

#### 編輯器偏好設定
```javascript
// 自定義編輯器設定
const editorConfig = {
    fontSize: '14px',           // 字體大小
    fontFamily: 'Fira Code',    // 字體
    tabSize: 4,                 // Tab 大小
    theme: 'eclipse',           // 主題
    lineNumbers: true,          // 行號
    autoCloseBrackets: true,    // 自動關閉括號
    matchBrackets: true,        // 括號配對
    foldGutter: true,           // 摺疊功能
    lineWrapping: true          // 自動換行
};
```

#### 快捷鍵自定義
```javascript
// 自定義快捷鍵
extraKeys: {
    'Ctrl-S': function(cm) {
        // 自定義儲存功能
        saveStrategy();
    },
    'Ctrl-R': function(cm) {
        // 自定義執行功能
        testStrategy();
    }
}
```

### 錯誤處理

#### 常見問題
1. **編輯器無法載入**：檢查網路連線和 CDN 資源
2. **語法高亮異常**：重新整理頁面或清除快取
3. **自動縮排失效**：檢查編輯器設定
4. **程式碼驗證錯誤**：檢查 Python 語法

#### 故障排除
- 檢查瀏覽器控制台錯誤訊息
- 確認 CodeMirror 資源載入成功
- 驗證編輯器初始化狀態
- 檢查 JavaScript 錯誤

### 未來擴展

#### 計劃功能
1. **智能程式碼補全**：基於上下文的補全
2. **程式碼片段**：預設程式碼片段
3. **即時錯誤檢查**：輸入時即時檢查
4. **程式碼重構**：自動重構工具
5. **版本控制整合**：Git 整合功能

#### 進階功能
1. **多檔案編輯**：支援多個策略檔案
2. **程式碼導航**：函數和類別導航
3. **程式碼摺疊**：更智能的摺疊邏輯
4. **主題自定義**：自定義編輯器主題
5. **外掛系統**：可擴展的外掛架構

### 測試

#### 執行測試
```bash
python test_code_editor_features.py
```

#### 測試項目
1. 程式碼編輯器頁面載入
2. 程式碼編輯器 API 功能
3. 程式碼驗證功能
4. 策略建立和編輯
5. 程式碼編輯器特色功能
6. 編輯器整合功能

#### 測試結果
- 所有測試通過表示功能正常
- 失敗的測試會顯示詳細錯誤訊息
- 測試報告包含通過率和詳細結果

### 技術支援

#### 開發文件
- [CodeMirror 官方文件](https://codemirror.net/doc/manual.html)
- [Python Mode 文件](https://codemirror.net/mode/python/)
- [編輯器 API 參考](https://codemirror.net/doc/manual.html#api)

#### 問題回報
如有問題或建議，請：
1. 檢查瀏覽器控制台錯誤
2. 查看系統日誌檔案
3. 執行測試腳本驗證功能
4. 提供詳細的錯誤訊息和重現步驟

## 資料預覽系統

### 概述

本系統新增了類似 Jupyter 的資料預覽功能，讓用戶在策略編輯器中可以：
1. 載入各種預設的範例資料
2. 以表格形式預覽資料內容
3. 管理自定義資料類型
4. 快速測試策略邏輯

### 主要功能

#### 1. 資料預覽功能

##### 1.1 資料預覽區域
- 在策略編輯器中新增了資料預覽區域
- 支援顯示最多 100 筆資料（避免頁面過載）
- 自動格式化數值和日期顯示
- 提供資料統計資訊（筆數、欄位數）

##### 1.2 資料載入控制
- **載入範例資料**：開啟資料選擇對話框
- **清除**：清除當前預覽的資料
- **資料資訊**：顯示資料筆數和欄位數

#### 2. 預設資料類型

系統提供以下預設資料類型：

##### 2.1 每日股價 (daily_price)
- **描述**：股票每日開盤、收盤、最高、最低價等基本資訊
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
- **資料欄位**：date, symbol, open, high, low, close, volume, change, change_pct

##### 2.2 分K股價 (minute_price)
- **描述**：股票分K線圖資料，包含開盤、收盤、最高、最低價
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `interval`：時間間隔（1, 5, 15, 30, 60分鐘）
  - `date`：日期
- **資料欄位**：datetime, symbol, open, high, low, close, volume, interval

##### 2.3 除權息資料 (dividend)
- **描述**：股票除權息相關資訊，包含除權息日期、金額等
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
- **資料欄位**：date, symbol, dividend_type, cash_dividend, stock_dividend, ex_dividend_date, payment_date, total_dividend

##### 2.4 每日股價合併除權息 (daily_price_with_dividend)
- **描述**：每日股價資料並包含除權息調整資訊
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
  - `adjust_type`：調整類型（all, dividend, none）
- **資料欄位**：包含每日股價所有欄位 + dividend_type, cash_dividend, stock_dividend, total_dividend, adjusted_close

##### 2.5 技術指標 (technical_indicators)
- **描述**：包含各種技術指標的股價資料
- **參數**：
  - `symbol`：股票代碼（預設：2330）
  - `start_date`：開始日期
  - `end_date`：結束日期
  - `indicators`：技術指標（all, ma, rsi, macd, bollinger）
- **資料欄位**：包含每日股價欄位 + ma5, ma10, ma20, rsi, macd, macd_signal, macd_histogram, bb_upper, bb_middle, bb_lower

#### 3. 資料類型管理

##### 3.1 新增自定義資料類型
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

##### 3.2 參數類型支援
- **text**：文字輸入
- **number**：數字輸入（支援 min, max, step）
- **select**：下拉選單（需要提供 options）
- **date**：日期選擇器

#### 4. API 端點

##### 4.1 取得資料類型列表
```
GET /api/sample-data/types
```

##### 4.2 載入範例資料
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

##### 4.3 取得特定資料類型
```
GET /api/sample-data/types/{data_type_id}
```

##### 4.4 新增資料類型
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

##### 4.5 移除資料類型
```
DELETE /api/sample-data/types/{data_type_id}
```

### 使用方式

#### 1. 在策略編輯器中使用

1. 開啟策略編輯器頁面
2. 點擊「載入範例資料」按鈕
3. 在對話框中選擇資料類型
4. 設定相關參數
5. 點擊「載入資料」
6. 資料將以表格形式顯示在預覽區域

#### 2. 在策略程式碼中使用

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

#### 3. 新增自定義資料類型

1. 準備資料類型定義 JSON
2. 使用 API 新增資料類型
3. 重新載入策略編輯器頁面
4. 新的資料類型將出現在選擇列表中

### 技術實作

#### 1. 資料提供器 (DataProvider)

- 位置：`core/data_provider.py`
- 功能：管理資料類型定義和資料生成
- 支援：模擬資料生成、資料類型管理、檔案儲存

#### 2. 前端整合

- 策略編輯器頁面：`web/templates/strategy_editor.html`
- JavaScript 功能：資料載入、預覽顯示、參數處理
- 響應式設計：支援不同螢幕尺寸

#### 3. 後端 API

- 路由定義：`main.py`
- 資料處理：非同步處理、錯誤處理
- 快取整合：可與現有快取系統整合

### 注意事項

#### 1. 資料限制
- 預覽最多顯示 100 筆資料
- 大量資料建議分批處理
- 資料為模擬資料，僅供測試使用

#### 2. 效能考量
- 資料載入為非同步處理
- 大量資料可能影響頁面響應速度
- 建議定期清理不需要的資料

#### 3. 安全性
- 資料類型定義需要驗證
- 防止惡意程式碼注入
- 參數值需要進行類型檢查

### 未來擴展

#### 1. 資料來源擴展
- 整合真實股票 API
- 支援更多資料格式
- 新增歷史資料查詢

#### 2. 功能增強
- 資料匯出功能
- 圖表視覺化
- 資料篩選和排序

#### 3. 使用者體驗
- 拖拽式資料載入
- 資料預覽快照
- 批次資料處理

### 測試

使用提供的測試腳本驗證功能：

```bash
python test_data_preview_system.py
```

測試包含：
- 資料類型載入
- 各種資料類型測試
- 資料類型管理
- 策略編輯器整合

### 總結

資料預覽系統為策略編輯器提供了強大的資料處理能力，讓用戶可以：
- 快速載入和預覽各種資料
- 測試策略邏輯
- 管理自定義資料類型
- 提升開發效率

這個功能讓系統更接近專業的量化交易平台，提供類似 Jupyter 的互動式資料分析體驗。

## 快取系統與自定義策略功能

### 概述

本次更新新增了兩個重要功能：

1. **快取系統**：類似 Jupyter 的記憶體快取機制，避免重複請求 API
2. **自定義策略系統**：類似 XQ 的功能，讓用戶可以自行新增和編輯策略

### 快取系統 (Cache System)

#### 功能特點

- **雙層快取**：記憶體快取 + 檔案快取
- **自動管理**：記憶體不足時自動清理最舊的資料
- **TTL 機制**：可設定快取存活時間
- **統計資訊**：提供詳細的快取使用統計
- **API 整合**：與 StockAPI 無縫整合

#### 使用方式

##### 1. 基本快取操作

```python
from core.cache_manager import cache_manager

# 儲存資料到快取
success = cache_manager.set_cached_data(
    stock_id="2330",
    start_date="2024-01-01",
    end_date="2024-01-03",
    data=stock_data,
    data_type="price",
    ttl_hours=24
)

# 從快取讀取資料
cached_data = cache_manager.get_cached_data(
    stock_id="2330",
    start_date="2024-01-01",
    end_date="2024-01-03",
    data_type="price"
)
```

##### 2. 與 StockAPI 整合

```python
from api.stock_api import StockAPI

async with StockAPI() as stock_api:
    # 第一次請求會從 API 取得並快取
    data1 = await stock_api.get_stock_price(
        stock_ids=["2330"],
        start_date="2024-01-01",
        end_date="2024-01-03",
        use_cache=True  # 啟用快取
    )
    
    # 第二次請求會從快取取得（更快）
    data2 = await stock_api.get_stock_price(
        stock_ids=["2330"],
        start_date="2024-01-01",
        end_date="2024-01-03",
        use_cache=True
    )
```

##### 3. 快取管理

```python
# 取得快取資訊
info = cache_manager.get_cache_info()
print(f"記憶體使用量: {info['memory_usage_mb']} MB")
print(f"檔案快取大小: {info['file_cache_size_mb']} MB")

# 清理快取
cache_manager.clear_cache("expired")  # 清理過期快取
cache_manager.clear_cache("memory")   # 清理記憶體快取
cache_manager.clear_cache("all")      # 清理所有快取
```

#### 快取管理頁面

訪問 `/cache-manager` 可以查看：
- 記憶體使用量統計
- 快取項目詳情
- 股票代碼列表
- 快取清理功能

### 自定義策略系統 (Custom Strategy System)

#### 功能特點

- **視覺化編輯器**：網頁版策略編輯器
- **即時驗證**：語法檢查和函數檢測
- **模板系統**：提供策略模板
- **版本管理**：策略的建立、更新、刪除
- **動態載入**：程式碼字串動態編譯執行

#### 使用方式

##### 1. 策略編輯器

訪問 `/strategy-editor` 進入策略編輯器，可以：
- 建立新策略
- 編輯現有策略
- 載入策略模板
- 驗證策略程式碼
- 測試策略功能

##### 2. 策略程式碼格式

```python
# 自定義策略模板
def should_entry(stock_data, current_index):
    """
    判斷是否應該進場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        
    Returns:
        tuple: (是否進場, 進場資訊)
    """
    current_row = stock_data[current_index]
    
    # 範例：當收盤價大於開盤價時進場
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    
    return False, {}

def should_exit(stock_data, current_index, position):
    """
    判斷是否應該出場
    
    Args:
        stock_data: 股價資料 (polars DataFrame)
        current_index: 當前資料索引
        position: 當前持倉資訊
        
    Returns:
        tuple: (是否出場, 出場資訊)
    """
    current_row = stock_data[current_index]
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    # 計算持有天數
    holding_days = (current_row["date"] - stock_data[entry_index]["date"]).days
    
    # 計算虧損率
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    # 範例：持有超過5天或虧損超過5%時出場
    if holding_days >= 5 or loss_rate <= -5:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    
    return False, {}

# 可選：自定義參數配置
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
```

##### 3. API 操作

```python
from strategies.strategy_manager import StrategyManager

manager = StrategyManager()

# 建立策略
strategy_id = manager.create_strategy(
    name="我的策略",
    description="這是一個自定義策略",
    code=python_code
)

# 取得策略
strategy = manager.get_strategy(strategy_id)

# 更新策略
manager.update_strategy(
    strategy_id,
    name="更新後的策略名稱",
    code=new_code
)

# 建立策略實例
strategy_instance = manager.create_strategy_instance(strategy_id)

# 刪除策略
manager.delete_strategy(strategy_id)
```

#### 策略管理器頁面

訪問 `/strategy-editor` 可以：
- 查看所有自定義策略
- 建立新策略
- 編輯現有策略
- 載入策略模板
- 驗證和測試策略
- 匯出/匯入策略

### 檔案結構

```
trading_web_system/
├── core/
│   └── cache_manager.py          # 快取管理器
├── strategies/
│   ├── dynamic_strategy.py       # 動態策略類別
│   └── strategy_manager.py       # 策略管理器
├── web/templates/
│   ├── cache_manager.html        # 快取管理頁面
│   └── strategy_editor.html      # 策略編輯器頁面
├── data/
│   ├── cache/                    # 快取檔案目錄
│   └── strategies/               # 策略檔案目錄
├── main.py                       # 主程式（已更新）
└── test_cache_system.py          # 測試腳本
```

### 測試

執行測試腳本來驗證功能：

```bash
python test_cache_system.py
```

### 配置選項

#### 快取配置

在 `core/cache_manager.py` 中可以調整：

```python
# 快取目錄
cache_dir = "data/cache"

# 最大記憶體使用量 (MB)
max_memory_mb = 1024

# 預設快取存活時間 (小時)
ttl_hours = 24
```

#### 策略配置

在 `strategies/strategy_manager.py` 中可以調整：

```python
# 策略儲存目錄
storage_dir = "data/strategies"
```

### 注意事項

1. **安全性**：自定義策略使用 `exec()` 執行，請確保程式碼來源可信
2. **記憶體管理**：快取系統會自動管理記憶體，但建議定期清理過期快取
3. **效能**：第一次請求會較慢（需要從 API 取得），後續請求會很快（從快取取得）
4. **相容性**：策略程式碼需要符合指定的函數簽名和返回格式

### 未來改進

1. **策略市場**：允許用戶分享和下載策略
2. **策略版本控制**：支援策略的版本管理
3. **進階快取**：支援更多資料類型的快取
4. **效能優化**：進一步優化快取和策略執行效能

## Jupyter 策略分析功能

### 功能概述

Jupyter 策略分析功能允許在 Jupyter 模式下自動分析策略程式碼，判斷策略類型（狀態機/向量化/混合式），並提供詳細的分析報告。

### 問題解決

#### 1. 新增 Jupyter 策略後仍顯示舊編輯模式

**問題描述：** 新建 Jupyter 策略後，編輯器仍顯示傳統模式而非 Jupyter 模式。

**解決方案：**
- 修改 `confirmCreateStrategy` 函數，避免呼叫 `loadStrategy` 覆蓋編輯器設定
- 直接設定策略資訊並根據編輯模式初始化對應的編輯器
- 確保 Jupyter 模式正確顯示和初始化

**修改檔案：**
- `web/templates/strategy_editor.html` - 修改新建策略邏輯

#### 2. Jupyter 模式下策略類型分辨

**問題描述：** 在 Jupyter 模式下無法像傳統模式那樣分辨策略類型（狀態機/向量化/混合式）。

**解決方案：**
- 新增策略程式碼分析 API
- 透過 AST 解析分析程式碼中的關鍵函數
- 根據函數存在與否判斷策略類型

### 技術實現

#### 後端實現

##### 1. Jupyter API 擴展 (`api/jupyter_api.py`)

```python
@staticmethod
async def analyze_strategy_type(request: Request):
    """分析策略類型（狀態機/向量化/混合式）"""
    # 分析程式碼中的函數
    analysis = JupyterAPI._analyze_strategy_functions(code)
    # 根據分析結果判斷策略類型
    strategy_type = JupyterAPI._determine_strategy_type(analysis)
```

##### 2. 策略函數分析

```python
def _analyze_strategy_functions(code: str) -> Dict[str, Any]:
    """分析策略程式碼中的函數"""
    # 使用 AST 解析程式碼
    tree = ast.parse(code)
    
    # 檢查關鍵函數
    has_should_entry = False  # 狀態機函數
    has_calculate_entry_signals = False  # 向量化函數
    
    # 遍歷 AST 尋找函數定義
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            if func_name == 'should_entry':
                has_should_entry = True
            elif func_name == 'calculate_entry_signals':
                has_calculate_entry_signals = True
```

##### 3. 策略類型判斷

```python
def _determine_strategy_type(analysis: Dict[str, Any]) -> str:
    """根據分析結果判斷策略類型"""
    has_should_entry = analysis.get("has_should_entry", False)
    has_calculate_entry_signals = analysis.get("has_calculate_entry_signals", False)
    
    if has_should_entry and has_calculate_entry_signals:
        return "mixed"  # 混合式
    elif has_should_entry:
        return "state_machine"  # 狀態機
    elif has_calculate_entry_signals:
        return "vectorized"  # 向量化
    else:
        return "unknown"  # 未知類型
```

#### 前端實現

##### 1. 分析按鈕

在 Jupyter 工具列中新增「分析策略類型」按鈕：

```html
<button class="btn btn-sm btn-outline-warning" onclick="analyzeStrategyType()">
    <i class="fas fa-search"></i> 分析策略類型
</button>
```

##### 2. 分析函數

```javascript
async function analyzeStrategyType() {
    // 收集所有單元格的程式碼
    let allCode = '';
    jupyterCells.forEach(cellId => {
        const editor = jupyterCellEditors[cellId];
        if (editor) {
            allCode += editor.getValue() + '\n\n';
        }
    });
    
    // 呼叫後端 API 分析
    const response = await fetch('/api/jupyter/analyze-strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: allCode })
    });
    
    // 顯示分析結果
    const data = await response.json();
    if (data.status === 'success') {
        displayAnalysisResult(data.strategy_type, data.analysis);
    }
}
```

##### 3. 結果顯示

分析結果以新的單元格形式顯示，包含：
- 策略類型標籤
- 函數檢測狀態
- 發現的函數列表
- 詳細分析說明

### API 端點

#### 策略分析 API

**端點：** `POST /api/jupyter/analyze-strategy`

**請求格式：**
```json
{
    "code": "策略程式碼內容"
}
```

**回應格式：**
```json
{
    "status": "success",
    "strategy_type": "state_machine|vectorized|mixed|unknown",
    "analysis": {
        "has_should_entry": true/false,
        "has_calculate_entry_signals": true/false,
        "functions_found": ["函數名稱列表"],
        "description": "分析描述"
    }
}
```

### 策略類型判斷規則

#### 1. 狀態機策略 (state_machine)
- **條件：** 包含 `should_entry` 函數
- **特點：** 逐筆處理資料，維護狀態
- **適用：** 複雜邏輯、狀態追蹤

#### 2. 向量化策略 (vectorized)
- **條件：** 包含 `calculate_entry_signals` 函數
- **特點：** 一次性處理所有資料
- **適用：** 簡單邏輯、高效能

#### 3. 混合式策略 (mixed)
- **條件：** 同時包含 `should_entry` 和 `calculate_entry_signals` 函數
- **特點：** 結合兩種模式的優點
- **適用：** 複雜策略需求

#### 4. 未知類型 (unknown)
- **條件：** 不包含關鍵函數
- **特點：** 一般分析或繪圖程式碼
- **適用：** 資料分析、視覺化

### 使用流程

1. **進入 Jupyter 模式**
   - 新建策略時選擇 Jupyter 模式
   - 或切換現有策略到 Jupyter 模式

2. **編寫策略程式碼**
   - 在單元格中輸入策略程式碼
   - 可以包含多個單元格的程式碼

3. **執行分析**
   - 點擊「分析策略類型」按鈕
   - 系統自動分析所有單元格的程式碼

4. **查看結果**
   - 分析結果以新單元格形式顯示
   - 包含詳細的策略類型資訊

### 測試驗證

使用 `test_jupyter_strategy_analysis.py` 測試腳本驗證功能：

```bash
python test_jupyter_strategy_analysis.py
```

測試案例包括：
- 狀態機策略測試
- 向量化策略測試
- 混合式策略測試
- 未知類型策略測試

### 注意事項

1. **程式碼格式：** 分析功能依賴正確的 Python 語法
2. **函數命名：** 關鍵函數必須使用標準命名（`should_entry`, `calculate_entry_signals`）
3. **單元格整合：** 分析會整合所有 Jupyter 單元格的程式碼
4. **即時分析：** 每次點擊分析按鈕都會重新分析當前程式碼

### 未來擴展

1. **更多函數檢測：** 支援更多策略相關函數的檢測
2. **程式碼建議：** 根據分析結果提供程式碼改進建議
3. **效能分析：** 分析策略的計算複雜度和效能特點
4. **自動分類：** 根據策略特點自動推薦適合的策略類型

## Jupyter 策略創建功能

### 功能概述

現在策略編輯器支援兩種創建模式：
1. **傳統編輯器模式** - 完整的策略程式碼編輯
2. **Jupyter 模式** - 互動式單元格編輯

### 新增策略流程

#### 1. 選擇編輯模式

在新建策略對話框中，首先選擇編輯模式：

- **傳統編輯器**：適用於完整的策略程式碼開發
- **Jupyter 模式**：適用於互動式策略開發和資料分析

#### 2. 選擇策略類型

##### 傳統編輯器模式下的策略類型：
- **向量化模板**：效能最佳，適用於簡單邏輯
- **狀態機模板**：適用於複雜邏輯和狀態追蹤
- **混合模式模板**：包含向量化和狀態機兩種模式
- **空白策略**：從零開始建立

##### Jupyter 模式下的策略類型：
- **向量化策略**：一次性計算所有信號
- **狀態機策略**：逐筆處理，追蹤狀態
- **混合策略**：結合向量化和狀態機優勢
- **分析模式**：純資料分析，無交易邏輯

### Jupyter 策略類型詳解

#### 1. 向量化策略 (Vectorized Strategy)

**特點：**
- 一次性處理所有資料
- 使用 NumPy/Pandas 向量化運算
- 效能最佳，適合大量資料處理

**適用場景：**
- 簡單的技術指標策略
- 基於統計的量化策略
- 需要快速回測的策略

**範例功能：**
- 移動平均交叉信號
- RSI 超買超賣信號
- 布林通道突破信號
- 綜合信號生成

#### 2. 狀態機策略 (State Machine Strategy)

**特點：**
- 逐筆處理資料
- 追蹤交易狀態
- 支援複雜的進出場邏輯

**適用場景：**
- 複雜的交易邏輯
- 需要狀態追蹤的策略
- 基於事件驅動的策略

**範例功能：**
- 狀態機邏輯實作
- 進出場條件判斷
- 交易記錄追蹤
- 績效分析

#### 3. 混合策略 (Hybrid Strategy)

**特點：**
- 結合向量化和狀態機優勢
- 向量化計算技術指標
- 狀態機過濾和優化信號

**適用場景：**
- 需要複雜信號過濾的策略
- 多指標組合策略
- 需要趨勢確認的策略

**範例功能：**
- 向量化信號生成
- 狀態機信號過濾
- 多重確認機制
- 止損止盈邏輯

#### 4. 分析模式 (Analysis Mode)

**特點：**
- 純資料分析
- 無交易邏輯
- 專注於資料探索和視覺化

**適用場景：**
- 資料探索和分析
- 策略研究和開發
- 市場研究

**範例功能：**
- 基本統計分析
- 技術指標計算
- 價格走勢分析
- 報酬率分析

### 使用流程

#### 1. 創建 Jupyter 策略

1. 點擊「新建策略」按鈕
2. 選擇「Jupyter 模式」
3. 選擇策略類型（向量化/狀態機/混合/分析）
4. 輸入策略名稱和描述
5. 點擊「建立」

#### 2. 編輯 Jupyter 策略

1. 系統自動切換到 Jupyter 模式
2. 載入對應類型的範例程式碼
3. 使用單元格編輯器修改程式碼
4. 按 Shift+Enter 執行單元格
5. 按 Ctrl+Enter 執行並新增單元格

#### 3. 載入現有策略

1. 從策略列表選擇策略
2. 系統自動檢測編輯模式
3. Jupyter 策略自動切換到 Jupyter 模式
4. 傳統策略使用傳統編輯器

### 技術實現

#### 後端支援

1. **策略管理器擴展**：
   - 支援 `editor_mode` 和 `jupyter_strategy_type` 欄位
   - 根據編輯模式載入不同模板

2. **Jupyter API**：
   - `/api/jupyter/execute` - 執行程式碼
   - `/api/jupyter/sample-data` - 載入範例資料

#### 前端實現

1. **編輯模式切換**：
   - 動態顯示/隱藏策略類型選項
   - 根據選擇載入對應模板

2. **Jupyter 編輯器**：
   - 多單元格編輯
   - 即時程式碼執行
   - 多種輸出格式支援

### 注意事項

1. **模式切換**：創建後無法更改編輯模式
2. **策略類型**：Jupyter 策略類型僅影響初始模板
3. **程式碼執行**：Jupyter 模式下的程式碼在後端安全環境中執行
4. **資料載入**：支援載入範例資料進行測試

### 未來擴展

1. **更多策略類型**：支援更多專業策略模板
2. **互動式圖表**：支援 Plotly 等互動式圖表
3. **策略分享**：支援 Jupyter 筆記本匯出/匯入
4. **協作功能**：支援多人協作編輯 