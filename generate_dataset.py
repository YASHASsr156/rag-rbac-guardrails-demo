"""
Generates a small, realistic "company knowledge base" dataset:
3 PDFs + 2 spreadsheets, mixing general-access and restricted documents,
so the RAG + RBAC + guardrail pipeline has something meaningful to
demonstrate access control on.

Run once:  python3 generate_dataset.py
Output:    ./dataset/*.pdf, ./dataset/*.xlsx
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

OUT = "dataset"
os.makedirs(OUT, exist_ok=True)
styles = getSampleStyleSheet()


def make_pdf(filename, title, paragraphs):
    doc = SimpleDocTemplate(os.path.join(OUT, filename), pagesize=letter)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 16)]
    for p in paragraphs:
        story.append(Paragraph(p, styles["Normal"]))
        story.append(Spacer(1, 10))
    doc.build(story)
    print(f"Created {filename}")


# ---------------------------------------------------------------------------
# PDF 1 — General access (everyone)
# ---------------------------------------------------------------------------
make_pdf(
    "employee_handbook.pdf",
    "Employee Handbook",
    [
        "All full-time employees are entitled to 18 days of paid annual leave "
        "and 10 days of paid sick leave per calendar year.",
        "Leave requests must be submitted at least 3 working days in advance "
        "through the HR portal, except for sick leave which may be reported "
        "on the day of absence.",
        "The standard work week is 40 hours, Monday to Friday. Core hours "
        "are 10:00 AM to 4:00 PM, with flexible start and end times outside "
        "of that window.",
        "Employees working from home more than 2 days a week must submit a "
        "remote work agreement to their manager and HR.",
        "New employees complete a 90-day probation period, during which "
        "either party may terminate employment with 1 week's notice.",
    ],
)

# ---------------------------------------------------------------------------
# PDF 2 — General access (everyone)
# ---------------------------------------------------------------------------
make_pdf(
    "it_security_policy.pdf",
    "IT Security Policy",
    [
        "All company-issued laptops must have full-disk encryption enabled "
        "(BitLocker on Windows, FileVault on macOS) before first use.",
        "VPN access is mandatory whenever connecting to internal systems "
        "(HR portal, finance systems, internal wikis) from outside the "
        "office network.",
        "Passwords must be at least 14 characters, changed every 90 days, "
        "and multi-factor authentication is required for all company "
        "accounts including email and Slack.",
        "Any suspected phishing email should be forwarded to "
        "security@company.com and not clicked on or replied to.",
        "USB storage devices are disabled by default on company laptops; "
        "exceptions require written approval from the IT security team.",
    ],
)

# ---------------------------------------------------------------------------
# PDF 3 — RESTRICTED (hr, admin only): confidential HR policy
# ---------------------------------------------------------------------------
make_pdf(
    "hr_disciplinary_policy_confidential.pdf",
    "Confidential: Employee Disciplinary Procedure",
    [
        "This document outlines the internal disciplinary escalation "
        "process and is restricted to HR and senior management only.",
        "Stage 1: Verbal warning, recorded privately in the employee's HR "
        "file, not disclosed to the wider team.",
        "Stage 2: Written warning issued after a repeat incident within 6 "
        "months, requiring sign-off from both the employee's manager and "
        "an HR business partner.",
        "Stage 3: Final written warning with a Performance Improvement Plan "
        "(PIP), reviewed every 2 weeks for a maximum of 8 weeks.",
        "Termination for cause requires approval from HR leadership and "
        "Legal, and must be documented with a full incident timeline before "
        "any conversation with the employee.",
    ],
)

# ---------------------------------------------------------------------------
# XLSX 1 — RESTRICTED (hr, admin only): salary bands
# ---------------------------------------------------------------------------
salary_df = pd.DataFrame({
    "Band": ["A", "B", "C", "D", "E"],
    "Level": ["Associate", "Senior Associate", "Manager", "Senior Manager", "Director"],
    "Min LPA": [6, 10, 18, 30, 45],
    "Max LPA": [10, 18, 30, 45, 70],
})
salary_df.to_excel(os.path.join(OUT, "salary_bands_confidential.xlsx"), index=False)
print("Created salary_bands_confidential.xlsx")

# ---------------------------------------------------------------------------
# XLSX 2 — RESTRICTED (manager, admin): Q3 project budget
# ---------------------------------------------------------------------------
budget_df = pd.DataFrame({
    "Project": ["RAG Platform", "Mobile App Revamp", "Data Warehouse Migration", "Customer Portal"],
    "Q3 Budget (USD)": [120000, 85000, 200000, 60000],
    "Spent So Far (USD)": [95000, 40000, 150000, 22000],
    "Status": ["On Track", "On Track", "At Risk", "On Track"],
})
budget_df.to_excel(os.path.join(OUT, "project_budget_q3_confidential.xlsx"), index=False)
print("Created project_budget_q3_confidential.xlsx")

print("\nDone. Files are in ./dataset/")
