import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



def enhance_content(data):
    """
    Mock LLM-based ATS enhancer.
    Replace this later with a real LLM or LangChain.
    """

    role = data.get("role", "the target role")

    enhanced_points = [
        f"Optimized resume content for {role} using ATS-friendly keywords",
        "Used strong action verbs to describe responsibilities and achievements",
        "Structured project descriptions with measurable outcomes",
        "Ensured clean, single-column layout for ATS compatibility"
    ]

    data["enhanced_points"] = enhanced_points
    return data