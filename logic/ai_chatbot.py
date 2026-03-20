import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_interview_response(user_message, resume_text, chat_history):

    # 🔥 SYSTEM PROMPT (THIS IS THE BRAIN)
    system_prompt = f"""
You are an AI Interviewer.

Candidate Resume:
{resume_text}

Rules:
- Ask technical interview questions based on candidate skills
- Start easy → go to advanced
- Do NOT repeat questions
- After every answer:
    1. Give Feedback
    2. Give Score out of 10
    3. Ask next question

Format STRICTLY:

Feedback: <your feedback>
Score: <x/10>

Next Question:
<question>
"""

    # 🔥 MEMORY (previous conversation)
    history_text = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""
{system_prompt}

Conversation so far:
{history_text}

User: {user_message}
AI:
"""

    # 🔥 CALL OLLAMA
    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    data = response.json()
    reply = data["response"]

    return reply