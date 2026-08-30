# RAG System with RBAC + Guardrails — Run Instructions

You have **two versions**. Use the **Simple version** unless you have 15+ spare
minutes and a stable internet connection.

| | Simple (`simple_rag.py`) | Advanced (`advanced_rag.py`) |
|---|---|---|
| Setup time | 0 min (uses only scikit-learn) | 5–10 min (installs + model download) |
| Retrieval method | TF-IDF + cosine similarity | Real sentence embeddings + FAISS |
| Works fully offline | Yes | No (needs internet once, to download the embedding model) |
| Good enough for a demo/submission | Yes | Yes (slightly more "textbook RAG") |

---

## 1. Simple version — recommended, fastest

### Step 1 — Check Python is installed
```bash
python3 --version
```
Any Python 3.8+ works.

### Step 2 — Install the one dependency (usually already present)
```bash
pip install scikit-learn
```

### Step 3 — Run it
```bash
python3 simple_rag.py
```

That's it. You'll see 4 demo queries run automatically, showing:
- A normal employee query being answered ✅
- An employee being **blocked by RBAC** from a salary-related doc ❌
- An HR user successfully retrieving that same salary doc ✅
- A prompt-injection style query being **blocked by the guardrail** 🚫

### Step 4 (optional) — Get real LLM-generated answers instead of extractive ones
If you have an Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-key-here"
python3 simple_rag.py
```
Without a key, the script still works — it just returns the retrieved
context directly as the "answer" (clearly labeled as extractive), which is
completely fine for demonstrating the RAG + RBAC + guardrail pipeline.

---

## 2. Advanced version — only if you have extra time

### Step 1 — Install dependencies
```bash
pip install sentence-transformers faiss-cpu
```
(This downloads a small ~80MB embedding model the first time you run it —
needs internet, takes 1-3 minutes depending on connection.)

### Step 2 — Run it
```bash
python3 advanced_rag.py
```
It reuses the same documents, RBAC rules, and guardrails from
`simple_rag.py`, but retrieves using real semantic embeddings instead of
TF-IDF.

---

## 3. Ready-made dataset (already generated for you)

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

## 4. Using your OWN PDFs / spreadsheets instead of the sample text

Replace the hardcoded `DOCUMENTS` list in `simple_rag.py` with content
extracted from real files:

```bash
pip install pypdf openpyxl pandas
```

```python
from pypdf import PdfReader
import pandas as pd

# PDF -> text
reader = PdfReader("your_file.pdf")
pdf_text = "\n".join(page.extract_text() for page in reader.pages)

# XLSX -> text
df = pd.read_excel("your_file.xlsx")
xlsx_text = df.to_string()

DOCUMENTS = [
    Document(doc_id="d1", source="your_file.pdf", text=pdf_text,
             allowed_roles=["employee", "manager", "hr", "admin"]),
    Document(doc_id="d2", source="your_file.xlsx", text=xlsx_text,
             allowed_roles=["hr", "admin"]),
]
```

For longer documents, split `pdf_text` into smaller chunks (e.g. every
500 words) and create one `Document` per chunk — this improves retrieval
quality since TF-IDF/embeddings work better on focused passages.

---

## 5. What to say in your submission write-up

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
