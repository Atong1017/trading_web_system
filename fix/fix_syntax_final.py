#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 main.py 中的語法錯誤
"""

def fix_syntax_errors():
    """修正 main.py 中的語法錯誤"""
    
    # 讀取檔案
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正1: 移除多餘的 else 語句
    # 找到連續的 else: 語句並移除第二個
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 檢查是否是多餘的 else 語句
        if (line.strip() == 'else:' and 
            i + 1 < len(lines) and 
            lines[i + 1].strip().startswith('backtest_results') and
            '無法取得測試資料' in lines[i + 1] and
            i > 0 and lines[i - 1].strip() == '}'):
            
            # 檢查前一個 else 是否也是處理 backtest_results
            j = i - 1
            while j >= 0 and lines[j].strip() != 'else:':
                j -= 1
            
            if j >= 0 and lines[j].strip() == 'else:':
                # 這是多餘的 else，跳過它
                print(f"移除第 {i+1} 行的多餘else語句")
                i += 4  # 跳過 else: 和其內容
                continue
        
        fixed_lines.append(line)
        i += 1
    
    # 寫回檔案
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("語法錯誤修正完成")

if __name__ == "__main__":
    fix_syntax_errors() 