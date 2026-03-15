"""
OMNIMIND AI — ui/history_viewer.py
Scan history viewer: browse past scans, re-read reports, re-send emails.
Call render_history() from app.py to embed this page.
"""

import os
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

HISTORY_CSS = """
<style>
.hist-section{background:linear-gradient(135deg,#00050e,#000812);border:1.5px solid #00aaff33;border-radius:14px;padding:1.3rem 1.4rem;margin-bottom:1rem;}
.hist-title{font-family:'Orbitron',monospace;font-size:0.78rem;font-weight:900;color:#00aaff;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.9rem;display:flex;align-items:center;gap:8px;}
.hist-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,#00aaff33,transparent);}
.hist-card{background:#020c16;border:1px solid #00aaff22;border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem;transition:all 0.25s;cursor:pointer;}
.hist-card:hover{border-color:#00aaff88;box-shadow:0 0 20px rgba(0,170,255,0.15);}
.hist-co{font-family:'Orbitron',monospace;font-size:0.9rem;font-weight:900;color:#fff;letter-spacing:0.08em;}
.hist-ticker{font-family:'Orbitron',monospace;font-size:0.72rem;color:#00ff88;background:rgba(0,255,136,0.1);padding:2px 8px;border-radius:6px;border:1px solid #00ff8833;margin-left:8px;}
.hist-date{font-family:'Exo 2',sans-serif;font-size:0.75rem;color:#555;margin-top:4px;}
.hist-badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:0.65rem;font-weight:700;background:rgba(0,170,255,0.1);color:#00aaff;border:1px solid #00aaff33;font-family:'Orbitron',monospace;letter-spacing:0.08em;}
.hist-empty{text-align:center;padding:3rem 1rem;color:#333;font-family:'Exo 2',sans-serif;font-size:1rem;font-weight:600;}
.hist-stat-box{background:#020c16;border:1px solid #00aaff22;border-radius:10px;padding:0.7rem 1rem;text-align:center;}
.hist-stat-num{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;color:#00aaff;text-shadow:0 0 14px rgba(0,170,255,0.5);}
.hist-stat-lbl{font-family:'Exo 2',sans-serif;font-size:0.7rem;color:#555;text-transform:uppercase;letter-spacing:0.1em;}
.preview-box{background:#020c16;border:1px solid #00aaff22;border-radius:10px;padding:1rem 1.2rem;font-family:'Exo 2',sans-serif;font-size:0.85rem;color:#ccc;line-height:1.8;white-space:pre-wrap;max-height:320px;overflow-y:auto;}
</style>
"""

OUTPUT_DIR = Path("output/scheduled")


def _load_all_scans(limit: int = 50) -> list[dict]:
    """Load all saved scan JSON files sorted newest first."""
    scans = []
    if not OUTPUT_DIR.exists():
        return scans
    for f in sorted(OUTPUT_DIR.glob("*.json"), reverse=True)[:limit]:
        try:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
                data["_file"] = str(f)
                scans.append(data)
        except Exception:
            continue
    return scans


