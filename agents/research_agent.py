"""
OMNIMIND AI — agents/research_agent.py
Researches a company using Groq LLM and returns a concise intelligence report.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def research_company(company_name):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a world-class business researcher with 20 years
    of experience analyzing companies across all industries globally.

    Research {company_name} and provide:
    1. Company overview and history
    2. Core products and services
    3. Revenue and financial highlights
    4. Key executives and leadership
    5. Recent major news and developments
    Keep it concise — under 300 words."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=500,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("🔬 Testing Research Agent...")
    result = research_company("Tesla")
    print(result)