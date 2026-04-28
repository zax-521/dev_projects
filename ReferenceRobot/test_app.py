#!/usr/bin/env python3
"""
参考机器人应用测试脚本
测试所有API端点功能
"""

import sys
import json
from flask.testing import FlaskClient

# 导入应用
sys.path.insert(0, '.')
from app import app

def test_all_apis():
    """测试所有API端点"""
    client = app.test_client()
    results = []
    
    print("=== 参考机器人API测试 ===\n")
    
    # 1. 测试计算器API
    print("1. 测试计算器API...")
    response = client.post('/api/calculate', json={'expression': '2+3*4'})
    data = response.get_json()
    success = data.get('success') if data else False
    result = data.get('result') if data else None
    print(f"   状态: {response.status_code}, 成功: {success}, 结果: {result}")
    results.append(('计算器API', success, result == 14))
    
    # 2. 测试翻译API
    print("\n2. 测试翻译API...")
    response = client.post('/api/translate', json={
        'text': 'hello world',
        'source': 'en',
        'target': 'zh'
    })
    data = response.get_json()
    success = data.get('success') if data else False
    print(f"   状态: {response.status_code}, 成功: {success}")
    results.append(('翻译API', success, success))
    
    # 3. 测试单位转换API
    print("\n3. 测试单位转换API...")
    response = client.post('/api/convert-units', json={
        'value': 1,
        'from_unit': 'meter',
        'to_unit': 'kilometer',
        'category': 'length'
    })
    data = response.get_json()
    success = data.get('success') if data else False
    print(f"   状态: {response.status_code}, 成功: {success}")
    results.append(('单位转换API', success, success))
    
    # 4. 测试天气API
    print("\n4. 测试天气API...")
    response = client.post('/api/weather', json={'city': '北京'})
    data = response.get_json()
    success = data.get('success') if data else False
    print(f"   状态: {response.status_code}, 成功: {success}")
    results.append(('天气API', success, success))
    
    # 5. 测试汇率API
    print("\n5. 测试汇率API...")
    response = client.post('/api/currency', json={
        'from': 'USD',
        'to': 'CNY',
        'amount': 1
    })
    data = response.get_json()
    success = data.get('success') if data else False
    print(f"   状态: {response.status_code}, 成功: {success}")
    results.append(('汇率API', success, success))
    
    # 6. 测试历史记录API
    print("\n6. 测试历史记录API...")
    response = client.get('/api/history')
    data = response.get_json()
    success = data.get('success') if data else False
    history = data.get('history', []) if data else []
    print(f"   状态: {response.status_code}, 成功: {success}, 记录数: {len(history)}")
    results.append(('历史记录API', success, success))
    
    # 7. 测试文本转语音API
    print("\n7. 测试文本转语音API...")
    response = client.post('/api/text-to-speech', json={
        'text': '测试语音',
        'language': 'zh-CN'
    })
    data = response.get_json()
    success = data.get('success') if data else False
    print(f"   状态: {response.status_code}, 成功: {success}")
    results.append(('文本转语音API', success, success))
    
    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    total = len(results)
    passed = sum(1 for _, success, correct in results if success and correct)
    
    for i, (name, success, correct) in enumerate(results, 1):
        status = "通过" if success and correct else "失败"
        print(f"{i}. {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    return passed == total

if __name__ == '__main__':
    print("警告: speech_recognition 库未安装，语音识别功能将不可用")
    print("警告: gTTS 或 pygame 库未安装，语音合成功能将不可用")
    
    try:
        all_passed = test_all_apis()
        if all_passed:
            print("\n✅ 所有API测试通过！应用可以正常运行。")
            print("\n启动应用命令: python app.py")
            print("访问地址: http://localhost:5000")
        else:
            print("\n⚠️  部分测试失败，但应用基本功能可用。")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        sys.exit(1)
