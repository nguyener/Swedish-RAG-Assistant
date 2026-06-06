from __future__ import annotations

import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)
chroma_client = chromadb.PersistentClient(
    path=settings.chroma_path,
    settings=ChromaSettings(anonymized_telemetry=False),
)
collection = chroma_client.get_or_create_collection(name=settings.collection_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    result = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [item.embedding for item in result.data]


def add_documents(ids: list[str], docs: list[str], metadatas: list[dict]) -> None:
    embeddings = embed_texts(docs)
    collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)


def query(question: str, top_k: int = 5) -> dict:
    question_embedding = embed_texts([question])[0]
    return collection.query(query_embeddings=[question_embedding], n_results=top_k)
