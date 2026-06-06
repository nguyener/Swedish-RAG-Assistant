from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from app.chunking import chunk_text
from app.scraper import fetch_page
from app.vector_store import add_documents


def stable_id(url: str, index: int) -> str:
    digest = hashlib.sha256(f"{url}:{index}".encode("utf-8")).hexdigest()[:24]
    return f"doc-{digest}"


def ingest_urls(urls: list[str]) -> int:
    total = 0
    for url in urls:
        print(f"Fetching {url}")
        page = fetch_page(url)
        chunks = chunk_text(page.text)
        if not chunks:
            print(f"No text extracted from {url}")
            continue

        ids = [stable_id(url, i) for i in range(len(chunks))]
        metadatas = [
            {"source": url, "title": page.title, "chunk_index": i}
            for i in range(len(chunks))
        ]
        add_documents(ids=ids, docs=chunks, metadatas=metadatas)
        print(f"Indexed {len(chunks)} chunks from {url}")
        total += len(chunks)
    return total


def load_urls(path: str) -> list[str]:
    return [line.strip() for line in Path(path).read_text().splitlines() if line.strip() and not line.startswith("#")]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Swedish public pages into Chroma")
    parser.add_argument("--urls-file", default="data/seed_urls/swedish_urls.txt")
    args = parser.parse_args()
    count = ingest_urls(load_urls(args.urls_file))
    print(f"Done. Indexed {count} chunks.")
