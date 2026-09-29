"""
brain_v3.py — Full Jarvis Brain: Context Memory + Emotion-Aware + Universal Open + Persistent Memory + Spotify + WhatsApp Mobile
"""

import os
import json
from openai import OpenAI
from config.settings import GROQ_API_KEY

# ---- Existing tool functions ----
from tools.universal_agent import launch_system_app, execute_mouse_action
from tools.app_control import open_application, get_system_stats, open_chrome_profile
from tools.browser_agent import send_gmail, play_youtube_video
from tools.file_manager import handle_file_operation
from tools.system_control import system_control
from tools.whatsapp_control import send_whatsapp_message
from tools.web_knowledge import search_web
from tools.system_executor import run_system_command
from tools.screen_watcher import start_watching, stop_watching, ask_about_screen
from tools.security_unlock import unlock_pc_screen
from tools.voice_biometrics import verify_speaker
from tools.gui_agent import open_windows_setting
from memory.memory_manager import save_memory, get_memories

# ---- New tool functions ----
from tools.spotify_control import play_on_spotify, pause_spotify, resume_spotify, next_track, previous_track
from tools.whatsapp_mobile import send_whatsapp_via_mobile

groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    timeout=30.0,
) if GROQ_API_KEY else None


# =========================================================
# Generic "open anything" tool
# =========================================================
def open_anything(path_or_name: str) -> str:
    candidates = [
        path_or_name,
        os.path.join(os.path.join(os.path.expanduser("~"), "Desktop"), path_or_name),
        os.path.join(os.path.join(os.path.expanduser("~"), "Documents"), path_or_name),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                os.startfile(path)
                return f"✅ '{path_or_name}' khol diya hai."
            except Exception as e:
                return f"❌ Open failed: {str(e)}"

    app_result = open_application(path_or_name)
    return app_result


# =========================================================
# TOOLS_SCHEMA
# =========================================================
TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "launch_system_app",
        "description": "Open a common app, or run a YouTube/Google search, from a free-form request.",
        "parameters": {"type": "object", "properties": {
            "command_str": {"type": "string"}}, "required": ["command_str"]}}},

    {"type": "function", "function": {
        "name": "open_anything",
        "description": "Open ANY file (Word doc, PDF, image, existing document on Desktop/Documents) or any installed application by name.",
        "parameters": {"type": "object", "properties": {
            "path_or_name": {"type": "string"}}, "required": ["path_or_name"]}}},

    {"type": "function", "function": {
        "name": "open_chrome_profile",
        "description": "Open a specific named Chrome profile, optionally with a search query.",
        "parameters": {"type": "object", "properties": {
            "profile_dir": {"type": "string"},
            "search_query": {"type": "string"}}, "required": ["profile_dir"]}}},

    {"type": "function", "function": {
        "name": "play_youtube_video",
        "description": "Search YouTube for a specific video/song and play the first result.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]}}},

    {"type": "function", "function": {
        "name": "send_gmail",
        "description": "Compose and send a Gmail email.",
        "parameters": {"type": "object", "properties": {
            "recipient": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
            "required": ["recipient", "subject", "body"]}}},

    {"type": "function", "function": {
        "name": "send_whatsapp_message",
        "description": "Send a WhatsApp message via WhatsApp Web (browser) to a named contact.",
        "parameters": {"type": "object", "properties": {
            "contact_name": {"type": "string"}, "message": {"type": "string"}},
            "required": ["contact_name", "message"]}}},

    {"type": "function", "function": {
        "name": "send_whatsapp_via_mobile",
        "description": "Open WhatsApp on the user's connected Android phone with a message pre-filled to a phone number, ready to send. Use this instead of the web version when the user has their phone connected.",
        "parameters": {"type": "object", "properties": {
            "phone_number": {"type": "string"}, "message": {"type": "string"}},
            "required": ["phone_number", "message"]}}},

    {"type": "function", "function": {
        "name": "execute_mouse_action",
        "description": "Type text at the current on-screen cursor position.",
        "parameters": {"type": "object", "properties": {
            "action_type": {"type": "string", "enum": ["type"]}, "text": {"type": "string"}},
            "required": ["action_type", "text"]}}},

    {"type": "function", "function": {
        "name": "handle_file_operation",
        "description": "Create a NEW file, write/append content to it, or read an existing text file's content out loud.",
        "parameters": {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["write", "create", "append", "read"]},
            "filename": {"type": "string"}, "content": {"type": "string"},
            "location": {"type": "string", "enum": ["desktop", "documents"]}},
            "required": ["action", "filename"]}}},

    {"type": "function", "function": {
        "name": "system_control",
        "description": "Lock PC, shut down, or change volume.",
        "parameters": {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["lock", "shutdown", "volume_up", "volume_down", "set_volume"]},
            "value": {"type": "integer"}}, "required": ["action"]}}},

    {"type": "function", "function": {
        "name": "open_windows_setting",
        "description": "Open a Windows Settings page (wifi, bluetooth, display, sound, apps, update).",
        "parameters": {"type": "object", "properties": {
            "setting_name": {"type": "string"}}, "required": ["setting_name"]}}},

    {"type": "function", "function": {
        "name": "get_system_stats",
        "description": "Report current CPU, RAM, and battery usage.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "search_web",
        "description": "Search the web for real-time facts/information.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]}}},

    {"type": "function", "function": {
        "name": "unlock_pc_screen",
        "description": "Unlock the PC lock screen with the saved password.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "remember_this",
        "description": "Save a fact the user wants Jarvis to remember permanently (across restarts).",
        "parameters": {"type": "object", "properties": {
            "key": {"type": "string"}, "value": {"type": "string"}},
            "required": ["key", "value"]}}},

    {"type": "function", "function": {
        "name": "play_on_spotify",
        "description": "Search Spotify for a song/artist and play it.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]}}},

    {"type": "function", "function": {
        "name": "pause_spotify",
        "description": "Pause current Spotify playback.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "resume_spotify",
        "description": "Resume paused Spotify playback.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "next_track",
        "description": "Skip to next song on Spotify.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "previous_track",
        "description": "Go to previous song on Spotify.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "run_system_command",
        "description": "Fallback tool: run any Windows PowerShell command for OS-level requests that no other specific tool covers (renaming files, checking disk space, listing processes, killing a process, changing settings, etc). Use this only when no other tool fits the request.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "the exact PowerShell command to run"}},
            "required": ["command"]}}},

    {"type": "function", "function": {
        "name": "start_watching",
        "description": "Start continuously watching the screen in the background until told to stop.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "stop_watching",
        "description": "Stop watching the screen.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "ask_about_screen",
        "description": "Answer a question about whatever is currently visible on the user's screen.",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string"}}, "required": ["question"]}}},
]

TOOL_REGISTRY = {
    "launch_system_app": lambda command_str: launch_system_app(command_str),
    "open_anything": lambda path_or_name: open_anything(path_or_name),
    "open_chrome_profile": lambda profile_dir, search_query="": open_chrome_profile(profile_dir, search_query),
    "play_youtube_video": lambda query: play_youtube_video(query),
    "send_gmail": lambda recipient, subject, body: send_gmail(recipient, subject, body),
    "send_whatsapp_message": lambda contact_name, message: send_whatsapp_message(contact_name, message),
    "send_whatsapp_via_mobile": lambda phone_number, message: send_whatsapp_via_mobile(phone_number, message),
    "execute_mouse_action": lambda action_type, text="": execute_mouse_action(action_type, text=text),
    "handle_file_operation": lambda action, filename, content="", location="documents": handle_file_operation(action, filename, content, location),
    "system_control": lambda action, value=10: system_control(action, value),
    "open_windows_setting": lambda setting_name: open_windows_setting(setting_name),
    "get_system_stats": lambda: get_system_stats(),
    "search_web": lambda query: search_web(query),
    "unlock_pc_screen": lambda: unlock_pc_screen(),
    "remember_this": lambda key, value: (save_memory("owner", key, value), f"✅ Yaad rakh liya: {key} = {value}")[1],
    "play_on_spotify": lambda query: play_on_spotify(query),
    "pause_spotify": lambda: pause_spotify(),
    "resume_spotify": lambda: resume_spotify(),
    "next_track": lambda: next_track(),
    "previous_track": lambda: previous_track(),
    "run_system_command": lambda command: run_system_command(command),
    "start_watching": lambda: start_watching(),
    "stop_watching": lambda: stop_watching(),
    "ask_about_screen": lambda question: ask_about_screen(question),
}

TIER_PERMISSIONS = {
    "Basic": {"search_web", "get_system_stats", "remember_this"},
    "Advanced": {"search_web", "get_system_stats", "launch_system_app", "open_anything",
                 "play_youtube_video", "handle_file_operation", "open_windows_setting", "remember_this"},
    "Pro": set(TOOL_REGISTRY.keys()),
}

# =========================================================
# CONVERSATION CONTEXT
# =========================================================
_conversation_history = []
MAX_HISTORY_TURNS = 6


def _trim_history():
    global _conversation_history
    if len(_conversation_history) > MAX_HISTORY_TURNS * 2:
        _conversation_history = _conversation_history[-MAX_HISTORY_TURNS * 2:]


# =========================================================
# MAIN ENTRY POINT
# =========================================================
def process_command(prompt: str, user_id: str = "owner", user_tier: str = "Pro", audio_path: str = None) -> str:
    if groq_client is None:
        raise ValueError("GROQ_API_KEY missing in .env file")

    prompt_lower = prompt.lower().strip()

    if any(w in prompt_lower for w in ["unlock", "password", "pc kholo", "laptop kholo"]):
        if audio_path and os.path.exists(audio_path):
            if verify_speaker(audio_path):
                return unlock_pc_screen()
            return "❌ Security Alert: Voice match nahi hui."
        return unlock_pc_screen()

    allowed_tools = TIER_PERMISSIONS.get(user_tier, TIER_PERMISSIONS["Basic"])
    available_schema = [t for t in TOOLS_SCHEMA if t["function"]["name"] in allowed_tools]

    remembered_facts = get_memories(user_id)

    system_prompt = f"""You are Jarvis — a warm, capable Windows voice assistant and companion.

PERSONALITY & TONE:
- Speak naturally, like a helpful friend, not a robotic command parser.
- Notice the user's tone/mood from their words and respond with warmth.
- Match their language and energy.
- Keep spoken replies SHORT (1-3 sentences) since this is voice, not text chat.

LANGUAGE:
- The user may mix English, Urdu, Roman Urdu, Hindi in the same sentence. Understand
  the INTENT regardless of exact phrasing or language.

MEMORY OF THIS USER (facts remembered across all past sessions):
{remembered_facts}

CAPABILITIES:
- If the request maps to one of your available tools, call it with the right arguments.
- If multiple things are asked in one sentence, call multiple tools.
- Use conversation history below for follow-up references ("usme search karo").
- If the user shares something worth remembering long-term, call remember_this to save it.
- If nothing needs a tool, reply directly and naturally.
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(_conversation_history)
    messages.append({"role": "user", "content": prompt})

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=available_schema,
            tool_choice="auto",
        )
    except Exception as e:
        return f"Error: {str(e)}"

    message = response.choices[0].message
    _conversation_history.append({"role": "user", "content": prompt})

    if not message.tool_calls:
        reply = message.content or "Samajh nahi aaya, dobara boliye."
        _conversation_history.append({"role": "assistant", "content": reply})
        _trim_history()
        return reply

    results = []
    for call in message.tool_calls:
        fn_name = call.function.name
        try:
            fn_args = json.loads(call.function.arguments or "{}")
        except json.JSONDecodeError:
            fn_args = {}

        if fn_name not in allowed_tools:
            results.append(f"❌ '{fn_name}' is not allowed for tier '{user_tier}'.")
            continue

        fn = TOOL_REGISTRY.get(fn_name)
        if fn is None:
            results.append(f"❌ Unknown tool '{fn_name}'.")
            continue

        try:
            result = fn(**fn_args)
            results.append(str(result))
        except Exception as e:
            results.append(f"❌ '{fn_name}' failed: {str(e)}")

    final_reply = "\n".join(results)
    _conversation_history.append({"role": "assistant", "content": final_reply})
    _trim_history()
    return final_reply