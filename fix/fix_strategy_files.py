#!/usr/bin/env python3
"""
批量修復策略檔案中的 stock_data.row() 調用
將 stock_data.row(index) 改為 stock_data.row(index, named=True)
"""

import os
import re
import glob

def fix_strategy_file(file_path):
    """修復單個策略檔案"""
    print(f"修復檔案: {file_path}")
    
    # 讀取檔案內容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正則表達式修復 stock_data.row() 調用
    # 匹配 stock_data.row(something) 但不包含 named=True
    pattern = r'stock_data\.row\(([^)]+)\)'
    
    def replace_func(match):
        args = match.group(1)
        # 如果已經有 named=True，就不修改
        if 'named=True' in args:
            return match.group(0)
        # 否則加上 named=True
        return f'stock_data.row({args}, named=True)'
    
    new_content = re.sub(pattern, replace_func, content)
    
    # 如果內容有變化，寫回檔案
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ 已修復")
        return True
    else:
        print(f"  ⏭️  無需修復")
        return False

def main():
    """主函數"""
    # 策略檔案目錄
    strategy_dir = "data/strategies"
    
    print(f"當前工作目錄: {os.getcwd()}")
    print(f"策略目錄是否存在: {os.path.exists(strategy_dir)}")
    
    # 取得所有 .py 檔案
    py_files = glob.glob(os.path.join(strategy_dir, "*.py"))
    
    print(f"找到 {len(py_files)} 個策略檔案")
    for file_path in py_files:
        print(f"  - {file_path}")
    
    print("=" * 50)
    
    fixed_count = 0
    for file_path in py_files:
        if fix_strategy_file(file_path):
            fixed_count += 1
    
    print("=" * 50)
    print(f"修復完成！共修復了 {fixed_count} 個檔案")

if __name__ == "__main__":
    main() 