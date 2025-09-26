import azure.cognitiveservices.speech as speechsdk
import io

def recognize_from_pcm_file(pcm_file_path):
    # 1. 配置 Azure 语音服务
    speech_key = "**"  # 替换为实际密钥
    service_region = "eastus"  # 例如：eastasia, chinaeast2
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "zh-CN"  # 根据音频语言设置

    # 2. 读取 PCM 文件
    with open(pcm_file_path, "rb") as pcm_file:
        pcm_data = pcm_file.read()

    # 3. 创建音频流
    audio_stream = io.BytesIO(pcm_data)
    audio_stream.seek(0)  # 重要：重置流位置到开头

    # 4. 定义 PCM 音频格式（根据你的文件实际参数修改）
    # 你需要知道你的 PCM 文件的采样率、位深和声道数
    stream_format = speechsdk.audio.AudioStreamFormat(
        samples_per_second=16000,  # 采样率：16000 Hz
        bits_per_sample=16,       # 位深：16 bit
        channels=1                # 声道数：单声道
    )

    # 5. 创建音频流回调类
    class PcmStreamCallback(speechsdk.audio.PullAudioInputStreamCallback):
        def __init__(self, stream):
            super().__init__()
            self._stream = stream

        def read(self, buffer: memoryview) -> int:
            size = buffer.nbytes
            data = self._stream.read(size)
            buffer[:len(data)] = data
            return len(data)

        def close(self):
            self._stream.close()

    # 6. 创建音频输入流
    pull_callback = PcmStreamCallback(audio_stream)
    audio_input = speechsdk.audio.PullAudioInputStream(pull_callback, stream_format)
    audio_config = speechsdk.audio.AudioConfig(stream=audio_input)

    # 7. 创建识别器并识别
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )

    print(f"开始识别 PCM 文件: {pcm_file_path}")
    
    result = speech_recognizer.recognize_once()
    
    # 处理识别结果
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"✅ 识别成功: {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("❌ 无法识别音频内容")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print(f"❌ 识别被取消: {cancellation.reason}")
        if cancellation.reason == speechsdk.CancellationReason.Error:
            print(f"错误详情: {cancellation.error_details}")
    
    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else None

# 使用示例
if __name__ == "__main__":
    pcm_file_path = "/workspaces/skills-getting-started-with-github-copilot/ElevenLabs_Pt_353.pcm"  # 替换为实际的 PCM 文件路径
    recognize_from_pcm_file(pcm_file_path)