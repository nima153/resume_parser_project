from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_


db = SQLAlchemy()


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False, default="Unknown")
    email = db.Column(db.String(255))
    phone = db.Column(db.String(100))
    location = db.Column(db.String(255))
    skills = db.Column(db.JSON, nullable=False, default=list)
    education = db.Column(db.JSON, nullable=False, default=list)
    experience = db.Column(db.JSON, nullable=False, default=list)
    raw_text = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_parsed_data(cls, filename, parsed):
        return cls(filename=filename, **parsed)

    @classmethod
    def search(cls, query):
        pattern = f"%{query}%"
        return cls.query.filter(
            or_(cls.name.ilike(pattern), cls.email.ilike(pattern), cls.raw_text.ilike(pattern))
        ).order_by(cls.created_at.desc()).all()
