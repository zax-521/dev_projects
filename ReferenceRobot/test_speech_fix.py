import requests
import time

def test_speech_api():
    print("测试语音识别API...")
    
    # 等待服务器启动
    time.sleep(2)
    
    # 首先测试API端点是否可达
    try:
        # 测试GET请求（应该返回405）
        response = requests.get('http://localhost:5000/api/speech-to-text', timeout=5)
        print(f"GET请求状态码: {response.status_code} (期望: 405)")
    except Exception as e:
        print(f"GET请求错误: {e}")
    
    # 创建一个简单的测试音频文件（空的，只是为了测试格式错误）
    import tempfile
    import os
    
    # 创建一个空的WebM文件（模拟前端上传）
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
        # 写入最小的WebM头部
        f.write(b'\x1A\x45\xDF\xA3')  # WebM签名
        test_file = f.name
    
    try:
        # 测试上传文件
        with open(test_file, 'rb') as audio_file:
            files = {'audio': ('test.webm', audio_file, 'audio/webm')}
            response = requests.post('http://localhost:5000/api/speech-to-text', files=files, timeout=10)
        
        print(f"\nPOST请求状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"文本: {data.get('text', 'N/A')}")
            if not data.get('success'):
                print(f"错误: {data.get('error', 'N/A')}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"POST请求错误: {e}")
    finally:
        # 清理测试文件
        try:
            os.unlink(test_file)
        except:
            pass
    
    print("\n" + "="*50)
    print("测试文本转语音API...")
    
    try:
        response = requests.post('http://localhost:5000/api/text-to-speech', 
                                json={'text': '测试语音合成', 'language': 'ru'},
                                timeout=10)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            if data.get('success'):
                print(f"音频数据长度: {len(data.get('audio', ''))} 字符")
            else:
                print(f"错误: {data.get('error', 'N/A')}")
        else:
            print(f"错误响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"文本转语音API错误: {e}")

if __name__ == '__main__':
    test_speech_api()
