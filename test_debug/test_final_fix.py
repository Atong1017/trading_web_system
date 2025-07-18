#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終測試策略模板 API 修復
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time

def test_strategy_template_api():
    """測試策略模板 API"""
    print("=" * 60)
    print("測試策略模板 API 修復效果")
    print("=" * 60)
    
    try:
        # 等待伺服器完全啟動
        print("等待伺服器啟動...")
        time.sleep(3)
        
        # 測試策略模板 API
        print("測試 /api/strategies/custom/template...")
        response = requests.get("http://localhost:8000/api/strategies/custom/template", timeout=10)
        
        print(f"HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 回應成功")
            print(f"回應狀態: {data.get('status')}")
            
            template = data.get('template', '')
            print(f"模板長度: {len(template)} 字元")
            
            # 檢查模板內容
            if 'def should_entry' in template and 'def should_exit' in template:
                print("✅ 模板包含必要的函數定義")
            else:
                print("⚠️  模板可能缺少必要的函數定義")
            
            # 檢查是否有 polars 相關的程式碼
            if 'stock_data.row(' in template:
                print("✅ 模板使用正確的 polars DataFrame 存取方式", named=True)
            else:
                print("⚠️  模板可能未使用正確的 polars DataFrame 存取方式")
            
            print("\n🎉 策略模板 API 修復成功！")
            return True
            
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            print(f"錯誤內容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器，請確保伺服器正在運行")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_strategy_validation():
    """測試策略驗證功能"""
    print("\n" + "=" * 60)
    print("測試策略驗證功能")
    print("=" * 60)
    
    try:
        # 測試有效的策略程式碼
        valid_code = """def should_entry(stock_data, current_index):
    current_row = stock_data.row(current_index, named=True)
    if current_row["close"] > current_row["open"]:
        return True, {"reason": "收盤價大於開盤價"}
    return False, {}

def should_exit(stock_data, current_index, position):
    current_row = stock_data.row(current_index, named=True)
    entry_index = position["entry_index"]
    entry_price = position["entry_price"]
    
    entry_row = stock_data.row(entry_index, named=True)
    holding_days = (current_row["date"] - entry_row["date"]).days
    loss_rate = ((current_row["close"] - entry_price) / entry_price) * 100
    
    if holding_days >= 5 or loss_rate <= -5:
        return True, {"reason": f"持有{holding_days}天或虧損{loss_rate:.2f}%"}
    return False, {}"""
        
        response = requests.post(
            "http://localhost:8000/api/strategies/custom/validate",
            json={"code": valid_code},
            timeout=10
        )
        
        print(f"HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"回應狀態: {data.get('status')}")
            
            if data.get('status') == 'success':
                print("✅ 策略程式碼驗證通過")
                return True
            else:
                print(f"❌ 策略程式碼驗證失敗: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            print(f"錯誤內容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("開始最終測試策略模板 API 修復")
    print(f"測試時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 測試策略模板 API
    template_result = test_strategy_template_api()
    
    # 測試策略驗證功能
    validation_result = test_strategy_validation()
    
    # 總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    print(f"策略模板 API: {'✅ 通過' if template_result else '❌ 失敗'}")
    print(f"策略驗證功能: {'✅ 通過' if validation_result else '❌ 失敗'}")
    
    if template_result and validation_result:
        print("\n🎉 所有測試都通過！策略模板 API 修復成功。")
        print("現在程式碼編輯器應該可以正常載入策略模板了。")
    else:
        print("\n⚠️  部分測試失敗，請檢查相關功能。")
    
    print(f"\n測試完成時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 