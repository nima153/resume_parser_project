# Resume Atlas

A small end-to-end automated resume parser using `pdfplumber`, `spaCy`, Flask, and PostgreSQL.

## What it does

- Uploads PDF resumes through a Flask UI.
- Extracts raw text page by page with `pdfplumber`.
- Uses spaCy named-entity recognition when `en_core_web_sm` is installed.
- Detects common skills, email, phone, location, education, and dated experience entries.
- Stores parsed profiles and source text in PostgreSQL.
- Searches indexed profiles by name, email, or extracted text.

The parser deliberately keeps rule-based extraction visible and easy to extend. Resume layouts vary widely, so production accuracy should be improved with labeled examples, section-aware parsing, and validation against real resumes.

## Prerequisites

- Python 3.11 or newer
- Docker Desktop (recommended for PostgreSQL)

## Setup on Windows

Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
Copy-Item .env.example .env
docker compose up -d postgres
python app.py
```

Open http://127.0.0.1:5000.

If PowerShell blocks activation, run the commands through `\.venv\Scripts\python.exe` directly or adjust the local execution policy for your user account.

## PostgreSQL without Docker

Create a database and user, then set `DATABASE_URL` in `.env`:

```text
DATABASE_URL=postgresql+psycopg://resume_user:resume_password@localhost:5432/resume_parser
```

Tables are created automatically when the application starts. For a larger deployment, replace `db.create_all()` with Alembic migrations.

## Project map

- `app.py`: Flask application factory and HTTP routes.
- `parser.py`: PDF extraction and NLP/rule-based parsing.
- `models.py`: PostgreSQL-backed resume model and search query.
- `templates/`: upload, search, and profile detail views.
- `static/styles.css`: responsive interface styling.
- `docker-compose.yml`: local PostgreSQL service.

## Next production steps

1. Add authentication and per-user data isolation.
2. Move uploads to object storage and scan files before parsing.
3. Add database migrations, pagination, and structured JSONB indexes.
4. Create a labeled resume test set and measure field-level precision/recall.
5. Add background jobs for large batches instead of parsing inside the request.
