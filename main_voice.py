import sys
import time
from pathlib import Path
from tools.wake_word import start_listening
from tools.stt import CAPTURED_AUDIO_PATH, listen_and_transcribe
from tools.tts import speak
from core.brain_v3 import process_command
from tools.planner import start_reminder_scheduler

def handle_voice_interaction():
    print("\n⚡ [JARVIS ACTIVATED]: Conversation Active")
    speak("G Boss, main sun raha hoon.")

    while True:
        print("\n🎙️ [LISTENING FOR COMMAND] (Silence timeout: 7s)...")
        
        # Capture user voice input
        user_prompt = listen_and_transcribe(timeout=7, phrase_limit=10)
        
        # 7s Khamoshi par Auto-Standby & Polite Farewell Message
        if not user_prompt:
            print("⏳ Khamoshi detect hui. Standby mode active...")
            speak("Aap ka kaam complete ho chuka hai. Jab bhi zaroorat ho, bas Jarvis keh kar bula lijiyega, main hamesha hazir hoon.")
            break

        prompt_lower = user_prompt.lower().strip()
        prompt_words = set(prompt_lower.split())

        # Stop Commands
        if prompt_lower in {"stop", "exit", "bye", "bas", "bas karo", "band karo", "stop listening"}:
            speak("Aap ka kaam complete ho chuka hai. Jab bhi zaroorat ho, bas Jarvis keh kar bula lijiyega, main hamesha hazir hoon.")
            break

        print(f"\n🧠 Processing: '{user_prompt}'")
        try:
            # Pass recorded voice input for password biometrics verification
            response = process_command(
                prompt=user_prompt,
                user_id="owner",
                user_tier="Pro",
                audio_path=str(CAPTURED_AUDIO_PATH),
            )
            print(f"\n🤖 Jarvis Response:\n{response}\n")
            
            speak(response)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            speak("Maazrat Boss, is command mein masla aaya hai.")
            break
        finally:
            CAPTURED_AUDIO_PATH.unlink(missing_ok=True)

    print("\n🟢 Standby Mode Active (Say 'Hey Jarvis' to wake up)...")

if __name__ == "__main__":
    print("===========================================")
    print("🚀 JARVIS VOICE ENGINE STARTED")
    print("Say 'Hey Jarvis' to wake up the assistant.")
    print("===========================================\n")
    
    start_reminder_scheduler(speak)
    start_listening(handle_voice_interaction)