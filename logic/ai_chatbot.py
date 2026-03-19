import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_interview_response(resume_text, user_answer, history):

    messages = [
        {
            "role": "system",
            "content": f"""
You are a professional AI Interviewer.

Candidate Resume:
{resume_text}

Instructions:
- Ask technical + HR questions
- Ask follow-up questions
- Be interactive like real interviewer
- Keep conversation flowing
"""
        }
    ]

    # add previous history
    messages.extend(history)

    # add latest user input
    messages.append({
        "role": "user",
        "content": user_answer
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # ✅ correct model
        messages=messages
    )

    return response.choices[0].message.content