"""
brain_v3.py — Full Jarvis Brain: Context Memory + Emotion-Aware + Universal Open + Persistent Memory + Spotify + WhatsApp Mobile
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from config.settings import GROQ_API_KEY

# ---- Existing tool functions ----
from tools.universal_agent import launch_system_app, execute_mouse_action
from tools.app_control import open_application, get_system_stats, open_chrome_profile
from tools.browser_agent import open_gmail, open_website, send_gmail, play_youtube_video
from tools.file_manager import handle_file_operation
from tools.system_control import system_control
from tools.whatsapp_control import open_whatsapp_web, send_whatsapp_message
from tools.web_knowledge import search_web
from tools.system_executor import run_system_command
from tools.screen_watcher import start_watching, stop_watching, ask_about_screen
from tools.security_unlock import unlock_pc_screen
from tools.voice_biometrics import verify_speaker
from tools.gui_agent import click_on_screen_element, open_windows_setting
from memory.memory_manager import save_memory, get_memories

# ---- New tool functions ----
from tools.spotify_control import play_on_spotify, pause_spotify, resume_spotify, next_track, previous_track
from tools.whatsapp_mobile import send_whatsapp_via_mobile
from tools.planner import cancel_planner_item, create_calendar_event, create_reminder, list_planner_items
from tools.smart_home import control_smart_home
from core.assistant_context import detect_user_context, response_style_for
from core.command_policy import tool_intent_allowed

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
        "name": "open_gmail",
        "description": "Open Gmail in the browser without sending anything.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "open_website",
        "description": "Open a public website URL in the browser.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string"}}, "required": ["url"]}}},

    {"type": "function", "function": {
        "name": "send_gmail",
        "description": "Compose and send a Gmail email.",
        "parameters": {"type": "object", "properties": {
            "recipient": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
            "required": ["recipient", "subject", "body"]}}},

    {"type": "function", "function": {
        "name": "open_whatsapp_web",
        "description": "Open an existing WhatsApp Web tab in Chrome, or open WhatsApp Web if no tab exists.",
        "parameters": {"type": "object", "properties": {}}}},

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
        "name": "click_on_screen_element",
        "description": "Click a named visible screen shortcut such as Google, Gmail, YouTube, GitHub, or ChatGPT.",
        "parameters": {"type": "object", "properties": {
            "target_name": {"type": "string"}}, "required": ["target_name"]}}},

    {"type": "function", "function": {
        "name": "handle_file_operation",
        "description": "Create a NEW file, write/append content to it, or read an existing text file's content out loud.",
        "parameters": {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["write", "create", "append", "read", "list", "rename", "delete"]},
            "filename": {"type": "string"}, "content": {"type": "string", "description": "File content, or the new filename when action is rename"},
            "location": {"type": "string", "description": "desktop, documents, downloads, pictures, videos, music, or a folder inside the user profile"}},
            "required": ["action"]}}},

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
        "name": "create_calendar_event",
        "description": "Create a local calendar event and an ICS file that can be opened in a calendar app.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"}, "start_time": {"type": "string", "description": "ISO date/time"},
            "duration_minutes": {"type": "integer"}, "details": {"type": "string"}},
            "required": ["title", "start_time"]}}},

    {"type": "function", "function": {
        "name": "create_reminder",
        "description": "Set a local spoken reminder at an ISO date/time.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"}, "remind_at": {"type": "string", "description": "ISO date/time"},
            "details": {"type": "string"}}, "required": ["title", "remind_at"]}}},

    {"type": "function", "function": {
        "name": "list_planner_items",
        "description": "List pending reminders, calendar events, or all planner items.",
        "parameters": {"type": "object", "properties": {
            "kind": {"type": "string", "enum": ["all", "event", "reminder"]}}}}},

    {"type": "function", "function": {
        "name": "cancel_planner_item",
        "description": "Cancel a reminder or calendar item by its ID from the planner list.",
        "parameters": {"type": "object", "properties": {
            "item_id": {"type": "string"}}, "required": ["item_id"]}}},

    {"type": "function", "function": {
        "name": "control_smart_home",
        "description": "Control a configured Home Assistant light, switch, fan, or climate entity.",
        "parameters": {"type": "object", "properties": {
            "entity_id": {"type": "string"}, "action": {"type": "string", "enum": ["turn_on", "turn_off", "toggle", "set_temperature"]},
            "value": {"type": "string"}}, "required": ["entity_id", "action"]}}},

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
    "open_gmail": lambda: open_gmail(),
    "open_website": lambda url: open_website(url),
    "send_gmail": lambda recipient, subject, body: send_gmail(recipient, subject, body),
    "open_whatsapp_web": lambda: open_whatsapp_web(),
    "send_whatsapp_message": lambda contact_name, message: send_whatsapp_message(contact_name, message),
    "send_whatsapp_via_mobile": lambda phone_number, message: send_whatsapp_via_mobile(phone_number, message),
    "execute_mouse_action": lambda action_type, text="": execute_mouse_action(action_type, text=text),
    "click_on_screen_element": lambda target_name: click_on_screen_element(target_name),
    "handle_file_operation": lambda action, filename="", content="", location="documents": handle_file_operation(action, filename, content, location),
    "system_control": lambda action, value=10: system_control(action, value),
    "open_windows_setting": lambda setting_name: open_windows_setting(setting_name),
    "get_system_stats": lambda: get_system_stats(),
    "search_web": lambda query: search_web(query),
    "unlock_pc_screen": lambda: unlock_pc_screen(),
    "remember_this": lambda key, value, user_id="owner": (save_memory(user_id, key, value), f"✅ Yaad rakh liya: {key} = {value}")[1],
    "create_calendar_event": lambda title, start_time, duration_minutes=60, details="": create_calendar_event(title, start_time, duration_minutes, details),
    "create_reminder": lambda title, remind_at, details="": create_reminder(title, remind_at, details),
    "list_planner_items": lambda kind="all": list_planner_items(kind),
    "cancel_planner_item": lambda item_id: cancel_planner_item(item_id),
    "control_smart_home": lambda entity_id, action, value="": control_smart_home(entity_id, action, value),
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

_PRO_TOOLS = set(TOOL_REGISTRY.keys()) - {"unlock_pc_screen", "run_system_command"}
if os.getenv("JARVIS_ALLOW_SYSTEM_COMMANDS") == "1":
    _PRO_TOOLS.add("run_system_command")

TIER_PERMISSIONS = {
    "Basic": {"search_web", "get_system_stats", "remember_this"},
    "Advanced": {"search_web", "get_system_stats", "launch_system_app", "open_anything",
                 "play_youtube_video", "handle_file_operation", "open_windows_setting", "remember_this"},
    "Pro": _PRO_TOOLS,
}

# =========================================================
# CONVERSATION CONTEXT
# =========================================================
_conversation_histories = {}
MAX_HISTORY_TURNS = 6


def _trim_history(history):
    if len(history) > MAX_HISTORY_TURNS * 2:
        del history[:-MAX_HISTORY_TURNS * 2]


# =========================================================
# MAIN ENTRY POINT
# =========================================================
def process_command(prompt: str, user_id: str = "owner", user_tier: str = "Pro", audio_path: str = None) -> str:
    if groq_client is None:
        raise ValueError("GROQ_API_KEY missing in .env file")

    prompt_lower = prompt.lower().strip()
    user_context = detect_user_context(prompt)

    if any(w in prompt_lower for w in ["unlock", "password", "pc kholo", "laptop kholo"]):
        if not audio_path or not os.path.exists(audio_path):
            return "❌ Security Alert: Voice verification audio unavailable hai."
        if verify_speaker(audio_path):
            return unlock_pc_screen()
        return "❌ Security Alert: Voice match nahi hui."

    allowed_tools = TIER_PERMISSIONS.get(user_tier, TIER_PERMISSIONS["Basic"])
    available_schema = [t for t in TOOLS_SCHEMA if t["function"]["name"] in allowed_tools]
    conversation_history = _conversation_histories.setdefault(user_id, [])

    remembered_facts = get_memories(user_id)
    current_local_time = datetime.now().astimezone().isoformat(timespec="minutes")

    system_prompt = f"""You are Jarvis — a warm, capable Windows voice assistant and companion.

