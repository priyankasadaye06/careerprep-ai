from flask import Flask, render_template, request, send_file, session
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Image, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

OUTPUT_FOLDER = "static/resumes"
UPLOAD_FOLDER = "static/uploads"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===============================
# STYLES
# ===============================

def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='NameStyle',
        fontSize=20,
        leading=24,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='HeadingStyle',
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.darkblue
    ))

    styles.add(ParagraphStyle(
        name='NormalStyle',
        fontSize=11,
        leading=15
    ))

    return styles


# ===============================
# ROUTES
# ===============================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/resume")
def resume():
    return render_template("resume_form.html")


@app.route("/generate", methods=["POST"])
def generate_preview():

    photo = request.files["photo"]
    photo_path = os.path.join(UPLOAD_FOLDER, photo.filename)
    photo.save(photo_path)

    session["resume_data"] = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "education": request.form.get("education"),
        "skills": request.form.get("skills"),
        "projects": request.form.get("projects"),
        "template": request.form.get("template"),
        "photo": photo_path
    }

    return render_template("preview.html", data=session["resume_data"])


@app.route("/download")
def download_resume():

    data = session.get("resume_data")
    if not data:
        return "No data found"

    file_path = os.path.join(
        OUTPUT_FOLDER,
        f"{data.get('name','resume')}_resume.pdf"
    )

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = get_styles()
    elements = []

    photo = Image(data["photo"], 1.5*inch, 1.5*inch)

    # ===============================
    # TEMPLATE 1: Corporate Executive
    # ===============================
    if data["template"] == "corporate":

        table = Table([
            [
                Paragraph(data["name"], styles["NameStyle"]),
                photo
            ]
        ], colWidths=[4*inch, 2*inch])

        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

    # ===============================
    # TEMPLATE 2: Modern Sidebar
    # ===============================
    elif data["template"] == "sidebar":

        sidebar = Table([
            [photo],
            [Paragraph(data["email"], styles["NormalStyle"])],
            [Paragraph(data["phone"], styles["NormalStyle"])]
        ], colWidths=[2*inch])

        sidebar.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))

        main = Paragraph(data["name"], styles["NameStyle"])

        table = Table([
            [sidebar, main]
        ], colWidths=[2*inch, 4*inch])

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

    # ===============================
    # TEMPLATE 3: Minimal Centered
    # ===============================
    elif data["template"] == "minimal":

        elements.append(photo)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(data["name"], styles["NameStyle"]))
        elements.append(Spacer(1, 0.2*inch))

    # ===============================
    # TEMPLATE 4: Creative Banner
    # ===============================
    elif data["template"] == "creative":

        banner = Table([[photo]], colWidths=[6*inch])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))

        elements.append(banner)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(data["name"], styles["NameStyle"]))
        elements.append(Spacer(1, 0.2*inch))

    # ===============================
    # TEMPLATE 5: Two Column Professional
    # ===============================
    elif data["template"] == "twocolumn":

        header = Table([
            [
                Paragraph(data["name"], styles["NameStyle"]),
                photo
            ]
        ], colWidths=[4*inch, 2*inch])

        elements.append(header)
        elements.append(Spacer(1, 0.3*inch))

    # ===============================
    # COMMON SECTIONS
    # ===============================

    contact = f"{data['email']} | {data['phone']}"
    elements.append(Paragraph(contact, styles["NormalStyle"]))
    elements.append(Spacer(1, 0.3*inch))

    elements.append(Paragraph("Education", styles["HeadingStyle"]))
    elements.append(Paragraph(data["education"], styles["NormalStyle"]))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("Skills", styles["HeadingStyle"]))
    elements.append(Paragraph(data["skills"], styles["NormalStyle"]))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("Projects", styles["HeadingStyle"]))
    elements.append(Paragraph(data["projects"], styles["NormalStyle"]))

    doc.build(elements)

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)