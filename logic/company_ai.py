from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_company_questions(resume_text, company):

    prompt = f"""
You are an interviewer at {company}.

Candidate Resume:
{resume_text}

Generate 10 interview questions based on:
- Skills
- Projects
- Experience

Include:
- Technical questions
- HR questions
- Scenario questions

Make them realistic and company-level.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content