"""Trigger an outbound Vani call.

Twilio dials the farmer's phone and runs the same IVR flow as an inbound call.
This avoids needing ISD on the caller's SIM.

Usage:
    python call_me.py                 # calls MY_NUMBER below
    python call_me.py +919876543210   # calls a specific number
"""
import sys

import requests

from app.config import settings

# Your verified phone number (must be verified in Twilio trial accounts)
MY_NUMBER = "+918136838296"


def place_call(to_number: str) -> None:
    if not settings.twilio_enabled:
        print("Twilio credentials missing in .env")
        return

    webhook = f"{settings.base_url}/ivr/voice2"

    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{settings.twilio_account_sid}/Calls.json"
    )

    resp = requests.post(
        url,
        auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        data={
            "To": to_number,
            "From": settings.twilio_phone_number,
            "Url": webhook,
            "Method": "POST",
        },
        timeout=30,
    )

    if resp.status_code in (200, 201):
        body = resp.json()
        print(f"Calling {to_number} from {settings.twilio_phone_number}")
        print(f"  webhook : {webhook}")
        print(f"  call sid: {body.get('sid')}")
        print(f"  status  : {body.get('status')}")
        print("\nPick up and ask your farming question after the greeting.")
    else:
        print(f"Twilio rejected the call ({resp.status_code}):")
        print(resp.text)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else MY_NUMBER
    place_call(target)
