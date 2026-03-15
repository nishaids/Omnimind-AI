"""
OMNIMIND AI — ui/settings_page.py
Settings panel: API keys, email config, scraper toggle, theme prefs.
Call render_settings() from app.py to embed this page.
"""

import os
import streamlit as st
from dotenv import load_dotenv, set_key, dotenv_values
from pathlib import Path

ENV_PATH = Path(".env")
load_dotenv(ENV_PATH)

SETTINGS_CSS = """
<style>
.set-section{background:linear-gradient(135deg,#0e0a00,#0a0800);border:1.5px solid #ff8c0033;border-radius:14px;padding:1.3rem 1.4rem;margin-bottom:1rem;}
.set-title{font-family:'Orbitron',monospace;font-size:0.78rem;font-weight:900;color:#ff8c00;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.9rem;display:flex;align-items:center;gap:8px;}
.set-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,#ff8c0033,transparent);}
.set-saved{background:rgba(0,255,136,0.08);border:1px solid #00ff6644;border-radius:8px;padding:8px 14px;color:#00ff88;font-family:'Exo 2',sans-serif;font-size:0.82rem;font-weight:700;margin-top:6px;}
.set-warn{background:rgba(255,200,0,0.07);border:1px solid #ffcc0044;border-radius:8px;padding:8px 14px;color:#ffcc00;font-family:'Exo 2',sans-serif;font-size:0.8rem;margin-top:6px;}
.set-info{background:rgba(0,170,255,0.07);border:1px solid #00aaff33;border-radius:8px;padding:8px 14px;color:#00aaff;font-family:'Exo 2',sans-serif;font-size:0.8rem;margin-top:6px;line-height:1.6;}
</style>
"""

def _save_env(key: str, value: str):
    """Write a key-value pair into .env file."""
    if not ENV_PATH.exists():
        ENV_PATH.touch()
    set_key(str(ENV_PATH), key, value)
    os.environ[key] = value


def render_settings():
    st.markdown(SETTINGS_CSS, unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⚙️ OMNIMIND Settings</div>', unsafe_allow_html=True)

    # ── 1. API KEYS ───────────────────────────────────────────────────────────
    st.markdown('<div class="set-section"><div class="set-title">🔑 API Keys</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        groq_key = st.text_input(
            "GROQ API Key",
            value=os.getenv("GROQ_API_KEY", ""),
            type="password",
            placeholder="gsk_...",
            key="set_groq"
        )
        if st.button("💾 Save GROQ Key", key="save_groq", use_container_width=True):
            if groq_key:
                _save_env("GROQ_API_KEY", groq_key)
                st.markdown('<div class="set-saved">✔ GROQ API Key saved!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="set-warn">⚠ Key cannot be empty.</div>', unsafe_allow_html=True)

    with col2:
        # Optional: if you add OpenAI or other providers later
        openai_key = st.text_input(
            "OpenAI API Key (optional)",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            placeholder="sk-...",
            key="set_openai"
        )
        if st.button("💾 Save OpenAI Key", key="save_openai", use_container_width=True):
            if openai_key:
                _save_env("OPENAI_API_KEY", openai_key)
                st.markdown('<div class="set-saved">✔ OpenAI Key saved!</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── 2. EMAIL CONFIG ───────────────────────────────────────────────────────
    st.markdown('<div class="set-section"><div class="set-title">📧 Email Configuration</div>', unsafe_allow_html=True)

    ec1, ec2 = st.columns(2)
    with ec1:
        email_sender = st.text_input(
            "Gmail Sender Address",
            value=os.getenv("EMAIL_SENDER", ""),
            placeholder="yourname@gmail.com",
            key="set_email_sender"
        )
        if st.button("💾 Save Sender Email", key="save_email_s", use_container_width=True):
            if email_sender:
                _save_env("EMAIL_SENDER", email_sender)
                st.markdown('<div class="set-saved">✔ Sender email saved!</div>', unsafe_allow_html=True)

    with ec2:
        email_pass = st.text_input(
            "Gmail App Password",
            value=os.getenv("EMAIL_PASSWORD", ""),
            type="password",
            placeholder="xxxx xxxx xxxx xxxx",
            key="set_email_pass"
        )
        if st.button("💾 Save App Password", key="save_email_p", use_container_width=True):
            if email_pass:
                _save_env("EMAIL_PASSWORD", email_pass)
                st.markdown('<div class="set-saved">✔ App password saved!</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="set-info">
      ℹ️ Use a <b>Gmail App Password</b> — not your normal Gmail login password.<br>
      Generate one at: <b>myaccount.google.com/apppasswords</b><br>
      Enable 2-Step Verification first, then create an App Password for "OMNIMIND AI".
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 3. SCRAPER SETTINGS ───────────────────────────────────────────────────
    st.markdown('<div class="set-section"><div class="set-title">🌐 Web Scraper Settings</div>', unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1:
        scraper_enabled = st.toggle(
            "Enable Live Web Scraping",
            value=os.getenv("SCRAPER_ENABLED", "true").lower() == "true",
            key="set_scraper"
        )
        _save_env("SCRAPER_ENABLED", "true" if scraper_enabled else "false")
        if scraper_enabled:
            st.markdown('<div class="set-saved">✔ Scraper ON — agents get live data</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="set-warn">⚠ Scraper OFF — agents use LLM knowledge only</div>', unsafe_allow_html=True)

    with sc2:
        scrape_delay = st.slider(
            "Delay between requests (seconds)",
            min_value=0.5, max_value=5.0, step=0.5,
            value=float(os.getenv("SCRAPER_DELAY", "1.0")),
            key="set_scraper_delay"
        )
        if st.button("💾 Save Delay", key="save_delay", use_container_width=True):
            _save_env("SCRAPER_DELAY", str(scrape_delay))
            st.markdown('<div class="set-saved">✔ Delay saved!</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── 4. OUTPUT SETTINGS ────────────────────────────────────────────────────
    st.markdown('<div class="set-section"><div class="set-title">📁 Output Settings</div>', unsafe_allow_html=True)

    oc1, oc2 = st.columns(2)
    with oc1:
        output_dir = st.text_input(
            "PDF Output Directory",
            value=os.getenv("OUTPUT_DIR", "output"),
            key="set_output_dir"
        )
        if st.button("💾 Save Output Dir", key="save_outdir", use_container_width=True):
            _save_env("OUTPUT_DIR", output_dir)
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            st.markdown('<div class="set-saved">✔ Output directory saved & created!</div>', unsafe_allow_html=True)

    with oc2:
        auto_pdf = st.toggle(
            "Auto-generate PDF on every scan",
            value=os.getenv("AUTO_PDF", "false").lower() == "true",
            key="set_auto_pdf"
        )
        _save_env("AUTO_PDF", "true" if auto_pdf else "false")
        if auto_pdf:
            st.markdown('<div class="set-saved">✔ PDF auto-generated after every scan</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── 5. ABOUT ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="set-section">
      <div class="set-title">ℹ️ About OMNIMIND AI</div>
      <div class="set-info">
        <b>OMNIMIND AI</b> — Autonomous Business Intelligence System<br>
        Version: <b>1.0.0</b> &nbsp;|&nbsp; Built with: <b>Python · Streamlit · Groq · LLaMA 3.3</b><br>
        Agents: Research · Stock · News · Report<br>
        Tools: Email Sender · PDF Exporter · Web Scraper · Scheduler<br><br>
        Built by <b>Nishanth R</b> · AI &amp; Data Science · Rajalakshmi Engineering College
      </div>
    </div>
    """, unsafe_allow_html=True)

