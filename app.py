from flask import Flask, render_template, request, session, redirect
from mock.sample_resume_data import get_sample_resume_data

app = Flask(__name__)
app.secret_key = "careerprep_secret"


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

    # clean fallback for custom roles
    clean_role = role.replace("-", " ").title()

    session["role"] = role_map.get(role, clean_role)
    return redirect("/resume-form")


# ---------------- RESUME FORM ----------------
@app.route("/resume-form")
def resume_form():
    role = session.get("role")
    if not role:
        return redirect("/roles")

    return render_template("form.html", role=role)


# ---------------- PREVIEW ----------------
@app.route("/preview", methods=["POST"])
def preview():

    print("FORM DATA:", request.form)

    if request.form.get("use_sample") == "true":
        data = get_sample_resume_data()
    else:
        # TEMP SAFE FALLBACK (no crash)
        data = request.form.to_dict()

    data["role"] = session.get("role")
    template = session.get("template", "template1")

    return render_template(f"resumes/{template}.html", **data)


# ---------------- INTERVIEW ----------------
@app.route("/interview")
def interview_training():
    return render_template("interview_home.html")


if __name__ == "__main__":
    app.run(debug=True)