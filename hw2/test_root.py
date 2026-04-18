import requests

def test_root():
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"内容类型: {response.headers.get('Content-Type')}")
        print(f"内容长度: {len(response.text)}")
        
        if response.status_code == 200:
            print("前200字符:")
            print(response.text[:200])
        else:
            print(f"错误响应: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器")
    except Exception as e:
        print(f"错误: {e}")

def test_static():
    try:
        response = requests.get('http://localhost:5000/static/css/style.css', timeout=5)
        print(f"\nCSS文件状态码: {response.status_code}")
        print(f"CSS文件长度: {len(response.text)}")
    except Exception as e:
        print(f"CSS文件错误: {e}")

if __name__ == '__main__':
    print("测试根路由 '/'...")
    test_root()
    print("\n测试静态文件...")
    test_static()
