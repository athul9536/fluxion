"""Tiny append-only logger so call flow can be inspected after a call."""
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "call_log.txt"


def log(message: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
