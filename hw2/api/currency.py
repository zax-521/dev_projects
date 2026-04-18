"""
汇率API模块
提供汇率转换功能
支持DeepSeek AI汇率查询和传统API
"""

import requests
import os
from datetime import datetime, timedelta

# 导入DeepSeek API模块
try:
    from .deepseek_api import get_exchange_rate_with_deepseek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

# 使用免费的汇率API
# 1. 优先使用xxapi.cn的免费API（需要密钥）
# 2. 备用：exchangerate-api.com（需要API密钥）
XXAPI_EXCHANGE_URL = "https://xxapi.cn/api/exchange"
XXAPI_KEY = os.environ.get('XXAPI_KEY', '')
EXCHANGE_API_KEY = os.environ.get('EXCHANGE_API_KEY', 'e63c66d4cb3a661597bc8456')
EXCHANGE_API_URL = "https://v6.exchangerate-api.com/v6/{}/latest/{}"

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

def get_exchange_rate(from_currency="USD", to_currency="CNY", amount=1, use_real_api=True):
    """
    获取汇率并计算转换金额
    
    Args:
        from_currency: 源货币代码
        to_currency: 目标货币代码
        amount: 金额
        use_real_api: 是否优先使用真实API（默认True）
    
    Returns:
        汇率数据字典
    """
    # 优先使用真实汇率API
    if use_real_api:
        try:
            result = get_real_exchange_rate(from_currency, to_currency, amount)
            # 检查是否成功获取到真实API数据（不是模拟数据）
            if result.get('source') != '模拟数据':
                return result
        except Exception as e:
            print(f"真实汇率API调用失败，使用备用方案: {e}")
    
    # 其次使用DeepSeek AI查询（如果配置了API密钥）
    if DEEPSEEK_AVAILABLE and DEEPSEEK_API_KEY:
        try:
            result = get_exchange_rate_with_deepseek(from_currency, to_currency, amount)
            if 'error' not in result or not result['error']:
                return result
        except Exception as e:
            print(f"DeepSeek汇率查询失败，使用模拟数据: {e}")
    
    # 最后使用模拟数据
    return get_mock_exchange_rate(from_currency, to_currency, amount)

