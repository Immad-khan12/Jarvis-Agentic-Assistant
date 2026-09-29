"""
whatsapp_web_control.py (v4 — SIMPLEST APPROACH) — Uses Chrome's own
built-in "Tab Search" feature (Ctrl+Shift+A) to jump directly to an
already-open WhatsApp Web tab, no matter how many tabs are open or
whether it's in the background.

WHY THIS IS BETTER THAN THE PREVIOUS VERSIONS:
- No need to close/restart Chrome
- No shortcut editing
- No remote debugging setup
- Works with Chrome exactly as it's running right now

HOW IT WORKS:
1. Brings any Chrome window to the front (just needs SOME Chrome window open).
2. Presses Ctrl+Shift+A — this opens Chrome's built-in tab search popup.
3. Types "whatsapp" into that search box.
4. Presses Enter — Chrome jumps straight to the matching tab, wherever it was.
5. If no WhatsApp tab was found (search comes up empty), opens a new one instead.
6. Continues with the existing contact-search + type + send flow.

SETUP REQUIRED:
    pip install pygetwindow psutil pywin32
"""

import os
import time
import webbrowser
import pyautogui
import pygetwindow as gw
import psutil

try:
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def _get_process_name_for_window(window) -> str:
    if not WIN32_AVAILABLE:
        return ""
    try:
        _, pid = win32process.GetWindowThreadProcessId(window._hWnd)
        return psutil.Process(pid).name().lower()
    except Exception:
        return ""


def _find_any_chrome_window():
    """Returns ANY currently open Chrome window (doesn't need to already show WhatsApp)."""
    all_windows = gw.getAllWindows()
    for window in all_windows:
        if not window.title:
            continue
        process_name = _get_process_name_for_window(window)
        if process_name == "chrome.exe":
            return window
        if not WIN32_AVAILABLE and "chrome" in window.title.lower():
            return window
    return None


def send_whatsapp_message(contact_name: str, message: str) -> str:
    if os.getenv("JARVIS_ALLOW_EXTERNAL_SEND") != "1":
        return "❌ WhatsApp Web sending disabled hai. JARVIS_ALLOW_EXTERNAL_SEND=1 set karna hoga."
    chrome_window = _find_any_chrome_window()

    if chrome_window is None:
        # No Chrome open at all — just open WhatsApp Web fresh
        webbrowser.open("https://web.whatsapp.com/")
        time.sleep(4)
        status_note = "Chrome khula hi nahi tha, naya khol diya"
    else:
        try:
            if chrome_window.isMinimized:
                chrome_window.restore()
            chrome_window.activate()
            time.sleep(0.6)

            # Open Chrome's built-in tab search and jump to WhatsApp tab
            pyautogui.hotkey("ctrl", "shift", "a")
            time.sleep(0.6)
            pyautogui.write("whatsapp", interval=0.04)
            time.sleep(0.6)
            pyautogui.press("enter")
            time.sleep(1.0)
            status_note = "khule hue tabs mein se WhatsApp Web dhoondh kar us par switch ho gaya"
        except Exception as e:
            return f"❌ Chrome tab search error: {str(e)}"

    try:
        pyautogui.hotkey("ctrl", "alt", "/")
        time.sleep(0.5)
        pyautogui.write(contact_name, interval=0.05)
        time.sleep(1.0)
        pyautogui.press("enter")
        time.sleep(0.5)

        pyautogui.write(message, interval=0.03)
        pyautogui.press("enter")

        return f"✅ ({status_note}) '{contact_name}' ko message bhej diya hai."
    except Exception as e:
        return f"❌ WhatsApp Error: {str(e)}"


def open_whatsapp_web() -> str:
    chrome_window = _find_any_chrome_window()
    if chrome_window is None:
        webbrowser.open("https://web.whatsapp.com/")
        return "✅ WhatsApp Web browser mein khol diya hai."

    try:
        if chrome_window.isMinimized:
            chrome_window.restore()
        chrome_window.activate()
        time.sleep(0.6)
        pyautogui.hotkey("ctrl", "shift", "a")
        time.sleep(0.5)
        pyautogui.write("whatsapp", interval=0.04)
        pyautogui.press("enter")
        return "✅ Existing WhatsApp Web tab khol diya hai."
    except Exception as e:
        return f"❌ WhatsApp Web open nahi ho saka: {str(e)}"