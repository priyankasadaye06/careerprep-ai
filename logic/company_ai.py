
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


# 🔥 COMPANY SKILL EXPECTATIONS
COMPANY_SKILLS = {
    "google": ["data structures", "algorithms", "system design", "problem solving"],
    "amazon": ["data structures", "algorithms", "system design", "behavioral"],
    "microsoft": ["data structures", "oop", "problem solving"],
    "apple": ["system design", "low level design", "c++", "performance"],
    "meta": ["data structures", "algorithms", "system design"],
    "adobe": ["data structures", "algorithms", "problem solving"],
    "uber": ["system design", "scalability", "backend"],
    "flipkart": ["data structures", "algorithms", "backend"],
    "cisco": ["networking", "os", "c"],
    "tcs": ["aptitude", "basic programming"],
    "infosys": ["aptitude", "dbms", "os"],
    "wipro": ["aptitude", "basic coding"],
    "cognizant": ["aptitude", "sql", "basics"]
}


def generate_company_questions(resume_text, company):
    company = company.lower()

    expected_skills = COMPANY_SKILLS.get(company, ["programming", "problem solving"])

    # 🔥 MATCH SCORE
    resume_lower = resume_text.lower()
    matched = [skill for skill in expected_skills if skill in resume_lower]

    score = int((len(matched) / len(expected_skills)) * 100)

    missing = list(set(expected_skills) - set(matched))

    # 🔥 PROMPT FOR OLLAMA
    prompt = f"""
You are a technical interviewer for {company.upper()}.

Candidate Resume:
{resume_text}

Company expects skills:
{expected_skills}

Tasks:

1. Generate 5 REALISTIC interview questions asked in {company} style
2. Questions must be based on:
   - Candidate resume
   - Company expectations

3. Also give:
   - 3 HR/Behavioral questions
   - 2 coding questions

Format:

Technical Questions:
1.
2.
3.
4.
5.

Coding Questions:
1.
2.

HR Questions:
1.
2.
3.
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "phi",
            "prompt": prompt,
            "stream": False
        })

        data = response.json()
        questions = data.get("response", "")

    except Exception as e:
        questions = "Error generating questions. Make sure Ollama is running."

    # 🔥 FINAL RESULT OBJECT
    result = {
        "company": company.upper(),
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "questions": questions,
        "suggestions": generate_suggestions(missing)
    }

    return result


# 🔥 SUGGESTION ENGINE
def generate_suggestions(missing_skills):

    if not missing_skills:
        return ["You are well prepared for this company."]

    suggestions = []

    for skill in missing_skills:
        suggestions.append(f"Improve your knowledge in {skill}")

    return suggestions