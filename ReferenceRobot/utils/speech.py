"""
语音模块
提供语音识别和语音合成功能
"""

import os
import base64
import tempfile
from typing import Optional

# 检查是否安装了必要的库
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("警告: speech_recognition 库未安装，语音识别功能将不可用")

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("警告: gTTS 或 pygame 库未安装，语音合成功能将不可用")

def speech_to_text(audio_file, language="zh-CN"):
    """
    将语音文件转换为文本
    
    Args:
        audio_file: 音频文件对象或文件路径
        language: 语言代码
    
    Returns:
        识别的文本
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        return "语音识别功能不可用，请安装 speech_recognition 库"
    
    try:
        recognizer = sr.Recognizer()
        
        # 处理文件对象或文件路径
        if hasattr(audio_file, 'read'):
            # 如果是文件对象，保存到临时文件
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
                audio_file.save(tmp.name)
                audio_path = tmp.name
                
                # 尝试转换为WAV格式
                try:
                    from pydub import AudioSegment
                    
                    # 读取WebM文件
                    audio = AudioSegment.from_file(audio_path, format="webm")
                    
                    # 转换为WAV
                    wav_path = audio_path.replace('.webm', '.wav')
                    audio.export(wav_path, format="wav")
                    
                    # 使用转换后的WAV文件
                    audio_path = wav_path
                    
                except ImportError:
                    # pydub不可用，尝试直接使用
                    pass
                except Exception as conv_error:
                    print(f"音频转换失败: {conv_error}")
                    # 继续使用原始文件
        else:
            audio_path = audio_file
        
        # 读取音频文件
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            
            # 识别语音
            text = recognizer.recognize_google(audio_data, language=language)
            
            # 清理临时文件
            if hasattr(audio_file, 'read'):
                try:
                    os.unlink(audio_path)
                    # 如果创建了WAV文件，也删除它
                    if audio_path.endswith('.wav') and os.path.exists(audio_path.replace('.wav', '.webm')):
                        os.unlink(audio_path.replace('.wav', '.webm'))
                except:
                    pass
            
            return text
            
    except sr.UnknownValueError:
        return "无法识别语音"
    except sr.RequestError as e:
        return f"语音识别服务错误: {str(e)}"
    except Exception as e:
        return f"语音识别失败: {str(e)}"

def text_to_speech(text, language="zh-CN"):
    """
    将文本转换为语音
    
    Args:
        text: 要转换为语音的文本
        language: 语言代码
    
    Returns:
        base64编码的音频数据
    """
    if not GTTS_AVAILABLE:
        return {
            'success': False,
            'error': '语音合成功能不可用，请安装 gTTS 和 pygame 库',
            'audio': None
        }
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            temp_file = tmp.name
        
        # 生成语音
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(temp_file)
        
        # 读取音频文件并转换为base64
        with open(temp_file, 'rb') as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # 清理临时文件
        os.unlink(temp_file)
        
        return {
            'success': True,
            'text': text,
            'language': language,
            'audio_format': 'mp3',
            'audio': audio_base64
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"语音合成失败: {str(e)}",
            'audio': None
        }

def play_audio(audio_base64):
    """
    播放base64编码的音频
    
    Args:
        audio_base64: base64编码的音频数据
    
    Returns:
        播放是否成功
    """
    if not GTTS_AVAILABLE:
        return False
    
    try:
        # 解码音频数据
        audio_data = base64.b64decode(audio_base64)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(audio_data)
            temp_file = tmp.name
        
        # 使用pygame播放音频
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # 等待播放完成
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # 清理
        pygame.mixer.quit()
        os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"音频播放失败: {e}")
        return False

def get_supported_languages():
    """获取支持的语音语言列表"""
    return {
        'zh-CN': '中文（普通话）',
        'zh-TW': '中文（台湾）',
        'en': '英语',
        'en-US': '英语（美国）',
        'en-GB': '英语（英国）',
        'ja': '日语',
        'ko': '韩语',
        'fr': '法语',
        'de': '德语',
        'es': '西班牙语',
        'it': '意大利语',
        'ru': '俄语',
        'ar': '阿拉伯语',
        'hi': '印地语'
    }

def record_audio(duration=5):
    """
    录制音频
    
    Args:
        duration: 录制时长（秒）
    
    Returns:
        录制的音频数据（base64编码）
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        return {
            'success': False,
            'error': '语音录制功能不可用',
            'audio': None
        }
    
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            print("正在录音...")
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.listen(source, timeout=duration)
            print("录音完成")
        
        # 将音频数据保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_file = tmp.name
        
        # 保存音频数据
        with open(temp_file, 'wb') as f:
            f.write(audio_data.get_wav_data())
        
        # 读取并编码
        with open(temp_file, 'rb') as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # 清理临时文件
        os.unlink(temp_file)
        
        return {
            'success': True,
            'duration': duration,
            'audio_format': 'wav',
            'audio': audio_base64
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"录音失败: {str(e)}",
            'audio': None
        }

def is_speech_available():
    """检查语音功能是否可用"""
    return {
        'speech_recognition': SPEECH_RECOGNITION_AVAILABLE,
        'text_to_speech': GTTS_AVAILABLE,
        'fully_available': SPEECH_RECOGNITION_AVAILABLE and GTTS_AVAILABLE
    }

if __name__ == '__main__':
    # 测试代码
    print("语音功能状态:", is_speech_available())
    print("\n支持的语言:", get_supported_languages())
    
    # 测试文本转语音
    if GTTS_AVAILABLE:
        result = text_to_speech("你好，我是参考机器人", "zh-CN")
        if result['success']:
            print("\n文本转语音测试成功")
            # 测试播放
            if play_audio(result['audio']):
                print("音频播放成功")
        else:
            print(f"\n文本转语音测试失败: {result['error']}")
