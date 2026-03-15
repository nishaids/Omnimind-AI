"""
OMNIMIND AI — main.py
Master entry point. Handles CLI commands, startup checks,
scheduler launch, and kicks off the Streamlit app.

Usage:
    python main.py              → launch the full app
    python main.py --check      → check all dependencies & API keys
    python main.py --scan Tesla TSLA          → run one scan from CLI
    python main.py --scheduler  → start scheduler in background + launch app
    python main.py --version    → show version info
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Version ───────────────────────────────────────────────────────────────────
VERSION     = "1.0.0"
APP_NAME    = "OMNIMIND AI"
AUTHOR      = "Nishanth R"
DESCRIPTION = "Autonomous Business Intelligence System"


# ── Terminal colours ──────────────────────────────────────────────────────────
class C:
    ORANGE  = "\033[38;5;208m"
    GOLD    = "\033[38;5;220m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"
    BOLD    = "\033[1m"
    RESET   = "\033[0m"


def banner():
    print(f"""
{C.ORANGE}{C.BOLD}
  ██████╗ ███╗   ███╗███╗   ██╗██╗███╗   ███╗██╗███╗   ██╗██████╗
 ██╔═══██╗████╗ ████║████╗  ██║██║████╗ ████║██║████╗  ██║██╔══██╗
 ██║   ██║██╔████╔██║██╔██╗ ██║██║██╔████╔██║██║██╔██╗ ██║██║  ██║
 ██║   ██║██║╚██╔╝██║██║╚██╗██║██║██║╚██╔╝██║██║██║╚██╗██║██║  ██║
 ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
{C.RESET}{C.GOLD}          ⚡  Autonomous Business Intelligence System  ⚡
{C.DIM}              v{VERSION}  ·  Built by {AUTHOR}  ·  2025{C.RESET}
""")


def log(label: str, msg: str, color=C.WHITE):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.DIM}[{ts}]{C.RESET} {color}{C.BOLD}{label}{C.RESET}  {msg}")


def ok(msg):   log("  ✔ ", msg, C.GREEN)
def err(msg):  log("  ✘ ", msg, C.RED)
def info(msg): log("  ▶ ", msg, C.CYAN)
def warn(msg): log("  ⚠ ", msg, C.GOLD)


# ── Dependency checker ────────────────────────────────────────────────────────
def check_dependencies() -> bool:
    info("Checking Python packages...")
    required = [
        ("streamlit",     "streamlit"),
        ("groq",          "groq"),
        ("dotenv",        "python-dotenv"),
        ("requests",      "requests"),
        ("bs4",           "beautifulsoup4"),
        ("reportlab",     "reportlab"),
        ("schedule",      "schedule"),
        ("yfinance",      "yfinance"),
    ]
    all_ok = True
    for module, pkg in required:
        try:
            __import__(module)
            ok(f"{pkg}")
        except ImportError:
            err(f"{pkg}  →  run: pip install {pkg}")
            all_ok = False
    return all_ok


def check_env() -> bool:
    info("Checking environment variables...")
    checks = [
        ("GROQ_API_KEY",    "Required — get from console.groq.com",     True),
        ("EMAIL_SENDER",    "Optional — for email reports",              False),
        ("EMAIL_PASSWORD",  "Optional — Gmail App Password",             False),
    ]
    all_ok = True
    for key, hint, required in checks:
        val = os.getenv(key, "")
        if val:
            masked = val[:6] + "..." + val[-4:] if len(val) > 10 else "***"
            ok(f"{key} = {masked}")
        elif required:
            err(f"{key} is MISSING  →  {hint}")
            all_ok = False
        else:
            warn(f"{key} not set  ({hint})")
    return all_ok


def check_folders():
    info("Checking project structure...")
    folders = ["agents", "tools", "ui", "output"]
    for folder in folders:
        p = Path(folder)
        if p.exists():
            ok(f"{folder}/")
        else:
            warn(f"{folder}/ missing — creating...")
            p.mkdir(parents=True, exist_ok=True)

    files = [
        "agents/research_agent.py",
        "agents/stock_agent.py",
        "agents/news_agent.py",
        "agents/report_agent.py",
        "tools/email_sender.py",
        "tools/pdf_exporter.py",
        "tools/web_scraper.py",
        "tools/scheduler.py",
        "ui/settings_page.py",
        "ui/scheduler_panel.py",
        "ui/history_viewer.py",
        "app.py",
        ".env",
    ]
    for f in files:
        if Path(f).exists():
            ok(f)
        else:
            err(f"{f}  →  FILE MISSING")


def run_full_check():
    banner()
    print(f"{C.GOLD}{'─'*60}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}  OMNIMIND AI — System Health Check{C.RESET}")
    print(f"{C.GOLD}{'─'*60}{C.RESET}\n")

    deps_ok = check_dependencies()
    print()
    env_ok  = check_env()
    print()
    check_folders()

    print(f"\n{C.GOLD}{'─'*60}{C.RESET}")
    if deps_ok and env_ok:
        print(f"{C.GREEN}{C.BOLD}  ✔ All checks passed! OMNIMIND AI is ready to launch.{C.RESET}")
    else:
        print(f"{C.RED}{C.BOLD}  ✘ Some issues found. Fix them before launching.{C.RESET}")
    print(f"{C.GOLD}{'─'*60}{C.RESET}\n")
    return deps_ok and env_ok


# ── CLI single scan ───────────────────────────────────────────────────────────
def cli_scan(company: str, ticker: str):
    banner()
    print(f"{C.GOLD}{'─'*60}{C.RESET}")
    info(f"Running CLI scan: {company} ({ticker})")
    print(f"{C.GOLD}{'─'*60}{C.RESET}\n")

    try:
        from agents.research_agent import research_company
        from agents.stock_agent    import analyze_stock
        from agents.news_agent     import analyze_news
        from agents.report_agent   import generate_report
        from tools.pdf_exporter    import export_pdf

        info("Research Agent scanning...")
        r = research_company(company)
        ok("Research done")

        info("Stock Agent fetching market data...")
        s = analyze_stock(company, ticker) if ticker else "No ticker provided."
        ok("Stock done")

        info("News Agent scanning headlines...")
        n = analyze_news(company)
        ok("News done")

        info("Report Agent generating executive report...")
        rep = generate_report(company, r, s, n)
        ok("Report done")

        # Save PDF
        info("Exporting PDF...")
        pdf = export_pdf(company, r, s, n, rep, output_dir="output")
        if pdf["success"]:
            ok(f"PDF saved → {pdf['path']}")
        else:
            warn(f"PDF failed: {pdf['message']}")

        # Print report summary to terminal
        print(f"\n{C.GOLD}{'─'*60}{C.RESET}")
        print(f"{C.ORANGE}{C.BOLD}  EXECUTIVE REPORT — {company.upper()}{C.RESET}")
        print(f"{C.GOLD}{'─'*60}{C.RESET}")
        print(f"{C.WHITE}{rep[:800]}...{C.RESET}")
        print(f"{C.GOLD}{'─'*60}{C.RESET}\n")

    except Exception as e:
        err(f"Scan failed: {e}")
        sys.exit(1)


# ── Launch Streamlit app ──────────────────────────────────────────────────────
def launch_app(with_scheduler: bool = False):
    banner()

    if with_scheduler:
        info("Starting background scheduler...")
        try:
            from tools.scheduler import start_scheduler_background
            msg = start_scheduler_background()
            ok(msg)
        except Exception as e:
            warn(f"Scheduler could not start: {e}")

    print(f"\n{C.GREEN}{C.BOLD}  ⚡ Launching OMNIMIND AI...{C.RESET}")
    print(f"{C.DIM}  Open your browser at: http://localhost:8501{C.RESET}\n")
    print(f"{C.GOLD}{'─'*60}{C.RESET}\n")

    # Ensure output folders exist
    Path("output").mkdir(exist_ok=True)
    Path("output/scheduled").mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "dark",
            "--theme.primaryColor", "#ff8c00",
            "--theme.backgroundColor", "#030303",
            "--theme.secondaryBackgroundColor", "#0e0e0e",
            "--theme.textColor", "#ffffff",
        ], check=True)
    except KeyboardInterrupt:
        print(f"\n{C.GOLD}  ⚡ OMNIMIND AI shut down. Goodbye!{C.RESET}\n")
    except subprocess.CalledProcessError as e:
        err(f"App crashed: {e}")
        sys.exit(1)


# ── Version info ──────────────────────────────────────────────────────────────
def show_version():
    banner()
    print(f"  {C.GOLD}App Name   :{C.RESET} {APP_NAME}")
    print(f"  {C.GOLD}Version    :{C.RESET} {VERSION}")
    print(f"  {C.GOLD}Author     :{C.RESET} {AUTHOR}")
    print(f"  {C.GOLD}Description:{C.RESET} {DESCRIPTION}")
    print(f"  {C.GOLD}Python     :{C.RESET} {sys.version.split()[0]}")
    print(f"  {C.GOLD}Platform   :{C.RESET} {sys.platform}\n")


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        prog="omnimind",
        description=f"{APP_NAME} — {DESCRIPTION}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Run system health check (dependencies, env vars, files)"
    )
    parser.add_argument(
        "--scan", nargs=2, metavar=("COMPANY", "TICKER"),
        help="Run a single scan from CLI\n  Example: --scan Tesla TSLA"
    )
    parser.add_argument(
        "--scheduler", action="store_true",
        help="Start background scheduler then launch the app"
    )
    parser.add_argument(
        "--version", action="store_true",
        help="Show version information"
    )
    return parser.parse_args()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = parse_args()

    if args.version:
        show_version()

    elif args.check:
        ok_flag = run_full_check()
        sys.exit(0 if ok_flag else 1)

    elif args.scan:
        company, ticker = args.scan
        cli_scan(company, ticker)

    elif args.scheduler:
        launch_app(with_scheduler=True)

    else:
        # Default: just launch the app
        launch_app(with_scheduler=False)
