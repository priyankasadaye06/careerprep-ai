import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_interview_response(user_message, resume_text, chat_history):

    # 🔥 SKILL EXTRACTION
    skills_db = [
        "python", "java", "c++", "sql", "flask",
        "machine learning", "data structures",
        "algorithms", "html", "css", "javascript"
    ]

    resume_lower = resume_text.lower()
    skills = [s for s in skills_db if s in resume_lower]
    skills_text = ", ".join(skills) if skills else "general programming"

    # 🔥 BETTER FIRST MESSAGE CHECK
    is_first = len([m for m in chat_history if m["role"] == "user"]) <= 1

    # 🔥 MEMORY LIMIT
    history_text = ""
    for msg in chat_history[-5:]:
        role = "User" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content']}\n"

    # 🔥 STRONGER PROMPT (FOR SMALL MODELS)
    base_prompt = f"""
You are a STRICT technical interviewer.

Candidate Skills: {skills_text}

RULES (VERY IMPORTANT):
- Ask ONLY ONE question
- Do NOT ask multiple questions
- Do NOT explain anything extra
- Be direct and professional
- Keep responses short

FORMAT RULES:

If first question:
→ Only output question

If user answered:
→ Output EXACTLY in this format:

Feedback: <short feedback>
Score: <number>/10

Next Question:
<one question only>

NO extra text.

"""

    if is_first:
        prompt = f"""
{base_prompt}

Ask ONE basic interview question.

User: {user_message}
AI:
"""
    else:
        prompt = f"""
{base_prompt}

Conversation:
{history_text}

User Answer:
{user_message}
AI:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()
        reply = data.get("response", "").strip()

        # 🔥 HARD FORMAT CLEANING
        if "Feedback:" not in reply and not is_first:
            reply = f"""Feedback: Answer lacks depth and structure.
Score: 5/10

Next Question:
Explain one of your projects in detail."""

        if is_first and ("?" not in reply):
            reply = "Tell me about yourself."

        return reply

    except Exception as e:
        print("ERROR:", e)

        return """Feedback: System error occurred.
Score: 5/10

Next Question:
Explain your strongest technical skill."""