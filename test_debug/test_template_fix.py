#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試模板修復效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string
import json

def test_template_rendering():
    """測試模板渲染是否正常"""
    print("=== 測試模板渲染 ===")
    
    # 測試 base.html 是否正常
    try:
        with open('web/templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        print("✓ base.html 載入成功")
    except Exception as e:
        print(f"✗ base.html 載入失敗: {e}")
        return False
    
    # 測試回測頁面是否正常
    try:
        with open('web/templates/backtest.html', 'r', encoding='utf-8') as f:
            backtest_content = f.read()
        print("✓ backtest.html 載入成功")
    except Exception as e:
        print(f"✗ backtest.html 載入失敗: {e}")
        return False
    
    # 檢查 block 結構
    if '{% block scripts %}' in backtest_content:
        print("✓ backtest.html 有 scripts block")
    else:
        print("✗ backtest.html 缺少 scripts block")
        return False
    
    if '{% block extra_js %}' in backtest_content:
        print("✗ backtest.html 仍有 extra_js block（應該已移除）")
        return False
    else:
        print("✓ backtest.html 已移除 extra_js block")
    
    # 檢查 base.html 的 block 結構
    if '{% block scripts %}{% endblock %}' in base_content:
        print("✓ base.html 有正確的 scripts block")
    else:
        print("✗ base.html 缺少 scripts block")
        return False
    
    return True

def test_strategy_editor_template():
    """測試策略編輯器模板"""
    print("\n=== 測試策略編輯器模板 ===")
    
    try:
        with open('web/templates/strategy_editor.html', 'r', encoding='utf-8') as f:
            editor_content = f.read()
        print("✓ strategy_editor.html 載入成功")
    except Exception as e:
        print(f"✗ strategy_editor.html 載入失敗: {e}")
        return False
    
    # 檢查 block 結構
    if '{% block scripts %}' in editor_content:
        print("✓ strategy_editor.html 有 scripts block")
    else:
        print("✗ strategy_editor.html 缺少 scripts block")
        return False
    
    return True

def test_javascript_functions():
    """測試 JavaScript 函數是否正確定義"""
    print("\n=== 測試 JavaScript 函數 ===")
    
    try:
        with open('web/templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
    except Exception as e:
        print(f"✗ 無法載入 base.html: {e}")
        return False
    
    # 檢查關鍵函數
    required_functions = [
        'showLoading',
        'hideLoading', 
        'showMessage',
        'showError',
        'formatNumber',
        'formatPercentage',
        'formatDate',
        'selectStrategy',
        'loadStrategyParameters',
        'displayParameters',
        'getParameters',
        'plotChart'
    ]
    
    missing_functions = []
    for func in required_functions:
        if func in base_content:
            print(f"✓ 找到函數: {func}")
        else:
            print(f"✗ 缺少函數: {func}")
            missing_functions.append(func)
    
    if missing_functions:
        print(f"警告: 缺少 {len(missing_functions)} 個函數")
        return False
    
    return True

def test_block_order():
    """測試 block 順序是否正確"""
    print("\n=== 測試 Block 順序 ===")
    
    try:
        with open('web/templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
    except Exception as e:
        print(f"✗ 無法載入 base.html: {e}")
        return False
    
    # 檢查 scripts block 是否在正確位置
    lines = base_content.split('\n')
    scripts_block_line = None
    base_script_start = None
    
    for i, line in enumerate(lines):
        if '{% block scripts %}{% endblock %}' in line:
            scripts_block_line = i
        if '// 全域變數' in line:
            base_script_start = i
    
    if scripts_block_line is None:
        print("✗ 找不到 scripts block")
        return False
    
    if base_script_start is None:
        print("✗ 找不到 base script 開始位置")
        return False
    
    if scripts_block_line < base_script_start:
        print("✓ scripts block 在 base script 之前（正確順序）")
        return True
    else:
        print("✗ scripts block 在 base script 之後（錯誤順序）")
        return False

def main():
    """主測試函數"""
    print("開始測試模板修復效果...\n")
    
    tests = [
        test_template_rendering,
        test_strategy_editor_template,
        test_javascript_functions,
        test_block_order
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"測試失敗: {e}\n")
    
    print(f"=== 測試結果 ===")
    print(f"通過: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有測試通過！模板修復成功。")
        return True
    else:
        print("❌ 部分測試失敗，請檢查問題。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 