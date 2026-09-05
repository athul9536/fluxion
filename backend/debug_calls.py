"""Inspect recent Twilio calls and any error alerts.

Usage:  python debug_calls.py
"""
import requests

from app.config import settings

AUTH = (settings.twilio_account_sid, settings.twilio_auth_token)
BASE = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}"


def recent_calls(limit: int = 5) -> None:
    resp = requests.get(f"{BASE}/Calls.json", auth=AUTH,
                        params={"PageSize": limit}, timeout=30)
    resp.raise_for_status()
    calls = resp.json().get("calls", [])

    print(f"=== Last {len(calls)} calls ===")
    for c in calls:
        print(f"\nSID      : {c['sid']}")
        print(f"To       : {c['to']}")
        print(f"Status   : {c['status']}")
        print(f"Duration : {c['duration']}s")
        print(f"Started  : {c['start_time']}")


def recent_alerts(limit: int = 10) -> None:
    resp = requests.get(
        "https://monitor.twilio.com/v1/Alerts",
        auth=AUTH, params={"PageSize": limit}, timeout=30,
    )
    if resp.status_code != 200:
        print(f"\nCould not fetch alerts ({resp.status_code})")
        return

    alerts = resp.json().get("alerts", [])
    print(f"\n\n=== Last {len(alerts)} alerts (errors/warnings) ===")
    if not alerts:
        print("None. No webhook or TwiML errors reported.")
        return

    for a in alerts:
        print(f"\nCode     : {a.get('error_code')}")
        print(f"Severity : {a.get('log_level')}")
        print(f"When     : {a.get('date_created')}")
        text = (a.get("alert_text") or "")[:400]
        print(f"Detail   : {text}")


if __name__ == "__main__":
    recent_calls()
    recent_alerts()
