#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統啟動腳本
"""

import uvicorn
import os
import sys

def main():
    """主函數"""
    print("台灣股票回測+自動下單系統")
    print("=" * 50)
    
    # 檢查必要目錄
    directories = [
        "data/uploads",
        "data/exports",
        "web/static/css",
        "web/static/js",
        "web/static/images"
    ]
    
    for directory in directories:
        # 確保路徑使用正斜線
        directory = directory.replace('\\', '/')
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"創建目錄: {directory}")
    
    # 設定主機和埠號
    host = "0.0.0.0"
    port = 8000
    
    print(f"啟動伺服器: http://{host}:{port}")
    print("使用單 worker 模式以確保 Jupyter 變數共享功能正常")
    print("按 Ctrl+C 停止伺服器")
    print("=" * 50)
    
    try:
        # 啟動FastAPI應用，使用單 worker 確保變數共享
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info",
            workers=1  # 使用單 worker 避免多進程變數共享問題
        )
    except KeyboardInterrupt:
        print("\n伺服器已停止")
    except Exception as e:
        print(f"啟動失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 