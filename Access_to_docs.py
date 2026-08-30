from load_dataset import load_documents
from simple_rag import SimpleRAG, guardrail_check_input

docs = load_documents()
for d in docs:
    print(d.source, "->", d.allowed_roles)
