#!/usr/bin/env python3
"""
DeepSeek API集成测试脚本
测试所有集成了DeepSeek API的功能模块
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, '.')

def test_deepseek_modules():
    """测试所有集成了DeepSeek的模块"""
    print("=== DeepSeek API集成测试 ===\n")
    
    # 检查环境变量
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')
    if not deepseek_key:
        print("⚠️  警告: DEEPSEEK_API_KEY环境变量未设置")
        print("   将使用模拟数据或备用API进行测试\n")
    
    # 测试翻译模块
    print("1. 测试翻译模块:")
    try:
        from api.translation import translate_text, DEEPSEEK_AVAILABLE
        print(f"   DeepSeek可用: {DEEPSEEK_AVAILABLE}")
        
        # 测试翻译
        result = translate_text("hello world", "en", "zh", use_deepseek=True)
        print(f"   原文: {result['original_text']}")
        print(f"   翻译: {result['translated_text']}")
        print(f"   来源: {result['source']}")
        print(f"   成功: {'error' not in result or not result.get('error')}")
    except Exception as e:
        print(f"   翻译模块测试失败: {e}")
    
    # 测试天气模块
    print("\n2. 测试天气模块:")
    try:
        from api.weather import get_weather, DEEPSEEK_AVAILABLE
        print(f"   DeepSeek可用: {DEEPSEEK_AVAILABLE}")
        
        # 测试天气查询
        result = get_weather("北京", use_deepseek=True)
        print(f"   城市: {result['city']}")
        print(f"   温度: {result['temperature']}°C")
        print(f"   天气: {result['weather']}")
        print(f"   来源: {result['source']}")
        print(f"   成功: {'error' not in result or not result.get('error')}")
    except Exception as e:
        print(f"   天气模块测试失败: {e}")
    
    # 测试汇率模块
    print("\n3. 测试汇率模块:")
    try:
        from api.currency import get_exchange_rate, DEEPSEEK_AVAILABLE
        print(f"   DeepSeek可用: {DEEPSEEK_AVAILABLE}")
        
        # 测试汇率查询
        result = get_exchange_rate("USD", "CNY", 100, use_deepseek=True)
        print(f"   汇率: 1 {result['from_currency']} = {result['exchange_rate']} {result['to_currency']}")
        print(f"   金额: {result['amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
        print(f"   来源: {result['source']}")
        print(f"   成功: {'error' not in result or not result.get('error')}")
    except Exception as e:
        print(f"   汇率模块测试失败: {e}")
    
    # 测试DeepSeek问答模块
    print("\n4. 测试DeepSeek问答模块:")
    try:
        from api.deepseek_api import ask_deepseek_question
        print("   DeepSeek问答模块可用")
        
        # 测试简单问题
        result = ask_deepseek_question("什么是人工智能？")
        print(f"   问题: {result['question']}")
        print(f"   回答长度: {len(result['answer'])} 字符")
        print(f"   来源: {result['source']}")
        print(f"   成功: {'error' not in result or not result.get('error')}")
    except Exception as e:
        print(f"   DeepSeek问答模块测试失败: {e}")
    
    print("\n=== 测试完成 ===")
    
    # 提供配置说明
    print("\n配置说明:")
    print("1. 要使用真实的DeepSeek API，请设置DEEPSEEK_API_KEY环境变量")
    print("2. 可以在DeepSeek官网注册并获取API密钥")
    print("3. 设置方法: export DEEPSEEK_API_KEY='your-api-key-here'")
    print("4. 或者创建.env文件并添加: DEEPSEEK_API_KEY=your-api-key-here")
    print("\n如果没有API密钥，系统将自动使用模拟数据或备用API")

if __name__ == '__main__':
    test_deepseek_modules()
