import os
import json
import subprocess
import webbrowser
import urllib.parse
import psutil

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "vscode": "code",
    "cmd": "cmd.exe"
}


def list_chrome_profiles() -> dict:
    local_state_path = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Google", "Chrome", "User Data", "Local State"
    )
    if not os.path.exists(local_state_path):
        return {}

    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        info_cache = data.get("profile", {}).get("info_cache", {})
        result = {}
        for folder, info in info_cache.items():
            result[folder] = {
                "name": info.get("name", folder),
                "email": info.get("user_name", ""),
            }
        return result
    except Exception:
        return {}


def find_matching_profile(hint: str) -> str:
    profiles = list_chrome_profiles()
    if not profiles:
        return "Default"

    hint_lower = hint.lower().strip()

    for folder, info in profiles.items():
        if hint_lower in info["name"].lower() or hint_lower in info["email"].lower():
            return folder

    return "Default"


def open_chrome_profile(profile_dir: str = "Default", search_query: str = "") -> str:
    try:
        known_profiles = list_chrome_profiles()
        if known_profiles and profile_dir not in known_profiles:
            profile_dir = find_matching_profile(profile_dir)

        url = ""
        if search_query:
            encoded = urllib.parse.quote(search_query)
            url = f"https://www.google.com/search?q={encoded}"

        if url:
            cmd = f'"{CHROME_PATH}" --profile-directory="{profile_dir}" "{url}"'
        else:
            cmd = f'"{CHROME_PATH}" --profile-directory="{profile_dir}"'

        subprocess.Popen(cmd, shell=True)

        if search_query:
            return f"✅ Chrome ({profile_dir}) par '{search_query}' search kar diya hai."
        return f"✅ Chrome ki '{profile_dir}' khol di gayi hai."

    except Exception as e:
        return f"❌ Chrome Error: {str(e)}"


def open_application(app_name: str, search_query: str = "") -> str:
    app_clean = app_name.lower().strip()

    if "chrome" in app_clean:
        return open_chrome_profile(profile_dir="Default", search_query=search_query)

    for key, path in APP_PATHS.items():
        if key in app_clean:
            try:
                subprocess.Popen(path, shell=True)
                return f"Opening {key.upper()}..."
            except Exception as e:
                return f"Failed to open {key}: {str(e)}"

    return f"Application '{app_name}' executed."


def get_system_stats() -> str:
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    battery_info = psutil.sensors_battery()
    battery_str = f"{battery_info.percent}%" if battery_info else "N/A"
    return f"CPU Usage: {cpu_usage}% | RAM Usage: {ram_usage}% | Battery: {battery_str}"