rag = SimpleRAG(docs)

for role, query in [
    ("employee", "How many leave days do I get?"),
    ("employee", "What is the salary band for a manager?"),
    ("hr", "What is the salary band for a manager?"),
]:
    print(f"\n>>> ROLE: {role} | QUERY: {query}")
    retrieved = rag.retrieve(query, role)
    print("Retrieved:", [d.source for d in retrieved])
    print("Answer:", rag.generate_answer(query, retrieved))

--------------------------------------------------------------------------------

for role, query in [
    ("manager", "What is the Q3 budget for the RAG platform project?"),
    ("employee", "What is the Q3 budget for the RAG platform project?"),
]:
    print(f"\n>>> ROLE: {role} | QUERY: {query}")
    retrieved = rag.retrieve(query, role)
    print("Retrieved:", [d.source for d in retrieved])
    print("Answer:", rag.generate_answer(query, retrieved))
