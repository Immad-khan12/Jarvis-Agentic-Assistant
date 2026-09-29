import os
import time
import re
import urllib.parse
from playwright.sync_api import sync_playwright


def open_gmail() -> str:
    try:
        import webbrowser
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
        return "✅ Gmail khol diya hai."
    except Exception as e:
        return f"❌ Gmail open nahi ho saka: {str(e)}"


def open_website(url: str) -> str:
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "❌ Valid http ya https website URL dein."
    try:
        import webbrowser
        webbrowser.open(url.strip())
        return f"✅ Website khol di: {url.strip()}"
    except Exception as e:
        return f"❌ Website open nahi ho saki: {str(e)}"

def send_gmail(recipient: str, subject: str, body: str) -> str:
    if os.getenv("JARVIS_ALLOW_EXTERNAL_SEND") != "1":
        return "❌ Email sending disabled hai. JARVIS_ALLOW_EXTERNAL_SEND=1 set karna hoga."
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", recipient.strip()):
        return "❌ Invalid email address."

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://mail.google.com/")
            time.sleep(3)

            page.click("text='Compose'")
            time.sleep(1)
            page.fill("input[aria-label='To recipients']", recipient)
            page.fill("input[name='subjectbox']", subject)
            page.fill("div[aria-label='Message Body']", body)
            page.click("text='Send'")
            time.sleep(2)
            browser.close()
            return f"✅ Email sent to '{recipient}'."
    except Exception as e:
        return f"❌ Gmail Error: {str(e)}"

def play_youtube_video(query: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}")
            time.sleep(2)
            page.click("ytd-video-renderer #video-title")
            browser.close()
            return f"▶️ Playing '{query}' on YouTube."
    except Exception as e:
        return f"❌ YouTube Error: {str(e)}"