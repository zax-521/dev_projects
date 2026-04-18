#!/usr/bin/env python3
"""
测试语音转文本API
"""

import requests
import json

def test_speech_to_text_api():
    """测试语音转文本API"""
    print("=== 测试语音转文本API ===")
    
    # 创建一个简单的测试音频文件（实际上只是一个文本文件，但我们会测试API端点）
    test_audio_content = b"test audio content"
    
    try:
        # 发送POST请求到语音转文本API
        response = requests.post(
            'http://localhost:5000/api/speech-to-text',
            files={'audio': ('test.wav', test_audio_content, 'audio/wav')}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success', False)}")
            if data.get('success'):
                print(f"识别的文本: {data.get('text', '无文本')}")
            else:
                print(f"错误: {data.get('error', '未知错误')}")
        elif response.status_code == 400:
            print("API端点正常工作（返回400，因为没有提供有效的音频文件）")
        else:
            print(f"API返回错误状态码: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器。请确保服务器正在运行。")
    except Exception as e:
        print(f"错误: {e}")

def test_text_to_speech_api():
    """测试文本转语音API"""
    print("\n=== 测试文本转语音API ===")
    
    try:
        # 发送POST请求到文本转语音API
        response = requests.post(
            'http://localhost:5000/api/text-to-speech',
            json={
                'text': 'Привет, это тест голосового API',
                'language': 'ru'
            }
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success', False)}")
            if data.get('success'):
                audio_data = data.get('audio', '')
                print(f"音频数据长度: {len(audio_data)} 字符")
                print("✅ 文本转语音API正常工作")
            else:
                print(f"错误: {data.get('error', '未知错误')}")
        else:
            print(f"API返回错误状态码: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器。请确保服务器正在运行。")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    test_speech_to_text_api()
    test_text_to_speech_api()
