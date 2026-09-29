"""Small, dependency-free context signals for Jarvis voice replies."""

import re


_MOOD_PHRASES = {
    "urgent": {
        "urgent", "jaldi", "foran", "abhi", "immediately", "quick", "asap",
        "emergency", "zaroori", "important",
    },
    "frustrated": {
        "stupid", "problem", "issue", "error", "nahi chal", "kaam nahi",
        "bekar", "pareshan", "frustrated", "annoyed", "why not", "phir se",
    },
    "sad": {
        "sad", "dukhi", "udaas", "down", "lonely", "akela", "bura lag",
        "rona", "ro raha", "ro rahi", "depressed",
    },
    "happy": {
        "happy", "khush", "great", "awesome", "shabash", "wah", "thanks",
        "thank you", "mubarak", "excited", "amazing",
    },
    "confused": {
        "confused", "samajh nahi", "what does", "kaise", "how do", "kyun",
        "help me understand", "pata nahi",
    },
}


def detect_user_context(prompt: str) -> dict[str, str]:
    """Return lightweight language and tone hints without diagnosing the user."""
    text = prompt.strip().lower()
    words = set(re.findall(r"[\w']+", text, flags=re.UNICODE))

    scores = {
        mood: sum(1 for phrase in phrases if phrase in text or phrase in words)
        for mood, phrases in _MOOD_PHRASES.items()
    }
    mood = max(scores, key=scores.get) if max(scores.values(), default=0) else "neutral"

    if re.search(r"[\u0900-\u097f]", prompt):
        language = "Hindi written in Devanagari"
    elif re.search(r"[\u0600-\u06ff]", prompt):
        language = "Urdu script"
    elif any(word in words for word in {"hai", "hain", "karo", "khol", "kholna", "aap", "mujhe", "mera"}):
        language = "Roman Urdu/Hinglish"
    else:
        language = "English or mixed language"

    return {"mood": mood, "language": language}


def response_style_for(mood: str) -> str:
    styles = {
        "urgent": "Be direct and fast. Lead with the action or the next concrete step.",
        "frustrated": "Stay patient and accountable. Acknowledge the problem briefly, then solve it without blaming the user.",
        "sad": "Use a gentle, supportive tone. Keep it human and brief; offer practical help without pretending to be a therapist.",
        "happy": "Match the positive energy naturally, while still completing the task precisely.",
        "confused": "Explain one step at a time in simple language and ask one focused question only when necessary.",
        "neutral": "Use a warm, efficient professional tone.",
    }
    return styles.get(mood, styles["neutral"])
