#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試快取刪除功能
"""

import requests
import json
import time

def test_cache_delete():
    """測試快取刪除功能"""
    try:
        print("=" * 60)
        print("測試快取刪除功能")
        print("=" * 60)
        
        # 1. 先取得快取資訊
        print("\n1. 取得快取資訊...")
        response = requests.get('http://localhost:8000/api/cache/info', timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 取得快取資訊失敗: {response.status_code}")
            return False
        
        data = response.json()
        if data.get('status') != 'success':
            print(f"❌ API返回錯誤: {data}")
            return False
        
        cache_info = data.get('info', {})
        cache_metadata = cache_info.get('cache_metadata', {})
        
        if not cache_metadata:
            print("⚠️  沒有快取項目可供測試")
            return True
        
        print(f"✅ 找到 {len(cache_metadata)} 個快取項目")
        
        # 2. 選擇第一個快取項目進行刪除測試
        cache_keys = list(cache_metadata.keys())
        test_cache_key = cache_keys[0]
        
        print(f"\n2. 測試刪除快取項目: {test_cache_key}")
        print(f"   快取項目資訊: {cache_metadata[test_cache_key]}")
        
        # 3. 執行刪除
        print("\n3. 執行刪除操作...")
        response = requests.delete(f'http://localhost:8000/api/cache/remove/{test_cache_key}', timeout=10)
        
        print(f"   狀態碼: {response.status_code}")
        print(f"   回應內容: {response.text}")
        
        if response.status_code != 200:
            print(f"❌ 刪除失敗: {response.status_code}")
            return False
        
        delete_data = response.json()
        if delete_data.get('status') != 'success':
            print(f"❌ 刪除API返回錯誤: {delete_data}")
            return False
        
        print("✅ 刪除操作成功")
        
        # 4. 驗證刪除結果
        print("\n4. 驗證刪除結果...")
        time.sleep(1)  # 等待一下確保操作完成
        
        response = requests.get('http://localhost:8000/api/cache/info', timeout=10)
        if response.status_code != 200:
            print(f"❌ 重新取得快取資訊失敗: {response.status_code}")
            return False
        
        data = response.json()
        if data.get('status') != 'success':
            print(f"❌ API返回錯誤: {data}")
            return False
        
        new_cache_info = data.get('info', {})
        new_cache_metadata = new_cache_info.get('cache_metadata', {})
        
        if test_cache_key in new_cache_metadata:
            print(f"❌ 快取項目仍然存在: {test_cache_key}")
            return False
        
        print(f"✅ 快取項目已成功刪除，剩餘 {len(new_cache_metadata)} 個項目")
        
        print("\n" + "=" * 60)
        print("✅ 快取刪除功能測試成功！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    test_cache_delete() 