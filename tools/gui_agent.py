import pyautogui
import time
import subprocess

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True

def click_on_screen_element(target_name: str) -> str:
    """Detects screen elements naturally (without needing the word 'click') and clicks them."""
    screen_w, screen_h = pyautogui.size()
    target_clean = target_name.lower().strip()

    # Screen Coordinates based on Chrome New Tab shortcuts
    if "youtube" in target_clean:
        x, y = int(screen_w * 0.25), int(screen_h * 0.41)
        pyautogui.click(x, y)
        return "✅ YouTube icon par click kar diya hai."

    elif "chatgpt" in target_clean or "gpt" in target_clean:
        x, y = int(screen_w * 0.66), int(screen_h * 0.41)
        pyautogui.click(x, y)
        return "✅ ChatGPT icon par click kar diya hai."

    elif "google" in target_clean:
        x, y = int(screen_w * 0.25), int(screen_h * 0.61)
        pyautogui.click(x, y)
        return "✅ Google icon par click kar diya hai."

    elif "gmail" in target_clean or "mail" in target_clean:
        x, y = int(screen_w * 0.03), int(screen_h * 0.12)
        pyautogui.click(x, y)
        return "✅ Gmail par click kar diya hai."

    elif "github" in target_clean:
        x, y = int(screen_w * 0.38), int(screen_h * 0.41)
        pyautogui.click(x, y)
        return "✅ GitHub icon par click kar diya hai."

    # Default Center Click
    pyautogui.click(screen_w // 2, screen_h // 2)
    return f"✅ Screen par '{target_name}' open karne ke liye click kar diya hai."

def open_windows_setting(setting_name: str) -> str:
    settings_map = {
        "wifi": "ms-settings:network-wifi",
        "bluetooth": "ms-settings:bluetooth",
        "display": "ms-settings:display",
        "sound": "ms-settings:apps-volume",
        "apps": "ms-settings:appsfeatures",
        "update": "ms-settings:windowsupdate"
    }
    
    clean_key = setting_name.lower().strip()
    if clean_key in settings_map:
        subprocess.Popen(f"start {settings_map[clean_key]}", shell=True)
        return f"Windows {clean_key.upper()} Settings khol di hain."
    
    subprocess.Popen("start ms-settings:", shell=True)
    return "Windows Settings khol di hain."