from pathlib import Path
import os

import speech_recognition as sr

CAPTURED_AUDIO_PATH = Path(__file__).resolve().parents[1] / "temp_input.wav"

def listen_and_transcribe(timeout: int = 5, phrase_limit: int = 8) -> str:
    """
    Listens to microphone input after wake-word trigger and converts voice to text ($0 cost).
    """
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print("\n🎙️ [JARVIS LISTENING]: Bolen, main sun raha hoon...")
        
        # Background noise adjustment
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            print("⏳ Processing voice input...")
            CAPTURED_AUDIO_PATH.write_bytes(audio.get_wav_data())
            
            # Try common mixed-language locales; the first one can be overridden in .env.
            preferred_language = os.getenv("JARVIS_STT_LANGUAGE", "en-IN")
            languages = [preferred_language, "ur-PK", "hi-IN", "en-US"]
            for language in dict.fromkeys(languages):
                try:
                    text = recognizer.recognize_google(audio, language=language)
                    print(f"🗣️ You said ({language}): '{text}'")
                    return text
                except sr.UnknownValueError:
                    continue

            print("⚠️ Voice kisi supported language mein clear nahi thi, dobara bolein.")
            return ""
            
        except sr.WaitTimeoutError:
            print("⚠️ Timeout: Koi voice detect nahi hui.")
            return ""
        except sr.UnknownValueError:
            print("⚠️ Voice clear nahi thi, dobara bolein.")
            return ""
        except Exception as e:
            print(f"❌ STT Error: {str(e)}")
            return ""

if __name__ == "__main__":
    # Test standalone STT
    result = listen_and_transcribe()
    print(f"\nFinal Transcribed Text: {result}")