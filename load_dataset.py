"""
Loads real PDF/XLSX files from ./dataset/ into the Document format used by
simple_rag.py / advanced_rag.py, with RBAC roles assigned automatically
based on filename convention:

    *_confidential.pdf / *_confidential.xlsx  -> restricted document
    everything else                            -> general access

Edit ROLE_MAP below to control exactly who can see which file.

Usage:
    python3 load_dataset.py          # quick sanity check / preview
    (or import load_documents() from your own script — see bottom)
"""

import os
from pypdf import PdfReader
import pandas as pd

from simple_rag import Document, SimpleRAG, guardrail_check_input

DATASET_DIR = "dataset"

# Explicit RBAC mapping — who is allowed to see each file.
# Anything not listed here defaults to ["employee", "manager", "hr", "admin"]
# (i.e. general access) unless its filename contains "confidential", in
# which case it defaults to ["hr", "admin"].
ROLE_MAP = {
    "employee_handbook.pdf": ["employee", "manager", "hr", "admin"],
    "it_security_policy.pdf": ["employee", "manager", "hr", "admin"],
    "hr_disciplinary_policy_confidential.pdf": ["hr", "admin"],
    "salary_bands_confidential.xlsx": ["hr", "admin"],
    "project_budget_q3_confidential.xlsx": ["manager", "admin"],
}


def _extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_xlsx_text(path: str) -> str:
    df = pd.read_excel(path)
    return df.to_string(index=False)


def load_documents(dataset_dir: str = DATASET_DIR) -> list[Document]:
    documents = []
    for i, filename in enumerate(sorted(os.listdir(dataset_dir)), start=1):
        path = os.path.join(dataset_dir, filename)
        if filename.lower().endswith(".pdf"):
            text = _extract_pdf_text(path)
        elif filename.lower().endswith((".xlsx", ".xls")):
            text = _extract_xlsx_text(path)
        else:
            continue

        roles = ROLE_MAP.get(
            filename,
            ["hr", "admin"] if "confidential" in filename.lower()
            else ["employee", "manager", "hr", "admin"],
        )

        documents.append(Document(
            doc_id=f"d{i}",
            source=filename,
            text=text,
            allowed_roles=roles,
        ))
    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from ./{DATASET_DIR}/\n")
    for d in docs:
        print(f"- {d.source}  (roles: {d.allowed_roles})")
        print(f"  preview: {d.text[:80].strip()}...\n")

    # quick end-to-end test using the real dataset
    rag = SimpleRAG(docs)

    print("=" * 60)
    print("DEMO QUERIES ON REAL DATASET")
    print("=" * 60)

    tests = [
        ("employee", "How many leave days do I get?"),
        ("employee", "What is the salary band for a manager?"),   # should be blocked
        ("hr", "What is the salary band for a manager?"),         # should work
        ("manager", "What is the Q3 budget for the RAG platform project?"),
        ("employee", "What is the Q3 budget for the RAG platform project?"),  # blocked
    ]
    for role, query in tests:
        print(f"\n>>> ROLE: {role} | QUERY: {query}")
        if guardrail_check_input(query):
            print(guardrail_check_input(query))
            continue
        retrieved = rag.retrieve(query, role)
        print(f"Retrieved: {[d.source for d in retrieved]}")
        print("ANSWER:", rag.generate_answer(query, retrieved))
