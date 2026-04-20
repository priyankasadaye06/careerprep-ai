import pdfkit
import os
import sqlite3

from flask import Flask, render_template, request, session, redirect, make_response, jsonify, url_for
from werkzeug.utils import secure_filename

from logic.template_parser import extract_template_fields
from logic.ai_chatbot import generate_interview_response
from interview.resume_parser import extract_text_from_pdf, extract_skills_from_resume
from logic.db_questions import get_questions   # ✅ DB आधारित questions

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "careerprep_secret"

# PDF config
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)


def get_db():
    return sqlite3.connect("database.db")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
        except:
            return "Email already exists!"

        return redirect("/login")

    return render_template("signup.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/landing")
        else:
            return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")

# ------------ DASHBOARD -------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html", name=session["user_name"])


# --------------- LOGOUT -----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- LANDING ----------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/landing")
    return redirect("/login")


@app.route("/landing")
def landing():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("landing.html", name=session["user_name"])

# ---------------- TEMPLATE ----------------
@app.route("/resume")
def resume_templates():
    return render_template("template_select.html")

@app.route("/select-template", methods=["POST"])
def select_template():
    session["template"] = request.form.get("template")
    return redirect("/resume-form")

# ---------------- FORM ----------------
@app.route("/resume-form")
def resume_form():
    template = session.get("template")
    return render_template(f"forms/{template}_form.html")

# ---------------- PROCESS FORM ----------------
def process_form_data(form):
    return {
        "name": form.get("name"),
        "email": form.get("email"),
        "phone": form.get("phone"),
        "location": form.get("location"),
        "linkedin": form.get("linkedin"),
        "github": form.get("github"),
        "summary": form.get("summary"),

        "education": [{
            "degree": form.get("degree"),
            "college": form.get("college"),
            "year": form.get("year")
        }],

        "skills": {
            "languages": form.get("languages", "").split(","),
            "frameworks": form.get("frameworks", "").split(","),
            "tools": form.get("tools", "").split(","),
            "databases": form.get("databases", "").split(",")
        },

        "experience": [{
            "role": form.get("exp_role"),
            "company": form.get("exp_company"),
            "duration": form.get("exp_duration"),
            "location": form.get("exp_location"),
            "points": form.get("exp_points", "").split("\n")
        }]
    }

# ---------------- PREVIEW ----------------
@app.route("/preview", methods=["POST"])
def preview():
    data = process_form_data(request.form)
    template = session.get("template")

    photo = request.files.get("photo")

    if photo and photo.filename != "":
        filename = secure_filename(photo.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(filepath)
        data["photo"] = f"/static/uploads/{filename}"
    else:
        data["photo"] = None

    # Custom sections
    custom_sections = {}
    for i in range(1, 11):
        key = request.form.get(f"custom_key_{i}")
        value = request.form.get(f"custom_value_{i}")
        if key and value:
            custom_sections[key] = value
    data["custom_sections"] = custom_sections

    # Projects
    projects = request.form.get("projects", "")
    data["projects"] = [p.strip() for p in projects.split("\n") if p.strip()]

    # Skills
    skills = {
        "languages": request.form.get("skills_languages", "").split(","),
        "frameworks": request.form.get("skills_frameworks", "").split(","),
        "tools": request.form.get("skills_tools", "").split(","),
        "databases": request.form.get("skills_databases", "").split(","),
    }

    for key in skills:
        skills[key] = [s.strip() for s in skills[key] if s.strip()]

    data["skills"] = skills if any(skills.values()) else None

    # Education
    education = []
    for i in range(1, 5):
        degree = request.form.get(f"edu_degree_{i}")
        college = request.form.get(f"edu_college_{i}")
        cgpa = request.form.get(f"edu_cgpa_{i}")
        if degree or college:
            education.append({
                "degree": degree,
                "college": college,
                "cgpa": cgpa
            })
    data["education"] = education if education else None

    # Experience
    experience = []
    for i in range(1, 5):
        role = request.form.get(f"exp_role_{i}")
        company = request.form.get(f"exp_company_{i}")
        duration = request.form.get(f"exp_duration_{i}")
        location = request.form.get(f"exp_location_{i}")
        points = request.form.get(f"exp_points_{i}", "").split("\n")
        points = [p.strip() for p in points if p.strip()]

        if role or company:
            experience.append({
                "role": role,
                "company": company,
                "duration": duration,
                "location": location,
                "points": points
            })

    data["experience"] = experience if experience else None

    return render_template(f"resumes/{template}.html", **data)

# ---------------- DOWNLOAD ----------------
@app.route("/download-resume", methods=["POST"])
def download_resume():
    template = session.get("template")
    html = request.form.get("resume_html")

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options={
            'enable-local-file-access': None,
            'page-size': 'A4',
            'encoding': "UTF-8",
            'quiet': ''
        },
        css=f"static/css/{template}.css"
    )

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=resume.pdf"
    return response

