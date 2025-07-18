#!/usr/bin/env python3
"""
全面修復 stock_data.row() 調用問題
將所有 stock_data.row(index) 改為 stock_data.row(index, named=True)
"""

import os
import re
import glob

def fix_file(file_path):
    """修復單個檔案"""
    print(f"檢查檔案: {file_path}")
    
    try:
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
            
    except Exception as e:
        print(f"  ❌ 修復失敗: {e}")
        return False

def main():
    """主函數"""
    # 需要檢查的目錄
    directories = [
        "data/strategies",
        "strategies", 
        "test_debug"
    ]
    
    print("開始全面修復 stock_data.row() 調用問題")
    print("=" * 60)
    
    total_fixed = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"目錄不存在: {directory}")
            continue
            
        print(f"\n檢查目錄: {directory}")
        print("-" * 40)
        
        # 取得所有 .py 檔案
        py_files = glob.glob(os.path.join(directory, "*.py"))
        
        if not py_files:
            print("  沒有找到 .py 檔案")
            continue
            
        print(f"  找到 {len(py_files)} 個 .py 檔案")
        
        for file_path in py_files:
            if fix_file(file_path):
                total_fixed += 1
    
    print("\n" + "=" * 60)
    print(f"修復完成！共修復了 {total_fixed} 個檔案")
    
    # 最後檢查是否還有遺漏
    print("\n檢查是否還有遺漏...")
    remaining = []
    
    for directory in directories:
        if os.path.exists(directory):
            py_files = glob.glob(os.path.join(directory, "*.py"))
            for file_path in py_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 檢查是否還有沒修復的
                    pattern = r'stock_data\.row\(([^)]+)\)'
                    matches = re.findall(pattern, content)
                    
                    for match in matches:
                        if 'named=True' not in match:
                            remaining.append(f"{file_path}: {match}")
                            
                except Exception:
                    pass
    
    if remaining:
        print(f"⚠️  發現 {len(remaining)} 個可能遺漏的地方:")
        for item in remaining[:10]:  # 只顯示前10個
            print(f"  {item}")
        if len(remaining) > 10:
            print(f"  ... 還有 {len(remaining) - 10} 個")
    else:
        print("✅ 沒有發現遺漏")

if __name__ == "__main__":
    main() 