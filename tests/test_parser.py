from parser import _extract_experience, _extract_skills, _first_match


def test_extracts_contact_fields():
    text = "Alex Morgan\nalex.morgan@example.com\n+1 (555) 123-4567"
    assert _first_match(r"([\w.+-]+@[\w-]+\.[\w.-]+)", text) == "alex.morgan@example.com"
    assert _first_match(r"(\+?\d[\d ().-]{7,}\d)", text) == "+1 (555) 123-4567"


def test_extracts_skills_and_experience():
    text = "Python, SQL, and React\nSoftware Engineer | 2020 - Present"
    assert _extract_skills(text) == ["python", "react", "sql"]
    assert _extract_experience(text) == ["Software Engineer | 2020 - Present"]
