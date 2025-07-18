#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的模板修復測試
"""

def test_template_fix():
    """測試模板修復效果"""
    print("=== 測試模板修復效果 ===")
    
    # 檢查 base.html
    try:
        with open('web/templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        print("✓ base.html 載入成功")
    except Exception as e:
        print(f"✗ base.html 載入失敗: {e}")
        return False
    
    # 檢查 scripts block 位置
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
    else:
        print("✗ scripts block 在 base script 之後（錯誤順序）")
        return False
    
    # 檢查 showError 函數
    if 'function showError(message)' in base_content:
        print("✓ 找到 showError 函數")
    else:
        print("✗ 缺少 showError 函數")
        return False
    
    # 檢查 backtest.html
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
    
    print("\n🎉 模板修復成功！")
    return True

if __name__ == "__main__":
    success = test_template_fix()
    if not success:
        print("\n❌ 模板修復失敗，請檢查問題。")
        exit(1)
    else:
        print("\n✅ 所有測試通過！") 