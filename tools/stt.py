import speech_recognition as sr

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
            
            # Google Speech Recognition (Free tier)
            text = recognizer.recognize_google(audio)
            print(f"🗣️ You said: '{text}'")
            return text
            
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