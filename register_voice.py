import wave
import pyaudio
import time
from tools.voice_biometrics import register_owner_voice

print("===========================================")
print("🎙️ OWNER VOICE REGISTRATION")
print("===========================================")
print("3 seconds mein recording start hogi...")
time.sleep(2)
print("🔴 RECORDING STARTED! Clear voice mein bolein:")
print("   'Mera naam Arham hai, main Jarvis ka owner hoon.'")

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 4

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

frames = []
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

audio_file = "owner_sample.wav"
wf = wave.open(audio_file, "wb")
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b"".join(frames))
wf.close()

register_owner_voice(audio_file)
print("🎉 Mubarak ho! Aap ki aawaz register ho chuki hai.")