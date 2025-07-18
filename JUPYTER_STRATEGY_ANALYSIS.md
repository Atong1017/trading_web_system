# Jupyter 策略分析功能說明

## 功能概述

Jupyter 策略分析功能允許在 Jupyter 模式下自動分析策略程式碼，判斷策略類型（狀態機/向量化/混合式），並提供詳細的分析報告。

## 問題解決

### 1. 新增 Jupyter 策略後仍顯示舊編輯模式

**問題描述：** 新建 Jupyter 策略後，編輯器仍顯示傳統模式而非 Jupyter 模式。

**解決方案：**
- 修改 `confirmCreateStrategy` 函數，避免呼叫 `loadStrategy` 覆蓋編輯器設定
- 直接設定策略資訊並根據編輯模式初始化對應的編輯器
- 確保 Jupyter 模式正確顯示和初始化

**修改檔案：**
- `web/templates/strategy_editor.html` - 修改新建策略邏輯

### 2. Jupyter 模式下策略類型分辨

**問題描述：** 在 Jupyter 模式下無法像傳統模式那樣分辨策略類型（狀態機/向量化/混合式）。

**解決方案：**
- 新增策略程式碼分析 API
- 透過 AST 解析分析程式碼中的關鍵函數
- 根據函數存在與否判斷策略類型

## 技術實現

### 後端實現

#### 1. Jupyter API 擴展 (`api/jupyter_api.py`)

```python
@staticmethod
async def analyze_strategy_type(request: Request):
    """分析策略類型（狀態機/向量化/混合式）"""
    # 分析程式碼中的函數
    analysis = JupyterAPI._analyze_strategy_functions(code)
    # 根據分析結果判斷策略類型
    strategy_type = JupyterAPI._determine_strategy_type(analysis)
```

#### 2. 策略函數分析

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

#### 3. 策略類型判斷

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

### 前端實現

#### 1. 分析按鈕

在 Jupyter 工具列中新增「分析策略類型」按鈕：

```html
<button class="btn btn-sm btn-outline-warning" onclick="analyzeStrategyType()">
    <i class="fas fa-search"></i> 分析策略類型
</button>
```

#### 2. 分析函數

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

#### 3. 結果顯示

分析結果以新的單元格形式顯示，包含：
- 策略類型標籤
- 函數檢測狀態
- 發現的函數列表
- 詳細分析說明

## API 端點

### 策略分析 API

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

## 策略類型判斷規則

### 1. 狀態機策略 (state_machine)
- **條件：** 包含 `should_entry` 函數
- **特點：** 逐筆處理資料，維護狀態
- **適用：** 複雜邏輯、狀態追蹤

### 2. 向量化策略 (vectorized)
- **條件：** 包含 `calculate_entry_signals` 函數
- **特點：** 一次性處理所有資料
- **適用：** 簡單邏輯、高效能

### 3. 混合式策略 (mixed)
- **條件：** 同時包含 `should_entry` 和 `calculate_entry_signals` 函數
- **特點：** 結合兩種模式的優點
- **適用：** 複雜策略需求

### 4. 未知類型 (unknown)
- **條件：** 不包含關鍵函數
- **特點：** 一般分析或繪圖程式碼
- **適用：** 資料分析、視覺化

## 使用流程

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

## 測試驗證

使用 `test_jupyter_strategy_analysis.py` 測試腳本驗證功能：

```bash
python test_jupyter_strategy_analysis.py
```

測試案例包括：
- 狀態機策略測試
- 向量化策略測試
- 混合式策略測試
- 未知類型策略測試

## 注意事項

1. **程式碼格式：** 分析功能依賴正確的 Python 語法
2. **函數命名：** 關鍵函數必須使用標準命名（`should_entry`, `calculate_entry_signals`）
3. **單元格整合：** 分析會整合所有 Jupyter 單元格的程式碼
4. **即時分析：** 每次點擊分析按鈕都會重新分析當前程式碼

## 未來擴展

1. **更多函數檢測：** 支援更多策略相關函數的檢測
2. **程式碼建議：** 根據分析結果提供程式碼改進建議
3. **效能分析：** 分析策略的計算複雜度和效能特點
4. **自動分類：** 根據策略特點自動推薦適合的策略類型 