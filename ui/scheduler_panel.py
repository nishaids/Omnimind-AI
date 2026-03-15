"""
OMNIMIND AI — ui/scheduler_panel.py
Scheduler control panel: view scheduled jobs, add new ones, start/stop.
Call render_scheduler_panel() from app.py to embed this page.
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

SCHED_CSS = """
<style>
.sched-section{background:linear-gradient(135deg,#0a0e00,#060800);border:1.5px solid #00ff8833;border-radius:14px;padding:1.3rem 1.4rem;margin-bottom:1rem;}
.sched-title{font-family:'Orbitron',monospace;font-size:0.78rem;font-weight:900;color:#00ff88;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.9rem;display:flex;align-items:center;gap:8px;}
.sched-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,#00ff8833,transparent);}
.job-card{background:#070f07;border:1px solid #00ff8822;border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;}
.job-co{font-family:'Orbitron',monospace;font-size:0.78rem;font-weight:900;color:#fff;letter-spacing:0.08em;}
.job-ticker{font-family:'Orbitron',monospace;font-size:0.72rem;color:#00ff88;letter-spacing:0.12em;background:rgba(0,255,136,0.1);padding:2px 8px;border-radius:6px;border:1px solid #00ff8833;}
.job-time{font-family:'Exo 2',sans-serif;font-size:0.8rem;color:#ffcc00;font-weight:700;}
.job-next{font-family:'Exo 2',sans-serif;font-size:0.72rem;color:#666;}
.status-on{display:inline-flex;align-items:center;gap:6px;background:rgba(0,255,136,0.1);border:1px solid #00ff6644;border-radius:20px;padding:4px 14px;font-family:'Orbitron',monospace;font-size:0.65rem;font-weight:700;color:#00ff88;letter-spacing:0.1em;}
.status-off{display:inline-flex;align-items:center;gap:6px;background:rgba(255,80,80,0.1);border:1px solid #ff444444;border-radius:20px;padding:4px 14px;font-family:'Orbitron',monospace;font-size:0.65rem;font-weight:700;color:#ff6666;letter-spacing:0.1em;}
.dot-on{width:7px;height:7px;background:#00ff88;border-radius:50%;box-shadow:0 0 6px #00ff88;animation:blink 1.2s ease-in-out infinite;}
.dot-off{width:7px;height:7px;background:#ff4444;border-radius:50%;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.2;}}
.sched-stat-box{background:#050f05;border:1px solid #00ff8822;border-radius:10px;padding:0.7rem 1rem;text-align:center;}
.sched-stat-num{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;color:#00ff88;text-shadow:0 0 15px rgba(0,255,136,0.5);}
.sched-stat-lbl{font-family:'Exo 2',sans-serif;font-size:0.7rem;color:#666;text-transform:uppercase;letter-spacing:0.1em;}
</style>
"""

# Default scheduled companies
DEFAULT_COMPANIES = [
    {"company": "Tesla",   "ticker": "TSLA",      "time": "08:00", "email": ""},
    {"company": "TCS",     "ticker": "TCS.NS",    "time": "08:05", "email": ""},
    {"company": "Apple",   "ticker": "AAPL",      "time": "08:10", "email": ""},
    {"company": "Zomato",  "ticker": "ZOMATO.NS", "time": "08:15", "email": ""},
    {"company": "Infosys", "ticker": "INFY",      "time": "08:20", "email": ""},
]


def _init_state():
    if "scheduler_running" not in st.session_state:
        st.session_state.scheduler_running = False
    if "scheduled_jobs" not in st.session_state:
        st.session_state.scheduled_jobs = list(DEFAULT_COMPANIES)
    if "sched_log" not in st.session_state:
        st.session_state.sched_log = []


def render_scheduler_panel():
    _init_state()
    st.markdown(SCHED_CSS, unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⏰ Scheduler Control Panel</div>', unsafe_allow_html=True)

    # ── STATUS BAR ────────────────────────────────────────────────────────────
    running = st.session_state.scheduler_running
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="sched-stat-box">
          <div class="sched-stat-num">{len(st.session_state.scheduled_jobs)}</div>
          <div class="sched-stat-lbl">Scheduled Jobs</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="sched-stat-box">
          <div class="sched-stat-num" style="color:#ffcc00">{len(st.session_state.sched_log)}</div>
          <div class="sched-stat-lbl">Scans Run Today</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        next_time = st.session_state.scheduled_jobs[0]["time"] if st.session_state.scheduled_jobs else "--"
        st.markdown(f"""
        <div class="sched-stat-box">
          <div class="sched-stat-num" style="color:#00aaff;font-size:1.2rem">{next_time}</div>
          <div class="sched-stat-lbl">Next Scan</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        dot = "dot-on" if running else "dot-off"
        badge = "status-on" if running else "status-off"
        label = "RUNNING" if running else "STOPPED"
        st.markdown(f"""
        <div class="sched-stat-box" style="display:flex;align-items:center;justify-content:center;height:100%;">
          <span class="{badge}"><span class="{dot}"></span>{label}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── START / STOP BUTTONS ──────────────────────────────────────────────────
    st.markdown('<div class="sched-section"><div class="sched-title">🎮 Scheduler Control</div>', unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        if st.button("▶ START SCHEDULER", key="sched_start",
                     disabled=running, use_container_width=True):
            try:
                from tools.scheduler import start_scheduler_background
                msg = start_scheduler_background()
                st.session_state.scheduler_running = True
                st.session_state.sched_log.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler started")
                st.success(f"✔ {msg}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    with bc2:
        if st.button("⏹ STOP SCHEDULER", key="sched_stop",
                     disabled=not running, use_container_width=True):
            try:
                from tools.scheduler import stop_scheduler
                stop_scheduler()
                st.session_state.scheduler_running = False
                st.session_state.sched_log.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler stopped")
                st.warning("⚠ Scheduler stopped.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    with bc3:
        if st.button("⚡ RUN ALL NOW", key="sched_now", use_container_width=True):
            with st.spinner("Running all scans now..."):
                try:
                    from tools.scheduler import run_scan
                    for job in st.session_state.scheduled_jobs:
                        run_scan(job["company"], job["ticker"], job.get("email", ""))
                        st.session_state.sched_log.append(
                            f"[{datetime.now().strftime('%H:%M:%S')}] Scanned: {job['company']}")
                    st.success("✔ All scans completed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SCHEDULED JOBS LIST ───────────────────────────────────────────────────
    st.markdown('<div class="sched-section"><div class="sched-title">📋 Scheduled Companies</div>', unsafe_allow_html=True)

    for i, job in enumerate(st.session_state.scheduled_jobs):
        jc1, jc2, jc3, jc4, jc5 = st.columns([2.5, 1.5, 1.2, 2, 0.8])
        with jc1:
            st.markdown(f'<div class="job-co">🎯 {job["company"]}</div>', unsafe_allow_html=True)
        with jc2:
            st.markdown(f'<div class="job-ticker">{job["ticker"]}</div>', unsafe_allow_html=True)
        with jc3:
            st.markdown(f'<div class="job-time">⏰ {job["time"]}</div>', unsafe_allow_html=True)
        with jc4:
            new_email = st.text_input(
                "Email", value=job.get("email", ""),
                placeholder="optional@email.com",
                key=f"job_email_{i}", label_visibility="collapsed"
            )
            st.session_state.scheduled_jobs[i]["email"] = new_email
        with jc5:
            if st.button("🗑", key=f"del_job_{i}", help="Remove this job"):
                st.session_state.scheduled_jobs.pop(i)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── ADD NEW JOB ───────────────────────────────────────────────────────────
    st.markdown('<div class="sched-section"><div class="sched-title">➕ Add New Scheduled Scan</div>', unsafe_allow_html=True)

    nc1, nc2, nc3, nc4 = st.columns([2.5, 1.5, 1.5, 1.5])
    with nc1:
        new_co = st.text_input("Company", placeholder="e.g. Nvidia", key="new_co")
    with nc2:
        new_tk = st.text_input("Ticker", placeholder="e.g. NVDA", key="new_tk")
    with nc3:
        new_time = st.text_input("Time (24h)", placeholder="e.g. 09:00", key="new_time", value="09:00")
    with nc4:
        new_mail = st.text_input("Email (opt)", placeholder="you@gmail.com", key="new_mail")

    if st.button("➕ ADD TO SCHEDULE", key="add_job", use_container_width=True):
        if new_co and new_tk and new_time:
            st.session_state.scheduled_jobs.append({
                "company": new_co, "ticker": new_tk,
                "time": new_time, "email": new_mail
            })
            try:
                from tools.scheduler import update_schedule
                update_schedule(new_co, new_tk, new_time, new_mail)
            except Exception:
                pass
            st.success(f"✔ Added: {new_co} ({new_tk}) at {new_time} daily!")
            st.rerun()
        else:
            st.warning("⚠ Please fill Company, Ticker, and Time.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── ACTIVITY LOG ─────────────────────────────────────────────────────────
    if st.session_state.sched_log:
        st.markdown('<div class="sched-section"><div class="sched-title">📜 Activity Log</div>', unsafe_allow_html=True)
        log_text = "\n".join(reversed(st.session_state.sched_log[-20:]))
        st.code(log_text, language="bash")
        if st.button("🗑 Clear Log", key="clear_log"):
            st.session_state.sched_log = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

