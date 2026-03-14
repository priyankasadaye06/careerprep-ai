import pdfkit
import os


from flask import Flask, render_template, request, session, redirect, make_response

from mock.sample_resume_data import get_sample_resume_data
from logic.role_bullets import get_role_based_bullets
from logic.template_parser import extract_template_fields
from logic.role_fields import ROLE_FIELDS



from interview.resume_parser import extract_text_from_pdf
from interview.resume_parser import extract_skills_from_resume
from interview.question_generator import generate_questions


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "careerprep_secret"


# PDF configuration
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- LANDING ----------------
@app.route("/")
def landing():
    return render_template("landing.html")


# ---------------- TEMPLATE SELECTION ----------------
@app.route("/resume")
def resume_templates():
    return render_template("template_select.html")


@app.route("/select-template", methods=["POST"])
def select_template():
    session["template"] = request.form.get("template")
    return redirect("/roles")


# ---------------- ROLE SELECTION ----------------
@app.route("/roles")
def roles():
    return render_template("role_select.html")


@app.route("/set-role/<role>")
def set_role(role):
    role_map = {
        "software-engineer": "Software Engineer",
        "data-analyst": "Data Analyst",
        "ml-engineer": "ML Engineer",
        "web-developer": "Web Developer"
    }

    clean_role = role.replace("-", " ").title()
    session["role"] = role_map.get(role, clean_role)

    return redirect("/resume-form")


# ---------------- RESUME FORM ----------------
@app.route("/resume-form")
def resume_form():

    template = session.get("template")
    role = session.get("role")

    if not template:
        return redirect("/resume")

    template_fields = extract_template_fields(template)

    role_fields = ROLE_FIELDS.get(role, [])

    return render_template(
        "form.html",
        template_fields=template_fields,
        role_fields=role_fields,
        role=role
    )



def process_form_data(form):

    data = {}

    for key in form:
        data[key] = form.get(key)

    return data


# ---------------- PREVIEW ----------------
def process_form_data(form):


    data = {}

    data["name"] = form.get("name")
    data["email"] = form.get("email")
    data["phone"] = form.get("phone")
    data["location"] = form.get("location")
    data["linkedin"] = form.get("linkedin")
    data["github"] = form.get("github")

    data["summary"] = form.get("summary")

# EDUCATION
    data["education"] = [
        {
            "degree": form.get("degree"),
            "college": form.get("college"),
            "year": form.get("year")
        }
    ]   

# SKILLS
    data["skills"] = {
        "languages": form.get("languages", "").split(","),
        "frameworks": form.get("frameworks", "").split(","),
        "tools": form.get("tools", "").split(","),
        "databases": form.get("databases", "").split(",")
    }

# EXPERIENCE
    data["experience"] = [
        {
            "role": form.get("exp_role"),
            "company": form.get("exp_company"),
            "duration": form.get("exp_duration"),
            "location": form.get("exp_location"),
            "points": form.get("exp_points", "").split("\n")
        }
    ]
    return data



@app.route("/preview", methods=["POST"])
def preview():


    data = process_form_data(request.form)

    role = session.get("role")
    data["role"] = role

    data["role_bullets"] = get_role_based_bullets(role)

    template = session.get("template", "template1")

    return render_template(f"resumes/{template}.html", **data)





# ----------------DOWNLOAD PDF ----------------
@app.route("/download-resume", methods=["POST"])
def download_resume():

    html = request.form.get("resume_html")

    pdf = pdfkit.from_string(html, False, configuration=config)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=resume.pdf"

    return response



# -------------- RESUME UPLOAD -----------------


@app.route("/upload-resume", methods=["POST"])
def upload_resume():

    file = request.files["resume"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    text = extract_text_from_pdf(path)

    skills = extract_skills_from_resume(text)

    questions = generate_questions(skills)

    session["questions"] = questions
    session["q_index"] = 0

    return render_template(
        "chat_interview.html",
        question=questions[0]
    )






# ---------------- INTERVIEW ----------------
@app.route("/interview")
def interview_training():
    return render_template("interview_home.html")


# ----------------Resume analysis -------------
@app.route("/analyze-resume")
def analyze_resume():

    path = session.get("resume_path")

    if not path:
        return redirect("/interview")

    text = extract_text_from_pdf(path)

    skills = extract_skills_from_resume(text)

    questions = generate_questions(skills)

    return render_template(
        "mock_interview.html",
        questions=questions
    )



# ----------------- MOCK INTERVIEW --------------
@app.route("/mock-interview")
def mock_interview():
    return render_template("mock_interview.html")



@app.route("/submit-interview", methods=["POST"])
def submit_interview():

    answers = []

    for key in request.form:
        answers.append(request.form[key])

    return render_template(
        "interview_result.html",
        answers=answers
    )



# ------------ Next question chat bot -------------

@app.route("/next-question", methods=["POST"])
def next_question():

    questions = session.get("questions")
    index = session.get("q_index", 0)

    index += 1

    if index >= len(questions):

        return "<h2>Interview Completed</h2>"

    session["q_index"] = index

    return render_template(
        "chat_interview.html",
        question=questions[index]
    )













if __name__ == "__main__":
    app.run(debug=True)