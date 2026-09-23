"""
whatsapp_mobile.py — Send WhatsApp messages via your connected Android phone (ADB).

NOTE: This pre-fills the WhatsApp message and opens the chat, but does NOT
tap Send automatically — you'll tap Send yourself on your phone. This is
intentional for safety (avoids blind auto-send mistakes).
"""

import subprocess
import urllib.parse


def send_whatsapp_via_mobile(phone_number: str, message: str) -> str:
    """
    Opens WhatsApp on the connected Android phone with the chat + message
    pre-filled, ready for the user to tap Send.

    phone_number must include country code, no spaces/dashes, e.g. '923001234567'
    """
    try:
        clean_number = "".join(ch for ch in phone_number if ch.isdigit())
        if not clean_number:
            return "❌ Phone number samajh nahi aaya."

        encoded_message = urllib.parse.quote(message)
        deep_link = f"whatsapp://send?phone={clean_number}&text={encoded_message}"

        cmd = [
            "adb", "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", deep_link,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

        if result.returncode != 0:
            return f"❌ ADB command failed: {result.stderr.strip()}"

        return f"📱 WhatsApp chat khol diya hai '{phone_number}' ke sath, message ready hai — bas Send dabana baaki hai."

    except FileNotFoundError:
        return "❌ ADB command nahi mila. Check karein ADB installed hai aur PATH mein add hai."
    except subprocess.TimeoutExpired:
        return "❌ ADB command timeout ho gaya — phone connected hai check karein (adb devices)."
    except Exception as e:
        return f"❌ Mobile WhatsApp error: {str(e)}"


def check_phone_connected() -> bool:
    """Quick check whether a phone is connected via ADB right now."""
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        lines = [l for l in result.stdout.strip().split("\n")[1:] if l.strip()]
        return len(lines) > 0
    except Exception:
        return False