import os
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from config.settings import GROQ_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

groq_client = None
if GROQ_API_KEY:
    groq_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1", timeout=30.0)

elevenlabs_client = None
if ELEVENLABS_API_KEY:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def detect_language_and_transcribe(audio_file_path: str) -> tuple[str, str]:
    if groq_client is None:
        return "Transcription unavailable: GROQ_API_KEY is missing.", "en-US"

    try:
        with open(audio_file_path, "rb") as audio_file:
            result = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json"
            )
        transcribed_text = result.text
        detected_locale = getattr(result, "language", None) or "en"
        return transcribed_text, detected_locale
    except Exception as e:
        return f"Transcription error: {str(e)}", "en-US"


def generate_accent_matched_response(prompt: str, detected_locale: str) -> str:
    if groq_client is None:
        return "Voice engine unavailable: GROQ_API_KEY is missing."

    system_instruction = f"""
    You are Jarvis, an advanced AI assistant.
    User Language Locale: {detected_locale}
    Keep response concise and direct.
    """
    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Voice engine error: {str(e)}"


def speak_response(text: str, locale: str, output_audio_path: str = "output.mp3"):
    """Converts text to speech using ElevenLabs. Falls back to a silent file if unavailable."""
    if elevenlabs_client is None:
        print("🔇 ElevenLabs client is None — ELEVENLABS_API_KEY missing or invalid.")
        with open(output_audio_path, "wb") as f:
            f.write(b"")
        return output_audio_path

    if not text:
        print("🔇 speak_response got empty text — nothing to synthesize.")
        with open(output_audio_path, "wb") as f:
            f.write(b"")
        return output_audio_path

    try:
        audio_stream = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        total_bytes = 0
        with open(output_audio_path, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)
                    total_bytes += len(chunk)
        print(f"🔊 ElevenLabs wrote {total_bytes} bytes to {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"ElevenLabs TTS error: {str(e)}")
        with open(output_audio_path, "wb") as f:
            f.write(b"")
        return output_audio_path