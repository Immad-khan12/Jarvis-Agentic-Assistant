import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model

def start_listening(on_wake_callback):
    print("🔄 Initializing Wake-Word Engine...")
    openwakeword.utils.download_models()

    # Load model
    owwModel = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    audio = pyaudio.PyAudio()

    # List default input devices for verification
    print("\n🎤 Active Input Device:")
    try:
        default_dev = audio.get_default_input_device_info()
        print(f"   ➜ Using: {default_dev.get('name')}")
    except Exception:
        print("   ⚠️ Could not detect default mic automatically.")

    stream = audio.open(
        format=FORMAT, 
        channels=CHANNELS, 
        rate=RATE, 
        input=True, 
        frames_per_buffer=CHUNK
    )

    print("\n🟢 Listening for 'Hey Jarvis' in background...")

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            owwModel.predict(audio_data)
            
            for model_name, scores in owwModel.prediction_buffer.items():
                score = scores[-1]
                
                # Print live score if audio is detected
                if score > 0.1:
                    print(f"👂 Sound picked up! Confidence: {score:.2f}")
                
                if score > 0.5:
                    print("\n⚡ [WAKE WORD DETECTED]: 'Hey Jarvis'")
                    on_wake_callback()
                    owwModel.reset()
                    
    except KeyboardInterrupt:
        print("\nStopping listener...")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    def test_trigger():
        print("🤖 Jarvis: 'Yes Boss, how can I help you?'")
        
    start_listening(test_trigger)