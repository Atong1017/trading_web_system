#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試不同類型的策略模板
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.strategy_manager import StrategyManager

def test_template_types():
    """測試三種不同的模板類型"""
    
    # 建立策略管理器
    strategy_manager = StrategyManager()
    
    print("=" * 60)
    print("測試策略模板類型")
    print("=" * 60)
    
    # 測試混合模式模板
    print("\n1. 混合模式模板（預設）")
    print("-" * 40)
    mixed_template = strategy_manager.get_strategy_template()
    print(f"模板長度: {len(mixed_template)} 字元")
    print("包含的關鍵字:")
    print("  - calculate_entry_signals:", "calculate_entry_signals" in mixed_template)
    print("  - calculate_exit_signals:", "calculate_exit_signals" in mixed_template)
    print("  - should_entry:", "should_entry" in mixed_template)
    print("  - should_exit:", "should_exit" in mixed_template)
    print("  - use_vectorized:", "use_vectorized" in mixed_template)
    
    # 測試向量化模板
    print("\n2. 向量化模板")
    print("-" * 40)
    vectorized_template = strategy_manager.get_vectorized_template()
    print(f"模板長度: {len(vectorized_template)} 字元")
    print("包含的關鍵字:")
    print("  - calculate_entry_signals:", "calculate_entry_signals" in vectorized_template)
    print("  - calculate_exit_signals:", "calculate_exit_signals" in vectorized_template)
    print("  - should_entry:", "should_entry" in vectorized_template)
    print("  - should_exit:", "should_exit" in vectorized_template)
    print("  - use_vectorized:", "use_vectorized" in vectorized_template)
    print("  - 向量化模式特點:", "向量化模式特點" in vectorized_template)
    
    # 測試狀態機模板
    print("\n3. 狀態機模板")
    print("-" * 40)
    state_machine_template = strategy_manager.get_state_machine_template()
    print(f"模板長度: {len(state_machine_template)} 字元")
    print("包含的關鍵字:")
    print("  - calculate_entry_signals:", "calculate_entry_signals" in state_machine_template)
    print("  - calculate_exit_signals:", "calculate_exit_signals" in state_machine_template)
    print("  - should_entry:", "should_entry" in state_machine_template)
    print("  - should_exit:", "should_exit" in state_machine_template)
    print("  - use_vectorized:", "use_vectorized" in state_machine_template)
    print("  - 狀態機模式特點:", "狀態機模式特點" in state_machine_template)
    
    # 比較模板差異
    print("\n4. 模板差異分析")
    print("-" * 40)
    
    # 檢查向量化模板是否只包含向量化函數
    has_vectorized_functions = ("calculate_entry_signals" in vectorized_template and 
                               "calculate_exit_signals" in vectorized_template)
    has_state_machine_functions = ("should_entry" in vectorized_template and 
                                  "should_exit" in vectorized_template)
    
    print(f"向量化模板:")
    print(f"  - 包含向量化函數: {has_vectorized_functions}")
    print(f"  - 包含狀態機函數: {has_state_machine_functions}")
    print(f"  - 預設 use_vectorized: {'default': True in vectorized_template}")
    
    # 檢查狀態機模板是否只包含狀態機函數
    has_vectorized_functions_sm = ("calculate_entry_signals" in state_machine_template and 
                                  "calculate_exit_signals" in state_machine_template)
    has_state_machine_functions_sm = ("should_entry" in state_machine_template and 
                                     "should_exit" in state_machine_template)
    
    print(f"狀態機模板:")
    print(f"  - 包含向量化函數: {has_vectorized_functions_sm}")
    print(f"  - 包含狀態機函數: {has_state_machine_functions_sm}")
    print(f"  - 預設 use_vectorized: {'default': False in state_machine_template}")
    
    # 檢查混合模板是否包含兩種函數
    has_vectorized_functions_mixed = ("calculate_entry_signals" in mixed_template and 
                                     "calculate_exit_signals" in mixed_template)
    has_state_machine_functions_mixed = ("should_entry" in mixed_template and 
                                        "should_exit" in mixed_template)
    
    print(f"混合模板:")
    print(f"  - 包含向量化函數: {has_vectorized_functions_mixed}")
    print(f"  - 包含狀態機函數: {has_state_machine_functions_mixed}")
    print(f"  - 預設 use_vectorized: {'default': True in mixed_template}")
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_template_types() 