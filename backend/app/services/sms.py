"""Send the spoken answer to the farmer as an SMS.

Voice is ephemeral: chemical names, dosages and variety names are hard to
retain from one listen. A text gives the farmer something to take to the
agri shop.
"""
import threading

import requests

from ..config import settings
from ..logbook import log

PREFIX = "Vani farming helpline: "

# Two SMS segments is plenty; keep a hard ceiling so a long answer cannot
# turn into a five part text.
MAX_BODY_CHARS = 300


def send_async(to: str, body: str) -> None:
    """Fire and forget, so the voice reply is never delayed by SMS."""
    if not settings.sms_enabled:
        return
    if not to:
        log("sms: no destination number, skipping")
        return

    threading.Thread(target=_send, args=(to, body), daemon=True).start()


def _send(to: str, body: str) -> None:
    text = PREFIX + body.strip()
    if len(text) > MAX_BODY_CHARS:
        text = text[: MAX_BODY_CHARS - 3].rstrip() + "..."

    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{settings.twilio_account_sid}/Messages.json"
    )

    try:
        resp = requests.post(
            url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            data={"To": to, "From": settings.twilio_phone_number, "Body": text},
            timeout=30,
        )
        if resp.status_code in (200, 201):
            log(f"sms queued to {to} ({len(text)} chars)")
        else:
            log(f"sms failed {resp.status_code}: {resp.text[:160]}")
    except Exception as e:
        log(f"sms error: {e}")
