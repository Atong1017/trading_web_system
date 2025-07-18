# 程式碼編輯器功能說明

## 概述

策略編輯器現在整合了專業的程式碼編輯器功能，基於 CodeMirror 5.65.2 實現，提供類似 Python IDE 的開發體驗。編輯器支援語法高亮、自動縮排、程式碼提示、搜尋替換等專業功能。

## 主要功能

### 1. 語法高亮
- **Python 語法支援**：完整的 Python 語法高亮
- **多主題選擇**：支援 Eclipse、Monokai、Dracula 等主題
- **即時高亮**：輸入時即時顯示語法高亮

### 2. 自動縮排
- **智能縮排**：輸入 `:` 後按 Enter 自動增加縮排
- **Tab 鍵支援**：Tab 鍵插入 4 個空格
- **選區縮排**：選中多行可批量縮排
- **自動對齊**：括號、引號自動配對

### 3. 程式碼提示
- **自動完成**：Ctrl+Space 觸發自動完成
- **函數提示**：顯示函數參數和說明
- **變數提示**：智能變數名稱建議

### 4. 程式碼摺疊
- **區塊摺疊**：可摺疊函數、類別、註解區塊
- **行號顯示**：顯示行號便於定位
- **摺疊指示器**：視覺化摺疊狀態

### 5. 搜尋與替換
- **快速搜尋**：Ctrl+F 開啟搜尋
- **替換功能**：Ctrl+H 開啟替換
- **跳轉行號**：快速跳轉到指定行

### 6. 程式碼格式化
- **一鍵格式化**：自動調整縮排和空行
- **語法檢查**：檢查括號配對和基本語法
- **程式碼清理**：移除多餘空格和空行

### 7. 全螢幕編輯
- **全螢幕模式**：專注程式碼編輯
- **快速切換**：一鍵進入/退出全螢幕
- **自適應大小**：自動調整編輯器大小

## 技術架構

### 前端技術
- **CodeMirror 5.65.2**：專業程式碼編輯器
- **Python Mode**：Python 語法支援
- **多種 Addon**：功能擴展模組

### 編輯器配置
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

### 快捷鍵設定
- **Tab**：插入縮排或選區縮排
- **Enter**：智能換行和縮排
- **Ctrl+Space**：觸發自動完成
- **Ctrl+F**：開啟搜尋
- **Ctrl+H**：開啟替換
- **Ctrl+/**：註解/取消註解

## 使用方式

### 1. 基本編輯
1. 進入策略編輯器頁面
2. 程式碼編輯器會自動載入預設模板
3. 開始輸入程式碼，享受語法高亮和自動縮排

### 2. 自動縮排範例
```python
# 輸入以下程式碼時會自動縮排
if a == 1:  # 輸入 : 後按 Enter
    print("a is 1")  # 自動縮排 4 個空格
    if b == 2:  # 再次縮排
        print("b is 2")  # 再縮排 4 個空格
```

### 3. 程式碼格式化
1. 點擊「格式化」按鈕
2. 系統自動調整縮排和空行
3. 檢查並修正基本語法問題

### 4. 語法驗證
1. 點擊「驗證語法」按鈕
2. 系統檢查括號配對和縮排
3. 顯示驗證結果和錯誤訊息

### 5. 全螢幕編輯
1. 點擊「全螢幕」按鈕
2. 編輯器進入全螢幕模式
3. 專注於程式碼編輯
4. 點擊「退出全螢幕」返回

## 程式碼模板

### 預設策略模板
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

## 編輯器主題

### 可用主題
1. **Eclipse**：淺色主題，適合日間使用
2. **Monokai**：深色主題，適合夜間使用
3. **Dracula**：深色主題，現代化設計

### 主題切換
- 可在編輯器設定中切換主題
- 主題設定會自動保存
- 支援自定義主題

## 程式碼驗證

### 驗證項目
1. **括號配對**：檢查 `()`, `[]`, `{}` 配對
2. **縮排檢查**：檢查 Python 縮排規則
3. **基本語法**：檢查常見語法錯誤
4. **程式碼結構**：檢查類別和函數定義

### 錯誤提示
- 即時顯示錯誤位置
- 提供錯誤說明和建議
- 支援錯誤快速修復

## 效能優化

### 編輯器效能
- **虛擬化渲染**：只渲染可見區域
- **延遲載入**：按需載入功能模組
- **記憶體管理**：自動清理未使用資源

### 大型檔案支援
- **分頁載入**：支援大型程式碼檔案
- **增量更新**：只更新變更的部分
- **背景處理**：非阻塞式語法檢查

## 自定義設定

### 編輯器偏好設定
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

### 快捷鍵自定義
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

## 錯誤處理

### 常見問題
1. **編輯器無法載入**：檢查網路連線和 CDN 資源
2. **語法高亮異常**：重新整理頁面或清除快取
3. **自動縮排失效**：檢查編輯器設定
4. **程式碼驗證錯誤**：檢查 Python 語法

### 故障排除
- 檢查瀏覽器控制台錯誤訊息
- 確認 CodeMirror 資源載入成功
- 驗證編輯器初始化狀態
- 檢查 JavaScript 錯誤

## 未來擴展

### 計劃功能
1. **智能程式碼補全**：基於上下文的補全
2. **程式碼片段**：預設程式碼片段
3. **即時錯誤檢查**：輸入時即時檢查
4. **程式碼重構**：自動重構工具
5. **版本控制整合**：Git 整合功能

### 進階功能
1. **多檔案編輯**：支援多個策略檔案
2. **程式碼導航**：函數和類別導航
3. **程式碼摺疊**：更智能的摺疊邏輯
4. **主題自定義**：自定義編輯器主題
5. **外掛系統**：可擴展的外掛架構

## 測試

### 執行測試
```bash
python test_code_editor_features.py
```

### 測試項目
1. 程式碼編輯器頁面載入
2. 程式碼編輯器 API 功能
3. 程式碼驗證功能
4. 策略建立和編輯
5. 程式碼編輯器特色功能
6. 編輯器整合功能

### 測試結果
- 所有測試通過表示功能正常
- 失敗的測試會顯示詳細錯誤訊息
- 測試報告包含通過率和詳細結果

## 技術支援

### 開發文件
- [CodeMirror 官方文件](https://codemirror.net/doc/manual.html)
- [Python Mode 文件](https://codemirror.net/mode/python/)
- [編輯器 API 參考](https://codemirror.net/doc/manual.html#api)

### 問題回報
如有問題或建議，請：
1. 檢查瀏覽器控制台錯誤
2. 查看系統日誌檔案
3. 執行測試腳本驗證功能
4. 提供詳細的錯誤訊息和重現步驟

---

*最後更新：2024年12月* 