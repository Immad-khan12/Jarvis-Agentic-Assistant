import os
import subprocess
from ctypes import cast, POINTER

try:
    import comtypes
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except Exception:
    PYCAW_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception:
    PYAUTOGUI_AVAILABLE = False


def _get_volume_interface():
    try:
        comtypes.CoInitialize()
    except Exception:
        pass

    devices = AudioUtilities.GetSpeakers()

    if hasattr(devices, "EndpointVolume"):
        return devices.EndpointVolume

    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def _flash_volume_osd():
    """Triggers Windows on-screen volume slider popup without altering level."""
    if not PYAUTOGUI_AVAILABLE:
        return
    try:
        pyautogui.press("volumeup")
        pyautogui.press("volumedown")
    except Exception:
        pass


def system_control(action: str, value: int = 10) -> str:
    """Controls OS system states: lock, shutdown, volume_up, volume_down, set_volume."""
    if action == "lock":
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "🔒 System locked successfully."

    if action == "shutdown":
        os.system("shutdown /s /t 5")
        return "🖥️ Laptop 5 seconds mein band ho raha hai..."

    if not PYCAW_AVAILABLE:
        return "Volume control unavailable: pycaw is not installed (run: pip install pycaw comtypes)."

    try:
        volume = _get_volume_interface()
        current_scalar = volume.GetMasterVolumeLevelScalar()
        current_pct = round(current_scalar * 100)

        if action == "volume_up":
            new_pct = max(0, min(100, current_pct + value))
            volume.SetMasterVolumeLevelScalar(new_pct / 100.0, None)
            _flash_volume_osd()
            return f"Volume increased from {current_pct}% to {new_pct}%."

        elif action == "volume_down":
            new_pct = max(0, min(100, current_pct - value))
            volume.SetMasterVolumeLevelScalar(new_pct / 100.0, None)
            _flash_volume_osd()
            return f"Volume decreased from {current_pct}% to {new_pct}%."

        elif action == "set_volume":
            new_pct = max(0, min(100, value))
            volume.SetMasterVolumeLevelScalar(new_pct / 100.0, None)
            _flash_volume_osd()
            return f"Volume set to {new_pct}%."

        return "Unknown action."
    except Exception as e:
        return f"Volume control error: {str(e)}"


def open_app(app_name: str) -> str:
    try:
        subprocess.Popen([app_name])
        return f"Opening {app_name}."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"