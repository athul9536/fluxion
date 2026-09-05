"""Simple RAG - loads text files and does keyword matching.

No heavy dependencies. For MVP, we embed agricultural knowledge directly.
"""
from pathlib import Path
from typing import List

from ..config import settings

_knowledge_base: List[dict] = []
_loaded = False


def _load_docs():
    global _knowledge_base, _loaded
    if _loaded:
        return
    
    docs_path = Path(settings.rag_docs_path)
    if docs_path.exists():
        for file in docs_path.glob("**/*.txt"):
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")
                # Split into chunks
                chunks = _chunk_text(content)
                for chunk in chunks:
                    _knowledge_base.append({
                        "content": chunk,
                        "source": file.name
                    })
            except Exception as e:
                print(f"Failed to load {file}: {e}")
    
    _loaded = True
    print(f"RAG: Loaded {len(_knowledge_base)} chunks")


def _chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks by paragraphs or size."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    
    for para in paragraphs:
        if len(current) + len(para) < chunk_size:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n"
    
    if current:
        chunks.append(current.strip())
    
    return chunks


def retrieve(query: str, n_results: int = 3) -> List[dict]:
    """Simple keyword-based retrieval."""
    _load_docs()
    
    if not _knowledge_base:
        return []
    
    query_words = set(query.lower().split())
    scored = []
    
    for doc in _knowledge_base:
        content_lower = doc["content"].lower()
        # Count matching words
        score = sum(1 for word in query_words if word in content_lower)
        if score > 0:
            scored.append((score, doc))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    
    return [doc for _, doc in scored[:n_results]]


def get_context_string(query: str) -> str:
    """Get formatted context string for LLM prompt."""
    chunks = retrieve(query)
    if not chunks:
        return ""
    
    context_parts = []
    sources = set()
    for chunk in chunks:
        context_parts.append(chunk["content"])
        sources.add(chunk["source"])
    
    context = "\n\n".join(context_parts)
    return f"Relevant agricultural knowledge:\n{context}"
