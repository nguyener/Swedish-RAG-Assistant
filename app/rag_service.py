from __future__ import annotations

from openai import OpenAI

from app.config import settings
from app.vector_store import query

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """
You are a patient information assistant for a RAG demo using public Swedish Health Services content.
Rules:
- Answer only from the provided context.
- Do not diagnose, prescribe, triage, or give treatment advice.
- For urgent or emergency symptoms, tell the user to call 911 or contact a clinician immediately.
- If the context does not contain the answer, say you do not know based on the available Swedish public information.
- Include concise source URLs at the end.
""".strip()


def build_context(results: dict) -> tuple[str, list[str]]:
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    blocks = []
    sources = []
    for doc, meta in zip(docs, metas):
        source = meta.get("source", "unknown") if meta else "unknown"
        title = meta.get("title", "") if meta else ""
        sources.append(source)
        blocks.append(f"Source: {source}\nTitle: {title}\nContent: {doc}")
    unique_sources = list(dict.fromkeys(sources))
    return "\n\n---\n\n".join(blocks), unique_sources


def answer_question(question: str, top_k: int = 5) -> dict:
    results = query(question, top_k=top_k)
    context, sources = build_context(results)

    user_prompt = f"""
Context:
{context}

Question:
{question}
""".strip()

    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    return {
        "answer": response.choices[0].message.content,
        "sources": sources,
    }
