def analyze_resume(text):

    text = text.lower()

    result = {
        "skills": [],
        "domain": "general"
    }

    # 🔥 detect domain
    if "machine learning" in text or "tensorflow" in text:
        result["domain"] = "ml"
    elif "react" in text or "javascript" in text:
        result["domain"] = "web"
    elif "sql" in text or "power bi" in text:
        result["domain"] = "data"

    # 🔥 extract skills
    skill_map = {
        "python": "Python",
        "java": "Java",
        "sql": "SQL",
        "react": "React",
        "flask": "Flask",
        "tensorflow": "TensorFlow",
        "excel": "Excel",
        "power bi": "Power BI"
    }

    for key, val in skill_map.items():
        if key in text:
            result["skills"].append(val)

    return result