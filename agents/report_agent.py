"""
OMNIMIND AI — agents/report_agent.py
Synthesizes research, stock, and news data into an executive intelligence report
using Groq LLM.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def generate_report(company_name, research_data, stock_data, news_data):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a Fortune 500 Chief Intelligence Officer who
    creates board-level reports combining research, financials, and news
    into actionable executive summaries.

    Create a complete Executive Intelligence Report for {company_name}.

    Use this data:
    RESEARCH: {research_data}
    STOCK: {stock_data}
    NEWS: {news_data}

    Structure the report as:

    🏢 EXECUTIVE SUMMARY
    📈 FINANCIAL SNAPSHOT
    📰 NEWS INTELLIGENCE
    ⚠️ RISK ASSESSMENT
    🚀 OPPORTUNITIES
    🎯 STRATEGIC RECOMMENDATION

    Make it professional, concise, and actionable. Max 400 words."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=600,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("📊 Testing Report Agent...")

    # Sample data for testing
    research = "Tesla is an EV company founded by Elon Musk. Leader in electric vehicles and clean energy."
    stock = "Current price $396. HOLD recommendation. PE ratio 370. Market cap $1.49T."
    news = "Tesla expanding in India. New Cybertruck deliveries started. FSD version 13 released."

    result = generate_report("Tesla", research, stock, news)
    print(result)