IDENTITY:
- Be dependable, respectful, proactive, and honest about what actually happened.
- Feel like a polished personal assistant: calm under pressure, friendly without being childish,
  and concise enough for speech.
- Do not overuse "Boss", emojis, apologies, or dramatic language. Use them only when natural.

PERSONALITY & TONE:
- Speak naturally, like a helpful friend, not a robotic command parser.
- User language signal: {user_context['language']}.
- User mood signal: {user_context['mood']}.
- Response style for this turn: {response_style_for(user_context['mood'])}
- Match the user's language and energy, but never imitate insults or panic.
- Keep spoken replies SHORT (1-3 sentences) since this is voice, not text chat.

LANGUAGE:
- The user may mix English, Urdu, Roman Urdu, Hindi in the same sentence. Understand
  the INTENT regardless of exact phrasing or language.
- Reply in the user's dominant language or natural mix. Preserve names, URLs, file names,
  email addresses, and code exactly.
- Current local date and time is {current_local_time}. Convert natural phrases such as
    "tomorrow at 5", "next Monday", or "in 20 minutes" to the required ISO time fields.

MEMORY OF THIS USER (facts remembered across all past sessions):
{remembered_facts}

CAPABILITIES:
- If the request maps to one of your available tools, call it with the right arguments.
- If multiple things are asked in one sentence, execute them in the order requested.
- After a tool returns, use its result to decide whether the next requested step is needed.
- Never claim an action succeeded unless the tool result says it succeeded.
- For irreversible actions such as sending messages, shutdown, or overwriting files, follow
    the tool's safety response and do not silently invent confirmation.
