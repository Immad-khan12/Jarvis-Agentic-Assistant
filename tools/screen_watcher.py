import os
import io
import base64
import threading
import time

import mss
from PIL import Image
from openai import OpenAI
from config.settings import GROQ_API_KEY

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    timeout=30.0,
) if GROQ_API_KEY else None

_latest_screenshot_b64 = None
_watching = False
_watch_thread = None
_capture_interval_seconds = 4


def _capture_loop():
    global _latest_screenshot_b64, _watching
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while _watching:
            try:
                shot = sct.grab(monitor)
                img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                img.thumbnail((1280, 1280))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=70)
                _latest_screenshot_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            except Exception as e:
                print(f"⚠️ Screen capture error: {str(e)}")
            time.sleep(_capture_interval_seconds)


def start_watching() -> str:
    global _watching, _watch_thread
    if _watching:
        return "👁️ Main already screen dekh raha hoon."

    _watching = True
    _watch_thread = threading.Thread(target=_capture_loop, daemon=True)
    _watch_thread.start()
    return "👁️ Screen dekhna shuru kar diya hai — jab tak aap band na karein, main dekhta rahunga."


def stop_watching() -> str:
    global _watching
    if not _watching:
        return "Main already screen nahi dekh raha tha."
    _watching = False
    return "🛑 Screen dekhna band kar diya hai."


def ask_about_screen(question: str) -> str:
    if groq_client is None:
        return "❌ GROQ_API_KEY missing — vision model use nahi ho sakta."

    if _latest_screenshot_b64 is None:
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                shot = sct.grab(monitor)
                img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                img.thumbnail((1280, 1280))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=70)
                image_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception as e:
            return f"❌ Screenshot nahi le saka: {str(e)}"
    else:
        image_b64 = _latest_screenshot_b64

    try:
        response = groq_client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Look at this screenshot of the user's screen and answer concisely: {question}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Screen analysis error: {str(e)}"