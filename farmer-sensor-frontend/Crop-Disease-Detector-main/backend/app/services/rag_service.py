"""Simple keyword-based retrieval over a local agricultural knowledge base.

Deliberately no embeddings and no vector database. Chunks live in
app/data/knowledge_base.json. Scoring is transparent keyword overlap, so it is
easy to reason about during a demo and easy to replace with a real retriever
later without touching the API layer.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_KB_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge_base.json"

# A single incidental word match is not enough to call a chunk relevant.
MIN_SCORE = 2.0

STOPWORDS = {
    "a", "about", "after", "all", "am", "an", "and", "any", "are", "as", "at",
    "be", "been", "before", "best", "but", "by", "can", "could", "did", "do",
    "does", "doing", "for", "from", "get", "give", "good", "has", "have", "how",
    "i", "if", "in", "is", "it", "its", "just", "know", "like", "me", "much",
    "my", "need", "no", "not", "now", "of", "on", "or", "our", "please", "should",
    "so", "some", "tell", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "to", "too", "up", "use", "very", "was", "we",
    "what", "when", "where", "which", "while", "who", "why", "will", "with",
    "would", "you", "your",
}

SYNONYMS = {
    "paddy": ["rice"],
    "nellu": ["rice"],
    "palm": ["coconut"],
    "thenga": ["coconut"],
    "manure": ["fertilizer"],
    "fertiliser": ["fertilizer"],
    "feeding": ["fertilizer"],
    "watering": ["irrigation", "water"],
    "irrigating": ["irrigation", "water"],
    "irrigate": ["irrigation", "water"],
    "rains": ["monsoon", "rain"],
    "rainy": ["monsoon"],
    "bug": ["pest"],
    "bugs": ["pest"],
    "insects": ["pest"],
    "fungus": ["disease"],
    "infection": ["disease"],
    "sick": ["disease"],
    "spot": ["spots"],
    "yellowing": ["yellow"],
    "browning": ["brown"],
}


@dataclass
class Chunk:
    id: str
    crop: str
    topic: str
    title: str
    keywords: list[str]
    text: str


def _load_chunks() -> list[Chunk]:
    try:
        with _KB_PATH.open(encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Could not load knowledge base: %s", exc)
        return []
    return [
        Chunk(
            id=item["id"],
            crop=item.get("crop", "General"),
            topic=item.get("topic", "general"),
            title=item.get("title", item["id"]),
            keywords=[k.lower() for k in item.get("keywords", [])],
            text=item["text"],
        )
        for item in raw
    ]


class RAGService:
    def __init__(self) -> None:
        self.chunks = _load_chunks()

    @staticmethod
    def extract_keywords(question: str) -> list[str]:
        words = re.findall(r"[a-zA-Z]+", (question or "").lower())
        keywords: list[str] = []
        for word in words:
            if len(word) < 3 or word in STOPWORDS:
                continue
            if word not in keywords:
                keywords.append(word)
            for extra in SYNONYMS.get(word, []):
                if extra not in keywords:
                    keywords.append(extra)
        return keywords

    def _score(self, chunk: Chunk, keywords: list[str]) -> float:
        score = 0.0
        haystack = f"{chunk.title} {chunk.text}".lower()
        for kw in keywords:
            if kw in chunk.keywords:
                score += 3.0
            elif kw in chunk.crop.lower() or kw in chunk.topic.lower():
                score += 2.0
            elif kw in haystack:
                score += 1.0
        return score

    def retrieve(
        self, question: str, hints: list[str] | None = None, limit: int = 4
    ) -> list[Chunk]:
        keywords = self.extract_keywords(question)
        for hint in hints or []:
            keywords.extend(self.extract_keywords(hint))
        if not keywords or not self.chunks:
            return []

        scored = [(self._score(c, keywords), c) for c in self.chunks]
        # Require a real keyword hit. Returning arbitrary chunks for an
        # unrelated question (e.g. "how do I grow tomatoes") would ground the
        # answer in irrelevant text, which is worse than no context at all.
        scored = [pair for pair in scored if pair[0] >= MIN_SCORE]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]

    @staticmethod
    def format_context(chunks: list[Chunk]) -> str:
        return "\n\n".join(
            f"[{i + 1}] {c.crop} / {c.topic} - {c.title}\n{c.text}"
            for i, c in enumerate(chunks)
        )


rag_service = RAGService()
