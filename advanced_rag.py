"""
ADVANCED RAG SYSTEM (optional upgrade — needs 2 pip installs + a small
one-time model download, so only use this if you have spare time /
working internet before the deadline).

Retrieval:   Real sentence embeddings (sentence-transformers) + FAISS
             vector search, instead of TF-IDF.
Generation:  Same as simple_rag.py (Anthropic API if key set, else
             extractive fallback).
RBAC:        Same role-based filtering as simple_rag.py.
Guardrails:  Same as simple_rag.py.

Install first:
    pip install sentence-transformers faiss-cpu

Run:
    python3 advanced_rag.py
"""

import os
from dataclasses import dataclass, field
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from simple_rag import (   # reuse documents, guardrails, LLM call
    DOCUMENTS,
    Document,
    guardrail_check_input,
    SYSTEM_PROMPT,
)


class AdvancedRAG:
    def __init__(self, documents: List[Document]):
        self.documents = documents
        # small, fast, good-quality embedding model (~80MB download, once)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = self.model.encode([d.text for d in documents])
        self.embeddings = np.array(embeddings).astype("float32")

    def retrieve(self, query: str, user_role: str, top_k: int = 2) -> List[Document]:
        allowed_idx = [i for i, d in enumerate(self.documents) if user_role in d.allowed_roles]
        if not allowed_idx:
            return []

        allowed_embeddings = self.embeddings[allowed_idx]
        index = faiss.IndexFlatIP(allowed_embeddings.shape[1])  # cosine-ish via normalized vectors
        norm_embeddings = allowed_embeddings / np.linalg.norm(allowed_embeddings, axis=1, keepdims=True)
        index.add(norm_embeddings)

        query_vec = self.model.encode([query]).astype("float32")
        query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

        scores, indices = index.search(query_vec, min(top_k, len(allowed_idx)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score > 0.2:  # relevance threshold
                results.append(self.documents[allowed_idx[idx]])
        return results

    def generate_answer(self, query: str, context_docs: List[Document]) -> str:
        if not context_docs:
            return ("I don't have permission-visible information to answer "
                    "that, or nothing relevant was found.")
        context = "\n".join(f"- ({d.source}) {d.text}" for d in context_docs)

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return f"[Extractive answer — no LLM API key set]\n{context}"

        import json
        import urllib.request
        body = json.dumps({
            "model": "claude-sonnet-4-5",
            "max_tokens": 300,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {query}"}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={"Content-Type": "application/json", "x-api-key": api_key,
                     "anthropic-version": "2023-06-01"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            return data["content"][0]["text"]
        except Exception as e:
            return f"[LLM call failed: {e}] Falling back to context:\n{context}"


if __name__ == "__main__":
    rag = AdvancedRAG(DOCUMENTS)

    for role, query in [
        ("employee", "How many paid leave days do I get?"),
        ("employee", "What is the salary band for a manager?"),
        ("hr", "What is the salary band for a manager?"),
    ]:
        print(f"\n>>> ROLE: {role} | QUERY: {query}")
        blocked = guardrail_check_input(query)
        if blocked:
            print(blocked)
            continue
        docs = rag.retrieve(query, role)
        print(f"Retrieved: {[d.source for d in docs]}")
        print("ANSWER:", rag.generate_answer(query, docs))
