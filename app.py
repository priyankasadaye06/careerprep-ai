from flask import Flask, render_template, request
from llm.ats_enhancer import enhance_content

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_resume():
    data = request.form.to_dict()

    enhanced_data = enhance_content(data)

    template_choice = data.get("template")

    return render_template(
        f"resumes/{template_choice}.html",
        **enhanced_data
    )

if __name__ == "__main__":
    app.run(debug=True)