def _format_dt(raw: str) -> str:
    """Format raw timestamp string nicely."""
    try:
        dt = datetime.strptime(raw, "%Y%m%d_%H%M%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return raw


def render_history():
    st.markdown(HISTORY_CSS, unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📜 Scan History Viewer</div>', unsafe_allow_html=True)

    scans = _load_all_scans()

    # ── STATS ROW ─────────────────────────────────────────────────────────────
    companies = list({s.get("company", "?") for s in scans})
    today = datetime.now().strftime("%Y%m%d")
    today_count = sum(1 for s in scans if s.get("scanned_at", "").startswith(today))

    st1, st2, st3 = st.columns(3)
    with st1:
        st.markdown(f"""
        <div class="hist-stat-box">
          <div class="hist-stat-num">{len(scans)}</div>
          <div class="hist-stat-lbl">Total Scans</div>
        </div>""", unsafe_allow_html=True)
    with st2:
        st.markdown(f"""
        <div class="hist-stat-box">
          <div class="hist-stat-num" style="color:#00ff88">{len(companies)}</div>
          <div class="hist-stat-lbl">Companies Tracked</div>
        </div>""", unsafe_allow_html=True)
    with st3:
        st.markdown(f"""
        <div class="hist-stat-box">
          <div class="hist-stat-num" style="color:#ffcc00">{today_count}</div>
          <div class="hist-stat-lbl">Scans Today</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not scans:
        st.markdown("""
        <div class="hist-section">
          <div class="hist-empty">
            📭 No scan history yet.<br><br>
            Run a scan from the main page or start the Scheduler<br>
            and your reports will appear here automatically!
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── FILTER BAR ────────────────────────────────────────────────────────────
    st.markdown('<div class="hist-section"><div class="hist-title">🔍 Filter History</div>', unsafe_allow_html=True)
    fc1, fc2 = st.columns([3, 1])
    with fc1:
        search = st.text_input("Search company", placeholder="e.g. Tesla, TCS...",
                               key="hist_search", label_visibility="collapsed")
    with fc2:
        limit = st.selectbox("Show", [10, 25, 50], key="hist_limit", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filter
    filtered = [s for s in scans if search.lower() in s.get("company", "").lower()] if search else scans
    filtered = filtered[:limit]

    # ── SCAN LIST ─────────────────────────────────────────────────────────────
    st.markdown('<div class="hist-section"><div class="hist-title">📋 Past Scans</div>', unsafe_allow_html=True)

    if not filtered:
        st.markdown('<div class="hist-empty">No results found for your search.</div>', unsafe_allow_html=True)

    selected_scan = None
    for i, scan in enumerate(filtered):
        co = scan.get("company", "Unknown")
        tk = scan.get("ticker", "")
        dt = _format_dt(scan.get("scanned_at", ""))
        has_error = "error" in scan

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="hist-card">
              <div>
                <span class="hist-co">{co}</span>
                <span class="hist-ticker">{tk}</span>
                {'<span class="hist-badge" style="color:#ff6666;border-color:#ff444433;background:rgba(255,50,50,0.08)">ERROR</span>' if has_error else '<span class="hist-badge">COMPLETE</span>'}
              </div>
              <div class="hist-date">📅 {dt}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("👁 View", key=f"view_{i}", use_container_width=True):
                st.session_state[f"hist_open_{i}"] = not st.session_state.get(f"hist_open_{i}", False)

        # Expandable report preview
        if st.session_state.get(f"hist_open_{i}", False):
            with st.expander(f"📊 {co} — Full Report", expanded=True):
                if has_error:
                    st.error(f"Scan failed: {scan['error']}")
                else:
                    rep_tab, res_tab, stk_tab, news_tab = st.tabs([
                        "📊 Report", "🔬 Research", "📈 Stock", "📰 News"
                    ])
                    with rep_tab:
                        st.markdown(f'<div class="preview-box">{scan.get("report","No data")}</div>',
                                    unsafe_allow_html=True)
                    with res_tab:
                        st.markdown(f'<div class="preview-box">{scan.get("research","No data")}</div>',
                                    unsafe_allow_html=True)
                    with stk_tab:
                        st.markdown(f'<div class="preview-box">{scan.get("stock","No data")}</div>',
                                    unsafe_allow_html=True)
                    with news_tab:
                        st.markdown(f'<div class="preview-box">{scan.get("news","No data")}</div>',
                                    unsafe_allow_html=True)

                    # Action buttons
                    ac1, ac2, ac3 = st.columns(3)
                    with ac1:
                        # Re-export PDF
                        if st.button("📄 Export PDF", key=f"re_pdf_{i}", use_container_width=True):
                            with st.spinner("Generating PDF..."):
                                try:
                                    from tools.pdf_exporter import export_pdf
                                    r = export_pdf(co, scan.get("research",""),
                                                   scan.get("stock",""), scan.get("news",""),
                                                   scan.get("report",""), output_dir="output")
                                    if r["success"]:
                                        with open(r["path"], "rb") as f:
                                            st.download_button("⬇️ Download PDF", f.read(),
                                                               file_name=f"{co}_Report.pdf",
                                                               mime="application/pdf",
                                                               key=f"dl_pdf_{i}",
                                                               use_container_width=True)
                                    else:
                                        st.error(r["message"])
                                except Exception as e:
                                    st.error(str(e))
                    with ac2:
                        # Re-send email
                        re_email = st.text_input("Email", placeholder="send to...",
                                                 key=f"re_email_{i}", label_visibility="collapsed")
                        if st.button("📧 Email Report", key=f"re_send_{i}", use_container_width=True):
                            if re_email:
                                with st.spinner("Sending..."):
                                    try:
                                        from tools.email_sender import send_report_email
                                        r = send_report_email(re_email, co,
                                                              scan.get("research",""),
                                                              scan.get("stock",""),
                                                              scan.get("news",""),
                                                              scan.get("report",""))
                                        if r["success"]:
                                            st.success(r["message"])
                                        else:
                                            st.error(r["message"])
                                    except Exception as e:
                                        st.error(str(e))
                            else:
                                st.warning("Enter an email address first!")
                    with ac3:
                        # Load into main session
                        if st.button("🔄 Load into App", key=f"load_{i}", use_container_width=True):
                            st.session_state.results = {
                                "company": co,
                                "research": scan.get("research",""),
                                "stock": scan.get("stock",""),
                                "news": scan.get("news",""),
                                "report": scan.get("report",""),
                            }
                            st.session_state.scan_done = True
                            st.success(f"✔ {co} loaded! Go to the main page to view.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── DELETE ALL ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear All History", key="clear_all_hist"):
        confirm = st.checkbox("⚠ Confirm delete ALL scan history?", key="confirm_del")
        if confirm:
            for f in OUTPUT_DIR.glob("*.json"):
                f.unlink()
            st.success("✔ All history cleared!")
            st.rerun()
