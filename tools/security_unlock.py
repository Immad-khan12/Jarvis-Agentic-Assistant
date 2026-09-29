import os
import time
import pyautogui

PC_PASSWORD = os.getenv("JARVIS_PC_PASSWORD")

def unlock_pc_screen() -> str:
    """Wakes up Windows Lock screen and auto-types the owner's password."""
    if not PC_PASSWORD:
        return "❌ Unlock disabled: JARVIS_PC_PASSWORD environment variable missing hai."

    try:
        # Press spacebar to reveal password input field
        pyautogui.press("space")
        time.sleep(0.8)
        
        # Type password character by character and press enter
        pyautogui.write(PC_PASSWORD, interval=0.05)
        pyautogui.press("enter")
        return "🔓 PC Password entered and screen unlocked successfully."
    except Exception as e:
        return f"❌ Unlock Error: {str(e)}"