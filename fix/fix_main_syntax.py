#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 main.py 中的語法錯誤
"""

def fix_main_syntax():
    """修正 main.py 中的語法錯誤"""
    
    # 讀取檔案
    with open('main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 修正1: 移除第1395-1398行的多餘else語句
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 檢查是否是多餘的else語句 (第1395行附近)
        if (i >= 1390 and i <= 1400 and 
            line.strip() == 'else:' and 
            i + 1 < len(lines) and 
            lines[i + 1].strip().startswith('backtest_results') and
            '無法取得測試資料' in lines[i + 1]):
            
            # 跳過這個多餘的else語句和其內容
            print(f"移除第 {i+1} 行的多餘else語句")
            i += 4  # 跳過 else: 和其內容
            continue
        
        fixed_lines.append(line)
        i += 1
    
    # 寫回檔案
    with open('main.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("語法錯誤修正完成")

if __name__ == "__main__":
    fix_main_syntax() 