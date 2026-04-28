try:
    import pydub
    print('pydub已安装')
except ImportError:
    print('pydub未安装')
    
# 检查其他可能的音频处理库
try:
    import wave
    print('wave已安装 (Python标准库)')
except ImportError:
    print('wave未安装')

try:
    import audioop
    print('audioop已安装 (Python标准库)')
except ImportError:
    print('audioop未安装')
