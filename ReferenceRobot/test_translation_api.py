import requests
import json

def test_translation_api():
    print("测试翻译API返回实时数据...")
    
    # 测试英译俄
    test_cases = [
        {"text": "Hello, how are you?", "source": "en", "target": "ru", "desc": "英译俄"},
        {"text": "Good morning", "source": "en", "target": "ru", "desc": "英译俄-简单短语"},
        {"text": "Thank you very much", "source": "en", "target": "ru", "desc": "英译俄-感谢"},
        {"text": "你好", "source": "zh", "target": "ru", "desc": "中译俄"},
        {"text": "天气很好", "source": "zh", "target": "ru", "desc": "中译俄-天气"},
    ]
    
    for test in test_cases:
        print(f"\n测试: {test['desc']}")
        print(f"原文: {test['text']} ({test['source']} -> {test['target']})")
        
        try:
            response = requests.post('http://localhost:5000/api/translate', 
                                   json={'text': test['text'], 'source': test['source'], 'target': test['target']},
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    translation = data['data']
                    print(f"译文: {translation.get('translated_text', 'N/A')}")
                    print(f"来源: {translation.get('source', 'N/A')}")
                    
                    if translation.get('source') != '模拟翻译':
                        print(f"✅ 使用实时翻译API")
                    else:
                        print(f"⚠️  使用模拟数据")
                else:
                    print(f"❌ 失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求错误: {e}")

if __name__ == '__main__':
    test_translation_api()
