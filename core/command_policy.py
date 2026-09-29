"""Explicit-intent checks for voice tool calls."""

import re


_INTENTS = {
    "launch_system_app": ("open", "khol", "launch", "start", "chala", "play", "search", "google", "youtube", "whatsapp"),
    "open_anything": ("open", "khol", "launch", "file", "folder", "document"),
    "open_chrome_profile": ("chrome", "profile"),
    "play_youtube_video": ("youtube", "play", "song", "video", "gaana"),
    "open_gmail": ("gmail", "email", "mail"),
    "open_website": ("website", "site", "url", "http", "www", "open"),
    "send_gmail": ("send", "email", "mail", "bhej", "message"),
    "open_whatsapp_web": ("whatsapp", "open", "khol"),
    "send_whatsapp_message": ("whatsapp", "send", "message", "bhej"),
    "send_whatsapp_via_mobile": ("whatsapp", "phone", "mobile", "send", "message", "bhej"),
    "execute_mouse_action": ("type", "likh", "write", "enter"),
    "click_on_screen_element": ("click", "press", "open", "icon", "button"),
    "handle_file_operation": ("create", "write", "edit", "read", "append", "rename", "delete", "list", "likh", "banao"),
    "system_control": ("lock", "shutdown", "shut down", "volume", "awaaz", "band karo"),
    "open_windows_setting": ("setting", "wifi", "bluetooth", "display", "sound", "update"),
    "get_system_stats": ("stats", "status", "cpu", "ram", "memory", "battery", "system"),
    "search_web": ("search", "khoj", "find", "research", "latest", "news", "maloomat"),
    "remember_this": ("remember", "yaad", "save", "bhoolna"),
    "create_calendar_event": ("calendar", "event", "meeting", "schedule", "appointment", "calendar mein"),
    "create_reminder": ("remind", "reminder", "yaad dila", "yaad dilana"),
    "list_planner_items": ("calendar", "schedule", "reminder", "appointments", "list", "show"),
    "cancel_planner_item": ("cancel", "remove", "delete", "reminder", "event"),
    "control_smart_home": ("smart home", "light", "switch", "fan", "ac", "heater", "temperature"),
    "play_on_spotify": ("spotify", "song", "music", "gaana", "play"),
    "pause_spotify": ("spotify", "pause", "rok"),
    "resume_spotify": ("spotify", "resume", "continue", "chala"),
    "next_track": ("spotify", "next", "agla"),
    "previous_track": ("spotify", "previous", "pichla"),
    "start_watching": ("screen", "watch", "monitor", "dekho", "dekh"),
    "stop_watching": ("screen", "watch", "monitor", "stop", "band"),
    "ask_about_screen": ("screen", "visible", "dikh", "dekho", "batao"),
    "run_system_command": ("command", "powershell", "system"),
}


def _is_negative_request(text: str) -> bool:
    return bool(re.search(
        r"(?:^|\s)(?:don't|dont|do not|mat|nahi)\s+"
        r"(?:open|khol|launch|start|search|send|bhej|write|likh|create|banao|play|"
        r"click|type|band|stop|shutdown|lock|delete|remove|run|karo|karna)\b",
        text,
    ))


def tool_intent_allowed(tool_name: str, prompt: str) -> bool:
    """Reject tool calls that have no clear lexical support in the spoken request."""
    text = prompt.strip().lower()
    if not text or _is_negative_request(text):
        return False

    if tool_name == "open_gmail":
        return "gmail" in text and any(word in text for word in ("open", "khol", "launch", "start"))
    if tool_name == "send_gmail":
        return any(word in text for word in ("email", "mail", "gmail")) and any(word in text for word in ("send", "bhej"))
    if tool_name == "open_whatsapp_web":
        return "whatsapp" in text and any(word in text for word in ("open", "khol", "launch", "start"))
    if tool_name in {"send_whatsapp_message", "send_whatsapp_via_mobile"}:
        return "whatsapp" in text and any(word in text for word in ("send", "bhej"))
    if tool_name == "open_chrome_profile":
        return "chrome" in text and any(word in text for word in ("open", "khol", "launch", "start"))
    if tool_name == "open_anything":
        return any(word in text for word in ("file", "folder", "document")) and any(word in text for word in ("open", "khol", "launch"))
    if tool_name == "open_website":
        return any(word in text for word in ("http", "www", "url")) or (
            any(word in text for word in ("website", "site"))
            and any(word in text for word in ("open", "khol", "launch"))
        )
    if tool_name == "launch_system_app":
        return any(word in text for word in ("open", "khol", "launch", "start", "chala", "play", "search", "khoj"))
    if tool_name == "get_system_stats":
        return any(word in text for word in ("stats", "status", "cpu", "ram", "memory", "battery"))
    if tool_name == "create_calendar_event":
        return any(word in text for word in ("calendar", "event", "meeting", "appointment")) and any(
            word in text for word in ("create", "schedule", "book", "add", "rakh", "banao")
        )
    if tool_name == "create_reminder":
        has_reminder_subject = any(word in text for word in ("remind", "reminder", "yaad"))
        has_explicit_action = any(word in text for word in ("set", "create", "schedule", "rakh", "dila"))
        has_direct_remind = bool(re.search(r"\bremind\s+me\b", text))
        return has_reminder_subject and (has_explicit_action or has_direct_remind)
    if tool_name == "list_planner_items":
        return any(word in text for word in ("list", "show", "upcoming", "pending", "what are", "batao")) and any(
            word in text for word in ("schedule", "calendar", "reminder", "appointment", "event")
        )
    if tool_name == "cancel_planner_item":
        return any(word in text for word in ("cancel", "remove", "delete"))
    if tool_name == "control_smart_home":
        return any(word in text for word in ("light", "switch", "fan", "ac", "heater", "temperature", "smart home")) and any(
            word in text for word in ("on", "off", "toggle", "turn", "set", "change", "chala", "band")
        )

    phrases = _INTENTS.get(tool_name)
    if phrases is None:
        return True
    return any(phrase in text for phrase in phrases)
