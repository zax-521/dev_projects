import requests

def verify_translation():
    try:
        response = requests.get('http://localhost:5000')
        content = response.text
        
        # 检查关键俄语词汇
        russian_keywords = [
            'Справочный Робот',
            'Многофункциональный помощник',
            'Прогноз погоды',
            'Конвертация валют',
            'Перевод',
            'Калькулятор',
            'Конвертер единиц',
            'Голосовые функции',
            'История'
        ]
        
        print("=== 俄语翻译验证 ===")
        found_count = 0
        for keyword in russian_keywords:
            if keyword in content:
                print(f"✓ 找到: {keyword}")
                found_count += 1
            else:
                print(f"✗ 未找到: {keyword}")
        
        print(f"\n总计: {found_count}/{len(russian_keywords)} 个关键词已翻译")
        
        if found_count == len(russian_keywords):
            print("\n✅ 所有关键内容已成功翻译成俄语！")
            return True
        else:
            print("\n⚠️  部分内容可能未完全翻译")
            return False
            
    except Exception as e:
        print(f"验证失败: {e}")
        return False

if __name__ == '__main__':
    verify_translation()
