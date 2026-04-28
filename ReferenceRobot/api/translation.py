"""
翻译API模块
提供单词和文本翻译功能
支持DeepSeek AI翻译和传统API
"""

import os
import requests
import re

# 导入DeepSeek API模块
try:
    from .deepseek_api import translate_with_deepseek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

# 使用免费的翻译API
# 1. LibreTranslate (免费开源翻译API)
LIBRETRANSLATE_URL = "https://libretranslate.com/translate"
# 2. MyMemory Translation API (免费，有限制)
MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

def detect_language(text):
    """检测文本语言"""
    # 简单的语言检测
    # 中文检测
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    
    # 日语检测
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return 'ja'
    
    # 韩语检测
    if re.search(r'[\uac00-\ud7af]', text):
        return 'ko'
    
    # 俄语检测
    if re.search(r'[\u0400-\u04FF]', text):
        return 'ru'
    
    # 默认英语
    return 'en'

def get_libretranslate_translation(text, source_lang, target_lang):
    """使用LibreTranslate API获取翻译"""
    # 如果源语言是auto，尝试检测
    if source_lang == 'auto':
        source_lang = detect_language(text)
    
    # LibreTranslate支持的语言代码映射
    libre_lang_map = {
        'zh': 'zh', 'en': 'en', 'ja': 'ja', 'ko': 'ko',
        'fr': 'fr', 'de': 'de', 'es': 'es', 'ru': 'ru',
        'pt': 'pt', 'it': 'it', 'ar': 'ar', 'hi': 'hi'
    }
    
    source = libre_lang_map.get(source_lang, 'en')
    target = libre_lang_map.get(target_lang, 'en')
    
    if source not in libre_lang_map.values() or target not in libre_lang_map.values():
        raise ValueError(f"LibreTranslate不支持的语言: {source_lang}->{target_lang}")
    
    payload = {
        'q': text,
        'source': source,
        'target': target,
        'format': 'text'
    }
    
    response = requests.post(LIBRETRANSLATE_URL, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if 'error' in data:
        raise ValueError(f"LibreTranslate错误: {data['error']}")
    
    return {
        'original_text': text,
        'translated_text': data.get('translatedText', ''),
        'source_lang': source_lang,
        'target_lang': target_lang,
        'source': 'LibreTranslate'
    }

def get_mymemory_translation(text, source_lang, target_lang):
    """使用MyMemory API获取翻译"""
    # MyMemory支持的语言代码
    mymemory_lang_map = {
        'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko',
        'fr': 'fr', 'de': 'de', 'es': 'es', 'ru': 'ru',
        'pt': 'pt', 'it': 'it', 'ar': 'ar', 'hi': 'hi'
    }
    
    source = mymemory_lang_map.get(source_lang, 'en')
    target = mymemory_lang_map.get(target_lang, 'en')
    
    params = {
        'q': text,
        'langpair': f'{source}|{target}',
        'de': 'user@example.com'  # 可选的电子邮件地址
    }
    
    response = requests.get(MYMEMORY_API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if data.get('responseStatus') != 200:
        raise ValueError(f"MyMemory错误: {data.get('responseDetails', '未知错误')}")
    
    translated_text = data.get('responseData', {}).get('translatedText', '')
    
    # 如果没有翻译结果，使用模拟数据
    if not translated_text or translated_text == text:
        raise ValueError("MyMemory返回空翻译")
    
    return {
        'original_text': text,
        'translated_text': translated_text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'source': 'MyMemory'
    }

def get_free_translation(text, source_lang, target_lang):
    """使用免费翻译API获取真实翻译"""
    try:
        # 首先尝试LibreTranslate
        try:
            return get_libretranslate_translation(text, source_lang, target_lang)
        except Exception as e1:
            print(f"LibreTranslate失败: {e1}")
            # 如果LibreTranslate失败，尝试MyMemory
            try:
                return get_mymemory_translation(text, source_lang, target_lang)
            except Exception as e2:
                print(f"MyMemory失败: {e2}")
                raise Exception(f"所有免费翻译API都失败: {e1}, {e2}")
    except Exception as e:
        raise Exception(f"免费翻译API调用失败: {e}")

def get_mock_translation(text, source_lang, target_lang):
    """生成模拟翻译数据"""
    # 常见单词和短语的模拟翻译
    mock_dictionary = {
        'en': {
            'ru': {
                'hello': 'привет',
                'world': 'мир',
                'good morning': 'доброе утро',
                'thank you': 'спасибо',
                'how are you': 'как дела',
                'weather': 'погода',
                'currency': 'валюта',
                'translation': 'перевод',
                'calculator': 'калькулятор',
                'unit converter': 'конвертер единиц',
                'reference robot': 'справочный робот',
                'artificial intelligence': 'искусственный интеллект',
                'machine learning': 'машинное обучение',
                'programming': 'программирование',
                'software development': 'разработка программного обеспечения'
            },
            'zh': {
                'hello': '你好',
                'world': '世界',
                'good morning': '早上好',
                'thank you': '谢谢',
                'how are you': '你好吗',
            }
        },
        'ru': {
            'en': {
                'привет': 'hello',
                'мир': 'world',
                'доброе утро': 'good morning',
                'спасибо': 'thank you',
                'как дела': 'how are you',
                'погода': 'weather',
                'валюта': 'currency',
                'перевод': 'translation',
                'калькулятор': 'calculator'
            }
        },
        'zh': {
            'en': {
                '你好': 'hello',
                '世界': 'world',
                '早上好': 'good morning',
                '谢谢': 'thank you',
                '天气': 'weather',
                '货币': 'currency',
                '翻译': 'translation',
                '计算器': 'calculator',
                '单位转换器': 'unit converter'
            },
            'ru': {
                '你好': 'привет',
                '世界': 'мир',
                '谢谢': 'спасибо',
                '天气': 'погода',
                '翻译': 'перевод'
            }
        }
    }
    
    # 标准化语言代码
    source = source_lang.lower()[:2]
    target = target_lang.lower()[:2]
    
    # 尝试获取精确匹配
    if (source in mock_dictionary and 
        target in mock_dictionary[source] and
        text.lower() in mock_dictionary[source][target]):
        
        translated = mock_dictionary[source][target][text.lower()]
    else:
        # 生成模拟翻译
        if source == 'en' and target == 'ru':
            # 英译俄模拟
            translated = f"{text} (перевод на русский)"
        elif source == 'ru' and target == 'en':
            # 俄译英模拟
            translated = f"{text} (translation to English)"
        elif source == 'en' and target == 'zh':
            # 英译中模拟
            translated = f"{text}的翻译"
        elif source == 'zh' and target == 'en':
            # 中译英模拟
            translated = f"translation of {text}"
        else:
            # 通用模拟
            translated = f"[{source.upper()}→{target.upper()}] {text}"
    
    return {
        'original_text': text,
        'translated_text': translated,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'source': '模拟翻译'
    }

def translate_text(text, source_lang="auto", target_lang="ru", use_deepseek=True):
    """
    翻译文本
    
    Args:
        text: 要翻译的文本
        source_lang: 源语言代码（auto表示自动检测）
        target_lang: 目标语言代码
        use_deepseek: 是否使用DeepSeek AI翻译（默认True）
    
    Returns:
        翻译结果字典
    """
    # 优先使用DeepSeek AI翻译
    if use_deepseek and DEEPSEEK_AVAILABLE and DEEPSEEK_API_KEY:
        try:
            result = translate_with_deepseek(text, source_lang, target_lang)
            if 'error' not in result or not result['error']:
                return result
        except Exception as e:
            print(f"DeepSeek翻译失败，使用备用方案: {e}")
    
    # 尝试使用免费翻译API
    try:
        return get_free_translation(text, source_lang, target_lang)
    except Exception as e:
        print(f"免费翻译API失败，使用模拟数据: {e}")
        # 使用模拟数据
        return get_mock_translation(text, source_lang, target_lang)

def get_supported_languages():
    """获取支持的语言列表"""
    return {
        'auto': '自动检测',
        'zh': '中文',
        'en': '英语',
        'ja': '日语',
        'ko': '韩语',
        'fr': '法语',
        'de': '德语',
        'es': '西班牙语',
        'ru': '俄语',
        'pt': '葡萄牙语',
        'it': '意大利语',
        'ar': '阿拉伯语',
        'hi': '印地语'
    }

if __name__ == '__main__':
    # 测试代码
    print("=== 翻译模块测试 ===")
    
    # 测试DeepSeek翻译（如果可用）
    if DEEPSEEK_AVAILABLE and DEEPSEEK_API_KEY:
        print("\n1. DeepSeek翻译测试:")
        result = translate_text("hello world", "en", "ru", use_deepseek=True)
        print(f"   原文: {result['original_text']}")
        print(f"   翻译: {result['translated_text']}")
        print(f"   来源: {result['source']}")
    else:
        print("\n1. DeepSeek翻译: 未配置API密钥，使用备用方案")
    
    print("\n2. 免费API翻译测试:")
    result = translate_text("hello world", "en", "ru", use_deepseek=False)
    print(f"   原文: {result['original_text']}")
    print(f"   翻译: {result['translated_text']}")
    print(f"   来源: {result['source']}")
    
    print("\n3. 中译俄测试:")
    result = translate_text("你好", "zh", "ru")
    print(f"   原文: {result['original_text']}")
    print(f"   翻译: {result['translated_text']}")
    print(f"   来源: {result['source']}")
