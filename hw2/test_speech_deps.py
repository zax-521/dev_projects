import sys

def check_dependencies():
    print("检查语音功能依赖库...")
    
    try:
        import speech_recognition as sr
        print('✓ speech_recognition 已安装')
    except ImportError:
        print('✗ speech_recognition 未安装')
    
    try:
        from gtts import gTTS
        print('✓ gTTS 已安装')
    except ImportError:
        print('✗ gTTS 未安装')
    
    try:
        import pygame
        print('✓ pygame 已安装')
    except ImportError:
        print('✗ pygame 未安装')

if __name__ == '__main__':
    check_dependencies()
