#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試多執行緒效能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import concurrent.futures
from functools import partial
import polars as pl
from datetime import datetime, timedelta

def simulate_stock_backtest(stock_id, delay=0.1):
    """模擬股票回測（包含延遲）"""
    print(f"開始處理股票 {stock_id}")
    time.sleep(delay)  # 模擬處理時間
    print(f"完成處理股票 {stock_id}")
    return {
        "stock_id": stock_id,
        "total_return": 0.05 + (stock_id % 10) * 0.01,
        "max_drawdown": 0.02 + (stock_id % 5) * 0.005
    }

def test_sequential_processing():
    """測試順序處理"""
    print("=== 測試順序處理 ===")
    start_time = time.time()
    
    results = []
    for i in range(10):
        result = simulate_stock_backtest(i)
        results.append(result)
    
    end_time = time.time()
    print(f"順序處理完成，耗時: {end_time - start_time:.2f} 秒")
    print(f"處理結果數量: {len(results)}")
    return end_time - start_time

def test_parallel_processing():
    """測試並行處理"""
    print("\n=== 測試並行處理 ===")
    start_time = time.time()
    
    # 準備任務
    tasks = []
    for i in range(10):
        task = partial(simulate_stock_backtest, stock_id=i)
        tasks.append(task)
    
    # 使用線程池執行
    max_workers = min(len(tasks), 5)  # 最多5個線程
    print(f"使用 {max_workers} 個線程並行處理")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任務
        future_to_task = {executor.submit(task): task for task in tasks}
        
        # 收集結果
        for future in concurrent.futures.as_completed(future_to_task):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"任務執行失敗: {e}")
    
    end_time = time.time()
    print(f"並行處理完成，耗時: {end_time - start_time:.2f} 秒")
    print(f"處理結果數量: {len(results)}")
    return end_time - start_time

def test_different_worker_counts():
    """測試不同線程數量的效能"""
    print("\n=== 測試不同線程數量的效能 ===")
    
    stock_count = 20
    delay = 0.1
    
    # 準備任務
    tasks = []
    for i in range(stock_count):
        task = partial(simulate_stock_backtest, stock_id=i, delay=delay)
        tasks.append(task)
    
    # 測試不同的線程數量
    worker_counts = [1, 2, 4, 8, 10]
    
    for max_workers in worker_counts:
        print(f"\n--- 測試 {max_workers} 個線程 ---")
        start_time = time.time()
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(task): task for task in tasks}
            
            for future in concurrent.futures.as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"任務執行失敗: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"線程數: {max_workers}, 耗時: {duration:.2f} 秒, 處理數量: {len(results)}")

def test_realistic_scenario():
    """測試真實場景"""
    print("\n=== 測試真實場景 ===")
    
    # 模擬100支股票的回測
    stock_count = 100
    delay = 0.05  # 每支股票處理50ms
    
    print(f"模擬處理 {stock_count} 支股票，每支股票處理時間 {delay*1000:.0f}ms")
    
    # 順序處理
    print("\n--- 順序處理 ---")
    start_time = time.time()
    sequential_results = []
    for i in range(stock_count):
        result = simulate_stock_backtest(i, delay)
        sequential_results.append(result)
    sequential_time = time.time() - start_time
    print(f"順序處理耗時: {sequential_time:.2f} 秒")
    
    # 並行處理
    print("\n--- 並行處理 ---")
    start_time = time.time()
    
    tasks = []
    for i in range(stock_count):
        task = partial(simulate_stock_backtest, stock_id=i, delay=delay)
        tasks.append(task)
    
    max_workers = 10
    parallel_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {executor.submit(task): task for task in tasks}
        
        for future in concurrent.futures.as_completed(future_to_task):
            try:
                result = future.result()
                parallel_results.append(result)
            except Exception as e:
                print(f"任務執行失敗: {e}")
    
    parallel_time = time.time() - start_time
    print(f"並行處理耗時: {parallel_time:.2f} 秒")
    
    # 計算效能提升
    speedup = sequential_time / parallel_time
    print(f"\n效能提升: {speedup:.2f}x")
    print(f"節省時間: {sequential_time - parallel_time:.2f} 秒")

if __name__ == "__main__":
    test_sequential_processing()
    test_parallel_processing()
    test_different_worker_counts()
    test_realistic_scenario() 