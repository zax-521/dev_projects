#!/usr/bin/env python3
"""
测试汇率API模块
"""

import sys
sys.path.insert(0, '.')

from api.currency import get_exchange_rate

def test_currency_api():
    print("=== 汇率API测试 ===\n")
    
    # 测试USD到CNY
    print("1. USD到CNY转换测试:")
    result = get_exchange_rate('USD', 'CNY', 100)
    print(f"   汇率: 1 {result['from_currency']} = {result['exchange_rate']} {result['to_currency']}")
    print(f"   金额: {result['amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
    print(f"   来源: {result['source']}")
    
    # 测试EUR到JPY
    print("\n2. EUR到JPY转换测试:")
    result = get_exchange_rate('EUR', 'JPY', 50)
    print(f"   汇率: 1 {result['from_currency']} = {result['exchange_rate']} {result['to_currency']}")
    print(f"   金额: {result['amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
    print(f"   来源: {result['source']}")
    
    # 测试CNY到USD
    print("\n3. CNY到USD转换测试:")
    result = get_exchange_rate('CNY', 'USD', 1000)
    print(f"   汇率: 1 {result['from_currency']} = {result['exchange_rate']} {result['to_currency']}")
    print(f"   金额: {result['amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
    print(f"   来源: {result['source']}")
    
    # 测试备用方案（禁用真实API）
    print("\n4. 备用方案测试（禁用真实API）:")
    result = get_exchange_rate('USD', 'CNY', 100, use_real_api=False)
    print(f"   汇率: 1 {result['from_currency']} = {result['exchange_rate']} {result['to_currency']}")
    print(f"   金额: {result['amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
    print(f"   来源: {result['source']}")
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_currency_api()
