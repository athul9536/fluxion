"""End-to-end smoke test of the IVR flow without placing a real call.

Walks the same webhook sequence Twilio would, so regressions show up here
instead of on a live call.

Usage:  python smoke_test.py
"""
import re
import time
import xml.dom.minidom as minidom

import requests

BASE = "http://127.0.0.1:8000"


def post(path: str, data: dict | None = None) -> str:
    resp = requests.post(f"{BASE}{path}", data=data or {}, timeout=90)
    resp.raise_for_status()
    minidom.parseString(resp.text)  # raises if the TwiML is malformed
    return resp.text


def spoken(xml: str) -> list[str]:
    return re.findall(r"<Say[^>]*>(.*?)</Say>", xml, flags=re.S)


def attr(xml: str, name: str) -> str | None:
    found = re.search(rf'{name}="([^"]+)"', xml)
    return found.group(1) if found else None


def check(label: str, condition: bool) -> None:
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")


def main() -> None:
    print("1. Greeting / location prompt")
    xml = post("/ivr/voice")
    check(f"language is {attr(xml, 'language')}",
          attr(xml, "language") in ("en-US", "en-GB"))
    check("uses phone_call speech model",
          attr(xml, "speechModel") == "phone_call")
    check("asks about Alappuzha", "Alappuzha" in xml)
    print(f"  says: {spoken(xml)[0]}")

    print("\n2. Location confirmed with 'yes'")
    xml = post("/ivr/confirm", {"SpeechResult": "yes"})
    check("invites a question", "question" in spoken(xml)[0].lower())
    azure_mode = "<Record" in xml
    check(f"pipeline is {'Azure STT (Record)' if azure_mode else 'Twilio ASR'}",
          True)
    if azure_mode:
        check("record posts to /ivr/recorded", "/ivr/recorded" in xml)
        check("beep enabled so caller knows when to speak",
              'playBeep="true"' in xml)
    print(f"  says: {spoken(xml)[0]}")

    print("\n2b. Recording with no audio fails gracefully")
    xml = post("/ivr/recorded", {"CallSid": "CAtest", "RecordingUrl": ""})
    check("hangs up politely", "<Hangup/>" in xml)

    print("\n2c. Result polling waits, then gives up")
    xml = post("/ivr/result?tries=0", {"CallSid": "CAunknown"})
    check("holds and re-polls", "/ivr/result?tries=1" in xml)
    check("pauses rather than sitting silent", "<Pause" in xml)
    xml = post("/ivr/result?tries=99", {"CallSid": "CAunknown"})
    check("eventually gives up", "<Hangup/>" in xml)
    print(f"  says: {spoken(xml)[0]}")

    print("\n3. Garbled Hinglish transcript still gets a real answer")
    garbled = "han Vastav best crop Tu grow Na Ho rice aur wheat"
    start = time.perf_counter()
    xml = post("/ivr/process?attempt=1", {"SpeechResult": garbled})
    elapsed = time.perf_counter() - start
    answer = spoken(xml)[0]
    words = len(re.findall(r"[A-Za-z]{2,}", answer))
    check(f"answer has real content ({words} words)", words >= 4)
    check(f"responded in {elapsed:.1f}s (under 10s)", elapsed < 10)
    check("no markdown leaked", "*" not in answer and "#" not in answer)
    print(f"  says: {answer[:170]}")

    print("\n4. Silence retries instead of hanging up")
    xml = post("/ivr/process?attempt=1", {"SpeechResult": ""})
    check("re-prompts the caller", "/ivr/process?attempt=2" in xml)
    print(f"  says: {spoken(xml)[0]}")

    print("\n5. Final attempt gives up gracefully")
    xml = post("/ivr/process?attempt=3", {"SpeechResult": ""})
    check("hangs up politely", "<Hangup/>" in xml)
    print(f"  says: {spoken(xml)[0]}")

    print("\n6. 'more questions' loop")
    xml = post("/ivr/more", {"SpeechResult": "yes"})
    # Either pipeline is acceptable: Record for Azure STT, Gather for Twilio.
    check("loops back to listen",
          "/ivr/recorded" in xml or "/ivr/process" in xml)
    xml = post("/ivr/more", {"SpeechResult": "no"})
    check("signs off on 'no'", "<Hangup/>" in xml)

    print("\n7. Low confidence reads the question back")
    xml = post("/ivr/process?attempt=1",
               {"SpeechResult": "how do I treat brown spots", "Confidence": "0.42"})
    check("asks for confirmation", "/ivr/verify" in xml)
    check("repeats what it heard", "I heard" in spoken(xml)[0])
    print(f"  says: {spoken(xml)[0]}")

    print("\n8. High confidence answers straight away")
    xml = post("/ivr/process?attempt=1",
               {"SpeechResult": "how do I treat brown spots on rice",
                "Confidence": "0.95"})
    check("skips confirmation", "/ivr/verify" not in xml)
    check("answers immediately", len(spoken(xml)[0].split()) > 6)
    print(f"  says: {spoken(xml)[0][:150]}")

    print("\n9. Confirming with 'yes' answers the question")
    xml = post("/ivr/verify?q=how%20do%20I%20treat%20brown%20spots&attempt=1",
               {"SpeechResult": "yes"})
    check("gives a real answer", len(spoken(xml)[0].split()) > 6)
    print(f"  says: {spoken(xml)[0][:150]}")

    print("\n10. Rejecting with 'no' re-listens")
    xml = post("/ivr/verify?q=wrong%20question&attempt=1",
               {"SpeechResult": "no"})
    check("asks again", "/ivr/process" in xml)
    print(f"  says: {spoken(xml)[0]}")


if __name__ == "__main__":
    main()
