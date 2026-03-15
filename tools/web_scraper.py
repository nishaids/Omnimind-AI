"""
OMNIMIND AI — tools/web_scraper.py
Scrapes live company data from the web to feed richer context into agents.
Uses: requests + BeautifulSoup4
pip install requests beautifulsoup4 lxml
"""

import re
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

# ── Rotating User-Agents to avoid blocks ─────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

TIMEOUT = 12  # seconds


# ── Helper ────────────────────────────────────────────────────────────────────
def _get(url: str) -> Optional[BeautifulSoup]:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        HEADERS["User-Agent"] = random.choice(USER_AGENTS)
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except Exception:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            return BeautifulSoup(resp.text, "html.parser")
        except Exception:
            return None


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── 1. Google News Headlines ──────────────────────────────────────────────────
def scrape_google_news(company: str, max_results: int = 8) -> list[dict]:
    """
    Fetch recent Google News headlines for a company.
    Returns list of { title, source, url, snippet }
    """
    query = company.replace(" ", "+") + "+stock+news"
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    results = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")[:max_results]
        for item in items:
            title = _clean(item.find("title").get_text() if item.find("title") else "")
            link  = item.find("link").get_text() if item.find("link") else ""
            pub   = item.find("pubDate").get_text() if item.find("pubDate") else ""
            source = item.find("source").get_text() if item.find("source") else "Google News"
            results.append({"title": title, "source": source, "url": link, "published": pub})
    except Exception as e:
        results.append({"title": f"Could not fetch news: {e}", "source": "", "url": "", "published": ""})
    return results


# ── 2. Wikipedia Company Summary ──────────────────────────────────────────────
def scrape_wikipedia(company: str) -> dict:
    """
    Scrape the Wikipedia introduction paragraph of a company.
    Returns { summary, url, categories }
    """
    slug = company.replace(" ", "_")
    url  = f"https://en.wikipedia.org/wiki/{slug}"
    soup = _get(url)
    if not soup:
        return {"summary": "Wikipedia unavailable.", "url": url, "categories": []}

    # First meaningful paragraph
    content = soup.find("div", {"id": "mw-content-text"})
    paragraphs = content.find_all("p") if content else []
    summary = ""
    for p in paragraphs:
        text = _clean(p.get_text())
        if len(text) > 80:
            summary = text
            break

    # Categories
    cat_div = soup.find("div", {"id": "mw-normal-catlinks"})
    cats = []
    if cat_div:
        cats = [_clean(a.get_text()) for a in cat_div.find_all("a")[1:6]]

    return {"summary": summary or "No summary found.", "url": url, "categories": cats}


# ── 3. Yahoo Finance Quick Stats ──────────────────────────────────────────────
def scrape_yahoo_finance(ticker: str) -> dict:
    """
    Scrape basic stock data from Yahoo Finance page.
    Returns { price, change, change_pct, market_cap, pe_ratio, 52w_high, 52w_low, volume }
    """
    if not ticker:
        return {"error": "No ticker provided"}

    url  = f"https://finance.yahoo.com/quote/{ticker}/"
    soup = _get(url)
    if not soup:
        return {"error": "Could not reach Yahoo Finance"}

    data = {}

    def _find_value(label_text):
        try:
            spans = soup.find_all("span")
            for i, s in enumerate(spans):
                if label_text.lower() in s.get_text().lower():
                    if i + 1 < len(spans):
                        return _clean(spans[i + 1].get_text())
        except Exception:
            pass
        return "N/A"

    # Price
    try:
        price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
        data["price"] = price_tag["value"] if price_tag else "N/A"
    except Exception:
        data["price"] = "N/A"

    # Change
    try:
        chg_tag = soup.find("fin-streamer", {"data-field": "regularMarketChange"})
        pct_tag = soup.find("fin-streamer", {"data-field": "regularMarketChangePercent"})
        data["change"] = chg_tag["value"] if chg_tag else "N/A"
        data["change_pct"] = f"{float(pct_tag['value']):.2f}%" if pct_tag else "N/A"
    except Exception:
        data["change"] = "N/A"
        data["change_pct"] = "N/A"

    # Table stats
    for key, label in [
        ("market_cap",  "Market Cap"),
        ("pe_ratio",    "PE Ratio"),
        ("52w_high",    "52 Week High"),
        ("52w_low",     "52 Week Low"),
        ("volume",      "Volume"),
        ("avg_volume",  "Avg. Volume"),
        ("eps",         "EPS"),
    ]:
        data[key] = _find_value(label)

    data["url"] = url
    return data


