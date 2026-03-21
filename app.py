import pdfkit
import os

from flask import Flask, render_template, request, session, redirect, make_response, jsonify

from logic.template_parser import extract_template_fields
from logic.role_fields import ROLE_FIELDS
from logic.ai_chatbot import generate_interview_response

from interview.resume_parser import extract_text_from_pdf, extract_skills_from_resume
from logic.company_ai import generate_company_questions

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
    return redirect("/roles")

# ---------------- ROLE ----------------
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
    session["custom_role"] = role not in role_map

    return redirect("/resume-form")

# ---------------- FORM ----------------
@app.route("/resume-form")
def resume_form():

    template = session.get("template")
    role = session.get("role")
    is_custom = session.get("custom_role", False)

    template_fields = extract_template_fields(template)
    role_fields = ROLE_FIELDS.get(role, [])

    return render_template(
        "form.html",
        template_fields=template_fields,
        role_fields=role_fields,
        role=role,
        is_custom=is_custom
    )

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

    role = session.get("role")
    template = session.get("template")
    is_custom = session.get("custom_role", False)

    role_fields = ROLE_FIELDS.get(role, [])
    role_data = {}

    for field in role_fields:
        if data.get(field):
            role_data[field] = data[field]

    if is_custom:
        for i in range(1, 4):
            key = request.form.get(f"custom_key_{i}")
            value = request.form.get(f"custom_value_{i}")

            if key and value:
                role_data[key] = value

    data["role_section"] = role_data
    data["role"] = role

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