import requests
import json

def test_all_features():
    print("=== 最终测试 - 所有功能 ===\n")
    
    # 1. 测试天气API - 实时数据
    print("1. 测试天气API (实时数据):")
    response = requests.post('http://localhost:5000/api/weather', 
                           json={'city': 'Moscow'},
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            weather = data['data']
            print(f"   ✅ 成功获取莫斯科天气")
            print(f"     来源: {weather['source']}")
            print(f"     温度: {weather['temperature']}°C")
            print(f"     天气: {weather['weather']}")
            print(f"     湿度: {weather['humidity']}%")
        else:
            print(f"   ❌ 失败: {data.get('error')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 2. 测试货币转换API
    print("\n2. 测试货币转换API:")
    response = requests.post('http://localhost:5000/api/currency', 
                           json={'from': 'USD', 'to': 'RUB', 'amount': 100},
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            currency = data['data']
            print(f"   ✅ 成功转换货币")
            print(f"     100 USD = {currency.get('converted_amount', 'N/A')} RUB")
            print(f"     汇率: {currency.get('rate', 'N/A')}")
        else:
            print(f"   ❌ 失败: {data.get('error')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 3. 测试翻译API
    print("\n3. 测试翻译API:")
    response = requests.post('http://localhost:5000/api/translate', 
                           json={'text': 'Hello, how are you?', 'source': 'en', 'target': 'ru'},
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            translation = data['data']
            print(f"   ✅ 成功翻译")
            print(f"     原文: {translation.get('original_text', 'N/A')}")
            print(f"     译文: {translation.get('translated_text', 'N/A')}")
        else:
            print(f"   ❌ 失败: {data.get('error')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 4. 测试计算器API
    print("\n4. 测试计算器API:")
    response = requests.post('http://localhost:5000/api/calculate', 
                           json={'expression': '2+3*4'},
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"   ✅ 成功计算")
            print(f"     表达式: 2+3*4")
            print(f"     结果: {data.get('result', 'N/A')}")
        else:
            print(f"   ❌ 失败: {data.get('error')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 5. 测试单位转换API
    print("\n5. 测试单位转换API:")
    response = requests.post('http://localhost:5000/api/convert-units', 
                           json={'value': 1000, 'from_unit': 'meter', 'to_unit': 'kilometer', 'category': 'length'},
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            conversion = data['data']
            print(f"   ✅ 成功转换单位")
            print(f"     1000 米 = {conversion.get('converted_value', 'N/A')} 公里")
        else:
            print(f"   ❌ 失败: {data.get('error')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 6. 测试历史记录API
    print("\n6. 测试历史记录API:")
    response = requests.get('http://localhost:5000/api/history')
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            history = data['history']
            print(f"   ✅ 成功获取历史记录")
            print(f"     记录数量: {len(history)}")
            if len(history) > 0:
                print(f"     最新记录: {history[0].get('operation_type', 'N/A')}")
        else:
            print(f"   ❌ 失败: {data.get('error')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_all_features()