- Do not infer an action from a casual mention. Only call a tool when the user's wording
    clearly requests that tool's action; otherwise ask a short clarification question.
- Use conversation history below for follow-up references ("usme search karo").
- If the user shares something worth remembering long-term, call remember_this to save it.
- If nothing needs a tool, reply directly and naturally.
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": prompt})

    conversation_history.append({"role": "user", "content": prompt})
    all_results = []

    for _ in range(3):
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
        if not message.tool_calls:
            reply = message.content or (
                "\n".join(all_results) or "Samajh nahi aaya, dobara boliye."
            )
            conversation_history.append({"role": "assistant", "content": reply})
            _trim_history(conversation_history)
            return reply

        assistant_tool_calls = []
        tool_messages = []
        for call in message.tool_calls:
            fn_name = call.function.name
            raw_arguments = call.function.arguments or "{}"
            try:
                fn_args = json.loads(raw_arguments)
                if not isinstance(fn_args, dict):
                    raise ValueError("tool arguments must be an object")
            except (json.JSONDecodeError, ValueError) as e:
                result = f"❌ '{fn_name}' ke arguments invalid hain: {e}"
                all_results.append(result)
                tool_messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
                assistant_tool_calls.append({
                    "id": call.id,
                    "type": "function",
                    "function": {"name": fn_name, "arguments": raw_arguments},
                })
                continue

            if fn_name not in allowed_tools:
                result = f"❌ '{fn_name}' is not allowed for tier '{user_tier}'."
            elif not tool_intent_allowed(fn_name, prompt):
                result = f"❌ '{fn_name}' was not executed because the user did not clearly request that action."
            else:
                fn = TOOL_REGISTRY.get(fn_name)
                if fn is None:
                    result = f"❌ Unknown tool '{fn_name}'."
                else:
                    try:
                        if fn_name == "remember_this":
                            result = fn(user_id=user_id, **fn_args)
                        else:
                            result = fn(**fn_args)
                        result = str(result)
                    except Exception as e:
                        result = f"❌ '{fn_name}' failed: {str(e)}"

            all_results.append(result)
            assistant_tool_calls.append({
                "id": call.id,
                "type": "function",
                "function": {"name": fn_name, "arguments": raw_arguments},
            })
            tool_messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": assistant_tool_calls,
        })
        messages.extend(tool_messages)

    final_reply = "\n".join(all_results) or "Command complete nahi ho saki."
    conversation_history.append({"role": "assistant", "content": final_reply})
    _trim_history(conversation_history)
    return final_reply