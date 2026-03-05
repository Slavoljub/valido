#!/usr/bin/env python3
"""Test Memory Optimization with Lazy Loading"""

import psutil
import os
import sys

print('🔍 Memory Usage with Lazy Loading')
print('=' * 50)

# Get initial memory
process = psutil.Process(os.getpid())
initial_memory = process.memory_info().rss / 1024 / 1024

print('.2f')
print(f'Initial Modules: {len(sys.modules)}')

# Import core components with lazy loading
imports_to_test = [
    ('Flask', 'flask'),
    ('SQLAlchemy', 'sqlalchemy'),
    ('ValidoAI Models', 'src.models.unified_models'),
    ('AI Sentiment', 'src.ai.sentiment'),
    ('Lazy Loader', 'src.core.lazy_loader'),
]

for name, module in imports_to_test:
    try:
        before = process.memory_info().rss / 1024 / 1024
        __import__(module)
        after = process.memory_info().rss / 1024 / 1024
        increase = after - before
        print("15")
    except ImportError as e:
        print("15")

final_memory = process.memory_info().rss / 1024 / 1024
total_increase = final_memory - initial_memory
print('.2f')
print(f'Final Modules: {len(sys.modules)}')

# Test lazy loading by accessing heavy modules
print('\n🔄 Testing Lazy Loading...')
try:
    from src.core.lazy_loader import get_torch, lazy_loader
    print(f'PyTorch loaded before: {lazy_loader.is_loaded("torch")}')

    before_torch = process.memory_info().rss / 1024 / 1024
    torch = get_torch()
    after_torch = process.memory_info().rss / 1024 / 1024
    torch_increase = after_torch - before_torch

    print('.2f')
    print(f'PyTorch loaded after: {lazy_loader.is_loaded("torch")}')

except Exception as e:
    print(f'Lazy loading test error: {e}')

print('\n✅ Memory optimization test completed!')
