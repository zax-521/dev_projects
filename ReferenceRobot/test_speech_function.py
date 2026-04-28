import requests
import json
import base64
import tempfile
import os

def test_text_to_speech():
    print("测试文本转语音功能...")
    
    # 测试文本转语音API
    test_text = "Привет, я Справочный Робот, рад вам помочь!"
    print(f"测试文本: {test_text}")
    
    try:
        response = requests.post('http://localhost:5000/api/text-to-speech', 
                               json={'text': test_text, 'language': 'ru'},
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data['success']:
                print("✅ 文本转语音API调用成功")
                
                # 检查是否有音频数据
                if data.get('audio'):
                    audio_base64 = data['audio']
                    print(f"收到音频数据 (base64长度: {len(audio_base64)})")
                    
                    # 保存音频文件以便检查
                    try:
                        audio_data = base64.b64decode(audio_base64)
                        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                            f.write(audio_data)
                            temp_file = f.name
                        
                        print(f"✅ 音频文件已保存到: {temp_file}")
                        print(f"文件大小: {os.path.getsize(temp_file)} 字节")
                        
                        # 清理临时文件
                        os.unlink(temp_file)
                        
                        return True
                    except Exception as e:
                        print(f"❌ 音频数据处理失败: {e}")
                        return False
                else:
                    print("❌ 响应中没有音频数据")
                    return False
            else:
                print(f"❌ API返回失败: {data.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_speech_to_text():
    print("\n测试语音转文本功能...")
    print("注意: 这个测试需要上传音频文件，我们只测试API端点是否响应")
    
    try:
        # 创建一个简单的测试请求（不带文件）
        response = requests.post('http://localhost:5000/api/speech-to-text',
                               timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 400:
            # 400是预期的，因为我们没有提供音频文件
            print("✅ 语音转文本API端点存在（返回400，因为没有提供音频文件）")
            return True
        else:
            print(f"响应: {response.status_code} - {response.text[:100]}")
            return response.status_code < 500  # 如果不是服务器错误，认为端点存在
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_speech_module_directly():
    print("\n直接测试语音模块...")
    
    try:
        from utils.speech import text_to_speech, is_speech_available
        
        # 检查语音功能状态
        status = is_speech_available()
        print(f"语音功能状态: {status}")
        
        if status['text_to_speech']:
            print("测试文本转语音...")
            result = text_to_speech("Тестовое сообщение", "ru")
            print(f"直接调用结果: {result['success']}")
            
            if result['success']:
                print("✅ 直接调用文本转语音成功")
                return True
            else:
                print(f"❌ 直接调用失败: {result.get('error')}")
                return False
        else:
            print("❌ 文本转语音功能不可用")
            return False
            
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        return False

if __name__ == '__main__':
    print("=== 语音功能测试 ===\n")
    
    # 测试1: 文本转语音API
    api_test = test_text_to_speech()
    
    # 测试2: 语音转文本API端点
    stt_test = test_speech_to_text()
    
    # 测试3: 直接模块测试
    direct_test = test_speech_module_directly()
    
    print("\n=== 测试总结 ===")
    print(f"文本转语音API: {'✅ 通过' if api_test else '❌ 失败'}")
    print(f"语音转文本API端点: {'✅ 存在' if stt_test else '❌ 问题'}")
    print(f"直接模块测试: {'✅ 通过' if direct_test else '❌ 失败'}")
    
    if api_test and stt_test and direct_test:
        print("\n🎉 所有语音功能测试通过！")
    else:
        print("\n⚠️  部分语音功能测试失败，需要进一步检查")
