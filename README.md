# RAG System with RBAC + Guardrails

## Step 1 — Check Python is installed
```bash
python3 --version
```
Any Python 3.8+ works.

## Step 2 — Install the one dependency 
```bash
pip install scikit-learn
```
## Step 3 — Run it
```bash
python3 simple_rag.py
```
. You'll see 4 demo queries run automatically, showing:
- A normal employee query being answered
- An employee being **blocked by RBAC** from a salary-related doc
- An HR user successfully retrieving that same salary doc
- A prompt-injection style query being **blocked by the guardrail**
---


## Ready-made dataset (already generated for you)

The `dataset/` folder contains 5 realistic company files, already built and
ready to use — no need to generate your own to hit the deadline:

| File | Type | Access |
|---|---|---|
| `employee_handbook.pdf` | PDF | Everyone |
| `it_security_policy.pdf` | PDF | Everyone |
| `hr_disciplinary_policy_confidential.pdf` | PDF | HR, Admin only |
| `salary_bands_confidential.xlsx` | Spreadsheet | HR, Admin only |
| `project_budget_q3_confidential.xlsx` | Spreadsheet | Manager, Admin only |

**Run it:**
```bash
pip install pypdf pandas openpyxl
python3 load_dataset.py
```
This reads all 5 real files, extracts their text/table content, wraps them
in the `Document` format with the correct RBAC roles, and runs 5 demo
queries against `simple_rag.py` — including cases where an employee is
correctly blocked from confidential salary/budget data, exactly like the
earlier hardcoded demo but now on real files.

Want to regenerate or customize the dataset yourself? Run:
```bash
python3 generate_dataset.py
```
It rebuilds all 5 files from scratch (edit the text inside the script to
change content, or add more documents/roles).

---

## The Problem
Imagine a company has a bunch of internal files — an employee handbook, an IT policy, salary sheets, budget spreadsheets, HR disciplinary records. Different people should see different things:
•	Everyone can read the handbook
•	Only HR should see salary numbers
•	Only managers should see budget numbers
•	Only HR should see disciplinary records
Now imagine you want an AI chatbot that can answer questions about all of this — like "how many leave days do I get?" or "what's the manager salary band?" The problem: if you just feed all the documents to an AI, anyone who asks gets an answer, even if they shouldn't have access to that info. A regular employee could ask about salaries and the AI would happily tell them.

## What this project does
It's a smart Q&A system that:
1.	Reads real documents (PDFs and spreadsheets) — like the AI's "library"
2.	Finds the relevant piece of a document when someone asks a question, instead of guessing or making things up
3.	Checks who's asking first — before it even looks for an answer, it checks: "does this person's role allow them to see this document?" If not, that document is completely excluded from consideration — the AI won't even peek at it
4.	Refuses to answer if it shouldn't — if there's no permitted document that answers the question, it says "I don't have access to that" instead of guessing.

---

## Working

**Architecture:**
`User Query → Guardrail Input Check → RBAC-Filtered Retrieval (TF-IDF/embeddings) → Context Assembly → LLM Generation (constrained to context) → Answer`

**RBAC:** Each document is tagged with the roles allowed to see it
(`allowed_roles`). Retrieval filters out documents the querying user's role
isn't permitted to access — even if that document is the most topically
relevant match. This is enforced *before* similarity ranking, not after, so
restricted content is never exposed even indirectly.

**Guardrails implemented:**
1. **Input guardrail** — blocks queries containing prompt-injection patterns
   (e.g. "ignore previous instructions").
2. **Grounding guardrail** — if no relevant context is retrieved, the system
   refuses to answer rather than letting the LLM hallucinate.
3. **System-prompt constraint** — the LLM is explicitly instructed to answer
   only from the provided context and never from its own general knowledge.

**Possible "future work" line for extra credit:** swap TF-IDF for the
embeddings+FAISS version, add per-query audit logging, add an output
guardrail (e.g. PII redaction) on the generated answer.
