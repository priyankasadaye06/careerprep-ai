import random

def enhance_text(text):

    starters = [
        "Developed",
        "Implemented",
        "Engineered",
        "Designed",
        "Optimized"
    ]

    results = []

    for line in text.split("\n"):

        if line.strip():

            starter = random.choice(starters)

            enhanced = f"{starter} {line.strip().lower()}"

            results.append(enhanced.capitalize())

    return results