"""
天气API模块
提供天气预报功能
支持DeepSeek AI天气查询和传统API
"""

import requests
import os
from datetime import datetime

# 导入DeepSeek API模块
try:
    from .deepseek_api import get_weather_with_deepseek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

# 使用免费的天气API（示例使用OpenWeatherMap，需要API密钥）
# 如果没有API密钥，可以使用模拟数据
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '56a64740ad69cec1b09a606d82d6b218')
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

def get_weather(city="北京", use_deepseek=True):
    """
    获取城市天气预报
    
    Args:
        city: 城市名称
        use_deepseek: 是否使用DeepSeek AI查询（默认True）
    
    Returns:
        天气数据字典
    """
    # 优先使用DeepSeek AI查询
    if use_deepseek and DEEPSEEK_AVAILABLE and DEEPSEEK_API_KEY:
        try:
            result = get_weather_with_deepseek(city)
            if 'error' not in result or not result['error']:
                return result
        except Exception as e:
            print(f"DeepSeek天气查询失败，使用备用方案: {e}")
    
    # 如果提供了OpenWeatherMap API密钥，使用真实API
    if WEATHER_API_KEY:
        return get_real_weather(city)
    else:
        # 使用模拟数据
        return get_mock_weather(city)

def get_real_weather(city):
    """使用OpenWeatherMap API获取真实天气数据"""
    try:
        # 将中文城市名称转换为英文/俄文名称
        city_mapping = {
            '北京': 'Beijing',
            '上海': 'Shanghai',
            '广州': 'Guangzhou',
            '深圳': 'Shenzhen',
            '杭州': 'Hangzhou',
            '成都': 'Chengdu',
            '武汉': 'Wuhan',
            '南京': 'Nanjing',
            '西安': "Xi'an",
            '重庆': 'Chongqing',
            '莫斯科': 'Moscow',
            '伦敦': 'London',
            '纽约': 'New York',
            '巴黎': 'Paris',
            '东京': 'Tokyo',
            '首尔': 'Seoul',
            '柏林': 'Berlin',
            '罗马': 'Rome',
            '马德里': 'Madrid',
            '悉尼': 'Sydney'
        }
        
        # 使用映射后的城市名称，如果没有映射则使用原名称
        api_city = city_mapping.get(city, city)
        
        params = {
            'q': api_city,
            'appid': WEATHER_API_KEY,
            'units': 'metric',  # 使用摄氏度
            'lang': 'ru'        # 俄语描述
        }
        
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'city': data.get('name', city),
            'country': data.get('sys', {}).get('country', ''),
            'temperature': data.get('main', {}).get('temp', 0),
            'feels_like': data.get('main', {}).get('feels_like', 0),
            'humidity': data.get('main', {}).get('humidity', 0),
            'pressure': data.get('main', {}).get('pressure', 0),
            'weather': data.get('weather', [{}])[0].get('description', ''),
            'weather_main': data.get('weather', [{}])[0].get('main', ''),
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'wind_deg': data.get('wind', {}).get('deg', 0),
            'clouds': data.get('clouds', {}).get('all', 0),
            'visibility': data.get('visibility', 0),
            'sunrise': datetime.fromtimestamp(data.get('sys', {}).get('sunrise', 0)).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(data.get('sys', {}).get('sunset', 0)).strftime('%H:%M'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'OpenWeatherMap'
        }
    except Exception as e:
        # 如果API调用失败，返回模拟数据
        print(f"天气API调用失败: {e}")
        return get_mock_weather(city)

def get_mock_weather(city):
    """生成模拟天气数据"""
    import random
    from datetime import datetime, timedelta
    
    # 模拟不同城市的基准温度
    city_temps = {
        '北京': (25, 35),
        '上海': (28, 38),
        '广州': (30, 40),
        '深圳': (29, 39),
        '杭州': (26, 36),
        '成都': (24, 34),
        '武汉': (27, 37),
        '南京': (26, 36),
        '西安': (23, 33),
        '重庆': (28, 38)
    }
    
    # 天气类型
    weather_types = [
        {'main': 'Clear', 'description': '晴天'},
        {'main': 'Clouds', 'description': '多云'},
        {'main': 'Rain', 'description': '小雨'},
        {'main': 'Rain', 'description': '中雨'},
        {'main': 'Rain', 'description': '大雨'},
        {'main': 'Snow', 'description': '小雪'},
        {'main': 'Snow', 'description': '中雪'},
        {'main': 'Thunderstorm', 'description': '雷阵雨'},
        {'main': 'Mist', 'description': '雾'},
        {'main': 'Fog', 'description': '浓雾'}
    ]
    
    # 获取城市温度范围
    temp_range = city_temps.get(city, (20, 30))
    temp = random.uniform(temp_range[0], temp_range[1])
    
    # 选择天气类型
    weather = random.choice(weather_types)
    
    # 生成时间
    now = datetime.now()
    sunrise = (now.replace(hour=6, minute=0, second=0) + 
               timedelta(minutes=random.randint(-30, 30)))
    sunset = (now.replace(hour=18, minute=0, second=0) + 
              timedelta(minutes=random.randint(-60, 60)))
    
    return {
        'city': city,
        'country': 'CN',
        'temperature': round(temp, 1),
        'feels_like': round(temp + random.uniform(-2, 2), 1),
        'humidity': random.randint(30, 90),
        'pressure': random.randint(980, 1030),
        'weather': weather['description'],
        'weather_main': weather['main'],
        'wind_speed': round(random.uniform(0, 10), 1),
        'wind_deg': random.randint(0, 360),
        'clouds': random.randint(0, 100),
        'visibility': random.randint(1000, 10000),
        'sunrise': sunrise.strftime('%H:%M'),
        'sunset': sunset.strftime('%H:%M'),
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
        'source': '模拟数据'
    }

def get_weather_forecast(city, days=3):
    """获取多日天气预报（模拟）"""
    forecast = []
    for i in range(days):
        day_data = get_mock_weather(city)
        day_data['date'] = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        day_data['day'] = ['今天', '明天', '后天'][i] if i < 3 else f'第{i+1}天'
        forecast.append(day_data)
    
    return forecast

if __name__ == '__main__':
    # 测试代码
    print("=== 天气模块测试 ===")
    
    # 测试DeepSeek天气查询（如果可用）
    if DEEPSEEK_AVAILABLE and DEEPSEEK_API_KEY:
        print("\n1. DeepSeek天气查询测试:")
        result = get_weather("北京", use_deepseek=True)
        print(f"   城市: {result['city']}")
        print(f"   温度: {result['temperature']}°C")
        print(f"   天气: {result['weather']}")
        print(f"   来源: {result['source']}")
    else:
        print("\n1. DeepSeek天气查询: 未配置API密钥，使用备用方案")
    
    print("\n2. 传统API/模拟天气测试:")
    result = get_weather("上海", use_deepseek=False)
    print(f"   城市: {result['city']}")
    print(f"   温度: {result['temperature']}°C")
    print(f"   天气: {result['weather']}")
    print(f"   来源: {result['source']}")