# ---------------- INTERVIEW HOME ----------------
@app.route("/interview")
def interview_training():
    return render_template("interview_home.html")

# ---------------- UPLOAD RESUME ----------------
@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    file = request.files["resume"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    text = extract_text_from_pdf(path)
    skills = extract_skills_from_resume(text)

    session["resume_text"] = text
    session["skills"] = skills
    session["chat_history"] = []

    return redirect(url_for("interview_options"))

# ---------------- INTERVIEW OPTIONS ----------------
@app.route("/interview-options")
def interview_options():
    return render_template("interview_options.html")

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")

        if not user_message:
            return jsonify({"reply": "Please enter a message."})

        resume_text = session.get("resume_text", "")
        chat_history = session.get("chat_history", [])

        chat_history.append({"role": "user", "content": user_message})
        chat_history = chat_history[-10:]

        reply = generate_interview_response(
            user_message,
            resume_text,
            chat_history
        )

        chat_history.append({"role": "assistant", "content": reply})
        session["chat_history"] = chat_history[-10:]

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"reply": "⚠️ AI error occurred"})

# ---------------- CHATBOT PAGE ----------------
@app.route("/chatbot")
def chatbot():
    session["chat_history"] = []
    return render_template("interview_chat.html")

# ---------------- COMPANY QUESTIONS ----------------
@app.route("/company-fyq")
def company_page():
    return render_template("company_select.html")

@app.route("/get-company-questions", methods=["POST"])
def get_company_questions():

    company = request.form.get("company")
    level = request.form.get("level")

    # 🔥 Normalize skills
    skills = [s.lower() for s in session.get("skills", [])]

    # 🔥 Get filtered questions
    questions = get_questions(company, skills, level)

    # ---------------- SKILL ANALYSIS ----------------
    COMPANY_SKILLS_MAP = {
        "Google": ["dsa", "system design", "dbms", "networking"],
        "Amazon": ["dsa", "system design", "dbms", "os", "business analytics", "hr"],
        "Microsoft": ["oop", "dbms"],
        "TCS": ["java", "sql"],
        "Infosys": ["python", "sql", "dbms"]
    }

    company_skills = COMPANY_SKILLS_MAP.get(company, [])

    # 🔥 SMART MATCHING
    matched = []
    missing = []

    for c_skill in company_skills:
        found = False
        for s in skills:
            if c_skill in s or s in c_skill:
                matched.append(c_skill)
                found = True
                break
        if not found:
            missing.append(c_skill)

    # 🔥 SCORE
    score = int((len(matched) / len(company_skills)) * 100) if company_skills else 0

    # 🔥 SUGGESTIONS
    suggestions = [f"Improve {s}" for s in missing]

    # 🔥 FINAL RESULT
    result = {
        "company": company,
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions,
        "questions": questions
    }

    return render_template("company_questions.html", result=result)
# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)