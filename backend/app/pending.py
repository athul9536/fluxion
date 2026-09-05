"""In-memory store for answers being prepared while the caller waits.

Transcribing a recording and asking the LLM takes several seconds. Rather
than leaving the caller in silence, the work runs in a background thread and
the call polls here until the answer is ready.

In-memory is fine for a single-process demo. A multi-worker deployment would
need Redis or similar.
"""
import threading
from typing import Callable, Optional

_lock = threading.Lock()
_jobs: dict[str, dict] = {}


def start(call_sid: str, work: Callable[[], tuple[str, str]]) -> None:
    """Run `work` in the background, storing its (question, answer) result."""
    with _lock:
        _jobs[call_sid] = {"done": False, "question": "", "answer": ""}

    def runner() -> None:
        try:
            question, answer = work()
        except Exception as e:  # never leave a job hanging
            print(f"pending job failed for {call_sid}: {e}")
            question, answer = "", ""
        with _lock:
            _jobs[call_sid] = {"done": True, "question": question,
                               "answer": answer}

    threading.Thread(target=runner, daemon=True).start()


def result(call_sid: str) -> Optional[dict]:
    """Return the job if finished, None while still working or unknown."""
    with _lock:
        job = _jobs.get(call_sid)
        if job and job["done"]:
            return job
    return None


def discard(call_sid: str) -> None:
    with _lock:
        _jobs.pop(call_sid, None)
