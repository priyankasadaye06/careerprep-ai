from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# Folder to store generated resumes
OUTPUT_FOLDER = "static/resumes"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("resume_form.html")

@app.route("/generate", methods=["POST"])
def generate_resume():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    education = request.form["education"]
    skills = request.form["skills"]
    projects = request.form["projects"]

    file_path = os.path.join(OUTPUT_FOLDER, f"{name}_resume.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, name)

    c.setFont("Helvetica", 11)
    y -= 25
    c.drawString(50, y, f"Email: {email} | Phone: {phone}")

    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Education")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(50, y, education)

    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Skills")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(50, y, skills)

    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Projects")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(50, y, projects)

    c.save()

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
