import os
import re
import datetime
from openai import OpenAI
from config.settings import GROQ_API_KEY
from tools.universal_agent import launch_system_app, execute_mouse_action
from tools.security_unlock import unlock_pc_screen
from tools.voice_biometrics import verify_speaker

groq_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1", timeout=30.0) if GROQ_API_KEY else None

def process_command(prompt: str, user_id: str = "owner", user_tier: str = "Pro", audio_path: str = None) -> str:
    if groq_client is None:
        raise ValueError("GROQ_API_KEY missing in .env file")

    prompt_lower = prompt.lower().strip()

    # 1. Security Password Unlock Check
    if any(w in prompt_lower for w in ["unlock", "password", "pc kholo", "laptop kholo"]):
        if audio_path and os.path.exists(audio_path):
            if verify_speaker(audio_path):
                return unlock_pc_screen()
            else:
                return "❌ Security Alert: Voice match nahi hui."
        return unlock_pc_screen()

    # 2. IMMEDIATE EXECUTION FOR ALL ACTION COMMANDS (No text hallucinations)
    action_keywords = ["open", "kholo", "chalao", "start", "launch", "search", "khojo", "youtube", "chrome", "task manager", "notepad", "calculator", "whatsapp"]
    if any(kw in prompt_lower for kw in action_keywords):
        return launch_system_app(prompt_lower)

    # 3. Universal Typing
    if any(w in prompt_lower for w in ["type", "likho", "write"]):
        text_to_type = re.sub(r'.*?(type|likho|write)\s*', '', prompt_lower).strip()
        if text_to_type:
            return execute_mouse_action("type", text=text_to_type)

    # 4. Fallback only for general questions/conversations
    system_prompt = "You are Jarvis, a helpful Windows AI assistant. Answer in 1 short sentence."
    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"