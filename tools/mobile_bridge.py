import re
import subprocess

def execute_mobile_command(action: str, target: str = "") -> str:
    """Executes actions directly on connected Android device via ADB over Wi-Fi."""
    try:
        if action == "open_app":
            if not re.fullmatch(r"[A-Za-z0-9_.]+", target):
                return "❌ Invalid Android package name."
            # Opens app on phone
            subprocess.run(
                ["adb", "shell", "monkey", "-p", target, "-c", "android.intent.category.LAUNCHER", "1"],
                capture_output=True,
                check=True,
            )
            return f"📱 Mobile: Opening {target}..."

        elif action == "type":
            # Types text on mobile focused field
            formatted_text = target.replace(" ", "%s")
            subprocess.run(["adb", "shell", "input", "text", formatted_text], capture_output=True, check=True)
            return "📱 Mobile: Text typed on phone screen."

        elif action == "home":
            subprocess.run(["adb", "shell", "input", "keyevent", "3"], check=True)
            return "📱 Mobile: Went to Home Screen."

    except Exception as e:
        return f"Mobile Control Error: {str(e)}"
    
    return "Action completed on mobile."