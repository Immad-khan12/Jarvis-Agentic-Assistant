import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")

if not GROQ_API_KEY:
    print("⚠️  WARNING: GROQ_API_KEY not found in .env file — Jarvis can't think or listen without it.")

if not TAVILY_API_KEY:
    print("⚠️  WARNING: TAVILY_API_KEY not found in .env file.")

if not ELEVENLABS_API_KEY:
    print("⚠️  WARNING: ELEVENLABS_API_KEY not found — Jarvis won't be able to speak.")

TIER_PERMISSIONS = {
    "Basic": ["search_web"],
    "Advanced": ["search_web", "open_app", "system_control"],
    "Pro": ["search_web", "open_app", "system_control"]
}