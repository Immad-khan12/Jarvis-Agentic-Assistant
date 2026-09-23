import time
from playwright.sync_api import sync_playwright

def send_gmail(recipient: str, subject: str, body: str) -> str:
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
            page.goto(f"https://www.youtube.com/results?search_query={query}")
            time.sleep(2)
            page.click("ytd-video-renderer #video-title")
            return f"▶️ Playing '{query}' on YouTube."
    except Exception as e:
        return f"❌ YouTube Error: {str(e)}"