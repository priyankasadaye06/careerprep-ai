import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_interview_response(user_message, resume_text, chat_history):

    # 🔥 EXTRACT SKILLS
    skills = []
    skills_db = [
        "python", "java", "c++", "sql", "flask",
        "machine learning", "data structures",
        "algorithms", "html", "css", "javascript"
    ]

    resume_lower = resume_text.lower()

    for skill in skills_db:
        if skill in resume_lower:
            skills.append(skill)

    skills_text = ", ".join(skills) if skills else "general programming"

    # 🔥 CHECK IF FIRST QUESTION
    is_first = len(chat_history) <= 1

    # 🔥 SYSTEM PROMPT (STRICT INTERVIEWER)
    system_prompt = f"""
You are a STRICT technical interviewer.

Candidate Skills:
{skills_text}

Rules:
- ONLY ask ONE question at a time
- NEVER ask multiple questions
- NEVER give score before candidate answers
- NEVER behave like chatbot (no greetings, no "how can I help")
- Be professional and slightly strict
- Questions must be based on candidate skills
- Start from basic → intermediate → advanced
- Ask follow-up questions if answer is weak

Flow:

IF this is FIRST message:
→ Ask ONLY ONE basic question

IF candidate answered:
→ Give:
Feedback: (2-3 lines)
Score: (x/10)

→ Then ask NEXT question

STRICT FORMAT:

Feedback: <feedback>
Score: <x/10>

Next Question:
<question>
"""

    # 🔥 MEMORY (LIMIT FOR PERFORMANCE)
    history_text = ""
    for msg in chat_history[-6:]:
        role = "User" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content']}\n"

    # 🔥 FINAL PROMPT
    if is_first:
        prompt = f"""
{system_prompt}

Ask ONLY ONE first interview question based on skills.

User: {user_message}
AI:
"""
    else:
        prompt = f"""
{system_prompt}

Conversation so far:
{history_text}

User: {user_message}
AI:
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "phi",   # ✅ LOW RAM MODEL
            "prompt": prompt,
            "stream": False
        })

        data = response.json()
        reply = data.get("response", "").strip()

        # 🔥 FALLBACK (if model behaves weird)
        if not reply or "error" in str(data).lower():
            reply = """Feedback: Your answer needs more clarity and technical depth.
Score: 5/10

Next Question:
Explain your main project in detail and your role in it."""

        return reply

    except Exception as e:
        return """Feedback: System error occurred.
Score: 5/10

Next Question:
Explain a project you have worked on."""