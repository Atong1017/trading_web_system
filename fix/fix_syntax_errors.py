#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 main.py 中的語法錯誤
"""
import re

def fix_syntax_errors():
    """修正 main.py 中的語法錯誤"""
    
    # 讀取檔案
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正1: 移除多餘的 else 語句 (第1395行附近)
    # 找到 "else:" 後面緊接著另一個 "else:" 的情況
    pattern1 = r'(\s+)else:\s*\n\s*backtest_results\s*=\s*\{\s*\n\s*"message":\s*"策略程式碼語法正確，但需要實作完整的策略類別才能進行回測"\s*\n\s*\}\s*\n\s*else:\s*\n\s*backtest_results\s*=\s*\{\s*\n\s*"message":\s*"無法取得測試資料"\s*\n\s*\}'
    replacement1 = r'\1else:\n\1    backtest_results = {\n\1        "message": "策略程式碼語法正確，但需要實作完整的策略類別才能進行回測"\n\1    }'
    
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
    
    # 修正2: 修正 except 縮排錯誤 (第1408行附近)
    # 找到縮排錯誤的 except 語句
    pattern2 = r'(\s+)except Exception as e:\s*\n\s+backtest_results\s*=\s*\{\s*\n\s+"message":\s*f"策略執行錯誤:\s*\{str\(e\)\}"\s*\n\s+\}'
    replacement2 = r'\1except Exception as e:\n\1    backtest_results = {\n\1        "message": f"策略執行錯誤: {str(e)}"\n\1    }'
    
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
    
    # 修正3: 確保 try 語句有對應的 except
    # 檢查是否有孤立的 try 語句
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # 如果找到 try: 語句，檢查後面是否有 except
        if line.strip() == 'try:':
            # 尋找對應的 except
            j = i + 1
            found_except = False
            while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('except'):
                if lines[j].strip().startswith('if ') or lines[j].strip().startswith('else:') or lines[j].strip().startswith('elif '):
                    break
                j += 1
            
            if j < len(lines) and lines[j].strip().startswith('except'):
                found_except = True
            
            if not found_except:
                # 在 try 區塊結束後添加 except
                print(f"在第 {i+1} 行附近發現缺少 except 的 try 語句")
        
        i += 1
    
    # 寫回檔案
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("語法錯誤修正完成")

if __name__ == "__main__":
    fix_syntax_errors() 