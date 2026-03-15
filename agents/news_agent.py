"""
OMNIMIND AI — agents/news_agent.py
Fetches company-specific news via NewsAPI, then runs Groq LLM analysis.
"""

import os
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def _fetch_news(company: str) -> list:
    """Fetch company-specific news using NewsAPI with targeted search."""
    api_key = os.getenv("NEWS_API_KEY", "")
    if not api_key:
        return []

    articles = []

    # Primary: /v2/everything with company-specific query
    try:
        query = f'"{company}" OR "{company} stock" OR "{company} earnings"'
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 7,
                "apiKey": api_key,
            },
            timeout=10,
        )
        data = resp.json()
        for art in data.get("articles", []):
            if art.get("title") and "[Removed]" not in art["title"]:
                articles.append({
                    "title": art["title"],
                    "description": art.get("description", ""),
                    "source": art.get("source", {}).get("name", "Unknown"),
                    "published": art.get("publishedAt", ""),
                })
    except Exception:
        pass

    # Fallback: /v2/top-headlines if primary returned nothing
    if not articles:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "category": "business",
                    "language": "en",
                    "pageSize": 5,
                    "apiKey": api_key,
                },
                timeout=10,
            )
            data = resp.json()
            for art in data.get("articles", []):
                if art.get("title") and "[Removed]" not in art["title"]:
                    articles.append({
                        "title": art["title"],
                        "description": art.get("description", ""),
                        "source": art.get("source", {}).get("name", "Unknown"),
                        "published": art.get("publishedAt", ""),
                    })
        except Exception:
            pass

    return articles


def analyze_news(company: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    articles = _fetch_news(company)

    if articles:
        news_text = "\n".join(
            f"  - [{a['source']}] {a['title']}: {a['description']}"
            for a in articles[:7]
        )
        context = f"""Here are the latest news articles specifically about {company}:
{news_text}

Analyze ONLY the news about {company}. Do NOT provide generic market news.
"""
    else:
        context = f"""No recent news articles were found for {company} via NewsAPI.
Use your OWN training knowledge about {company} to provide a news and sentiment analysis.
Talk about recent known developments, product launches, earnings, partnerships, or controversies specific to {company}.
Do NOT say news is unavailable — provide your best informed analysis about {company} specifically.
"""

    prompt = f"""You are a senior news intelligence analyst specializing in {company}.

{context}

Provide a COMPANY-SPECIFIC news analysis for {company} with these sections:

1. Top 3 Most Important News Highlights
   - Each highlight must be specifically about {company}, not generic market news
   - Include the source if available

2. Overall Sentiment: Positive / Negative / Neutral
   - Explain WHY in 1-2 sentences specific to {company}

3. Business Impact Assessment
   - How do these developments affect {company}'s business operations, revenue, or market position?

4. Opportunities or Threats
   - Specific opportunities and threats facing {company} based on the news

IMPORTANT: Every point must be SPECIFIC to {company}. Do NOT include generic stock market or economy news.
Keep under 250 words.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=450,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("📰 Testing News Agent...")
    result = analyze_news("Tesla")
    print(result)