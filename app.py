import pdfkit
import os

from flask import Flask, render_template, request, session, redirect, make_response, jsonify

from logic.template_parser import extract_template_fields
from logic.role_fields import ROLE_FIELDS
from logic.ai_chatbot import generate_interview_response

from interview.resume_parser import extract_text_from_pdf, extract_skills_from_resume
from logic.company_ai import generate_company_questions

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- SETUP ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "careerprep_secret"

# PDF config
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

# ---------------- LANDING ----------------
@app.route("/")
def landing():
    return render_template("landing.html")

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

    # 🔹 Base data
    data = process_form_data(request.form)

    template = session.get("template")
   
    photo = request.files.get("photo")

    if photo and photo.filename != "":
        filename = secure_filename(photo.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(filepath)

        data["photo"] = "/" + filepath   # important for HTML
    else:
        data["photo"] = None

    # 🔥 CUSTOM SECTIONS
    custom_sections = {}
    for i in range(1, 11):
        key = request.form.get(f"custom_key_{i}")
        value = request.form.get(f"custom_value_{i}")
        if key and value:
            custom_sections[key] = value

    data["custom_sections"] = custom_sections

    # 🔹 PROJECTS
    projects = request.form.get("projects", "")
    data["projects"] = [p.strip() for p in projects.split("\n") if p.strip()]

    # -------- ✅ SKILLS --------
    skills = {
        "languages": request.form.get("skills_languages", "").split(","),
        "frameworks": request.form.get("skills_frameworks", "").split(","),
        "tools": request.form.get("skills_tools", "").split(","),
        "databases": request.form.get("skills_databases", "").split(","),
    }

    for key in skills:
        skills[key] = [s.strip() for s in skills[key] if s.strip()]

    data["skills"] = skills if any(skills.values()) else None

    # -------- ✅ EDUCATION --------
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

    # -------- ✅ EXPERIENCE --------
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

    # 🔥 DEBUG (optional)
    print("SKILLS:", data["skills"])
    print("EDUCATION:", data["education"])
    print("EXPERIENCE:", data["experience"])

    return render_template(f"resumes/{template}.html", **data)
# ---------------- DOWNLOAD ----------------
@app.route("/download-resume", methods=["POST"])
def download_resume():

    html = request.form.get("resume_html")

    pdf = pdfkit.from_string(html, False, configuration=config)

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

    # 📄 Extract text
    text = extract_text_from_pdf(path)

    # 🧠 Extract skills
    skills = extract_skills_from_resume(text)

    # 🔥 Store in session
    session["resume_text"] = text
    session["skills"] = skills
    session["chat_history"] = []

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
        skills = session.get("skills", [])

        # 🔥 Add user message
        chat_history.append({
            "role": "user",
            "content": user_message
        })

        # 🔥 Limit memory
        chat_history = chat_history[-10:]

        # 🧠 Enhance context
        enhanced_resume = resume_text + f"\n\nSkills: {skills}"

        # 🤖 Generate response
        reply = generate_interview_response(
            user_message,
            enhanced_resume,
            chat_history
        )

        # 🔥 Add AI response
        chat_history.append({
            "role": "assistant",
            "content": reply
        })

        # 🔥 Save memory
        session["chat_history"] = chat_history[-10:]

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "reply": "⚠️ Error: Make sure Ollama is running (ollama run phi)"
        })

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
    resume_text = session.get("resume_text", "")

    questions = generate_company_questions(
        resume_text + f"\nDifficulty: {level}",
        company
    )

    return render_template(
        "company_questions.html",
        company=company,
        questions=questions
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)