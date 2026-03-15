"""
OMNIMIND AI — agents/stock_agent.py
Fetches REAL stock data via yfinance (info + fast_info fallback) then runs LLM analysis.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def _fmt(num):
    """Format large numbers with B/M/K suffix."""
    if num is None or num == "N/A":
        return "N/A"
    try:
        n = float(num)
        if n >= 1e12:
            return f"${n/1e12:.2f}T"
        if n >= 1e9:
            return f"${n/1e9:.2f}B"
        if n >= 1e6:
            return f"${n/1e6:.2f}M"
        if n >= 1e3:
            return f"${n/1e3:.1f}K"
        return f"${n:,.2f}"
    except (ValueError, TypeError):
        return str(num)


def _fetch_real_stock_data(ticker: str) -> dict:
    """Fetch live stock data using yfinance with info + fast_info fallback."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = {}
        try:
            info = stock.info or {}
        except Exception:
            info = {}

        # Helper: try info first, then fast_info as fallback
        def safe(key, default="N/A"):
            val = info.get(key)
            if val not in (None, "", 0, "N/A"):
                return val
            # Try fast_info fallback
            try:
                fi = stock.fast_info
                fi_val = getattr(fi, key, None)
                if fi_val is not None and fi_val != 0:
                    return fi_val
            except Exception:
                pass
            return default

        # Get price — try multiple keys
        price = safe("currentPrice") or safe("regularMarketPrice")
        if price == "N/A":
            try:
                price = stock.fast_info.last_price
            except Exception:
                price = "N/A"

        prev_close = safe("previousClose")
        if prev_close == "N/A":
            try:
                prev_close = stock.fast_info.previous_close
            except Exception:
                prev_close = "N/A"

        # Calculate change manually
        try:
            p = float(price)
            pc = float(prev_close)
            change = round(p - pc, 2)
            change_pct = round((change / pc) * 100, 2)
        except (ValueError, TypeError, ZeroDivisionError):
            change, change_pct = "N/A", "N/A"

        # Market cap fallback
        market_cap = safe("marketCap")
        if market_cap == "N/A":
            try:
                market_cap = stock.fast_info.market_cap
            except Exception:
                market_cap = "N/A"

        # Volume fallback
        volume = safe("volume")
        if volume == "N/A":
            try:
                volume = stock.fast_info.last_volume
            except Exception:
                volume = "N/A"

        return {
            "current_price": f"${price}" if price != "N/A" else "N/A",
            "change": f"{change:+}" if change != "N/A" else "N/A",
            "change_pct": f"{change_pct:+}%" if change_pct != "N/A" else "N/A",
            "previous_close": f"${prev_close}" if prev_close != "N/A" else "N/A",
            "market_cap": _fmt(market_cap),
            "pe_ratio": safe("trailingPE"),
            "forward_pe": safe("forwardPE"),
            "eps": safe("trailingEps"),
            "52w_high": f"${safe('fiftyTwoWeekHigh')}" if safe("fiftyTwoWeekHigh") != "N/A" else "N/A",
            "52w_low": f"${safe('fiftyTwoWeekLow')}" if safe("fiftyTwoWeekLow") != "N/A" else "N/A",
            "volume": f"{int(volume):,}" if volume != "N/A" else "N/A",
            "avg_volume": f"{int(safe('averageVolume')):,}" if safe("averageVolume") != "N/A" else "N/A",
            "revenue": _fmt(safe("totalRevenue")),
            "net_income": _fmt(safe("netIncomeToCommon")),
            "profit_margin": f"{round(float(safe('profitMargins', 0)) * 100, 1)}%" if safe("profitMargins") != "N/A" else "N/A",
            "dividend_yield": f"{round(float(safe('dividendYield', 0)) * 100, 2)}%" if safe("dividendYield") not in ("N/A", None) else "N/A",
            "beta": safe("beta"),
            "sector": safe("sector"),
            "industry": safe("industry"),
            "country": safe("country"),
            "employees": f"{int(safe('fullTimeEmployees')):,}" if safe("fullTimeEmployees") != "N/A" else "N/A",
            "exchange": safe("exchange"),
            "currency": safe("currency"),
            "recommendation": safe("recommendationKey", "N/A").upper() if safe("recommendationKey", "N/A") != "N/A" else "N/A",
            "analyst_count": safe("numberOfAnalystOpinions"),
            "target_price": f"${safe('targetMeanPrice')}" if safe("targetMeanPrice") != "N/A" else "N/A",
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_stock(company: str, ticker: str = "") -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # ── Fetch real data ───────────────────────────────────────────────────────
    data_block = ""
    all_na = True

    if ticker:
        data = _fetch_real_stock_data(ticker)
        if "error" not in data:
            # Check if all values are N/A
            all_na = all(v == "N/A" for v in data.values())
            rows = "\n".join(f"  {k.replace('_',' ').title()}: {v}" for k, v in data.items())
            if not all_na:
                data_block = f"""
LIVE MARKET DATA FOR {company.upper()} ({ticker}):
{rows}

Use ALL of the above real numbers in your analysis. Do NOT say data is unavailable.
"""
            else:
                data_block = f"""Note: All data returned N/A for {ticker}. Use your training knowledge about {company} ({ticker}).
Provide your best analysis based on what you know about this company's stock performance, financials, and market position.
Do NOT say data is unavailable — give a confident analysis using your knowledge."""
        else:
            data_block = f"""Note: yfinance fetch failed ({data['error']}). Use your training knowledge about {company}.
Provide your best analysis based on what you know about this company's stock performance, financials, and market position.
Do NOT say data is unavailable — give a confident analysis using your knowledge."""

    prompt = f"""You are an expert stock market analyst. Analyze {company} ({ticker}) and produce a detailed stock report.

{data_block}

Write a comprehensive Stock Analysis Report with these EXACT sections:

1. Current Stock Performance Summary
   - Quote all the real numbers above (price, change, market cap etc.)
   - Current price trend (up/down/neutral)

2. Key Financial Metrics
   - P/E Ratio analysis and what it means
   - Revenue and profitability overview
   - Earnings per share

3. Technical Analysis
   - 52-week high/low position — is the stock near highs or lows?
   - Volume vs average volume — is there unusual activity?
   - Beta / volatility assessment

4. Buy / Hold / Sell Recommendation
   - Clear recommendation based on analyst consensus and data
   - Target price vs current price
   - Risk level (Low / Medium / High)

5. Key Risk Factors
   - Top 3 specific risks for this company

6. Growth Catalysts
   - Top 3 specific reasons this stock could rise

Format clearly with numbered sections and bullet points. Be specific, confident, and data-driven.
Do NOT say data is unavailable — use the numbers provided or your best knowledge about this company.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=500,
    )
    return response.choices[0].message.content
