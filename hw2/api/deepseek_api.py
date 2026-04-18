"""
DeepSeek API集成模块
提供AI驱动的翻译、问答和其他功能
"""

import os
import requests
import json
from typing import Dict, Any, Optional

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(
    messages: list,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Dict[str, Any]:
    """
    调用DeepSeek API
    
    Args:
        messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大token数
    
    Returns:
        API响应字典
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API密钥未设置，请设置DEEPSEEK_API_KEY环境变量")
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"DeepSeek API调用失败: {e}")

def translate_with_deepseek(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "zh",
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用DeepSeek API进行翻译
    
    Args:
        text: 要翻译的文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
        context: 上下文信息（可选）
    
    Returns:
        翻译结果字典
    """
    # 语言代码映射
    language_names = {
        "zh": "中文",
        "en": "英语",
        "ja": "日语",
        "ko": "韩语",
        "fr": "法语",
        "de": "德语",
        "es": "西班牙语",
        "ru": "俄语",
        "pt": "葡萄牙语",
        "it": "意大利语",
        "ar": "阿拉伯语",
        "hi": "印地语"
    }
    
    source_name = language_names.get(source_lang, source_lang)
    target_name = language_names.get(target_lang, target_lang)
    
    # 构建提示词
    if source_lang == "auto":
        prompt = f"请将以下文本翻译成{target_name}：\n\n{text}"
    else:
        prompt = f"请将以下{source_name}文本翻译成{target_name}：\n\n{text}"
    
    if context:
        prompt += f"\n\n上下文：{context}"
    
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的翻译助手，能够准确翻译各种语言的文本。请只返回翻译结果，不要添加额外解释。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    try:
        response = call_deepseek_api(messages, temperature=0.3, max_tokens=1000)
        
        # 提取翻译结果
        translated_text = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        return {
            'original_text': text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'source': 'DeepSeek AI',
            'model': response.get("model", "deepseek-chat"),
            'usage': response.get("usage", {})
        }
    except Exception as e:
        # 如果API调用失败，返回错误信息
        return {
            'original_text': text,
            'translated_text': f"翻译失败: {str(e)}",
            'source_lang': source_lang,
            'target_lang': target_lang,
            'source': 'DeepSeek AI (错误)',
            'error': str(e)
        }

def get_weather_with_deepseek(city: str) -> Dict[str, Any]:
    """
    使用DeepSeek API获取天气信息（模拟真实天气查询）
    
    Args:
        city: 城市名称
    
    Returns:
        天气数据字典
    """
    prompt = f"""请提供{city}的当前天气信息，包括：
1. 温度（摄氏度）
2. 天气状况（如晴天、多云、下雨等）
3. 湿度百分比
4. 风速
5. 体感温度

请以JSON格式返回，包含以下字段：
- city: 城市名称
- temperature: 温度（数字）
- weather: 天气状况描述
- humidity: 湿度百分比（数字）
- wind_speed: 风速（数字，单位：米/秒）
- feels_like: 体感温度（数字）
- description: 详细描述
- source: "DeepSeek AI天气模拟"
"""
    
    messages = [
        {
            "role": "system",
            "content": "你是一个天气信息助手，能够根据常识提供合理的天气信息。请返回准确的JSON格式数据。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    try:
        response = call_deepseek_api(messages, temperature=0.5, max_tokens=500)
        
        # 提取JSON响应
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # 尝试解析JSON
        try:
            weather_data = json.loads(content)
        except json.JSONDecodeError:
            # 如果不是JSON，创建模拟数据
            weather_data = {
                'city': city,
                'temperature': 25.0,
                'weather': '晴天',
                'humidity': 65,
                'wind_speed': 3.5,
                'feels_like': 26.0,
                'description': f'{city}当前天气晴朗，温度适宜',
                'source': 'DeepSeek AI天气模拟'
            }
        
        # 添加额外字段
        from datetime import datetime
        weather_data.update({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'country': 'CN',
            'pressure': 1013,
            'clouds': 20,
            'visibility': 10000
        })
        
        return weather_data
    except Exception as e:
        # 如果API调用失败，返回模拟数据
        from datetime import datetime
        return {
            'city': city,
            'temperature': 22.5,
            'weather': '多云',
            'humidity': 70,
            'wind_speed': 2.5,
            'feels_like': 23.0,
            'description': f'{city}天气信息获取失败，使用模拟数据',
            'source': 'DeepSeek AI (模拟)',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'country': 'CN',
            'pressure': 1013,
            'clouds': 20,
            'visibility': 10000,
            'error': str(e)
        }

def get_exchange_rate_with_deepseek(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0
) -> Dict[str, Any]:
    """
    使用DeepSeek API获取汇率信息
    
    Args:
        from_currency: 源货币代码
        to_currency: 目标货币代码
        amount: 金额
    
    Returns:
        汇率数据字典
    """
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
        'RUB': '俄罗斯卢布'
    }
    
    from_name = currency_names.get(from_currency.upper(), from_currency)
    to_name = currency_names.get(to_currency.upper(), to_currency)
    
    prompt = f"""请提供{from_name}({from_currency})到{to_name}({to_currency})的当前汇率。
如果{amount} {from_currency}可以兑换多少{to_currency}？

请以JSON格式返回，包含以下字段：
- from_currency: 源货币代码
- to_currency: 目标货币代码
- exchange_rate: 汇率（数字）
- converted_amount: 转换后的金额（数字）
- description: 简要描述
- source: "DeepSeek AI汇率模拟"
"""
    
    messages = [
        {
            "role": "system",
            "content": "你是一个金融信息助手，能够根据常识提供合理的汇率信息。请返回准确的JSON格式数据。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    try:
        response = call_deepseek_api(messages, temperature=0.3, max_tokens=500)
        
        # 提取JSON响应
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # 尝试解析JSON
        try:
            exchange_data = json.loads(content)
        except json.JSONDecodeError:
            # 如果不是JSON，创建模拟数据
            import random
            base_rate = 7.25 if from_currency.upper() == 'USD' and to_currency.upper() == 'CNY' else 1.0
            rate = base_rate * random.uniform(0.95, 1.05)
            
            exchange_data = {
                'from_currency': from_currency.upper(),
                'to_currency': to_currency.upper(),
                'exchange_rate': round(rate, 4),
                'converted_amount': round(amount * rate, 2),
                'description': f'{from_currency}到{to_currency}的汇率模拟数据',
                'source': 'DeepSeek AI汇率模拟'
            }
        
        # 添加额外字段
        from datetime import datetime
        exchange_data.update({
            'amount': amount,
            'from_currency_name': currency_names.get(from_currency.upper(), from_currency),
            'to_currency_name': currency_names.get(to_currency.upper(), to_currency),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return exchange_data
    except Exception as e:
        # 如果API调用失败，返回模拟数据
        import random
        from datetime import datetime
        
        base_rate = 7.25 if from_currency.upper() == 'USD' and to_currency.upper() == 'CNY' else 1.0
        rate = base_rate * random.uniform(0.95, 1.05)
        
        return {
            'from_currency': from_currency.upper(),
            'to_currency': to_currency.upper(),
            'from_currency_name': currency_names.get(from_currency.upper(), from_currency),
            'to_currency_name': currency_names.get(to_currency.upper(), to_currency),
            'amount': amount,
            'exchange_rate': round(rate, 4),
            'converted_amount': round(amount * rate, 2),
            'description': f'{from_currency}到{to_currency}的汇率信息',
            'source': 'DeepSeek AI (模拟)',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }

def ask_deepseek_question(question: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    向DeepSeek提问
    
    Args:
        question: 问题
        context: 上下文信息（可选）
    
    Returns:
        回答字典
    """
    messages = []
    
    if context:
        messages.append({
            "role": "system",
            "content": f"上下文信息：{context}\n\n请根据以上上下文回答问题。"
        })
    
    messages.append({
        "role": "user",
        "content": question
    })
    
    try:
        response = call_deepseek_api(messages, temperature=0.7, max_tokens=2000)
        
        answer = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        return {
            'question': question,
            'answer': answer,
            'source': 'DeepSeek AI',
            'model': response.get("model", "deepseek-chat"),
            'usage': response.get("usage", {})
        }
    except Exception as e:
        return {
            'question': question,
            'answer': f"抱歉，无法回答这个问题：{str(e)}",
            'source': 'DeepSeek AI (错误)',
            'error': str(e)
        }

if __name__ == '__main__':
    # 测试代码
    print("=== DeepSeek API模块测试 ===")
    
    # 测试翻译功能（模拟，因为没有API密钥）
    print("\n1. 翻译测试（模拟）:")
    result = translate_with_deepseek("hello world", "en", "zh")
    print(f"   原文: {result['original_text']}")
    print(f"   翻译: {result['translated_text']}")
    print(f"   来源: {result['source']}")
    
    print("\n2. 天气查询测试（模拟）:")
    weather = get_weather_with_deepseek("北京")
    print(f"   城市: {weather['city']}")
    print(f"   温度: {weather['temperature']}°C")
    print(f"   天气: {weather['weather']}")
    
    print("\n3. 汇率查询测试（模拟）:")
    exchange = get_exchange_rate_with_deepseek("USD", "CNY", 100)
    print(f"   汇率: 1 {exchange['from_currency']} = {exchange['exchange_rate']} {exchange['to_currency']}")
    print(f"   金额: {exchange['amount']} {exchange['from_currency']} = {exchange['converted_amount']} {exchange['to_currency']}")
    
    print("\n注意：需要设置DEEPSEEK_API_KEY环境变量才能使用真实API。")
