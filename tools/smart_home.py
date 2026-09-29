"""Optional Home Assistant REST control with explicit safe actions."""

import os
import re
import requests


_ALLOWED_ACTIONS = {"turn_on", "turn_off", "toggle", "set_temperature"}


def control_smart_home(entity_id: str, action: str, value: str = "") -> str:
    base_url = os.getenv("HOME_ASSISTANT_URL", "").rstrip("/")
    token = os.getenv("HOME_ASSISTANT_TOKEN", "")
    if not base_url or not token:
        return "❌ Smart home configured nahi hai. HOME_ASSISTANT_URL aur HOME_ASSISTANT_TOKEN set karein."
    if not re.fullmatch(r"[a-z0-9_]+\.[a-z0-9_]+", entity_id.strip().lower()):
        return "❌ Invalid Home Assistant entity ID."
    if action not in _ALLOWED_ACTIONS:
        return "❌ Allowed smart-home actions: turn_on, turn_off, toggle, set_temperature."

    domain = entity_id.split(".", 1)[0].lower()
    service = action
    data = {"entity_id": entity_id.strip().lower()}
    if action == "set_temperature":
        try:
            temperature = float(value)
        except ValueError:
            return "❌ Temperature numeric honi chahiye."
        if not 5 <= temperature <= 35:
            return "❌ Temperature 5 se 35 degrees ke darmiyan honi chahiye."
        service = "set_temperature"
        data["temperature"] = temperature
        domain = "climate"

    try:
        response = requests.post(
            f"{base_url}/api/services/{domain}/{service}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=data,
            timeout=10,
        )
        response.raise_for_status()
        return f"✅ Smart home action complete: {action} on {entity_id}."
    except requests.RequestException as exc:
        return f"❌ Smart home request failed: {exc}"
