"""Tiny in-process counters for dashboard stats (no Redis, by design)."""

from dataclasses import dataclass


@dataclass
class Counters:
    questions_asked: int = 0


counters = Counters()
