"""
spotify_control.py — Real Spotify playback control via Spotify Web API.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

_sp_client = None


def _get_client():
    global _sp_client
    if _sp_client is not None:
        return _sp_client

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

    if not client_id or not client_secret:
        return None

    _sp_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-modify-playback-state user-read-playback-state",
    ))
    return _sp_client


def _active_device_id(sp):
    devices = sp.devices().get("devices", [])
    if not devices:
        return None
    for d in devices:
        if d.get("is_active"):
            return d["id"]
    return devices[0]["id"]


def play_on_spotify(query: str) -> str:
    sp = _get_client()
    if sp is None:
        return "❌ Spotify not configured — add SPOTIPY_CLIENT_ID/SECRET to .env (see setup notes)."

    try:
        results = sp.search(q=query, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])
        if not items:
            return f"❌ '{query}' Spotify par nahi mila."

        track = items[0]
        device_id = _active_device_id(sp)
        if device_id is None:
            return "❌ Koi active Spotify device nahi mila. Pehle Spotify app kholkar ek gaana manually play karein, phir dobara try karein."

        sp.start_playback(device_id=device_id, uris=[track["uri"]])
        artist = track["artists"][0]["name"] if track["artists"] else "Unknown"
        return f"🎵 Spotify par '{track['name']}' by {artist} chala diya hai."
    except Exception as e:
        return f"❌ Spotify error: {str(e)}"


def pause_spotify() -> str:
    sp = _get_client()
    if sp is None:
        return "❌ Spotify not configured."
    try:
        sp.pause_playback()
        return "⏸️ Spotify pause kar diya."
    except Exception as e:
        return f"❌ Spotify error: {str(e)}"


def resume_spotify() -> str:
    sp = _get_client()
    if sp is None:
        return "❌ Spotify not configured."
    try:
        sp.start_playback()
        return "▶️ Spotify resume kar diya."
    except Exception as e:
        return f"❌ Spotify error: {str(e)}"


def next_track() -> str:
    sp = _get_client()
    if sp is None:
        return "❌ Spotify not configured."
    try:
        sp.next_track()
        return "⏭️ Next gaana chala diya."
    except Exception as e:
        return f"❌ Spotify error: {str(e)}"


def previous_track() -> str:
    sp = _get_client()
    if sp is None:
        return "❌ Spotify not configured."
    try:
        sp.previous_track()
        return "⏮️ Pichla gaana chala diya."
    except Exception as e:
        return f"❌ Spotify error: {str(e)}"