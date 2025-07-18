import requests
import json

def test_cache_api():
    try:
        # 測試快取檔案API
        response = requests.get('http://localhost:8000/api/cache/files')
        # print(f"Status Code: {response.status_code}")
        # print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Parsed JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('status') == 'success':
                files = data.get('data', {}).get('files', [])
                print(f"Found {len(files)} cache files")
                for file_info in files:
                    if file_info.get('friendly_display_name') == 'price_multiple_20221112_20230630':
                        print(f"  - {file_info.get('friendly_display_name', 'Unknown')} ({file_info.get('size_mb', 0)}MB)")
            else:
                print("API returned error status")
        else:
            print(f"HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cache_api() 