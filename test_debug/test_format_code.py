#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試程式碼格式化功能
"""

import requests
import json

def test_format_code():
    """測試程式碼格式化 API"""
    
    # 測試用的未格式化程式碼
    test_code = '''def calculate_signals(data):
    signals=[]
    for i in range(len(data)):
        if i<20:
            signals.append(0)
        else:
            sma_20=sum(data[i-20:i])/20
            if data[i]>sma_20:
                signals.append(1)
            else:
                signals.append(-1)
    return signals'''
    
    print("原始程式碼:")
    print(test_code)
    print("\n" + "="*50 + "\n")
    
    try:
        # 調用格式化 API
        response = requests.post(
            'http://localhost:8000/api/strategies/custom/format',
            headers={'Content-Type': 'application/json'},
            json={'code': test_code}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("API 回應:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result['status'] == 'success':
                print("\n格式化後的程式碼:")
                print(result['formatted_code'])
            else:
                print(f"格式化失敗: {result['message']}")
        else:
            print(f"API 請求失敗: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("無法連接到伺服器，請確保 FastAPI 服務正在運行")
    except Exception as e:
        print(f"測試失敗: {e}")

def test_black_direct():
    """直接測試 black 格式化功能"""
    try:
        import black
        
        test_code = '''def calculate_signals(data):
    signals=[]
    for i in range(len(data)):
        if i<20:
            signals.append(0)
        else:
            sma_20=sum(data[i-20:i])/20
            if data[i]>sma_20:
                signals.append(1)
            else:
                signals.append(-1)
    return signals'''
        
        print("直接使用 black 格式化:")
        mode = black.FileMode(
            target_versions={black.TargetVersion.PY37},
            line_length=88,
            string_normalization=True,
            is_pyi=False,
        )
        
        formatted_code = black.format_str(test_code, mode=mode)
        print(formatted_code)
        
    except ImportError:
        print("black 模組未安裝")
    except Exception as e:
        print(f"black 格式化失敗: {e}")

if __name__ == "__main__":
    print("測試程式碼格式化功能")
    print("="*50)
    
    print("\n1. 測試 black 直接格式化:")
    test_black_direct()
    
    print("\n" + "="*50)
    print("\n2. 測試 API 格式化:")
    test_format_code() 