import requests
import json

def test_real_weather():
    print("=== 测试实时天气数据 ===")
    
    # 测试莫斯科的天气
    test_cases = [
        {"city": "Moscow", "expected": "OpenWeatherMap"},
        {"city": "London", "expected": "OpenWeatherMap"},
        {"city": "北京", "expected": "OpenWeatherMap"},  # 应该被映射到Beijing
        {"city": "莫斯科", "expected": "OpenWeatherMap"},  # 应该被映射到Moscow
    ]
    
    for test in test_cases:
        print(f"\n测试城市: {test['city']}")
        try:
            response = requests.post('http://localhost:5000/api/weather', 
                                   json={'city': test['city']},
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    weather_data = data['data']
                    print(f"  状态: 成功")
                    print(f"  来源: {weather_data.get('source', '未知')}")
                    print(f"  城市: {weather_data.get('city', '未知')}")
                    print(f"  温度: {weather_data.get('temperature', '未知')}°C")
                    print(f"  天气: {weather_data.get('weather', '未知')}")
                    
                    if weather_data.get('source') == test['expected']:
                        print(f"  ✅ 来源正确: {weather_data['source']}")
                    else:
                        print(f"  ⚠️  来源不正确: {weather_data.get('source')} (期望: {test['expected']})")
                else:
                    print(f"  状态: 失败 - {data.get('error', '未知错误')}")
            else:
                print(f"  状态: HTTP错误 {response.status_code}")
                
        except Exception as e:
            print(f"  错误: {e}")

if __name__ == '__main__':
    test_real_weather()
