"""Speech to text via Azure gpt-4o-transcribe.

More accurate than Twilio's recogniser on accented narrowband phone audio.
The prompt below biases the model toward Kerala farming vocabulary, which is
where a general recogniser usually goes wrong.
"""
import io

import requests

from ..config import settings

# Steers spelling and word choice toward the terms a farmer here would use.
VOCAB_PROMPT = (
    "A farmer in Alappuzha, Kerala, India is asking a farming question in "
    "English over a phone call. Likely terms: paddy, rice, coconut, banana, "
    "tapioca, pepper, cardamom, areca nut, okra, cowpea, amaranthus, "
    "bitter gourd, snake gourd, brinjal, leaf blight, rice blast, brown spot, "
    "root wilt, stem borer, plant hopper, rhinoceros beetle, red palm weevil, "
    "mancozeb, carbendazim, neem oil, urea, potash, Jyothi, Uma, "
    "Krishi Bhavan, monsoon, Virippu, Mundakan, Puncha, waterlogging."
)


def transcribe(audio: bytes, filename: str = "call.wav") -> str:
    """Return the transcribed text, or an empty string on failure."""
    if not settings.azure_stt_enabled:
        return ""

    try:
        buf = io.BytesIO(audio)
        resp = requests.post(
            settings.stt_endpoint,
            headers={"api-key": settings.stt_key},
            files={"file": (filename, buf, "audio/wav")},
            data={
                "language": "en",
                "prompt": VOCAB_PROMPT,
                "response_format": "json",
            },
            timeout=60,
        )
        if resp.status_code != 200:
            print(f"STT failed {resp.status_code}: {resp.text[:200]}")
            return ""
        return (resp.json().get("text") or "").strip()
    except Exception as e:
        print(f"STT error: {e}")
        return ""


def fetch_twilio_recording(recording_url: str) -> bytes:
    """Download a Twilio recording as WAV.

    Twilio needs a moment before the recording is retrievable, and the URL
    needs account auth.
    """
    url = recording_url if recording_url.endswith(".wav") else f"{recording_url}.wav"
    resp = requests.get(
        url,
        auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        timeout=45,
    )
    resp.raise_for_status()
    return resp.content
