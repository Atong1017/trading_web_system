# 快取系統與自定義策略功能說明

## 概述

本次更新新增了兩個重要功能：

1. **快取系統**：類似 Jupyter 的記憶體快取機制，避免重複請求 API
2. **自定義策略系統**：類似 XQ 的功能，讓用戶可以自行新增和編輯策略

## 快取系統 (Cache System)

### 功能特點

- **雙層快取**：記憶體快取 + 檔案快取
- **自動管理**：記憶體不足時自動清理最舊的資料
- **TTL 機制**：可設定快取存活時間
- **統計資訊**：提供詳細的快取使用統計
- **API 整合**：與 StockAPI 無縫整合

### 使用方式

#### 1. 基本快取操作

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

#### 2. 與 StockAPI 整合

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

#### 3. 快取管理

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

### 快取管理頁面

訪問 `/cache-manager` 可以查看：
- 記憶體使用量統計
- 快取項目詳情
- 股票代碼列表
- 快取清理功能

## 自定義策略系統 (Custom Strategy System)

### 功能特點

- **視覺化編輯器**：網頁版策略編輯器
- **即時驗證**：語法檢查和函數檢測
- **模板系統**：提供策略模板
- **版本管理**：策略的建立、更新、刪除
- **動態載入**：程式碼字串動態編譯執行

### 使用方式

#### 1. 策略編輯器

訪問 `/strategy-editor` 進入策略編輯器，可以：
- 建立新策略
- 編輯現有策略
- 載入策略模板
- 驗證策略程式碼
- 測試策略功能

#### 2. 策略程式碼格式

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

#### 3. API 操作

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

### 策略管理器頁面

訪問 `/strategy-editor` 可以：
- 查看所有自定義策略
- 建立新策略
- 編輯現有策略
- 載入策略模板
- 驗證和測試策略
- 匯出/匯入策略

## 檔案結構

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

## 測試

執行測試腳本來驗證功能：

```bash
python test_cache_system.py
```

## 配置選項

### 快取配置

在 `core/cache_manager.py` 中可以調整：

```python
# 快取目錄
cache_dir = "data/cache"

# 最大記憶體使用量 (MB)
max_memory_mb = 1024

# 預設快取存活時間 (小時)
ttl_hours = 24
```

### 策略配置

在 `strategies/strategy_manager.py` 中可以調整：

```python
# 策略儲存目錄
storage_dir = "data/strategies"
```

## 注意事項

1. **安全性**：自定義策略使用 `exec()` 執行，請確保程式碼來源可信
2. **記憶體管理**：快取系統會自動管理記憶體，但建議定期清理過期快取
3. **效能**：第一次請求會較慢（需要從 API 取得），後續請求會很快（從快取取得）
4. **相容性**：策略程式碼需要符合指定的函數簽名和返回格式

## 未來改進

1. **策略市場**：允許用戶分享和下載策略
2. **策略版本控制**：支援策略的版本管理
3. **進階快取**：支援更多資料類型的快取
4. **效能優化**：進一步優化快取和策略執行效能 