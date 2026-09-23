import time
import pyautogui

# Yahan apna actual PC password likhein (e.g., "1234" ya "mySecretPass")
PC_PASSWORD = "cvbnm"

def unlock_pc_screen() -> str:
    """Wakes up Windows Lock screen and auto-types the owner's password."""
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