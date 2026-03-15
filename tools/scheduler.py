"""
OMNIMIND AI — tools/scheduler.py
Auto-run company intelligence scans on a schedule.
Saves results to output/ folder and optionally emails them.

Usage:
    python tools/scheduler.py                  # runs scheduler in background
    python tools/scheduler.py --now TSLA Tesla # run one scan immediately

pip install schedule
"""

import os
import json
import time
import argparse
import schedule
import threading
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Output directory ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output/scheduled")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Scheduled companies config ────────────────────────────────────────────────
# Edit this list to set which companies to auto-scan and when
SCHEDULE_CONFIG = [
    # { company, ticker, time (24h), email_to (optional) }
    {"company": "Tesla",     "ticker": "TSLA",         "time": "08:00", "email_to": ""},
    {"company": "TCS",       "ticker": "TCS.NS",       "time": "08:05", "email_to": ""},
    {"company": "Apple",     "ticker": "AAPL",         "time": "08:10", "email_to": ""},
    {"company": "Zomato",    "ticker": "ZOMATO.NS",    "time": "08:15", "email_to": ""},
    {"company": "Infosys",   "ticker": "INFY",         "time": "08:20", "email_to": ""},
]


# ── Core scan runner ──────────────────────────────────────────────────────────
def run_scan(company: str, ticker: str, email_to: str = "") -> dict:
    """
    Run a full OMNIMIND 4-agent scan for one company and save result.
    Optionally email the report.
    """
    print(f"\n[Scheduler] ⚡ Starting scan: {company} ({ticker}) at {datetime.now().strftime('%H:%M:%S')}")

    try:
        # Import agents dynamically (avoids circular imports)
        from agents.research_agent import research_company
        from agents.stock_agent import analyze_stock
        from agents.news_agent import analyze_news
        from agents.report_agent import generate_report

        print(f"[Scheduler] 🔬 Research Agent running...")
        r = research_company(company)

        print(f"[Scheduler] 📈 Stock Agent running...")
        s = analyze_stock(company, ticker) if ticker else "No ticker provided."

        print(f"[Scheduler] 📰 News Agent running...")
        n = analyze_news(company)

        print(f"[Scheduler] 📊 Report Agent running...")
        rep = generate_report(company, r, s, n)

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = {
            "company":   company,
            "ticker":    ticker,
            "scanned_at": timestamp,
            "research":  r,
            "stock":     s,
            "news":      n,
            "report":    rep,
        }
        out_path = OUTPUT_DIR / f"{company.replace(' ','_')}_{timestamp}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[Scheduler] ✅ Saved: {out_path}")

        # Export PDF
        try:
            from tools.pdf_exporter import export_pdf
            pdf = export_pdf(company, r, s, n, rep, output_dir=str(OUTPUT_DIR))
            pdf_path = pdf.get("path")
            print(f"[Scheduler] 📄 PDF: {pdf_path}")
        except Exception as pdf_err:
            pdf_path = None
            print(f"[Scheduler] ⚠️ PDF skipped: {pdf_err}")

        # Send email
        if email_to:
            try:
                from tools.email_sender import send_report_email
                em = send_report_email(email_to, company, r, s, n, rep, pdf_path)
                print(f"[Scheduler] 📧 Email: {em['message']}")
            except Exception as em_err:
                print(f"[Scheduler] ⚠️ Email skipped: {em_err}")

        return result

    except Exception as e:
        print(f"[Scheduler] ❌ Scan failed for {company}: {e}")
        return {"company": company, "error": str(e)}


# ── Schedule jobs ─────────────────────────────────────────────────────────────
def setup_schedule():
    """Register all company scans from SCHEDULE_CONFIG."""
    for cfg in SCHEDULE_CONFIG:
        company  = cfg["company"]
        ticker   = cfg.get("ticker", "")
        run_time = cfg.get("time", "08:00")
        email_to = cfg.get("email_to", "")

        # Daily at specified time
        schedule.every().day.at(run_time).do(
            run_scan, company=company, ticker=ticker, email_to=email_to
        )
        print(f"[Scheduler] 📅 Scheduled: {company} ({ticker}) at {run_time} daily")

    # Also run a portfolio summary every Sunday at 09:00
    schedule.every().sunday.at("09:00").do(run_weekly_summary)
    print("[Scheduler] 📅 Weekly summary: Sundays at 09:00")


def run_weekly_summary():
    """Run all companies and compile a weekly summary."""
    print("\n[Scheduler] ⭐ Running weekly portfolio summary...")
    for cfg in SCHEDULE_CONFIG:
        run_scan(cfg["company"], cfg.get("ticker", ""), cfg.get("email_to", ""))
        time.sleep(5)  # avoid rate limits between scans


# ── Background thread ─────────────────────────────────────────────────────────
_scheduler_thread = None
_scheduler_running = False


def start_scheduler_background():
    """Start the scheduler in a background daemon thread (called from app.py)."""
    global _scheduler_thread, _scheduler_running
    if _scheduler_running:
        return "Scheduler already running."

    setup_schedule()
    _scheduler_running = True

    def _loop():
        while _scheduler_running:
            schedule.run_pending()
            time.sleep(30)

    _scheduler_thread = threading.Thread(target=_loop, daemon=True)
    _scheduler_thread.start()
    return "Scheduler started successfully."


def stop_scheduler():
    global _scheduler_running
    _scheduler_running = False
    schedule.clear()
    return "Scheduler stopped."


def get_next_jobs(n: int = 5) -> list[dict]:
    """Return the next N scheduled jobs as a list of dicts."""
    jobs = []
    for job in sorted(schedule.jobs, key=lambda j: j.next_run)[:n]:
        jobs.append({
            "job": str(job.job_func.func.__name__ if hasattr(job.job_func, 'func') else job.job_func),
            "next_run": str(job.next_run),
            "interval": str(job.interval),
        })
    return jobs


def update_schedule(company: str, ticker: str, run_time: str, email_to: str = ""):
    """Dynamically add a new company to the scheduler at runtime."""
    schedule.every().day.at(run_time).do(
        run_scan, company=company, ticker=ticker, email_to=email_to
    )
    SCHEDULE_CONFIG.append({"company": company, "ticker": ticker, "time": run_time, "email_to": email_to})
    return f"Added: {company} at {run_time} daily."


def load_past_results(company: str = "", limit: int = 10) -> list[dict]:
    """Load past saved scan results from output/scheduled/ folder."""
    results = []
    pattern = f"{company.replace(' ','_')}*.json" if company else "*.json"
    files = sorted(OUTPUT_DIR.glob(pattern), reverse=True)[:limit]
    for f in files:
        try:
            with open(f, encoding="utf-8") as fp:
                results.append(json.load(fp))
        except Exception:
            continue
    return results


# ── CLI entrypoint ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMNIMIND AI Scheduler")
    parser.add_argument("--now", nargs=2, metavar=("TICKER", "COMPANY"),
                        help="Run a scan immediately: --now TSLA Tesla")
    parser.add_argument("--list", action="store_true", help="List scheduled jobs")
    args = parser.parse_args()

    if args.now:
        ticker, company = args.now
        run_scan(company, ticker)
    elif args.list:
        setup_schedule()
        jobs = get_next_jobs(10)
        print("\nScheduled Jobs:")
        for j in jobs:
            print(f"  Next: {j['next_run']} — {j['job']}")
    else:
        print("\n⚡ OMNIMIND AI Scheduler Starting...\n")
        setup_schedule()
        print("\n[Scheduler] Running... Press Ctrl+C to stop.\n")
        while True:
            schedule.run_pending()
            time.sleep(30)
