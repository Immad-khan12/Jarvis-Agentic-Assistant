import asyncio
import os
import re
import time
import uuid
import edge_tts
import pygame
import pyaudio
import numpy as np
from langdetect import detect

VOICE_MAP = {
    "ur": "ur-PK-UzmaNeural",        # Urdu Female Voice
    "en": "en-US-JennyNeural",       # English Female Voice
    "hi": "hi-IN-SwaraNeural",       # Hindi Female Voice
}
DEFAULT_VOICE = "en-US-JennyNeural"

def clean_text_for_speech(text: str) -> str:
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'[\*\_~#`>|-]', '', text)
    text = re.sub(r'http\S+', '', text)
    return text.strip()

def get_voice_for_text(text: str) -> str:
    if re.search(r'[\u0600-\u06FF]', text):
        return VOICE_MAP.get("ur", DEFAULT_VOICE)

    roman_words = ["aaj", "hai", "haan", "nahi", "kya", "kaise", "mera", "aap", "ho", "karo", "yeh", "woh", "boss", "g"]
    text_words = re.findall(r'\b\w+\b', text.lower())
    if sum(1 for word in text_words if word in roman_words) >= 1:
        return VOICE_MAP.get("ur", DEFAULT_VOICE)

    try:
        lang = detect(text)
        return VOICE_MAP.get(lang, DEFAULT_VOICE)
    except Exception:
        return DEFAULT_VOICE

async def _generate_audio(text: str, voice: str, output_file: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def speak(text: str):
    cleaned_text = clean_text_for_speech(text)
    if not cleaned_text:
        return

    selected_voice = get_voice_for_text(cleaned_text)
    unique_id = uuid.uuid4().hex[:8]
    output_file = os.path.join(os.getcwd(), f"temp_tts_{unique_id}.mp3")

    try:
        asyncio.run(_generate_audio(cleaned_text, selected_voice, output_file))
        time.sleep(0.1)

        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            return

        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()

        # Monitor Mic during speech for direct user interrupt (filters background noise)
        p = pyaudio.PyAudio()
        try:
            mic_stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            start_time = time.time()

            while pygame.mixer.music.get_busy():
                # Allow 0.6s grace period to avoid speaker echo self-triggering
                if time.time() - start_time > 0.6:
                    try:
                        data = mic_stream.read(1024, exception_on_overflow=False)
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        energy = np.linalg.norm(audio_data) / len(audio_data)

                        # Higher energy threshold (55.0) filters out background noise
                        # Only loud direct user voice interrupts Jarvis speech
                        if energy > 55.0:
                            print("\n🛑 [INTERRUPT]: Direct user voice detected! Stopping speech...")
                            pygame.mixer.music.stop()
                            break
                    except Exception:
                        pass
                
                pygame.time.Clock().tick(10)

        except Exception:
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            try:
                mic_stream.stop_stream()
                mic_stream.close()
                p.terminate()
            except Exception:
                pass

        pygame.mixer.music.unload()
        pygame.mixer.quit()

    except Exception as e:
        print(f"❌ TTS Error: {str(e)}")
    finally:
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except Exception:
                pass