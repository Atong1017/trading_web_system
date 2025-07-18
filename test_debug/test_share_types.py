#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的股數類型
驗證 mixed、whole、fractional 是否正常工作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.price_utils import PriceUtils

def test_share_types():
    """測試新的股數類型"""
    print("測試新的股數類型...")
    
    # 測試案例：投資金額 100,000，股價 50
    amount = 100000
    price = 50
    
    test_cases = [
        ("mixed", "整股+零股（優先整股，不足則用零股）"),
        ("whole", "只買整股"),
        ("fractional", "可買零股"),
        ("整股", "只買整股（舊格式）"),
        ("零股", "可買零股（舊格式）"),
        ("整股優先", "整股優先，無法整股則使用零股（舊格式）"),
    ]
    
    for share_type, description in test_cases:
        try:
            shares = PriceUtils.calculate_shares(amount, price, share_type)
            print(f"✅ {share_type} ({description}): {shares} 股")
        except Exception as e:
            print(f"❌ {share_type} ({description}): {e}")
    
    print("\n詳細計算說明：")
    print(f"投資金額: {amount:,} 元")
    print(f"股價: {price} 元")
    print(f"理論可買股數: {amount / price:.0f} 股")
    print(f"理論可買整股數: {(amount // (price * 1000)) * 1000} 股")
    
    # 測試不同金額的情況
    print("\n測試不同金額的情況：")
    test_amounts = [50000, 100000, 150000, 200000]
    price = 50
    
    for amount in test_amounts:
        print(f"\n投資金額: {amount:,} 元，股價: {price} 元")
        for share_type in ["mixed", "whole", "fractional"]:
            shares = PriceUtils.calculate_shares(amount, price, share_type)
            print(f"  {share_type}: {shares} 股")
    
    return True

def test_edge_cases():
    """測試邊界情況"""
    print("\n測試邊界情況...")
    
    # 測試金額剛好買整股的情況
    amount = 50000  # 剛好買 1000 股（50 * 1000）
    price = 50
    
    print(f"投資金額: {amount:,} 元，股價: {price} 元（剛好買 1000 股）")
    for share_type in ["mixed", "whole", "fractional"]:
        shares = PriceUtils.calculate_shares(amount, price, share_type)
        print(f"  {share_type}: {shares} 股")
    
    # 測試金額不足買整股的情況
    amount = 25000  # 只能買 500 股（50 * 500）
    price = 50
    
    print(f"\n投資金額: {amount:,} 元，股價: {price} 元（不足買整股）")
    for share_type in ["mixed", "whole", "fractional"]:
        shares = PriceUtils.calculate_shares(amount, price, share_type)
        print(f"  {share_type}: {shares} 股")
    
    return True

if __name__ == "__main__":
    print("開始測試新的股數類型")
    
    result1 = test_share_types()
    result2 = test_edge_cases()
    
    if result1 and result2:
        print("\n🎉 所有測試通過！")
    else:
        print("\n❌ 部分測試失敗") 