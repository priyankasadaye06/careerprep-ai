import re
import os

def extract_template_fields(template_name):

    path = os.path.join("templates", "resumes", f"{template_name}.html")

    with open(path, "r", encoding="utf-8") as file:
        html = file.read()

    pattern = r"{{\s*([a-zA-Z0-9_]+)\s*}}"

    fields = re.findall(pattern, html)

    ignore = [
        "loop", "exp", "edu", "point",
        "role_bullets"
    ]

    clean_fields = []

    for f in fields:
        if f not in ignore and f not in clean_fields:
            clean_fields.append(f)

    return clean_fields
