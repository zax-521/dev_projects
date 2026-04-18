try:
    from pydub import AudioSegment
    print('pydub导入成功')
    
    # 创建一个简单的测试文件
    import tempfile
    import os
    
    # 创建一个最小的有效WebM文件
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
        # 写入一个有效的WebM头部（EBML + Segment）
        f.write(b'\x1A\x45\xDF\xA3\x93\x42\x82\x84w\xE8')  # EBML Header
        f.write(b'\x18\x53\x80\x67\x01\x00\x00\x00\x00\x00\x00\x00')  # Segment
        test_file = f.name
    
    try:
        print(f'测试文件: {test_file}')
        audio = AudioSegment.from_file(test_file, format='webm')
        print('WebM读取成功')
        print(f'音频时长: {len(audio)} ms')
        
        # 测试转换为WAV
        wav_file = test_file.replace('.webm', '.wav')
        audio.export(wav_file, format='wav')
        print(f'WAV文件已创建: {wav_file}')
        
        # 检查文件大小
        if os.path.exists(wav_file):
            print(f'WAV文件大小: {os.path.getsize(wav_file)} 字节')
            os.unlink(wav_file)
        
    except Exception as e:
        print(f'WebM读取失败: {e}')
        print(f'错误类型: {type(e).__name__}')
        
        # 检查是否需要ffmpeg
        import subprocess
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print('ffmpeg已安装')
            else:
                print('ffmpeg未安装或不可用')
        except:
            print('ffmpeg检查失败')
    finally:
        try:
            os.unlink(test_file)
        except:
            pass
            
except ImportError as e:
    print(f'pydub导入失败: {e}')
except Exception as e:
    print(f'其他错误: {e}')
