import re
from pathlib import Path

import pdfplumber
import spacy


SKILL_VOCABULARY = {
    "python", "java", "javascript", "typescript", "react", "angular", "vue", "flask",
    "django", "sql", "postgresql", "mysql", "mongodb", "aws", "azure", "docker",
    "kubernetes", "git", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "machine learning", "deep learning", "nlp", "excel", "tableau", "power bi",
}

try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    NLP = spacy.blank("en")


def extract_text(pdf_path: Path) -> str:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def _first_match(pattern, text):
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_name(text, doc):
    for entity in doc.ents:
        if entity.label_ == "PERSON":
            return entity.text.strip()
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "Unknown")
    return first_line[:255]


def _extract_skills(text):
    normalized_text = text.lower()
    return sorted(skill for skill in SKILL_VOCABULARY if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", normalized_text))


def _extract_education(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    keywords = ("university", "college", "institute", "bachelor", "master", "ph.d", "degree", "education")
    return list(dict.fromkeys(line[:500] for line in lines if any(keyword in line.lower() for keyword in keywords)))[:10]


def _extract_experience(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    date_pattern = re.compile(r"\b(?:19|20)\d{2}\s*(?:-|to|–)\s*(?:present|(?:19|20)\d{2})\b", re.I)
    return list(dict.fromkeys(line[:500] for line in lines if date_pattern.search(line)))[:20]


def parse_resume_pdf(pdf_path: Path):
    raw_text = extract_text(pdf_path)
    doc = NLP(raw_text)
    return {
        "name": _extract_name(raw_text, doc),
        "email": _first_match(r"([\w.+-]+@[\w-]+\.[\w.-]+)", raw_text),
        "phone": _first_match(r"(\+?\d[\d ().-]{7,}\d)", raw_text),
        "location": _first_match(r"(?:location|address)\s*[:|-]\s*(.+)", raw_text),
        "skills": _extract_skills(raw_text),
        "education": _extract_education(raw_text),
        "experience": _extract_experience(raw_text),
        "raw_text": raw_text,
    }
