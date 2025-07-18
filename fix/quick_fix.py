#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修正 main.py 中的語法錯誤
"""

import re

def quick_fix():
    """快速修正語法錯誤"""
    
    # 讀取檔案
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正多餘的 else 語句
    pattern = r'else:\s*\n\s*backtest_results\s*=\s*\{\s*\n\s*"message":\s*"無法取得測試資料"\s*\n\s*\}'
    content = re.sub(pattern, '', content)
    
    # 寫回檔案
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("快速修正完成")

if __name__ == "__main__":
    quick_fix() 