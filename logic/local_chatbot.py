from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

def generate_interview_response(resume_text, user_input, history):

    history_text = ""
    for h in history:
        history_text += f"{h['role']}: {h['content']}\n"

    prompt = f"""
You are a strict professional interviewer.

RULES:
- DO NOT act like ChatGPT
- DO NOT explain you are an AI
- ONLY conduct interview
- Ask ONE question at a time
- Ask follow-up questions based on answers
- Focus on resume

Candidate Resume:
{resume_text}

Conversation so far:
{history_text}

Candidate Answer:
{user_input}

Now:
Ask the NEXT interview question.
"""

    response = llm.invoke(prompt)

    return response