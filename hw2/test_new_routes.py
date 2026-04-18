import requests

def test_route(url, name):
    try:
        response = requests.get(f'http://localhost:5000{url}', timeout=5)
        print(f"{name} ({url}):")
        print(f"  状态码: {response.status_code}")
        print(f"  内容类型: {response.headers.get('Content-Type')}")
        print(f"  内容长度: {len(response.text)}")
        
        if response.status_code == 200:
            if 'html' in response.headers.get('Content-Type', ''):
                print(f"  前50字符: {response.text[:50]}")
            return True
        else:
            print(f"  错误: {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"{name} ({url}): 错误: 无法连接到服务器")
        return False
    except Exception as e:
        print(f"{name} ({url}): 错误: {e}")
        return False

if __name__ == '__main__':
    print("测试新路由...")
    print("=" * 50)
    
    routes = [
        ('/', '主页面'),
        ('/debug_voice.html', '调试页面'),
        ('/test_voice_recording.html', '测试页面'),
        ('/static/css/style.css', 'CSS文件'),
        ('/api/text-to-speech', 'API端点 (需要POST)')
    ]
    
    results = []
    for url, name in routes:
        results.append(test_route(url, name))
        print()
    
    print("=" * 50)
    success_count = sum(results)
    total_count = len(results)
    print(f"测试完成: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("✅ 所有路由正常工作")
    else:
        print("⚠ 有些路由有问题")
