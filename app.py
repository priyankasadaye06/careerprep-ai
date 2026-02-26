from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/resume")
def resume_templates():
    return render_template("template_select.html")

@app.route("/select-template", methods=["POST"])
def select_template():
    selected_template = request.form.get("template")
    return f"Template selected: {selected_template} (Role selection comes next)"

@app.route("/interview")
def interview_training():
    return render_template("interview_home.html")

if __name__ == "__main__":
    app.run(debug=True)