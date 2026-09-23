import os
import re
import subprocess
import urllib.parse
import pyautogui

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

FILLER_WORDS = [
    "open", "kholo", "khol", "karo", "kar", "do", "chalao", "chala",
    "play", "start", "launch", "search", "khojo", "dhoondo", "par", "pe",
    "mera", "meri", "apna", "apni", "please", "plz", "ka", "ki", "ke",
    "wala", "wali", "jara", "zara",
]


def _strip_filler_words(text: str) -> str:
    words = text.split()
    cleaned = [w for w in words if w.lower().strip(".,!?") not in FILLER_WORDS]
    result = " ".join(cleaned).strip()
    result = re.sub(r"\s+", " ", result)
    return result


def launch_system_app(command_str: str) -> str:
    clean = command_str.lower().strip()

    try:
        if "youtube" in clean:
            query = clean.replace("youtube", "")
            query = _strip_filler_words(query)
            if not query:
                query = "trending"
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            subprocess.Popen([CHROME_PATH, url])
            return f"▶️ YouTube par '{query}' search kar ke khol diya hai."

        if "search" in clean or "google" in clean:
            query = clean.replace("google", "")
            query = _strip_filler_words(query)
            if query:
                url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                subprocess.Popen([CHROME_PATH, url])
                return f"🌐 Google par '{query}' search kar diya hai."

        if "chrome" in clean:
            subprocess.Popen([CHROME_PATH])
            return "✅ Chrome open kar diya hai."
        elif "task manager" in clean or "taskmanager" in clean:
            subprocess.Popen("taskmgr", shell=True)
            return "✅ Task Manager open kar diya hai."
        elif "notepad" in clean:
            subprocess.Popen("notepad", shell=True)
            return "✅ Notepad open kar diya hai."
        elif "calculator" in clean or "calc" in clean:
            subprocess.Popen("calc", shell=True)
            return "✅ Calculator open kar diya hai."
        elif "whatsapp" in clean:
            subprocess.Popen("start whatsapp:", shell=True)
            return "✅ WhatsApp open kar diya hai."

        app_target = _strip_filler_words(clean)

        if app_target:
            subprocess.Popen(f'start "" "{app_target}"', shell=True)
            return f"✅ '{app_target}' open kar diya hai."

    except Exception as e:
        try:
            import webbrowser
            webbrowser.open("https://www.google.com")
            return "✅ Browser par open kar diya hai."
        except Exception as ex:
            return f"❌ Error: {str(ex)}"

    return "Command execute nahi ho saki."


def execute_mouse_action(action_type: str, x: int = None, y: int = None, text: str = ""):
    try:
        if action_type == "type":
            pyautogui.write(text, interval=0.02)
            return f"Typed: '{text}'"
    except Exception as e:
        return f"Action Error: {str(e)}"
    return "No action taken."