"""Check whether SMS actually reaches an Indian mobile from the Twilio number.

Twilio may report success while India's DLT filtering silently drops the
message, so this polls the message status rather than trusting the initial
response.

Usage:  python test_sms.py
"""
import sys
import time

import requests

from app.config import settings

TO = "+918136838296"

BODY = (
    "Vani farming helpline: For rice brown spot, apply potassium and zinc "
    "based on a soil test, then spray mancozeb at the label dose."
)

AUTH = (settings.twilio_account_sid, settings.twilio_auth_token)
BASE = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}"


def send(to: str) -> str | None:
    resp = requests.post(
        f"{BASE}/Messages.json",
        auth=AUTH,
        data={"To": to, "From": settings.twilio_phone_number, "Body": BODY},
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        print(f"Rejected at send ({resp.status_code}):")
        print(resp.text)
        return None

    body = resp.json()
    print(f"Queued to {to} from {settings.twilio_phone_number}")
    print(f"  sid    : {body.get('sid')}")
    print(f"  status : {body.get('status')}")
    print(f"  segments: {body.get('num_segments')}  price: {body.get('price')}")
    return body.get("sid")


def track(sid: str, checks: int = 8, gap: int = 4) -> None:
    """Poll delivery status. 'sent' is not 'delivered'."""
    print("\nTracking delivery...")
    last = None
    for _ in range(checks):
        time.sleep(gap)
        resp = requests.get(f"{BASE}/Messages/{sid}.json", auth=AUTH, timeout=30)
        if resp.status_code != 200:
            print(f"  lookup failed {resp.status_code}")
            return

        msg = resp.json()
        status = msg.get("status")
        if status != last:
            print(f"  status: {status}")
            last = status

        if status == "delivered":
            print("\nDELIVERED. SMS is viable, safe to build on.")
            return
        if status in ("failed", "undelivered"):
            print(f"\nNOT DELIVERED. error_code={msg.get('error_code')} "
                  f"{msg.get('error_message')}")
            print("Likely India DLT filtering. Do not build on SMS.")
            return

    print(f"\nStill '{last}' after {checks * gap}s. 'sent' without 'delivered' "
          f"often means the carrier accepted it but filtered it.")
    print("Check whether the message actually arrived on the handset.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else TO
    sid = send(target)
    if sid:
        track(sid)
