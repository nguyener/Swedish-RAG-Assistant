from __future__ import annotations

import tiktoken


def chunk_text(text: str, chunk_tokens: int = 450, overlap_tokens: int = 75) -> list[str]:
    if not text:
        return []
    if overlap_tokens >= chunk_tokens:
        raise ValueError("overlap_tokens must be smaller than chunk_tokens")

    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_tokens, len(tokens))
        chunk = enc.decode(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(tokens):
            break
        start = end - overlap_tokens
    return chunks
