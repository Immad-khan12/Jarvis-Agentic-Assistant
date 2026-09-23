import subprocess

def execute_mobile_command(action: str, target: str = "") -> str:
    """Executes actions directly on connected Android device via ADB over Wi-Fi."""
    try:
        if action == "open_app":
            # Opens app on phone
            cmd = f"adb shell monkey -p {target} -c android.intent.category.LAUNCHER 1"
            subprocess.run(cmd, shell=True, capture_output=True)
            return f"📱 Mobile: Opening {target}..."

        elif action == "type":
            # Types text on mobile focused field
            formatted_text = target.replace(" ", "%s")
            cmd = f"adb shell input text '{formatted_text}'"
            subprocess.run(cmd, shell=True, capture_output=True)
            return "📱 Mobile: Text typed on phone screen."

        elif action == "home":
            subprocess.run("adb shell input keyevent 3", shell=True)
            return "📱 Mobile: Went to Home Screen."

    except Exception as e:
        return f"Mobile Control Error: {str(e)}"
    
    return "Action completed on mobile."