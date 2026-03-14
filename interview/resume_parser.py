import PyPDF2

def extract_text_from_pdf(filepath):

    text = ""

    with open(filepath, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()

    return text


def extract_skills_from_resume(text):

    skills_db = [
        "python",
        "sql",
        "machine learning",
        "flask",
        "pandas",
        "numpy",
        "tensorflow",
        "pytorch",
        "excel",
        "power bi",
        "git",
        "docker"
    ]

    found_skills = []

    text = text.lower()

    for skill in skills_db:
        if skill in text:
            found_skills.append(skill)

    return found_skills