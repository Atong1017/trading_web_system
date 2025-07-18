#!/usr/bin/env python3
"""
修復 main.py 中的分散 import 語句
將所有 import 語句整合到檔案頂部
"""

import re

def fix_imports():
    # 讀取 main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找出所有分散的 import 語句
    import_patterns = [
        r'^\s*import traceback\s*$',
        r'^\s*import re\s*$',
        r'^\s*import pandas as pd\s*$',
        r'^\s*from io import BytesIO\s*$',
        r'^\s*import polars as pl\s*$',
        r'^\s*from strategies\.dynamic_strategy import DynamicStrategy\s*$',
        r'^\s*from datetime import datetime, timedelta\s*$',
        r'^\s*import os\s*$',
        r'^\s*import tempfile\s*$'
    ]
    
    # 移除分散的 import 語句
    for pattern in import_patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # 移除多餘的空行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # 寫回檔案
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已修復 main.py 中的分散 import 語句")

if __name__ == "__main__":
    fix_imports() 