# ── 4. Moneycontrol / Economic Times News (India-focused) ────────────────────
def scrape_india_news(company: str, max_results: int = 5) -> list[dict]:
    """
    Scrape Economic Times news for Indian companies.
    Returns list of { title, url, date }
    """
    query = company.replace(" ", "+")
    url   = f"https://economictimes.indiatimes.com/searchresult.cms?query={query}"
    soup  = _get(url)
    results = []
    if not soup:
        return [{"title": "Could not reach Economic Times", "url": "", "date": ""}]

    articles = soup.select("div.eachStory")[:max_results]
    for a in articles:
        try:
            title = _clean(a.find("h3").get_text()) if a.find("h3") else ""
            link  = "https://economictimes.indiatimes.com" + a.find("a")["href"] if a.find("a") else ""
            date  = _clean(a.find("time").get_text()) if a.find("time") else ""
            if title:
                results.append({"title": title, "url": link, "date": date})
        except Exception:
            continue

    return results or [{"title": "No results found on Economic Times", "url": "", "date": ""}]


# ── 5. Master scrape function ─────────────────────────────────────────────────
def scrape_all(company: str, ticker: str = "") -> dict:
    """
    Run all scrapers and return a combined context dict.
    This is called by agents to enrich their prompts with live web data.
    """
    print(f"[WebScraper] Scraping live data for: {company} ({ticker})")
    result = {
        "company": company,
        "ticker": ticker,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "wikipedia": {},
        "google_news": [],
        "yahoo_finance": {},
        "india_news": [],
    }

    # Wikipedia
    result["wikipedia"] = scrape_wikipedia(company)
    time.sleep(0.5)

    # Google News
    result["google_news"] = scrape_google_news(company)
    time.sleep(0.5)

    # Yahoo Finance
    if ticker:
        result["yahoo_finance"] = scrape_yahoo_finance(ticker)
        time.sleep(0.5)

    # India News (for Indian companies)
    indian_keywords = ["tcs", "infosys", "wipro", "reliance", "zomato", "paytm",
                       "hdfc", "icici", "ola", "tata"]
    if any(kw in company.lower() for kw in indian_keywords):
        result["india_news"] = scrape_india_news(company)

    return result


def format_scrape_for_prompt(scraped: dict) -> str:
    """
    Convert scraped data into a clean text block for injecting into agent prompts.
    """
    lines = [f"=== LIVE WEB DATA: {scraped['company'].upper()} (scraped {scraped['scraped_at']}) ===\n"]

    wiki = scraped.get("wikipedia", {})
    if wiki.get("summary"):
        lines.append(f"WIKIPEDIA SUMMARY:\n{wiki['summary']}\n")

    yf = scraped.get("yahoo_finance", {})
    if yf and "price" in yf:
        lines.append("YAHOO FINANCE LIVE STATS:")
        for k, v in yf.items():
            if k != "url" and v and v != "N/A":
                lines.append(f"  {k.replace('_',' ').title()}: {v}")
        lines.append("")

    news = scraped.get("google_news", [])
    if news:
        lines.append("LATEST GOOGLE NEWS:")
        for n in news[:6]:
            lines.append(f"  • [{n.get('source','')}] {n.get('title','')}")
        lines.append("")

    india = scraped.get("india_news", [])
    if india and india[0].get("title", "").startswith("No") is False:
        lines.append("ECONOMIC TIMES HEADLINES:")
        for n in india:
            lines.append(f"  • {n.get('title','')}")

    return "\n".join(lines)
