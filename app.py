import pdfkit
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
from flask import Flask, render_template, request, session, redirect, make_response

from mock.sample_resume_data import get_sample_resume_data
from logic.role_bullets import get_role_based_bullets


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

    if not role:
        return redirect("/roles")

    return render_template(
        "form.html",
        template=template,
        role=role
    )


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



# -------------- INTERVIEW UPLOAD -----------------





@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    file = request.files["resume"]

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    session["resume_path"] = filepath

    return redirect("/analyze-resume")




# ---------------- INTERVIEW ----------------
@app.route("/interview")
def interview_training():
    return render_template("interview_home.html")


# ----------------Resume analysis -------------
@app.route("/analyze-resume")
def analyze_resume():

    resume_path = session.get("resume_path")

    if not resume_path:
        return redirect("/interview")

    return render_template("resume_analysis.html")




# ----------------- MOCK INTERVIEW --------------
@app.route("/mock-interview")
def mock_interview():
    return render_template("mock_interview.html")



if __name__ == "__main__":
    app.run(debug=True)