def get_real_exchange_rate(from_currency, to_currency, amount):
    """使用真实API获取汇率数据"""
    # 首先尝试xxapi.cn的免费API（如果配置了密钥）
    if XXAPI_KEY:
        try:
            params = {
                'from': from_currency.upper(),
                'to': to_currency.upper(),
                'money': amount,
                'key': XXAPI_KEY
            }
            response = requests.get(XXAPI_EXCHANGE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 检查API返回状态
            if data.get('code') != 200:
                raise ValueError(f"API返回错误: {data.get('msg', '未知错误')}")
            
            rate = data.get('data', {}).get('rate', 0)
            converted_amount = data.get('data', {}).get('converted', 0)
            
            if rate == 0 or converted_amount == 0:
                raise ValueError("API返回的汇率数据无效")
            
            return {
                'from_currency': from_currency.upper(),
                'to_currency': to_currency.upper(),
                'amount': amount,
                'exchange_rate': round(rate, 6),
                'converted_amount': round(converted_amount, 2),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'next_update': (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'xxapi.cn汇率API'
            }
        except Exception as e:
            print(f"xxapi.cn汇率API调用失败，尝试备用API: {e}")
    
    # 如果xxapi.cn失败或未配置密钥，尝试exchangerate-api.com（如果配置了API密钥）
    if EXCHANGE_API_KEY:
        try:
            url = EXCHANGE_API_URL.format(EXCHANGE_API_KEY, from_currency.upper())
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') != 'success':
                raise ValueError(f"API返回错误: {data.get('error-type', '未知错误')}")
            
            rates = data.get('conversion_rates', {})
            rate = rates.get(to_currency.upper(), 0)
            
            if rate == 0:
                raise ValueError(f"未找到货币 {to_currency} 的汇率")
            
            converted_amount = amount * rate
            
            return {
                'from_currency': from_currency.upper(),
                'to_currency': to_currency.upper(),
                'amount': amount,
                'exchange_rate': round(rate, 6),
                'converted_amount': round(converted_amount, 2),
                'last_updated': data.get('time_last_update_utc', ''),
                'next_update': data.get('time_next_update_utc', ''),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'ExchangeRate-API'
            }
        except Exception as e:
            print(f"ExchangeRate-API调用失败: {e}")
    
    # 如果所有真实API都失败，返回模拟数据
    return get_mock_exchange_rate(from_currency, to_currency, amount)

def get_mock_exchange_rate(from_currency, to_currency, amount):
    """生成模拟汇率数据"""
    import random
    from datetime import datetime
    
    # 常见货币对的基础汇率（模拟）
    base_rates = {
        'USD_CNY': 7.25,
        'USD_EUR': 0.92,
        'USD_JPY': 150.5,
        'USD_GBP': 0.79,
        'USD_CAD': 1.36,
        'USD_AUD': 1.52,
        'USD_CHF': 0.88,
        'EUR_CNY': 7.88,
        'EUR_GBP': 0.86,
        'GBP_CNY': 9.18,
        'JPY_CNY': 0.048,
        'CAD_CNY': 5.33,
        'AUD_CNY': 4.77,
        'CHF_CNY': 8.24
    }
    
    # 标准化货币代码
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()
    
    # 尝试直接获取汇率
    key = f"{from_curr}_{to_curr}"
    if key in base_rates:
        rate = base_rates[key]
    else:
        # 尝试反向汇率
        reverse_key = f"{to_curr}_{from_curr}"
        if reverse_key in base_rates:
            rate = 1 / base_rates[reverse_key]
        else:
            # 使用USD作为中间货币计算
            if from_curr == 'USD':
                usd_to_target = base_rates.get(f"USD_{to_curr}", 1)
                rate = usd_to_target
            elif to_curr == 'USD':
                usd_from_source = base_rates.get(f"USD_{from_curr}", 1)
                rate = 1 / usd_from_source if usd_from_source != 0 else 1
            else:
                # 通过USD转换
                usd_from_source = base_rates.get(f"USD_{from_curr}", 1)
                usd_to_target = base_rates.get(f"USD_{to_curr}", 1)
                
                if usd_from_source == 0 or usd_to_target == 0:
                    # 如果找不到，使用随机汇率
                    rate = random.uniform(0.5, 10)
                else:
                    rate = usd_to_target / usd_from_source
    
    # 添加一些随机波动
    rate = rate * random.uniform(0.995, 1.005)
    converted_amount = amount * rate
    
    # 货币名称映射
    currency_names = {
        'USD': '美元',
        'CNY': '人民币',
        'EUR': '欧元',
        'JPY': '日元',
        'GBP': '英镑',
        'CAD': '加元',
        'AUD': '澳元',
        'CHF': '瑞士法郎',
        'HKD': '港币',
        'KRW': '韩元'
    }
    
    return {
        'from_currency': from_curr,
        'to_currency': to_curr,
        'from_currency_name': currency_names.get(from_curr, from_curr),
        'to_currency_name': currency_names.get(to_curr, to_curr),
        'amount': amount,
        'exchange_rate': round(rate, 6),
        'converted_amount': round(converted_amount, 2),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'next_update': (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': '模拟数据'
    }

def get_supported_currencies():
    """获取支持的货币列表"""
    return {
        'USD': {'name': '美元', 'symbol': '$'},
        'CNY': {'name': '人民币', 'symbol': '¥'},
        'EUR': {'name': '欧元', 'symbol': '€'},
        'JPY': {'name': '日元', 'symbol': '¥'},
        'GBP': {'name': '英镑', 'symbol': '£'},
        'CAD': {'name': '加元', 'symbol': 'C$'},
        'AUD': {'name': '澳元', 'symbol': 'A$'},
        'CHF': {'name': '瑞士法郎', 'symbol': 'CHF'},
        'HKD': {'name': '港币', 'symbol': 'HK$'},
        'KRW': {'name': '韩元', 'symbol': '₩'},
        'SGD': {'name': '新加坡元', 'symbol': 'S$'},
        'INR': {'name': '印度卢比', 'symbol': '₹'},
        'RUB': {'name': '俄罗斯卢布', 'symbol': '₽'},
        'BRL': {'name': '巴西雷亚尔', 'symbol': 'R$'},
        'MXN': {'name': '墨西哥比索', 'symbol': '$'}
    }

if __name__ == '__main__':
    # 测试代码
    print("=== 汇率模块测试 ===")
    
    # 检查API密钥配置
    print(f"xxapi.cn API密钥配置: {'已配置' if XXAPI_KEY else '未配置'}")
    print(f"ExchangeRate API密钥配置: {'已配置' if EXCHANGE_API_KEY else '未配置'}")
    print(f"DeepSeek API密钥配置: {'已配置' if DEEPSEEK_API_KEY else '未配置'}")
    
    # 测试真实API（如果可用）
    print("\n1. 真实汇率API测试:")
    result = get_exchange_rate("USD", "CNY", 100, use_real_api=True)
    print(f"   汇率: 1 {result['from_currency']} = {result['exchange_rate']} {result['to_currency']}")
    print(f"   金额: {result['amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
    print(f"   来源: {result['source']}")
    
    # 测试备用方案
    print("\n2. 备用方案测试:")
    result = get_exchange_rate("EUR", "JPY", 50, use_real_api=False)
    print(f"   汇率: 1 {result['from_currency']} = {result['exchange_rate']} {result['to_currency']}")
    print(f"   金额: {result['amount']} {result['from_currency']} = {result['converted_amount']} {result['to_currency']}")
    print(f"   来源: {result['source']}")
    
    # 提供配置建议
    if not XXAPI_KEY and not EXCHANGE_API_KEY:
        print("\n⚠️  建议: 要获取实时汇率，请配置以下任一API密钥:")
        print("   1. xxapi.cn API密钥: export XXAPI_KEY='your-xxapi-key'")
        print("   2. ExchangeRate-API密钥: export EXCHANGE_API_KEY='your-exchange-api-key'")
        print("   可以在相应网站注册获取免费API密钥")
