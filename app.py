import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from models import db, Resume
from parser import parse_resume_pdf

load_dotenv()

ALLOWED_EXTENSIONS = {"pdf"}


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://resume_user:resume_password@localhost:5432/resume_parser"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        resumes = Resume.query.order_by(Resume.created_at.desc()).all()
        return render_template("index.html", resumes=resumes)

    @app.post("/upload")
    def upload():
        uploaded_file = request.files.get("resume")
        if not uploaded_file or not uploaded_file.filename:
            flash("Choose a PDF resume to upload.", "error")
            return redirect(url_for("index"))

        filename = secure_filename(uploaded_file.filename)
        if not filename.lower().endswith(".pdf"):
            flash("Only PDF files are supported.", "error")
            return redirect(url_for("index"))

        file_path = Path(app.config["UPLOAD_FOLDER"]) / filename
        uploaded_file.save(file_path)
        try:
            parsed = parse_resume_pdf(file_path)
            resume = Resume.from_parsed_data(filename, parsed)
            db.session.add(resume)
            db.session.commit()
            flash(f"Parsed {filename} successfully.", "success")
        except Exception as error:
            db.session.rollback()
            app.logger.exception("Resume parsing failed")
            flash(f"Could not parse this resume: {error}", "error")
        finally:
            file_path.unlink(missing_ok=True)

        return redirect(url_for("index"))

    @app.get("/resume/<int:resume_id>")
    def resume_detail(resume_id):
        resume = db.get_or_404(Resume, resume_id)
        return render_template("resume_detail.html", resume=resume)

    @app.get("/search")
    def search():
        query = request.args.get("q", "").strip()
        resumes = Resume.search(query) if query else Resume.query.order_by(Resume.created_at.desc()).all()
        return render_template("index.html", resumes=resumes, query=query)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
