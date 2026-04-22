import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

# simple fallback question bank
QUESTION_BANK = [
    "Tell me about yourself.",
    "Explain one of your projects in detail.",
    "What are your strengths?",
    "Explain a challenge you faced in a project.",
    "What is your favorite programming language and why?"
]


def generate_interview_response(user_message, resume_text, chat_history):

    skills_db = [
        "python", "java", "c++", "sql", "flask",
        "machine learning", "data structures",
        "algorithms", "html", "css", "javascript"
    ]

    resume_lower = resume_text.lower()
    skills = [s for s in skills_db if s in resume_lower]
    skills_text = ", ".join(skills) if skills else "general programming"

    # detect first message
    user_msgs = [m for m in chat_history if m["role"] == "user"]
    is_first = len(user_msgs) <= 1

    # track question index
    q_index = len(user_msgs)

    history_text = ""
    for msg in chat_history[-5:]:
        role = "User" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content']}\n"

    base_prompt = f"""
You are a STRICT technical interviewer.

Candidate Skills: {skills_text}

RULES:
- Ask ONLY ONE question
- Give SHORT feedback
- Give score out of 10
- DO NOT repeat same question
- Be strict but fair



FORMAT:

Feedback: <short feedback>
Score: <number>/10
Next Question: <question>
"""

    if is_first:
        return QUESTION_BANK[0]

    prompt = f"""
{base_prompt}

Conversation:
{history_text}

User Answer:
{user_message}

Generate response.
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

        print("AI RAW RESPONSE:", reply)
        # ✅ fallback ONLY if completely broken
        if len(reply.strip()) < 20:
            next_q = QUESTION_BANK[q_index % len(QUESTION_BANK)]

            reply = f"""Feedback: Good attempt, but improve structure and technical depth.
Score: 6/10

Next Question:
{next_q}"""

        return reply

    except Exception as e:
        print("ERROR:", e)

        next_q = QUESTION_BANK[q_index % len(QUESTION_BANK)]

        return f"""Feedback: System error occurred.
Score: 5/10

Next Question:
{next_q}"""