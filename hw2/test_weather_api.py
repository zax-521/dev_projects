import requests
import os

WEATHER_API_KEY = '56a64740ad69cec1b09a606d82d6b218'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'

def test_api_key():
    try:
        params = {
            'q': 'Moscow',
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'lang': 'ru'
        }
        
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'API密钥有效! 城市: {data.get("name")}, 温度: {data.get("main", {}).get("temp")}°C')
            return True
        else:
            print(f'API调用失败: {response.text}')
            return False
    except Exception as e:
        print(f'API测试错误: {e}')
        return False

if __name__ == '__main__':
    test_api_key()
