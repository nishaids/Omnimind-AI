import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv

load_dotenv()

COMPANIES = [
    "Tesla","Apple","Google","Microsoft","Amazon","Meta","Netflix","Nvidia",
    "Samsung","Sony","Toyota","BMW","Mercedes","Tata Motors","Infosys","TCS",
    "Wipro","Reliance","Zomato","Paytm","HDFC Bank","ICICI Bank",
    "Ola","Uber","Airbnb","SpaceX","Stripe","Salesforce","Adobe","Intel",
    "OpenAI","Anthropic","IBM","Oracle","Cisco","Qualcomm","AMD","TSMC"
]
TICKERS = {
    "Tesla":"TSLA","Apple":"AAPL","Google":"GOOGL","Microsoft":"MSFT",
    "Amazon":"AMZN","Meta":"META","Netflix":"NFLX","Nvidia":"NVDA",
    "Samsung":"005930.KS","Sony":"SONY","Toyota":"TM","BMW":"BMW.DE",
    "Infosys":"INFY","TCS":"TCS.NS","Wipro":"WIPRO.NS","Reliance":"RELIANCE.NS",
    "Zomato":"ZOMATO.NS","HDFC Bank":"HDFCBANK.NS","ICICI Bank":"ICICIBANK.NS",
    "Intel":"INTC","Adobe":"ADBE","Salesforce":"CRM","IBM":"IBM",
    "Oracle":"ORCL","Cisco":"CSCO","Qualcomm":"QCOM","AMD":"AMD","TSMC":"TSM"
}

st.set_page_config(page_title="OMNIMIND AI", page_icon="[OMNIMIND]", layout="wide", initial_sidebar_state="collapsed")

if "bot_mood" not in st.session_state: st.session_state.bot_mood = "idle"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "show_tutorial" not in st.session_state: st.session_state.show_tutorial = True
if "scan_done" not in st.session_state: st.session_state.scan_done = False
if "results" not in st.session_state: st.session_state.results = {}
if "chat_input_key" not in st.session_state: st.session_state.chat_input_key = 0
if "chat_sending" not in st.session_state: st.session_state.chat_sending = False
if "pdf_path" not in st.session_state: st.session_state.pdf_path = None
if "pdf_status" not in st.session_state: st.session_state.pdf_status = ""
if "email_status" not in st.session_state: st.session_state.email_status = ""
if "email_sending" not in st.session_state: st.session_state.email_sending = False
if "active_page" not in st.session_state: st.session_state.active_page = "main"
if "scan_triggered" not in st.session_state: st.session_state.scan_triggered = False
if "scan_company" not in st.session_state: st.session_state.scan_company = ""
if "scan_ticker" not in st.session_state: st.session_state.scan_ticker = ""

# ── SIDEBAR NAVIGATION ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#0a0500,#050300) !important;border-right:1px solid #ff8c0033 !important;}
    .nav-logo{font-family:'Orbitron',monospace;font-size:1rem;font-weight:900;color:#ff8c00;letter-spacing:0.15em;text-align:center;padding:1rem 0 0.3rem;text-shadow:0 0 16px rgba(255,140,0,0.6);}
    .nav-sub{font-family:'Exo 2',sans-serif;font-size:0.6rem;color:#ff8c0077;text-align:center;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:1.2rem;}
    .nav-divider{height:1px;background:linear-gradient(90deg,transparent,#ff8c0033,transparent);margin:0.6rem 0;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-logo">⚡ OMNIMIND</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-sub">Business Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    pages = {
        "main":      "🏠  Intelligence Scanner",
        "history":   "📜  Scan History",
        "scheduler": "⏰  Scheduler",
        "settings":  "⚙️  Settings",
    }
    for key, label in pages.items():
        active = st.session_state.active_page == key
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.active_page = key
            st.rerun()

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Exo 2',sans-serif;font-size:0.65rem;color:#333;text-align:center;padding:0.5rem 0;letter-spacing:0.1em;">
      Built by Nishanth R
    </div>
    """, unsafe_allow_html=True)

mood = st.session_state.bot_mood
active_page = st.session_state.active_page

# ── PAGE ROUTER ───────────────────────────────────────────────────────────────
if active_page == "settings":
    try:
        from ui.settings_page import render_settings
        render_settings()
    except Exception as e:
        st.error(f"Settings error: {e}")
    st.stop()

elif active_page == "scheduler":
    try:
        from ui.scheduler_panel import render_scheduler_panel
        render_scheduler_panel()
    except Exception as e:
        st.error(f"Scheduler error: {e}")
    st.stop()

elif active_page == "history":
    try:
        from ui.history_viewer import render_history
        render_history()
    except Exception as e:
        st.error(f"History error: {e}")
    st.stop()

# else: fall through to main page below

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Exo+2:wght@400;600;700;800&family=Rajdhani:wght@600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{background:#030303 !important;font-family:'Exo 2',sans-serif !important;}
.block-container{padding:1.5rem 2rem 4rem !important;max-width:1500px !important;}

.odiv{height:2px;background:linear-gradient(90deg,transparent,#ff8c00,#ffcc00,#ff4500,#ff8c00,transparent);margin:0.8rem 0;box-shadow:0 0 12px rgba(255,140,0,0.6);}

.stTextInput>div>div>input{background:#0e0e0e !important;color:#ffffff !important;border:1.5px solid #ff8c0066 !important;border-radius:10px !important;font-family:'Exo 2',sans-serif !important;font-size:1rem !important;font-weight:600 !important;padding:0.7rem 1rem !important;transition:all 0.3s !important;}
.stTextInput>div>div>input:focus{border-color:#ff8c00 !important;box-shadow:0 0 20px rgba(255,140,0,0.35) !important;}
.stTextInput>div>div>input::placeholder{color:#444 !important;}
.stTextInput label{color:#ff8c00 !important;font-family:'Exo 2',sans-serif !important;font-weight:700 !important;font-size:0.82rem !important;letter-spacing:0.12em !important;text-transform:uppercase !important;}

.suggestion-wrap{display:flex;flex-wrap:wrap;gap:6px;margin-top:5px;}
.suggestion-pill{background:rgba(255,140,0,0.12);border:1px solid #ff8c0055;border-radius:20px;padding:3px 12px;font-size:0.76rem;font-family:'Exo 2',sans-serif;font-weight:600;color:#ff8c00;}
.ticker-suggest{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:linear-gradient(135deg,rgba(0,255,136,0.07),rgba(0,170,255,0.05));border:1px solid rgba(0,255,136,0.3);border-radius:10px;padding:7px 14px;margin-top:6px;}
.ts-label{font-family:'Exo 2',sans-serif;font-size:0.8rem;font-weight:600;color:#aaa;}
.ts-ticker{font-family:'Orbitron',monospace;font-size:1rem;font-weight:900;color:#00ff88;letter-spacing:0.15em;text-shadow:0 0 12px rgba(0,255,136,0.7);padding:2px 10px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.4);border-radius:6px;}
.ts-note{font-family:'Exo 2',sans-serif;font-size:0.7rem;color:#00ff8877;font-style:italic;}
.ticker-pill{background:rgba(0,170,255,0.1);border:1px solid rgba(0,170,255,0.3);border-radius:20px;padding:3px 12px;font-size:0.76rem;font-family:'Exo 2',sans-serif;font-weight:600;color:#aae8ff;}
.tp-code{font-family:'Orbitron',monospace;font-size:0.72rem;color:#00aaff;font-weight:900;letter-spacing:0.08em;}

.sec-title{font-family:'Orbitron',monospace;font-size:0.85rem;font-weight:700;color:#ff8c00;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.8rem;}

.agent-card{background:linear-gradient(145deg,#0e0e0e,#1a0f00);border:1.5px solid #ff8c0044;border-radius:16px;padding:1.2rem 1rem;text-align:center;transition:all 0.3s;box-shadow:0 4px 20px rgba(255,140,0,0.06);}
.agent-card:hover{border-color:#ff8c00aa;transform:translateY(-4px);box-shadow:0 0 30px rgba(255,140,0,0.3);}
.agent-icon{font-size:2rem;display:block;margin-bottom:0.4rem;filter:drop-shadow(0 0 10px rgba(255,140,0,0.7));}
.agent-name{font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;color:#fff;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.2rem;}
.agent-desc{font-size:0.73rem;color:#ff8c00;font-weight:600;margin-bottom:0.4rem;}
.agent-badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:0.66rem;font-weight:700;letter-spacing:0.1em;background:rgba(255,140,0,0.15);color:#ff8c00;border:1px solid #ff8c0055;}

.stButton>button{background:linear-gradient(135deg,#ff8c00,#ff4500) !important;color:#000 !important;font-family:'Orbitron',monospace !important;font-size:0.9rem !important;font-weight:900 !important;letter-spacing:0.06em !important;text-transform:uppercase !important;border:none !important;border-radius:12px !important;padding:0.85rem 1.1rem !important;width:100% !important;box-shadow:0 0 35px rgba(255,140,0,0.55) !important;transition:all 0.3s !important;white-space:nowrap !important;word-break:keep-all !important;overflow-wrap:normal !important;}
.stButton>button:hover{box-shadow:0 0 60px rgba(255,140,0,0.9) !important;transform:translateY(-2px) !important;}
.stButton>button p{margin:0 !important;white-space:nowrap !important;}

.chat-panel{background:#070707;border:1.5px solid #ff8c0044;border-radius:16px;overflow:hidden;}
.chat-header{background:linear-gradient(135deg,#1a0f00,#0e0800);padding:0;border-bottom:1px solid #ff8c0033;display:flex;align-items:center;gap:0;}
.chat-dot{width:8px;height:8px;border-radius:50%;background:#ff8c00;animation:cpulse 1.5s ease-in-out infinite;box-shadow:0 0 6px #ff8c00;}
@keyframes cpulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.3;transform:scale(0.7)}}
.chat-msgs{padding:1rem;height:300px;overflow-y:auto;display:flex;flex-direction:column;gap:0.5rem;}
.cmsg-u{background:linear-gradient(135deg,#1a0f00,#2a1800);border:1px solid #ff8c0055;border-radius:12px 12px 2px 12px;padding:0.6rem 0.9rem;color:#fff;font-size:0.85rem;font-weight:500;font-family:'Exo 2',sans-serif;align-self:flex-end;max-width:85%;}
.cmsg-b{background:linear-gradient(135deg,#0a1a00,#061200);border:1px solid #00ff6644;border-radius:12px 12px 12px 2px;padding:0.6rem 0.9rem;color:#aaffaa;font-size:0.85rem;font-weight:500;font-family:'Exo 2',sans-serif;align-self:flex-start;max-width:85%;}
.clbl{font-size:0.65rem;font-weight:700;letter-spacing:0.08em;margin-bottom:2px;}
.cmsg-u .clbl{color:#ff8c00;}.cmsg-b .clbl{color:#00ff88;}
.chat-empty{color:#00ff88;font-family:'Exo 2',sans-serif;font-size:1rem;font-weight:700;text-align:center;padding:2.5rem 1rem;line-height:1.8;text-shadow:0 0 15px rgba(0,255,136,0.5);}

.result-box{background:#080808;border:1px solid #ff8c0033;border-radius:12px;padding:1.5rem;font-family:'Exo 2',sans-serif;font-size:0.9rem;line-height:1.9;}
.rb-h1{font-family:'Orbitron',monospace;font-size:0.85rem;font-weight:900;letter-spacing:0.15em;text-transform:uppercase;margin:1.3rem 0 0.5rem;padding:0.45rem 0.9rem;border-left:3px solid #ff8c00;background:rgba(255,140,0,0.08);border-radius:0 8px 8px 0;animation:colorCycle 2.5s linear infinite;}
.rb-h2{font-family:'Exo 2',sans-serif;font-size:0.92rem;font-weight:800;letter-spacing:0.05em;margin:0.9rem 0 0.3rem;text-shadow:0 0 10px rgba(255,200,0,0.5);animation:colorCycle 3s linear infinite;}
.rb-h1:first-child{margin-top:0;}
.rb-num-head{display:flex;align-items:baseline;gap:8px;margin:1rem 0 0.35rem;padding:0.4rem 0.8rem;background:linear-gradient(90deg,rgba(0,200,255,0.08),transparent);border-left:2px solid #00aaff;border-radius:0 6px 6px 0;}
.rb-num{font-family:'Orbitron',monospace;font-size:0.8rem;font-weight:900;flex-shrink:0;text-shadow:0 0 8px rgba(0,170,255,0.7);animation:colorCycle 5s linear infinite;}
.rb-num-label{font-family:'Exo 2',sans-serif;font-size:0.9rem;font-weight:800;text-shadow:0 0 8px rgba(0,220,255,0.4);animation:colorCycle 3.5s linear infinite;}
.rb-num-kv{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px;margin:0.55rem 0 0.2rem;padding-left:0.5rem;}
.rb-num-key{font-family:'Exo 2',sans-serif;font-size:0.88rem;font-weight:800;color:#ff8c00;}
.rb-num-val{color:#ffe0c0;font-weight:500;}
.rb-bullet{display:flex;gap:0.6rem;align-items:flex-start;margin:0.3rem 0 0.3rem 0.8rem;}
.rb-dot{font-weight:900;flex-shrink:0;text-shadow:0 0 6px rgba(0,255,136,0.7);margin-top:2px;animation:colorCycle 4.5s linear infinite;}
.rb-btext{color:#d4f5e0;font-weight:500;}
.rb-kv{margin:0.25rem 0;}
.rb-key{font-weight:700;animation:colorCycle 4s linear infinite;}
.rb-val{color:#e8f4ff;font-weight:400;}
.rb-body{color:#ccd6e8;font-weight:400;margin:0.25rem 0;line-height:1.75;}
.rb-inline-bold{color:#ffcc00;font-weight:800;}
.rb-rec-buy{display:inline-block;padding:2px 14px;border-radius:20px;font-weight:900;background:rgba(0,255,100,0.13);color:#00ff88;border:1px solid #00ff6666;font-size:0.82rem;letter-spacing:0.05em;}
.rb-rec-hold{display:inline-block;padding:2px 14px;border-radius:20px;font-weight:900;background:rgba(255,200,0,0.12);color:#ffcc00;border:1px solid #ffcc0055;font-size:0.82rem;letter-spacing:0.05em;}
.rb-rec-sell{display:inline-block;padding:2px 14px;border-radius:20px;font-weight:900;background:rgba(255,60,60,0.12);color:#ff6666;border:1px solid #ff444466;font-size:0.82rem;letter-spacing:0.05em;}
.rb-divider{height:1px;background:linear-gradient(90deg,transparent,#ff8c0022,transparent);margin:0.5rem 0;}
.send-btn-wrap .stButton>button{white-space:nowrap !important;overflow:hidden !important;width:auto !important;min-width:80px !important;max-width:80px !important;padding:0.72rem 0.5rem !important;font-size:0.78rem !important;font-weight:900 !important;letter-spacing:0.05em !important;line-height:1 !important;display:block !important;word-break:keep-all !important;word-spacing:-1px !important;}

.stTabs [data-baseweb="tab-list"]{background:#0a0a0a !important;border-bottom:1px solid #ff8c0033 !important;gap:4px !important;}
.stTabs [data-baseweb="tab"]{font-family:'Exo 2',sans-serif !important;font-weight:700 !important;font-size:0.82rem !important;color:#555 !important;letter-spacing:0.08em !important;padding:0.55rem 1rem !important;border:none !important;background:transparent !important;}
.stTabs [aria-selected="true"]{color:#ff8c00 !important;background:rgba(255,140,0,0.1) !important;border-bottom:2px solid #ff8c00 !important;}
.stTabs [data-baseweb="tab-panel"]{background:#080808 !important;border:1px solid #ff8c0022 !important;border-top:none !important;border-radius:0 0 12px 12px !important;padding:1.2rem !important;}

.tutorial-box{background:linear-gradient(135deg,#0e0a00,#1a1000);border:1.5px solid #ff8c0066;border-radius:16px;padding:1.4rem;margin-bottom:1rem;}
.tutorial-title{font-family:'Orbitron',monospace;font-size:0.9rem;font-weight:900;color:#ffcc00;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.7rem;text-shadow:0 0 15px rgba(255,200,0,0.5);}
.tstep{display:flex;align-items:flex-start;gap:0.7rem;margin-bottom:0.5rem;padding:0.5rem 0.7rem;background:rgba(255,140,0,0.05);border-radius:8px;border-left:3px solid #ff8c00;}
.tstep-n{font-family:'Orbitron',monospace;font-size:0.9rem;font-weight:900;color:#ff8c00;min-width:24px;}
.tstep-t{font-family:'Exo 2',sans-serif;font-size:0.83rem;font-weight:600;color:#e0e0e0;line-height:1.5;}
.tstep-t span{color:#ffcc00;}

.mega-footer{text-align:center;padding:1rem 0 0.8rem;}
.footer-brand{font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:900;letter-spacing:0.15em;animation:colorCycle 2.5s linear infinite;margin-bottom:0.3rem;}
.footer-info{font-family:'Rajdhani',sans-serif;font-size:0.95rem;font-weight:700;letter-spacing:0.1em;animation:colorCycle 2.5s linear infinite;margin-bottom:0.2rem;}
.footer-built{font-family:'Orbitron',monospace;font-size:0.8rem;font-weight:700;letter-spacing:0.15em;animation:colorCycle 2.5s linear infinite;margin-bottom:0.15rem;}
@keyframes colorCycle{
  0%{color:#ff4500;text-shadow:0 0 18px #ff4500;}
  14%{color:#ff8c00;text-shadow:0 0 18px #ff8c00;}
  28%{color:#ffcc00;text-shadow:0 0 18px #ffcc00;}
  42%{color:#00ff88;text-shadow:0 0 18px #00ff88;}
  57%{color:#00aaff;text-shadow:0 0 18px #00aaff;}
  71%{color:#aa44ff;text-shadow:0 0 18px #aa44ff;}
  85%{color:#ff00cc;text-shadow:0 0 18px #ff00cc;}
  100%{color:#ff4500;text-shadow:0 0 18px #ff4500;}
}
.fdiv{width:50%;margin:0.5rem auto;height:1px;background:linear-gradient(90deg,transparent,#ff8c00,#ffcc00,transparent);box-shadow:0 0 8px rgba(255,140,0,0.4);}

.stSuccess>div{background:rgba(0,255,100,0.08) !important;color:#00ff88 !important;border:1px solid #00ff6655 !important;font-family:'Exo 2' !important;font-weight:600 !important;}
.stError>div{background:rgba(255,50,50,0.1) !important;color:#ff6666 !important;border:1px solid #ff444455 !important;}
.stSpinner>div{border-top-color:#ff8c00 !important;}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:#050505;}::-webkit-scrollbar-thumb{background:#ff8c0055;border-radius:3px;}::-webkit-scrollbar-thumb:hover{background:#ff8c00;}

/* ── ACTION BAR ── */
.action-bar{background:linear-gradient(135deg,#0e0800,#070500);border:1.5px solid #ff8c0044;border-radius:14px;padding:1.2rem 1.4rem;margin-top:1rem;}
.action-bar-title{font-family:'Orbitron',monospace;font-size:0.75rem;font-weight:700;color:#ff8c00;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.9rem;display:flex;align-items:center;gap:8px;}
.action-bar-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,#ff8c0044,transparent);}
.ab-pdf-done{background:rgba(0,255,136,0.08);border:1px solid #00ff6655;border-radius:10px;padding:0.6rem 1rem;display:flex;align-items:center;gap:10px;margin-top:0.5rem;}
.ab-pdf-icon{font-size:1.4rem;}
.ab-pdf-label{font-family:'Exo 2',sans-serif;font-size:0.82rem;font-weight:700;color:#00ff88;}
.ab-email-wrap{margin-top:0.8rem;}
.ab-email-label{font-family:'Exo 2',sans-serif;font-size:0.75rem;font-weight:700;color:#aaa;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px;}
.ab-status-ok{color:#00ff88;font-family:'Exo 2',sans-serif;font-size:0.8rem;font-weight:700;padding:6px 0;}
.ab-status-err{color:#ff6666;font-family:'Exo 2',sans-serif;font-size:0.8rem;font-weight:700;padding:6px 0;}
</style>
""", unsafe_allow_html=True)

# ─── HERO: Particle + Glitch + Neon animated heading ───────────────────────
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Exo+2:wght@600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
html,body{width:100%;height:100%;overflow:hidden;background:transparent;}

#particle-canvas{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1;}

.scene{
  position:relative;width:100%;height:100%;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:10px;isolation:isolate;background:transparent;
}

/* ── TITLE ROW ── */
.word-wrap{
  position:relative;z-index:2;
  display:inline-flex;align-items:flex-end;justify-content:center;
  white-space:pre;letter-spacing:0.06em;user-select:none;
}
.word{
  margin:0;display:inline-flex;align-items:flex-end;justify-content:center;
  white-space:pre;transform-origin:center;will-change:transform;
  font-size:clamp(2.6rem,9vw,5.2rem);line-height:1;font-weight:900;
  text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased;
  font-family:'Orbitron','Trebuchet MS',sans-serif;
}
.word.float-loop{animation:hoverFloat 4.4s ease-in-out infinite;}
@keyframes hoverFloat{0%,100%{transform:translateY(0);}50%{transform:translateY(-9px);}}

.char{
  position:relative;display:inline-block;
  transform:translateY(40px) scale(0.2);transform-origin:center;
  opacity:0;
  transition:transform 760ms cubic-bezier(0.16,1,0.3,1),opacity 560ms ease;
  transition-delay:calc(200ms + var(--i) * 100ms);
  will-change:transform,opacity;
}
.word.reveal .char{transform:translateY(0) scale(1);opacity:1;}
.char.space{width:0.32em;opacity:1;transform:none;transition:none;}

/* Neon orange-gold gradient glyph */
.glyph{
  position:relative;display:block;
  color:transparent;
  background:linear-gradient(110deg,#ff8c00 0%,#ffcc00 35%,#ff4500 65%,#ff8c00 100%);
  background-size:250% 250%;background-position:0% 50%;
  -webkit-background-clip:text;background-clip:text;
  text-shadow:0 0 14px rgba(255,140,0,0.6),0 0 30px rgba(255,80,0,0.3);
  animation:gradientDrift 5s ease-in-out infinite;
}
.word.active .glyph{
  animation:gradientDrift 5s ease-in-out infinite,neonPulse 2.5s ease-in-out infinite;
  animation-delay:calc(var(--i)*55ms),calc(var(--i)*80ms);
}
@keyframes neonPulse{
  0%,100%{text-shadow:0 0 10px rgba(255,140,0,0.6),0 0 28px rgba(255,80,0,0.4);}
  50%{text-shadow:0 0 22px rgba(255,180,0,1),0 0 50px rgba(255,100,0,0.9),0 0 80px rgba(255,60,0,0.35);}
}
@keyframes gradientDrift{0%,100%{background-position:0% 50%;}50%{background-position:100% 50%;}}

/* Glitch ghost layers */
.ghost{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;opacity:0;}
.ghost.red{color:#ff2d95;-webkit-text-fill-color:#ff2d95;background:none;}
.ghost.blue{color:#00eaff;-webkit-text-fill-color:#00eaff;background:none;}
.word.glitch .char:not(.space) .ghost{opacity:0.85;}
.word.glitch .char:not(.space) .ghost.red{animation:gR 140ms steps(2,end) 1;}
.word.glitch .char:not(.space) .ghost.blue{animation:gB 140ms steps(2,end) 1;}
.word.glitch .char.slice .glyph{
  clip-path:polygon(0 6%,100% 0,100% 56%,0 64%);
  transform:translate(var(--gx),var(--gy)) skewX(var(--sk));
}
.word.glitch .char.slice:nth-child(odd) .glyph{clip-path:polygon(0 47%,100% 39%,100% 100%,0 100%);}
@keyframes gR{0%{transform:translate(-2px,0);}50%{transform:translate(-5px,1px);}100%{transform:translate(-1px,-1px);}}
@keyframes gB{0%{transform:translate(2px,0);}50%{transform:translate(5px,-1px);}100%{transform:translate(1px,1px);}}

/* ── SUBTITLE ── */
.hero-sub{
  position:relative;z-index:2;
  font-family:'Exo 2',sans-serif;
  font-size:clamp(0.65rem,2vw,0.95rem);
  font-weight:700;letter-spacing:0.22em;text-transform:uppercase;
  background:linear-gradient(90deg,#ff8c00,#ffcc00,#ff4500,#ff8c00);
  background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:subShimmer 3s linear infinite,subFadeIn 0.6s ease 3.2s both;
  white-space:nowrap;
}
@keyframes subShimmer{0%{background-position:0%}100%{background-position:300%}}
@keyframes subFadeIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}

/* Scanlines overlay */
.scanlines{position:absolute;inset:0;z-index:3;pointer-events:none;
  background:repeating-linear-gradient(to bottom,rgba(255,255,255,0.018) 0px,rgba(255,255,255,0.018) 1px,transparent 2px,transparent 4px);
  opacity:0.15;}

/* Divider line */
.hero-line{
  position:relative;z-index:2;
  width:min(600px,80vw);height:2px;
  background:linear-gradient(90deg,transparent,#ff8c00,#ffcc00,#ff4500,transparent);
  box-shadow:0 0 14px rgba(255,140,0,0.6);
  animation:subFadeIn 0.4s ease 3.5s both;
}
</style>

<div class="scene">
  <canvas id="particle-canvas"></canvas>
  <div class="word-wrap">
    <h1 class="word" id="name"></h1>
  </div>
  <div class="hero-sub">&#x26A1;&nbsp; Autonomous Business Intelligence System &nbsp;&#x26A1;</div>
  <div class="hero-line"></div>
  <div class="scanlines"></div>
</div>

<script>
(function(){
  const TEXT = "OMNIMIND AI";
  const word = document.getElementById("name");
  const canvas = document.getElementById("particle-canvas");
  const ctx = canvas.getContext("2d");
  const particles = [];
  let raf, settleStart = 0;

  function createLetters(){
    word.innerHTML = "";
    for(let i = 0; i < TEXT.length; i++){
      const ch = TEXT[i];
      const char = document.createElement("span");
      char.className = ch === " " ? "char space" : "char";
      char.style.setProperty("--i", i);
      char.style.setProperty("--gx","0px");
      char.style.setProperty("--gy","0px");
      char.style.setProperty("--sk","0deg");
      if(ch !== " "){
        const glyph = document.createElement("span");
        glyph.className = "glyph"; glyph.textContent = ch;
        const gr = document.createElement("span");
        gr.className = "ghost red"; gr.setAttribute("aria-hidden","true"); gr.textContent = ch;
        const gb = document.createElement("span");
        gb.className = "ghost blue"; gb.setAttribute("aria-hidden","true"); gb.textContent = ch;
        char.appendChild(glyph); char.appendChild(gr); char.appendChild(gb);
      } else { char.textContent = " "; }
      word.appendChild(char);
    }
  }

  function sizeCanvas(){
    const dpr = Math.min(window.devicePixelRatio||1, 2);
    canvas.width = Math.floor(window.innerWidth * dpr);
    canvas.height = Math.floor(window.innerHeight * dpr);
    canvas.style.width = window.innerWidth + "px";
    canvas.style.height = window.innerHeight + "px";
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }

  function edgePt(){
    const s = Math.floor(Math.random()*4);
    if(s===0) return {x:Math.random()*window.innerWidth, y:-40};
    if(s===1) return {x:window.innerWidth+40, y:Math.random()*window.innerHeight};
    if(s===2) return {x:Math.random()*window.innerWidth, y:window.innerHeight+40};
    return {x:-40, y:Math.random()*window.innerHeight};
  }

  function buildParticles(){
    particles.length = 0;
    const chars = [...word.querySelectorAll(".char:not(.space)")];
    for(let i = 0; i < chars.length; i++){
      const rect = chars[i].getBoundingClientRect();
      const n = Math.max(18, Math.floor(rect.width * 1.0));
      for(let j = 0; j < n; j++){
        const s = edgePt();
        // orange / gold / red-orange palette to match the brand
        const pick = j % 3;
        particles.push({
          x:s.x, y:s.y,
          vx:(Math.random()-0.5)*1.5, vy:(Math.random()-0.5)*1.5,
          tx:rect.left + Math.random()*rect.width,
          ty:rect.top  + Math.random()*rect.height,
          size:1 + Math.random()*2,
          alpha:0.3 + Math.random()*0.6,
          done:false,
          r: pick===0 ? 255 : pick===1 ? 255 : 255,
          g: pick===0 ? 140 :  pick===1 ? 200 : 69,
          b: pick===0 ?   0 :  pick===1 ?   0 :  0
        });
      }
    }
  }

  function renderParticles(ts){
    ctx.clearRect(0,0,window.innerWidth,window.innerHeight);
    let settled = 0;
    for(let i = 0; i < particles.length; i++){
      const p = particles[i];
      const dx = p.tx-p.x, dy = p.ty-p.y;
      const dist = Math.hypot(dx,dy);
      p.vx += dx*0.018; p.vy += dy*0.018;
      p.vx *= 0.87;     p.vy *= 0.87;
      p.x += p.vx;      p.y += p.vy;
      if(dist < 2.5){ p.done=true; settled++; p.alpha *= 0.96; }
      if(p.alpha > 0.01){
        ctx.beginPath();
        ctx.fillStyle = `rgba(${p.r},${p.g},${p.b},${p.alpha.toFixed(3)})`;
        ctx.arc(p.x,p.y,p.size,0,Math.PI*2);
        ctx.fill();
      }
    }
    if(!settleStart && settled > particles.length*0.65) settleStart = ts;
    if(settleStart && (ts-settleStart) > 900){
      ctx.clearRect(0,0,window.innerWidth,window.innerHeight);
      return;
    }
    raf = requestAnimationFrame(renderParticles);
  }

  function runReveal(){
    requestAnimationFrame(()=> word.classList.add("reveal"));
    const end = 200 + TEXT.replace(/[\\s]/g,"").length*100 + 900;
    setTimeout(()=>{
      word.classList.add("active","float-loop");
      startGlitch();
    }, end);
  }

  function startGlitch(){
    const chars = [...word.querySelectorAll(".char:not(.space)")];
    function trigger(){
      word.classList.add("glitch");
      for(let i = 0; i < chars.length; i++){
        if(Math.random() < 0.5){
          chars[i].classList.add("slice");
          chars[i].style.setProperty("--gx",((Math.random()-0.5)*9)+"px");
          chars[i].style.setProperty("--gy",((Math.random()-0.5)*5)+"px");
          chars[i].style.setProperty("--sk",((Math.random()-0.5)*12)+"deg");
        }
      }
      setTimeout(()=>{
        word.classList.remove("glitch");
        chars.forEach(c=>{ c.classList.remove("slice"); c.style.setProperty("--gx","0px"); c.style.setProperty("--gy","0px"); c.style.setProperty("--sk","0deg"); });
      }, 145);
      setTimeout(trigger, 1800 + Math.random()*3000);
    }
    setTimeout(trigger, 1600);
  }

  function start(){
    cancelAnimationFrame(raf); settleStart = 0;
    createLetters(); sizeCanvas(); buildParticles();
    runReveal();
    raf = requestAnimationFrame(renderParticles);
  }

  window.addEventListener("resize",()=>{ sizeCanvas(); buildParticles(); });
  start();
})();
</script>
""", height=200)

st.markdown('<div class="odiv"></div>', unsafe_allow_html=True)

# TUTORIAL
if st.session_state.show_tutorial:
    st.markdown("""
    <div class="tutorial-box">
      <div class="tutorial-title">&#x1F393; Quick Start Guide</div>
      <div class="tstep"><div class="tstep-n">01</div><div class="tstep-t">Type a <span>Company Name</span> below -- e.g. <span>Tesla, Apple, TCS, Zomato</span>. Suggestions appear as you type!</div></div>
      <div class="tstep"><div class="tstep-n">02</div><div class="tstep-t"><span>Stock Ticker auto-fills!</span> Or type manually -- e.g. <span>TSLA, AAPL, TCS.NS</span></div></div>
      <div class="tstep"><div class="tstep-n">03</div><div class="tstep-t">Click <span>ACTIVATE OMNIMIND</span> right below -- 4 AI agents fire up instantly!</div></div>
      <div class="tstep"><div class="tstep-n">04</div><div class="tstep-t">Results appear on the <span>left tabs</span>. Use <span>AI Chat</span> on the right to ask follow-up questions!</div></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Got It! Hide Tutorial"):
        st.session_state.show_tutorial = False
        st.rerun()

# INPUTS
c1, c2 = st.columns([3,1])
with c1:
    company = st.text_input("Company Name", placeholder="e.g. Tesla, Apple, Zomato, TCS...", key="co_inp")
with c2:
    auto_ticker = TICKERS.get(company, "") if company else ""
    ticker = st.text_input("Stock Ticker", value=auto_ticker, placeholder="e.g. TSLA, AAPL", key="tk_inp")

if company:
    matches = [c for c in COMPANIES if company.lower() in c.lower() and c != company][:6]
    if matches:
        pills = " ".join([f'<span class="suggestion-pill">{m}</span>' for m in matches])
        st.markdown(f'<div class="suggestion-wrap">{pills}</div>', unsafe_allow_html=True)
        st.caption("Tip: Copy a suggestion above and paste into the Company field")
    if auto_ticker:
        st.markdown(f"""
        <div class="ticker-suggest">
          <span class="ts-label">Suggested Ticker for <b>{company}</b></span>
          <span class="ts-ticker">{auto_ticker}</span>
          <span class="ts-note">Auto-filled above</span>
        </div>
        """, unsafe_allow_html=True)
    elif company and not auto_ticker:
        close = [(k,v) for k,v in TICKERS.items() if company.lower() in k.lower()][:4]
        if close:
            ticker_pills = " ".join([f'<span class="ticker-pill"><b>{k}</b> &rarr; <span class="tp-code">{v}</span></span>' for k,v in close])
            st.markdown(f'<div class="suggestion-wrap" style="margin-top:6px;">{ticker_pills}</div>', unsafe_allow_html=True)
            st.caption("Tip: Pick the matching company above to auto-fill the ticker")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="odiv"></div>', unsafe_allow_html=True)
activate_pressed = st.button("ACTIVATE OMNIMIND -- FULL INTELLIGENCE SCAN")
st.markdown('<div class="odiv"></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# AGENT CARDS
st.markdown('<div class="sec-title">AI Agent Army -- Ready for Deployment</div>', unsafe_allow_html=True)
acols = st.columns(4)
agents_info = [
    ("&#x1F52C;","Research","Company Intelligence"),
    ("&#x1F4C8;","Stock","Market Analysis"),
    ("&#x1F4F0;","News","News Intelligence"),
    ("&#x1F4CA;","Report","Executive Report"),
]
for col,(icon,name,desc) in zip(acols, agents_info):
    with col:
        st.markdown(f"""
        <div class="agent-card">
          <span class="agent-icon">{icon}</span>
          <div class="agent-name">{name} Agent</div>
          <div class="agent-desc">{desc}</div>
          <span class="agent-badge">STANDBY</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="odiv"></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── CINEMATIC LOADING ANIMATION ─────────────────────────────────────────────
def agent_loading_html(step, done, company_name):
    agents = [
        ("&#x1F52C;","RESEARCH","Scanning corporate data"),
        ("&#x1F4C8;","STOCK","Fetching live market data"),
        ("&#x1F4F0;","NEWS","Crawling news headlines"),
        ("&#x1F4CA;","REPORT","Generating executive report"),
    ]
    ops = [
        "Scanning company intelligence & fundamentals...",
        "Fetching live stock prices & market signals...",
        "Analysing breaking news & sentiment...",
        "Compiling your executive intelligence report...",
    ]
    pct = int(len(done) / 4 * 100)
    op = ops[step] if step < 4 else "Complete!"

    cards_html = ""
    for i, (icon, name, desc) in enumerate(agents):
        s = "done" if i in done else ("active" if i == step else "wait")
        b = ("&#x2713; COMPLETE" if s == "done" else ("&#x26A1; RUNNING" if s == "active" else "&#x25E6; STANDBY"))
        cards_html += f'<div class="lc {s}"><div class="li">{icon}</div><div class="ln">{name}</div><div class="ld">{desc}</div><div class="lb {s}">{b}</div></div>'

    return f"""
<div class="omnimind-loader">
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Exo+2:wght@600;700&display=swap');
.omnimind-loader{{background:linear-gradient(135deg,#070707,#0e0800);border:2px solid #ff8c0066;border-radius:18px;padding:1.8rem 1.5rem 1.4rem;position:relative;overflow:hidden;}}
.omnimind-loader::before{{content:'';position:absolute;inset:0;background:
  repeating-linear-gradient(90deg,transparent,transparent 40px,rgba(255,140,0,0.02) 41px),
  repeating-linear-gradient(0deg,transparent,transparent 40px,rgba(255,140,0,0.02) 41px);pointer-events:none;}}
.om-title{{font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:900;color:#ff8c00;letter-spacing:0.18em;text-align:center;text-shadow:0 0 22px #ff8c00,0 0 50px rgba(255,140,0,0.4);margin-bottom:0.2rem;animation:titlePulse 1.2s ease-in-out infinite;}}
@keyframes titlePulse{{0%,100%{{text-shadow:0 0 18px #ff8c00,0 0 40px rgba(255,140,0,0.3);}} 50%{{text-shadow:0 0 35px #ffcc00,0 0 80px rgba(255,200,0,0.6);}}}}
.om-co{{font-family:'Exo 2',sans-serif;font-size:0.85rem;font-weight:700;color:#ffcc00;text-align:center;letter-spacing:0.14em;margin-bottom:1.1rem;text-shadow:0 0 10px rgba(255,200,0,0.5);}}
.radar-wrap{{display:flex;justify-content:center;align-items:center;margin-bottom:1.1rem;position:relative;height:90px;}}
.radar{{width:90px;height:90px;position:relative;display:flex;align-items:center;justify-content:center;}}
.ring{{position:absolute;border-radius:50%;border:1.5px solid rgba(255,140,0,0.6);animation:ringExpand 2s ease-out infinite;}}
.ring:nth-child(1){{width:90px;height:90px;animation-delay:0s;}}
.ring:nth-child(2){{width:64px;height:64px;animation-delay:0.6s;}}
.ring:nth-child(3){{width:40px;height:40px;animation-delay:1.2s;}}
@keyframes ringExpand{{0%{{transform:scale(0.2);opacity:0.9;border-color:#ff8c00;box-shadow:0 0 8px #ff8c00;}} 100%{{transform:scale(1.5);opacity:0;border-color:#ff4500;}}}}
.radar-core{{width:16px;height:16px;background:radial-gradient(circle,#ffcc00,#ff8c00);border-radius:50%;box-shadow:0 0 20px #ff8c00,0 0 40px rgba(255,140,0,0.6);z-index:2;animation:corePulse 0.9s ease-in-out infinite;}}
@keyframes corePulse{{0%,100%{{transform:scale(1);box-shadow:0 0 15px #ff8c00,0 0 30px rgba(255,140,0,0.4);}} 50%{{transform:scale(1.6);box-shadow:0 0 30px #ffcc00,0 0 60px rgba(255,200,0,0.7);}}}}
.radar-sweep{{position:absolute;width:45px;height:1.5px;background:linear-gradient(90deg,transparent,#ff8c00);transform-origin:left center;left:50%;top:50%;animation:sweep 2.5s linear infinite;box-shadow:0 0 6px #ff8c00;}}
@keyframes sweep{{from{{transform:rotate(0deg);}} to{{transform:rotate(360deg);}}}}
.lc-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:0.9rem;}}
.lc{{background:#0a0a0a;border:1.5px solid #222;border-radius:10px;padding:0.7rem 0.4rem;text-align:center;transition:all 0.4s;}}
.lc.done{{border-color:#00ff6699;background:linear-gradient(135deg,#001500,#000e00);box-shadow:0 0 18px rgba(0,255,100,0.18);}}
.lc.active{{border-color:#ff8c00;background:linear-gradient(135deg,#1a0900,#0a0400);box-shadow:0 0 30px rgba(255,140,0,0.5);animation:activePulse 1s ease-in-out infinite;}}
.lc.wait{{border-color:#1a1a1a;opacity:0.45;}}
@keyframes activePulse{{0%,100%{{box-shadow:0 0 20px rgba(255,140,0,0.35);border-color:#ff8c00aa;}} 50%{{box-shadow:0 0 50px rgba(255,140,0,0.8);border-color:#ffcc00;}}}}
.li{{font-size:1.6rem;margin-bottom:0.25rem;filter:drop-shadow(0 0 8px rgba(255,140,0,0.7));}}
.lc.wait .li{{filter:none;opacity:0.3;}}
.lc.done .li{{filter:drop-shadow(0 0 10px rgba(0,255,100,0.7));}}
.ln{{font-family:'Orbitron',monospace;font-size:0.56rem;font-weight:900;color:#fff;letter-spacing:0.1em;margin-bottom:0.18rem;text-transform:uppercase;}}
.ld{{font-family:'Exo 2',sans-serif;font-size:0.6rem;color:#666;margin-bottom:0.35rem;line-height:1.3;}}
.lc.active .ld{{color:#ffcc00;}}
.lc.done .ld{{color:#00ff88;}}
.lb{{display:inline-block;padding:2px 7px;border-radius:20px;font-family:'Orbitron',monospace;font-size:0.5rem;font-weight:700;letter-spacing:0.06em;}}
.lb.done{{background:rgba(0,255,100,0.12);color:#00ff88;border:1px solid #00ff6644;}}
.lb.active{{background:rgba(255,140,0,0.18);color:#ff8c00;border:1px solid #ff8c0066;animation:lblink 0.7s ease-in-out infinite;}}
.lb.wait{{background:rgba(40,40,40,0.3);color:#444;border:1px solid #2a2a2a;}}
@keyframes lblink{{0%,100%{{opacity:1;}} 50%{{opacity:0.35;}}}}
.om-op{{font-family:'Exo 2',sans-serif;font-size:0.82rem;font-weight:600;color:#ccc;text-align:center;letter-spacing:0.06em;margin-bottom:0.7rem;}}
.om-op span{{color:#ff8c00;font-weight:800;}}
.pb-track{{background:#0a0a0a;border:1px solid #ff8c0022;border-radius:20px;overflow:hidden;height:7px;}}
.pb-fill{{height:100%;background:linear-gradient(90deg,#ff4500,#ff8c00,#ffcc00);border-radius:20px;width:{pct}%;box-shadow:0 0 12px rgba(255,140,0,0.7);transition:width 0.6s ease;}}
.pb-label{{font-family:'Orbitron',monospace;font-size:0.58rem;color:#ff8c0099;text-align:right;margin-top:4px;letter-spacing:0.1em;}}</style>
<div class="om-title">&#x26A1; OMNIMIND ACTIVATING &#x26A1;</div>
<div class="om-co">&#x1F3AF; TARGET: {company_name.upper()}</div>
<div class="radar-wrap">
  <div class="radar">
    <div class="ring"></div><div class="ring"></div><div class="ring"></div>
    <div class="radar-sweep"></div>
    <div class="radar-core"></div>
  </div>
</div>
<div class="lc-row">{cards_html}</div>
<div class="om-op"><span>&#x25B6;</span> {op}</div>
<div class="pb-track"><div class="pb-fill"></div></div>
<div class="pb-label">{pct}% COMPLETE</div>
</div>
"""

# ── EPIC RESULTS REVEAL ANIMATION ────────────────────────────────────────────
REVEAL_ANIM_HTML = """
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{background:transparent;overflow:hidden;width:100%;height:100%;}
#rv{position:absolute;inset:0;width:100%;height:100%;}
.scene{position:relative;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;}
.t1{font-family:'Orbitron',monospace;font-size:clamp(1.4rem,5vw,2.6rem);font-weight:900;letter-spacing:0.18em;color:transparent;background:linear-gradient(90deg,#ff4500,#ff8c00,#ffcc00,#ff8c00,#ff4500);background-size:300%;-webkit-background-clip:text;background-clip:text;animation:shimText 1.5s linear infinite,popIn 0.5s cubic-bezier(0.16,1,0.3,1) 0.3s both;text-shadow:none;filter:drop-shadow(0 0 20px rgba(255,140,0,0.9));}
.t2{font-family:'Exo 2',sans-serif;font-size:clamp(0.8rem,2.5vw,1.1rem);font-weight:800;letter-spacing:0.3em;text-transform:uppercase;color:#00ff88;text-shadow:0 0 20px rgba(0,255,136,0.8);animation:popIn 0.6s cubic-bezier(0.16,1,0.3,1) 0.7s both;}
.t3{font-family:'Exo 2',sans-serif;font-size:clamp(0.6rem,1.8vw,0.85rem);font-weight:700;letter-spacing:0.22em;color:#ffcc00;text-shadow:0 0 12px rgba(255,200,0,0.6);animation:popIn 0.5s ease 1.1s both;}
@keyframes shimText{0%{background-position:0%}100%{background-position:300%}}
@keyframes popIn{from{opacity:0;transform:scale(0.3) translateY(20px);}to{opacity:1;transform:scale(1) translateY(0);}}
</style>
<canvas id="rv"></canvas>
<div class="scene">
  <div class="t1">&#x26A1; SCAN COMPLETE &#x26A1;</div>
  <div class="t2">&#x2714; Intelligence Unlocked</div>
  <div class="t3">&#x2B50; Your report is ready below &#x2B50;</div>
</div>
<script>
(function(){
  const cv=document.getElementById('rv');
  const ctx=cv.getContext('2d');
  const W=()=>window.innerWidth, H=()=>window.innerHeight;
  function resize(){cv.width=Math.floor(W()*Math.min(devicePixelRatio,2));cv.height=Math.floor(H()*Math.min(devicePixelRatio,2));ctx.setTransform(Math.min(devicePixelRatio,2),0,0,Math.min(devicePixelRatio,2),0,0);}
  resize();

  const DURATION=3800;
  const start=performance.now();
  const cx=W()/2, cy=H()/2;

  // Particles
  const P=[];
  for(let i=0;i<280;i++){
    const ang=Math.random()*Math.PI*2;
    const spd=3+Math.random()*12;
    const hue=[0,30,45,55][Math.floor(Math.random()*4)]; // red-orange-gold
    P.push({
      x:cx,y:cy,vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,
      life:1,decay:0.008+Math.random()*0.015,
      size:1.5+Math.random()*4,
      r:hue===0?255:hue===30?255:hue===45?255:255,
      g:hue===0?60:hue===30?140:hue===45?200:220,
      b:0,
      trail:[],spark:Math.random()<0.3
    });
  }
  // Stars
  const ST=[];
  for(let i=0;i<60;i++){
    ST.push({x:Math.random()*W(),y:Math.random()*H(),r:0.5+Math.random()*2.5,a:Math.random(),da:0.02+Math.random()*0.04});
  }
  // Shockwaves
  const SW=[
    {r:0,maxR:Math.max(W(),H())*0.8,spd:18,a:1,w:3,col:[255,140,0]},
    {r:0,maxR:Math.max(W(),H())*0.6,spd:14,a:0.8,w:2,col:[255,200,0]},
    {r:0,maxR:Math.max(W(),H())*0.5,spd:10,a:0.6,w:1.5,col:[255,80,0]},
  ];

  let flashAlpha=1.0;

  function draw(ts){
    const elapsed=ts-start;
    const globalAlpha=elapsed>DURATION-600?Math.max(0,1-(elapsed-(DURATION-600))/600):1;
    if(globalAlpha<=0) return;

    ctx.clearRect(0,0,W(),H());
    ctx.globalAlpha=globalAlpha;

    // Background tint
    ctx.fillStyle=`rgba(5,5,5,0.15)`;
    ctx.fillRect(0,0,W(),H());

    // Flash
    if(flashAlpha>0){
      ctx.fillStyle=`rgba(255,200,80,${flashAlpha*0.35})`;
      ctx.fillRect(0,0,W(),H());
      flashAlpha=Math.max(0,flashAlpha-0.06);
    }

    // Shockwaves
    for(const sw of SW){
      if(sw.r<=sw.maxR){
        sw.r+=sw.spd; sw.a=Math.max(0,sw.a-0.012);
        ctx.beginPath();
        ctx.arc(cx,cy,sw.r,0,Math.PI*2);
        ctx.strokeStyle=`rgba(${sw.col[0]},${sw.col[1]},${sw.col[2]},${sw.a})`;
        ctx.lineWidth=sw.w*(1-sw.r/sw.maxR)*3+0.5;
        ctx.shadowColor=`rgba(${sw.col[0]},${sw.col[1]},0,0.5)`;
        ctx.shadowBlur=sw.a*20;
        ctx.stroke();
        ctx.shadowBlur=0;
      }
    }

    // Particles
    for(const p of P){
      p.trail.push({x:p.x,y:p.y,a:p.life});
      if(p.trail.length>8) p.trail.shift();
      p.x+=p.vx; p.y+=p.vy;
      p.vx*=0.97; p.vy*=0.97;
      p.vy+=0.06; // gravity
      p.life-=p.decay;
      if(p.life<=0) continue;

      // Trail
      if(p.spark){
        for(let ti=0;ti<p.trail.length-1;ti++){
          const t0=p.trail[ti],t1=p.trail[ti+1];
          const tf=ti/p.trail.length;
          ctx.beginPath();
          ctx.moveTo(t0.x,t0.y);
          ctx.lineTo(t1.x,t1.y);
          ctx.strokeStyle=`rgba(${p.r},${p.g},${p.b},${t0.a*tf*0.5})`;
          ctx.lineWidth=p.size*tf*0.7;
          ctx.stroke();
        }
      }

      ctx.beginPath();
      ctx.arc(p.x,p.y,Math.max(0.5,p.size*p.life),0,Math.PI*2);
      ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
      ctx.shadowColor=`rgba(${p.r},${p.g},0,${p.life*0.7})`;
      ctx.shadowBlur=p.spark?p.size*6:p.size*3;
      ctx.fill();
      ctx.shadowBlur=0;
    }

    // Stars twinkling
    for(const s of ST){
      s.a+=s.da; if(s.a>1||s.a<0) s.da*=-1;
      ctx.beginPath();
      ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(255,${200+Math.floor(s.a*55)},80,${s.a*0.7})`;
      ctx.shadowColor=`rgba(255,200,80,${s.a*0.4})`;
      ctx.shadowBlur=s.r*4;
      ctx.fill();
      ctx.shadowBlur=0;
    }

    // Central glow
    const cgr=ctx.createRadialGradient(cx,cy,0,cx,cy,120);
    cgr.addColorStop(0,`rgba(255,200,80,${0.15*Math.max(0,1-elapsed/1200)})`);
    cgr.addColorStop(1,'rgba(255,140,0,0)');
    ctx.fillStyle=cgr;
    ctx.fillRect(0,0,W(),H());

    ctx.globalAlpha=1;
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();
</script>
"""

# ACTIVATION HANDLER — Step 2: Set session state and rerun immediately
if activate_pressed:
    if not company:
        st.error("Please enter a company name first!")
        st.session_state.bot_mood = "error"
    else:
        st.session_state.scan_triggered = True
        st.session_state.scan_company = company
        st.session_state.scan_ticker = ticker
        st.session_state.bot_mood = "thinking"
        st.rerun()

# ACTIVATION HANDLER — Step 3: If scan was triggered, show animation + run agents
if st.session_state.scan_triggered:
    import time

    _scan_company = st.session_state.scan_company
    _scan_ticker = st.session_state.scan_ticker

    # Show loading animation immediately
    loader = st.empty()
    loader.markdown(agent_loading_html(0, set(), _scan_company), unsafe_allow_html=True)

    # Auto-scroll to the animation (Issue 8)
    components.html("""
    <script>
    window.parent.document.querySelector('.omnimind-loader')
      ? window.parent.document.querySelector('.omnimind-loader').scrollIntoView({behavior:'smooth', block:'center'})
      : window.parent.scrollTo({top: 400, behavior: 'smooth'});
    </script>
    """, height=0)

    # Reset trigger BEFORE calling agents
    st.session_state.scan_triggered = False

    def run_with_retry(fn, *args, retries=3, delay=2, label="Agent"):
        for attempt in range(retries):
            try:
                return fn(*args)
            except Exception as e:
                err_str = str(e).lower()
                if attempt < retries - 1 and any(x in err_str for x in [
                    "disconnected", "timeout", "connection", "server error",
                    "internalservererror", "503", "502", "overloaded"
                ]):
                    time.sleep(delay * (attempt + 1))
                    continue
                raise

    try:
        from agents.research_agent import research_company
        from agents.stock_agent import analyze_stock
        from agents.news_agent import analyze_news
        from agents.report_agent import generate_report

        # Agent 1: Research
        r = run_with_retry(research_company, _scan_company, label="Research")
        time.sleep(0.15)

        # Agent 2: Stock
        loader.markdown(agent_loading_html(1, {0}, _scan_company), unsafe_allow_html=True)
        s = run_with_retry(analyze_stock, _scan_company, _scan_ticker, label="Stock") if _scan_ticker else "No ticker provided."
        time.sleep(0.15)

        # Agent 3: News
        st.session_state.bot_mood = "working"
        loader.markdown(agent_loading_html(2, {0,1}, _scan_company), unsafe_allow_html=True)
        n = run_with_retry(analyze_news, _scan_company, label="News")
        time.sleep(0.15)

        # Agent 4: Report
        loader.markdown(agent_loading_html(3, {0,1,2}, _scan_company), unsafe_allow_html=True)
        rep = run_with_retry(generate_report, _scan_company, r, s, n, label="Report")

        loader.empty()
        st.session_state.bot_mood = "happy"
        st.session_state.scan_done = True
        st.session_state.results = {"research":r, "stock":s, "news":n, "report":rep, "company":_scan_company}
        st.rerun()

    except Exception as e:
        err_msg = str(e)
        if "disconnected" in err_msg.lower() or "internalservererror" in err_msg.lower():
            friendly = "The AI server timed out. This is a temporary Groq issue. Please try again in a few seconds."
        elif "overloaded" in err_msg.lower() or "503" in err_msg:
            friendly = "The AI server is overloaded right now. Please wait 10 seconds and try again."
        elif "api" in err_msg.lower() and "key" in err_msg.lower():
            friendly = "API key error. Please check your GROQ_API_KEY in the .env file."
        elif "rate" in err_msg.lower() or "limit" in err_msg.lower():
            friendly = "Rate limit reached. Please wait 30 seconds and try again."
        else:
            friendly = f"Scan failed: {err_msg}"
        st.error(f"Agent Error -- {friendly}")
        st.session_state.bot_mood = "error"

# RESULT FORMATTER
def format_result(raw_text):
    if not raw_text:
        return '<div class="rb-body">No data available.</div>'
    import re

    def inline_bold(text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<span class="rb-inline-bold">\1</span>', text)
        return text

    lines = str(raw_text).split('\n')
    html = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            html.append('<div class="rb-divider"></div>')
            continue
        if re.match(r'^[A-Z][A-Z0-9 \-\:\/\|]{3,}$', stripped) or re.match(r'^[\U0001F000-\U0001FFFF\u2600-\u26FF\u2700-\u27BF]\s+[A-Z][A-Z0-9 \-\:\/\|]{3,}$', stripped):
            clean = re.sub(r'^[^\w]+', '', stripped).strip()
            html.append(f'<div class="rb-h1">{clean}</div>')
            continue
        elif re.match(r'^[\U0001F000-\U0001FFFF\u2600-\u26FF\u2700-\u27BF\u26A0]\s+\S+', stripped) and len(stripped) < 60:
            clean = stripped.strip()
            html.append(f'<div class="rb-h1">{clean}</div>')
            continue
        num_head = re.match(r'^\*{0,2}(\d+)[\.\)]\s+\*{0,2}(.+?)\*{0,2}:?\*{0,2}$', stripped)
        if num_head and len(num_head.group(2)) < 80:
            label = re.sub(r':$', '', num_head.group(2)).strip()
            html.append(f'<div class="rb-num-head"><span class="rb-num">{num_head.group(1)}.</span><span class="rb-num-label">{label}</span></div>')
            continue
        num_kv = re.match(r'^\*{0,2}(\d+)[\.\)]\s+\*{0,2}(.+?)\*{0,2}:\s+(.+)$', stripped)
        if num_kv and len(num_kv.group(2)) < 60:
            num = num_kv.group(1); key = num_kv.group(2).strip().rstrip('*').strip()
            val = inline_bold(num_kv.group(3).strip())
            val_up = num_kv.group(3).strip().upper()
            if val_up in ['BUY', 'STRONG BUY']: val = f'<span class="rb-rec-buy">{val_up}</span>'
            elif val_up in ['HOLD', 'NEUTRAL']: val = f'<span class="rb-rec-hold">{val_up}</span>'
            elif val_up in ['SELL', 'STRONG SELL']: val = f'<span class="rb-rec-sell">{val_up}</span>'
            html.append(f'<div class="rb-num-kv"><span class="rb-num">{num}.</span><span class="rb-num-key">{key}:</span> <span class="rb-num-val">{val}</span></div>')
            continue
        if re.match(r'^#{1,3}\s', stripped):
            txt = re.sub(r'^#{1,3}\s+', '', stripped)
            html.append(f'<div class="rb-h2">{inline_bold(txt)}</div>')
            continue
        full_bold = re.match(r'^\*\*(.+?)\*\*:?\s*$', stripped)
        if full_bold:
            html.append(f'<div class="rb-h2">{full_bold.group(1).rstrip(":")}</div>')
            continue
        kv_match = re.match(r'^([A-Za-z][A-Za-z0-9 \-\/\(\)]{1,38}):\s*(.+)$', stripped)
        if kv_match:
            key = kv_match.group(1).strip(); val = kv_match.group(2).strip()
            val_up = val.upper()
            if val_up in ['BUY', 'STRONG BUY']: val = f'<span class="rb-rec-buy">{val_up}</span>'
            elif val_up in ['HOLD', 'NEUTRAL']: val = f'<span class="rb-rec-hold">{val_up}</span>'
            elif val_up in ['SELL', 'STRONG SELL']: val = f'<span class="rb-rec-sell">{val_up}</span>'
            else: val = inline_bold(val)
            html.append(f'<div class="rb-kv"><span class="rb-key">{key}:</span> <span class="rb-val">{val}</span></div>')
            continue
        bullet_m = re.match(r'^[\-\*\+\u2022\u25CF]\s+(.+)$', stripped)
        if bullet_m:
            html.append(f'<div class="rb-bullet"><span class="rb-dot">&#x25BA;</span><span class="rb-btext">{inline_bold(bullet_m.group(1))}</span></div>')
            continue
        html.append(f'<div class="rb-body">{inline_bold(stripped)}</div>')

    return '\n'.join(html)

# CHAT HTML BUILDER
def build_chat_html(history):
    if not history:
        return '<div class="chat-empty">Hi! I am OMNIMIND.<br><br>Ask me anything about<br>companies, stocks or markets!</div>'
    html = ""
    for msg in history[-12:]:
        if msg["role"] == "user":
            html += f'<div class="cmsg-u"><div class="clbl">YOU</div>{msg["content"]}</div>'
        else:
            html += f'<div class="cmsg-b"><div class="clbl">OMNIMIND</div>{msg["content"]}</div>'
    return html

def send_chat(user_q, context=""):
    if st.session_state.chat_sending:
        return
    st.session_state.chat_sending = True
    st.session_state.bot_mood = "chat"
    st.session_state.chat_history.append({"role":"user","content":user_q})
    st.session_state.chat_input_key += 1
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        sys_msg = f"You are OMNIMIND AI expert business intelligence assistant. {context} Be concise, max 100 words, always actionable."
        msgs = [{"role":"system","content":sys_msg}] + st.session_state.chat_history[-6:]
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, max_tokens=150)
        st.session_state.chat_history.append({"role":"assistant","content":resp.choices[0].message.content})
        st.session_state.bot_mood = "happy"
    except Exception as e:
        st.session_state.chat_history.append({"role":"assistant","content":f"Error: {str(e)}"})
        st.session_state.bot_mood = "error"
    st.session_state.chat_sending = False
    st.rerun()

# ROBOT CANVAS
def robot_canvas(mood_val, height=160):
    return components.html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
body{{margin:0;padding:0;background:transparent;overflow:hidden;}}
.rw{{display:flex;align-items:center;justify-content:center;gap:12px;padding:6px 10px;}}
canvas{{display:block;flex-shrink:0;}}
.ri{{display:flex;flex-direction:column;gap:3px;}}
.rl{{font-family:'Orbitron',monospace;font-size:0.68rem;font-weight:700;color:#ff8c00;letter-spacing:0.12em;text-shadow:0 0 8px #ff8c00;}}
.rs{{font-family:'Orbitron',monospace;font-size:0.55rem;color:#ff8c0077;letter-spacing:0.1em;}}
</style>
<div class="rw">
  <canvas id="rc" width="90" height="100"></canvas>
  <div class="ri">
    <div class="rl" id="rl">OMNIMIND</div>
    <div class="rs" id="rs">STANDING BY</div>
  </div>
</div>
<script>
const cv=document.getElementById('rc');
const ctx=cv.getContext('2d');
const md='{mood_val}';
const lb={{'idle':'OMNIMIND','thinking':'THINKING...','working':'SCANNING...','happy':'COMPLETE!','chat':'CHATTING!','error':'ERROR!'}};
const sb={{'idle':'STANDING BY','thinking':'PROCESSING DATA','working':'AGENTS ACTIVE','happy':'MISSION DONE!','chat':'RESPONDING','error':'CHECK INPUT'}};
document.getElementById('rl').textContent=lb[md]||lb.idle;
document.getElementById('rs').textContent=sb[md]||sb.idle;
function rr(c,x,y,w,h,r){{c.beginPath();c.moveTo(x+r,y);c.lineTo(x+w-r,y);c.quadraticCurveTo(x+w,y,x+w,y+r);c.lineTo(x+w,y+h-r);c.quadraticCurveTo(x+w,y+h,x+w-r,y+h);c.lineTo(x+r,y+h);c.quadraticCurveTo(x,y+h,x,y+h-r);c.lineTo(x,y+r);c.quadraticCurveTo(x,y,x+r,y);c.closePath();}}
function star(c,cx,cy,sp,or,ir,col){{c.fillStyle=col;c.shadowColor=col;c.shadowBlur=10;let rot=(Math.PI/2)*3,step=Math.PI/sp;c.beginPath();c.moveTo(cx,cy-or);for(let i=0;i<sp;i++){{c.lineTo(cx+Math.cos(rot)*or,cy+Math.sin(rot)*or);rot+=step;c.lineTo(cx+Math.cos(rot)*ir,cy+Math.sin(rot)*ir);rot+=step;}}c.lineTo(cx,cy-or);c.closePath();c.fill();c.shadowBlur=0;}}
let t=0;
function draw(){{
  ctx.clearRect(0,0,90,100);
  const scan=md==='thinking'||md==='working';
  const happy=md==='happy';
  const err=md==='error';
  const chat=md==='chat';
  const bounce=scan?Math.sin(t*0.25)*2.5:Math.sin(t*0.05)*1.5;
  const cx=45,by=12+bounce;
  ctx.strokeStyle='#ff8c00';ctx.lineWidth=1.5;ctx.shadowColor='#ff8c00';ctx.shadowBlur=scan?10:5;
  ctx.beginPath();ctx.moveTo(cx,by);ctx.lineTo(cx,by-11);ctx.stroke();
  const bp=scan?(Math.sin(t*0.3)*0.5+0.5):0.7;
  ctx.fillStyle=scan?`hsl(${{(t*3)%360}},100%,65%)`:'#ff8c00';ctx.shadowBlur=12*bp;
  ctx.beginPath();ctx.arc(cx,by-13,3,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
  const hg=ctx.createLinearGradient(cx-17,by,cx+17,by+23);
  hg.addColorStop(0,'#1a1a2e');hg.addColorStop(1,'#0e0e1a');
  ctx.fillStyle=hg;ctx.strokeStyle=scan?`hsl(${{(t*2)%360}},100%,55%)`:'#ff8c00';
  ctx.lineWidth=1.5;ctx.shadowColor=scan?`hsl(${{(t*2)%360}},100%,55%)`:'#ff8c00';ctx.shadowBlur=scan?12:6;
  rr(ctx,cx-17,by,34,24,6);ctx.fill();ctx.stroke();ctx.shadowBlur=0;
  if(scan){{
    for(let e=0;e<2;e++){{
      const ex=cx+(e===0?-7:7),ey=by+10;
      ctx.strokeStyle='#ff8c00';ctx.lineWidth=1.2;ctx.shadowColor='#ff8c00';ctx.shadowBlur=8;
      ctx.beginPath();ctx.arc(ex,ey,5,0,Math.PI*2);ctx.stroke();
      const ang=t*0.2+e*Math.PI;
      ctx.beginPath();ctx.moveTo(ex,ey);ctx.lineTo(ex+Math.cos(ang)*5,ey+Math.sin(ang)*5);
      ctx.strokeStyle='#ffcc00';ctx.lineWidth=1.5;ctx.stroke();
      ctx.fillStyle='#ff4500';ctx.shadowBlur=12;ctx.beginPath();ctx.arc(ex,ey,2,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
    }}
  }} else if(happy){{
    for(let e=0;e<2;e++){{star(ctx,cx+(e===0?-7:7),by+10,5,5,2,'#ffcc00');}}
  }} else if(err){{
    for(let e=0;e<2;e++){{
      const ex=cx+(e===0?-7:7),ey=by+10;
      ctx.strokeStyle='#ff4444';ctx.lineWidth=2;
      ctx.beginPath();ctx.moveTo(ex-4,ey-4);ctx.lineTo(ex+4,ey+4);ctx.stroke();
      ctx.beginPath();ctx.moveTo(ex+4,ey-4);ctx.lineTo(ex-4,ey+4);ctx.stroke();
    }}
  }} else {{
    const blink=(Math.floor(t*0.04)%25===0);
    for(let e=0;e<2;e++){{
      const ex=cx+(e===0?-7:7),ey=by+10;
      if(blink){{ctx.fillStyle='#00ddff';ctx.fillRect(ex-4,ey-1,8,2);}}
      else{{
        ctx.fillStyle='#00ddff';ctx.shadowColor='#00ddff';ctx.shadowBlur=8;
        ctx.beginPath();ctx.arc(ex,ey,chat?4+Math.sin(t*0.15)*1.5:4,0,Math.PI*2);ctx.fill();
        ctx.fillStyle='#003366';ctx.shadowBlur=0;ctx.beginPath();ctx.arc(ex+1,ey+1,2,0,Math.PI*2);ctx.fill();
        ctx.fillStyle='white';ctx.beginPath();ctx.arc(ex-1,ey-1,1,0,Math.PI*2);ctx.fill();
      }}
      ctx.shadowBlur=0;
    }}
  }}
  const mx2=cx,my2=by+20;
  ctx.strokeStyle=happy?'#00ff88':err?'#ff4444':'#ff8c00';ctx.lineWidth=1.5;ctx.shadowColor=ctx.strokeStyle;ctx.shadowBlur=6;
  ctx.beginPath();
  if(happy){{ctx.arc(mx2,my2-2,6,0.1*Math.PI,0.9*Math.PI);}}
  else if(err){{ctx.arc(mx2,my2+2,6,1.1*Math.PI,1.9*Math.PI);}}
  else if(scan){{ctx.moveTo(mx2-6,my2);ctx.lineTo(mx2+6,my2);}}
  else{{ctx.arc(mx2,my2,5,0.15*Math.PI,0.85*Math.PI);}}
  ctx.stroke();ctx.shadowBlur=0;
  const bg2=ctx.createLinearGradient(cx-15,by+26,cx+15,by+55);
  bg2.addColorStop(0,'#111122');bg2.addColorStop(1,'#0a0a15');
  ctx.fillStyle=bg2;ctx.strokeStyle=scan?`hsl(${{(t*2+90)%360}},100%,50%)`:'#ff8c0077';ctx.lineWidth=1.2;
  ctx.shadowColor=scan?'#ff8c00':'#ff8c0033';ctx.shadowBlur=scan?10:3;
  rr(ctx,cx-15,by+26,30,28,5);ctx.fill();ctx.stroke();ctx.shadowBlur=0;
  ctx.fillStyle=scan?`hsla(${{(t*3)%360}},80%,20%,0.8)`:'#001133';ctx.strokeStyle='#0055aa';ctx.lineWidth=0.8;
  rr(ctx,cx-10,by+30,20,12,2);ctx.fill();ctx.stroke();
  if(scan){{const sy=by+30+((t*1.2)%12);ctx.fillStyle='rgba(0,255,136,0.5)';ctx.fillRect(cx-10,sy,20,1.5);}}
  else{{ctx.fillStyle='#00aaff';ctx.font='bold 5px monospace';ctx.textAlign='center';ctx.fillText(happy?'100%':chat?'CHAT':'READY',cx,by+39);}}
  const gc=scan?`hsl(${{(t*4)%360}},100%,60%)`:'#ff8c00';
  ctx.fillStyle=gc;ctx.shadowColor=gc;ctx.shadowBlur=scan?15:8;
  ctx.beginPath();ctx.arc(cx,by+48,3,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
  for(let a=0;a<2;a++){{
    const ax=a===0?cx-22:cx+15,dir=a===0?-1:1;
    const sw=scan?Math.sin(t*0.2+a*Math.PI)*6:Math.sin(t*0.04+a*Math.PI)*3;
    ctx.strokeStyle='#ff8c0077';ctx.lineWidth=4.5;ctx.lineCap='round';ctx.shadowColor='#ff8c00';ctx.shadowBlur=3;
    ctx.beginPath();ctx.moveTo(ax+(a===0?6:0),by+30);ctx.lineTo(ax+(a===0?0:6)+dir*sw,by+45);ctx.stroke();ctx.shadowBlur=0;
    ctx.fillStyle='#ff8c0055';ctx.beginPath();ctx.arc(ax+(a===0?0:6)+dir*sw,by+47,4,0,Math.PI*2);ctx.fill();
  }}
  for(let l=0;l<2;l++){{
    const lx=cx+(l===0?-8:8);const lb2=scan?Math.sin(t*0.2+l*Math.PI)*4:0;
    ctx.strokeStyle='#ff8c0066';ctx.lineWidth=5.5;ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(lx,by+54);ctx.lineTo(lx,by+68+lb2);ctx.stroke();
    ctx.fillStyle='#ff8c0044';ctx.beginPath();ctx.ellipse(lx,by+70+lb2,6,3,0,0,Math.PI*2);ctx.fill();
  }}
  if(scan){{
    for(let p=0;p<5;p++){{
      const ang=(t*0.08)+p*(Math.PI*2/5);
      const px2=cx+Math.cos(ang)*(22+Math.sin(t*0.1)*4);
      const py2=(by+35)+Math.sin(ang)*(18+Math.cos(t*0.1)*3);
      const pc=`hsl(${{(t*3+p*72)%360}},100%,65%)`;
      ctx.fillStyle=pc;ctx.shadowColor=pc;ctx.shadowBlur=6;
      ctx.beginPath();ctx.arc(px2,py2,2,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
    }}
  }}
  if(happy){{
    for(let c2=0;c2<7;c2++){{
      const ang=(t*0.05)+c2*(Math.PI*2/7);
      const px2=cx+Math.cos(ang)*(30+Math.sin(t*0.07+c2)*4);
      const py2=(by+35)+Math.sin(ang)*(22+Math.cos(t*0.07+c2)*3);
      ctx.fillStyle=`hsl(${{(t*5+c2*51)%360}},100%,65%)`;ctx.shadowColor=ctx.fillStyle;ctx.shadowBlur=5;
      ctx.fillRect(px2-1.5,py2-1.5,3,3);ctx.shadowBlur=0;
    }}
  }}
  t++;requestAnimationFrame(draw);
}}
draw();
</script>
""", height=height)

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS SECTION
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.scan_done and st.session_state.results:
    res = st.session_state.results

    # ── REVEAL ANIMATION ──────────────────────────────────────────────────────
    components.html(REVEAL_ANIM_HTML, height=260)

    # ── COMPANY HEADER ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0e0600,#1a0a00);border:1.5px solid #ff8c0066;
                border-radius:14px;padding:1rem 1.6rem;margin-bottom:1.2rem;
                display:flex;align-items:center;justify-content:space-between;">
      <div>
        <div style="font-family:'Orbitron',monospace;font-size:0.6rem;color:#ff8c0077;
                    letter-spacing:0.25em;text-transform:uppercase;margin-bottom:4px;">
          ⚡ Intelligence Report
        </div>
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;font-weight:900;
                    color:#fff;letter-spacing:0.1em;text-shadow:0 0 20px rgba(255,140,0,0.5);">
          🎯 {res["company"].upper()}
        </div>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        <span style="background:rgba(0,255,136,0.1);border:1px solid #00ff6644;border-radius:8px;
                     padding:4px 12px;font-size:0.65rem;color:#00ff88;font-family:'Orbitron',monospace;
                     letter-spacing:0.1em;">✔ SCAN COMPLETE</span>
        <span style="background:rgba(255,140,0,0.12);border:1px solid #ff8c0044;border-radius:8px;
                     padding:4px 12px;font-size:0.65rem;color:#ff8c00;font-family:'Orbitron',monospace;
                     letter-spacing:0.1em;">4 AGENTS</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # STEP 1 — FULL-WIDTH RESULT TABS
    # ════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Executive Report",
        "🔬  Research",
        "📈  Stock Analysis",
        "📰  News"
    ])
    with tab1:
        st.markdown(f'<div class="result-box">{format_result(res["report"])}</div>',   unsafe_allow_html=True)
    with tab2:
        st.markdown(f'<div class="result-box">{format_result(res["research"])}</div>', unsafe_allow_html=True)
    with tab3:
        st.markdown(f'<div class="result-box">{format_result(res["stock"])}</div>',    unsafe_allow_html=True)
    with tab4:
        st.markdown(f'<div class="result-box">{format_result(res["news"])}</div>',     unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # STEP 2 — PDF + EMAIL SIDE BY SIDE
    # ════════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;
                color:#ff8c00;letter-spacing:0.18em;text-transform:uppercase;
                margin-bottom:0.8rem;display:flex;align-items:center;gap:10px;">
      ⚡ Export &amp; Share Report
      <span style="flex:1;height:1px;background:linear-gradient(90deg,#ff8c0055,transparent);"></span>
    </div>
    """, unsafe_allow_html=True)

    pdf_col, email_col = st.columns(2, gap="large")

    # ── PDF column ─────────────────────────────────────────────────────
    with pdf_col:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0c0800,#180f00);
                    border:1.5px solid #ff8c0055;border-radius:14px;
                    padding:1.1rem 1.3rem;margin-bottom:0.7rem;">
          <div style="font-family:'Orbitron',monospace;font-size:0.68rem;font-weight:700;
                      color:#ff8c00;letter-spacing:0.18em;margin-bottom:0.3rem;">
            📄 DOWNLOAD AS PDF
          </div>
          <div style="font-family:'Exo 2',sans-serif;font-size:0.75rem;color:#888;">
            Save the full intelligence report as a professional PDF document
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📄 GENERATE PDF REPORT", key="pdf_btn", use_container_width=True):
            with st.spinner("Generating PDF..."):
                try:
                    from tools.pdf_exporter import export_pdf
                    result_pdf = export_pdf(
                        company=res["company"], research=res["research"],
                        stock=res["stock"], news=res["news"],
                        report=res["report"], output_dir="output"
                    )
                    st.session_state.pdf_path   = result_pdf["path"] if result_pdf["success"] else None
                    st.session_state.pdf_status = "ok" if result_pdf["success"] else result_pdf["message"]
                except Exception as e:
                    st.session_state.pdf_path   = None
                    st.session_state.pdf_status = f"Error: {str(e)}"
            st.rerun()

        if st.session_state.pdf_status == "ok" and st.session_state.pdf_path:
            try:
                with open(st.session_state.pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="⬇️ CLICK TO DOWNLOAD PDF",
                    data=pdf_bytes,
                    file_name=f"{res['company']}_OMNIMIND_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True, key="pdf_dl"
                )
                st.markdown('<div class="ab-status-ok">✔ PDF ready — click above to save!</div>', unsafe_allow_html=True)
            except Exception:
                st.markdown('<div class="ab-status-err">⚠ PDF not found. Try regenerating.</div>', unsafe_allow_html=True)
        elif st.session_state.pdf_status and st.session_state.pdf_status != "ok":
            st.markdown(f'<div class="ab-status-err">❌ {st.session_state.pdf_status}</div>', unsafe_allow_html=True)

    # ── Email column ───────────────────────────────────────────────────
    with email_col:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#00080a,#001814);
                    border:1.5px solid #00ff8844;border-radius:14px;
                    padding:1.1rem 1.3rem;margin-bottom:0.7rem;">
          <div style="font-family:'Orbitron',monospace;font-size:0.68rem;font-weight:700;
                      color:#00ff88;letter-spacing:0.18em;margin-bottom:0.3rem;">
            📧 SEND BY EMAIL
          </div>
          <div style="font-family:'Exo 2',sans-serif;font-size:0.75rem;color:#888;">
            Email the full report (with PDF attachment) to any address
          </div>
        </div>
        """, unsafe_allow_html=True)

        email_input = st.text_input(
            "Email", placeholder="Enter recipient email address",
            key="email_inp", label_visibility="collapsed"
        )
        if st.button("📧 SEND REPORT BY EMAIL", key="email_btn",
                     disabled=st.session_state.email_sending, use_container_width=True):
            if not email_input:
                st.session_state.email_status = "err:Please enter an email address first!"
            else:
                st.session_state.email_sending = True
                with st.spinner("Sending email..."):
                    try:
                        from tools.email_sender import send_report_email
                        result_email = send_report_email(
                            to_email=email_input, company=res["company"],
                            research=res["research"], stock=res["stock"],
                            news=res["news"], report=res["report"],
                            pdf_path=st.session_state.pdf_path
                        )
                        st.session_state.email_status = (
                            f"ok:{result_email['message']}" if result_email["success"]
                            else f"err:{result_email['message']}"
                        )
                    except Exception as e:
                        st.session_state.email_status = f"err:Email failed: {str(e)}"
                st.session_state.email_sending = False
                st.rerun()

        if st.session_state.email_status:
            kind, msg = st.session_state.email_status.split(":", 1)
            st.markdown(
                f'<div class="{"ab-status-ok" if kind=="ok" else "ab-status-err"}">{"✔" if kind=="ok" else "❌"} {msg}</div>',
                unsafe_allow_html=True
            )

    # ════════════════════════════════════════════════════════════════════
    # STEP 3 — CHATBOT BELOW (full width)
    # ════════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;
                color:#00ff88;letter-spacing:0.18em;text-transform:uppercase;
                margin-bottom:0.8rem;display:flex;align-items:center;gap:10px;">
      🤖 Ask OMNIMIND About This Report
      <span style="flex:1;height:1px;background:linear-gradient(90deg,#00ff8844,transparent);"></span>
    </div>
    """, unsafe_allow_html=True)

    # Robot + chat side by side
    bot_col, chat_col = st.columns([1, 4])
    with bot_col:
        robot_canvas(mood, height=160)
    with chat_col:
        chat_html = build_chat_html(st.session_state.chat_history)
        st.markdown(
            f'<div class="chat-panel"><div class="chat-msgs" style="height:240px;">{chat_html}</div></div>',
            unsafe_allow_html=True
        )

    # Input row
    inp_col, btn_col = st.columns([5, 1])
    input_key = f"chat_scan_{st.session_state.chat_input_key}"
    with inp_col:
        q = st.text_input(
            "Ask", placeholder="e.g. Should I invest? What are the key risks? Compare with competitors.",
            key=input_key, label_visibility="collapsed",
            disabled=st.session_state.chat_sending
        )
    with btn_col:
        send_clicked = st.button(
            "⚡ SEND", key="send_scan",
            disabled=st.session_state.chat_sending, use_container_width=True
        )
    if send_clicked and q and not st.session_state.chat_sending:
        send_chat(q, f"User scanned: {res['company']}. Report summary: {res['report'][:400]}")
else:
    st.markdown('<div class="sec-title">AI Chat Assistant</div>', unsafe_allow_html=True)
    left_gap, center, right_gap = st.columns([1,3,1])
    with center:
        chat_html = build_chat_html(st.session_state.chat_history)
        st.markdown('<div class="chat-panel"><div class="chat-header">', unsafe_allow_html=True)
        robot_canvas(mood, height=120)
        st.markdown(f'</div><div class="chat-msgs">{chat_html}</div></div>', unsafe_allow_html=True)
        pre_key = f"pre_chat_{st.session_state.chat_input_key}"
        pq = st.text_input("Ask anything...", placeholder="e.g. What is Tesla's biggest competitive advantage?",
                           key=pre_key, label_visibility="collapsed",
                           disabled=st.session_state.chat_sending)
        pre_clicked = st.button("⚡ SEND TO OMNIMIND", key="pre_send",
                                 disabled=st.session_state.chat_sending, use_container_width=True)
        if pre_clicked and pq and not st.session_state.chat_sending:
            send_chat(pq)

# FOOTER
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="odiv"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="mega-footer">
  <div class="footer-brand">OMNIMIND AI</div>
  <div class="fdiv"></div>
  <div class="footer-info">Autonomous Business Intelligence &nbsp;|&nbsp; AI Agents</div>
  <div class="footer-built">BUILT BY</div>
</div>
""", unsafe_allow_html=True)

components.html("""
<style>
*{box-sizing:border-box;margin:0;padding:0;}
html,body{width:100%;height:100%;overflow:hidden;background:transparent;}
#particle-canvas{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1;}
.scene{position:relative;width:100%;height:100%;display:grid;place-items:center;isolation:isolate;background:transparent;}
.word-wrap{position:relative;z-index:2;display:inline-flex;align-items:flex-end;justify-content:center;white-space:pre;letter-spacing:0.06em;user-select:none;}
.word{margin:0;display:inline-flex;align-items:flex-end;justify-content:center;white-space:pre;transform-origin:center;will-change:transform;font-size:clamp(2rem,8vw,3.6rem);line-height:1;font-weight:800;text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased;font-family:'Orbitron','Trebuchet MS',sans-serif;}
.word.float-loop{animation:hoverFloat 4.4s ease-in-out infinite;}
@keyframes hoverFloat{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
.char{position:relative;display:inline-block;transform:translateY(40px) scale(0.2);transform-origin:center;opacity:0;transition:transform 760ms cubic-bezier(0.16,1,0.3,1),opacity 560ms ease;transition-delay:calc(260ms + var(--i) * 120ms);will-change:transform,opacity;}
.word.reveal .char{transform:translateY(0) scale(1);opacity:1;}
.char.space{width:0.38em;opacity:1;transform:none;transition:none;}
.glyph{position:relative;display:block;color:transparent;background:linear-gradient(110deg,#00f5ff 10%,#73e6ff 32%,#9f5fff 67%,#a855f7 100%);background-size:170% 170%;background-position:0% 50%;-webkit-background-clip:text;background-clip:text;text-shadow:0 0 10px rgba(0,245,255,0.5),0 0 22px rgba(91,78,255,0.4);animation:gradientDrift 6s ease-in-out infinite;}
.word.active .glyph{animation:gradientDrift 6s ease-in-out infinite,neonPulse 2.7s ease-in-out infinite;animation-delay:calc(var(--i)*60ms),calc(var(--i)*90ms);}
@keyframes neonPulse{0%,100%{text-shadow:0 0 8px rgba(0,245,255,0.55),0 0 20px rgba(105,75,255,0.45);}50%{text-shadow:0 0 16px rgba(0,245,255,0.95),0 0 36px rgba(168,85,247,0.85),0 0 54px rgba(0,245,255,0.3);}}
@keyframes gradientDrift{0%,100%{background-position:0% 50%;}50%{background-position:100% 50%;}}
.ghost{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;opacity:0;}
.ghost.red{color:#ff2d95;-webkit-text-fill-color:#ff2d95;background:none;}
.ghost.blue{color:#16d9ff;-webkit-text-fill-color:#16d9ff;background:none;}
.word.glitch .char:not(.space) .ghost{opacity:0.88;}
.word.glitch .char:not(.space) .ghost.red{animation:gR 140ms steps(2,end) 1;}
.word.glitch .char:not(.space) .ghost.blue{animation:gB 140ms steps(2,end) 1;}
.word.glitch .char.slice .glyph{clip-path:polygon(0 6%,100% 0,100% 56%,0 64%);transform:translate(var(--gx),var(--gy)) skewX(var(--sk));}
.word.glitch .char.slice:nth-child(odd) .glyph{clip-path:polygon(0 47%,100% 39%,100% 100%,0 100%);}
@keyframes gR{0%{transform:translate(-2px,0);}50%{transform:translate(-5px,1px);}100%{transform:translate(-1px,-1px);}}
@keyframes gB{0%{transform:translate(2px,0);}50%{transform:translate(5px,-1px);}100%{transform:translate(1px,1px);}}
.scanlines{position:absolute;inset:0;z-index:3;pointer-events:none;background:repeating-linear-gradient(to bottom,rgba(255,255,255,0.025) 0px,rgba(255,255,255,0.025) 1px,transparent 2px,transparent 4px);opacity:0.18;}
.sub{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);font-family:'Orbitron','Trebuchet MS',sans-serif;font-size:0.48rem;letter-spacing:0.42em;color:#00f5ff;opacity:0;animation:fadeIn 0.5s ease 4s forwards;text-shadow:0 0 8px rgba(0,245,255,0.5);text-transform:uppercase;white-space:nowrap;}
@keyframes fadeIn{to{opacity:0.5;}}
</style>
<div class="scene">
  <canvas id="particle-canvas"></canvas>
  <div class="word-wrap"><h1 class="word" id="name"></h1></div>
  <div class="scanlines"></div>
  <div class="sub">AI &nbsp;|&nbsp; Data Science &nbsp;|&nbsp; Creator</div>
</div>
<script>
(function(){
const TEXT="NISHANTH R";
const word=document.getElementById("name");
const canvas=document.getElementById("particle-canvas");
const ctx=canvas.getContext("2d");
const particles=[];
let raf;let settleStart=0;
function createLetters(){word.innerHTML="";for(let i=0;i<TEXT.length;i++){const ch=TEXT[i];const char=document.createElement("span");char.className=ch===" "?"char space":"char";char.style.setProperty("--i",i);char.style.setProperty("--gx","0px");char.style.setProperty("--gy","0px");char.style.setProperty("--sk","0deg");if(ch!==" "){const glyph=document.createElement("span");glyph.className="glyph";glyph.textContent=ch;const gr=document.createElement("span");gr.className="ghost red";gr.setAttribute("aria-hidden","true");gr.textContent=ch;const gb=document.createElement("span");gb.className="ghost blue";gb.setAttribute("aria-hidden","true");gb.textContent=ch;char.appendChild(glyph);char.appendChild(gr);char.appendChild(gb);}else{char.textContent=" ";}word.appendChild(char);}}
function sizeCanvas(){const dpr=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.floor(window.innerWidth*dpr);canvas.height=Math.floor(window.innerHeight*dpr);canvas.style.width=window.innerWidth+"px";canvas.style.height=window.innerHeight+"px";ctx.setTransform(dpr,0,0,dpr,0,0);}
function edgePt(){const s=Math.floor(Math.random()*4);if(s===0)return{x:Math.random()*window.innerWidth,y:-40};if(s===1)return{x:window.innerWidth+40,y:Math.random()*window.innerHeight};if(s===2)return{x:Math.random()*window.innerWidth,y:window.innerHeight+40};return{x:-40,y:Math.random()*window.innerHeight};}
function buildParticles(){particles.length=0;const chars=[...word.querySelectorAll(".char:not(.space)")];for(let i=0;i<chars.length;i++){const rect=chars[i].getBoundingClientRect();const n=Math.max(20,Math.floor(rect.width*1.1));for(let j=0;j<n;j++){const s=edgePt();const useCyan=j%2===0;particles.push({x:s.x,y:s.y,vx:(Math.random()-0.5)*1.5,vy:(Math.random()-0.5)*1.5,tx:rect.left+Math.random()*rect.width,ty:rect.top+Math.random()*rect.height,size:1+Math.random()*2,alpha:0.25+Math.random()*0.65,done:false,r:useCyan?0:168,g:useCyan?245:85,b:useCyan?255:247});}}}
function renderParticles(ts){ctx.clearRect(0,0,window.innerWidth,window.innerHeight);let settled=0;for(let i=0;i<particles.length;i++){const p=particles[i];const dx=p.tx-p.x,dy=p.ty-p.y;const dist=Math.hypot(dx,dy);p.vx+=dx*0.018;p.vy+=dy*0.018;p.vx*=0.87;p.vy*=0.87;p.x+=p.vx;p.y+=p.vy;if(dist<2.5){p.done=true;settled++;p.alpha*=0.96;}if(p.alpha>0.01){ctx.beginPath();ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.alpha.toFixed(3)})`;ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill();}}
if(!settleStart&&settled>particles.length*0.65)settleStart=ts;if(settleStart&&(ts-settleStart)>900){ctx.clearRect(0,0,window.innerWidth,window.innerHeight);return;}raf=requestAnimationFrame(renderParticles);}
function runReveal(){requestAnimationFrame(()=>word.classList.add("reveal"));const end=260+TEXT.replace(/[\\s]/g,"").length*120+900;setTimeout(()=>{word.classList.add("active","float-loop");startGlitch();},end);}
function startGlitch(){const chars=[...word.querySelectorAll(".char:not(.space)")];function trigger(){word.classList.add("glitch");for(let i=0;i<chars.length;i++){if(Math.random()<0.5){chars[i].classList.add("slice");chars[i].style.setProperty("--gx",((Math.random()-0.5)*9)+"px");chars[i].style.setProperty("--gy",((Math.random()-0.5)*5)+"px");chars[i].style.setProperty("--sk",((Math.random()-0.5)*12)+"deg");}}setTimeout(()=>{word.classList.remove("glitch");for(let i=0;i<chars.length;i++){chars[i].classList.remove("slice");chars[i].style.setProperty("--gx","0px");chars[i].style.setProperty("--gy","0px");chars[i].style.setProperty("--sk","0deg");}},145);setTimeout(trigger,1500+Math.random()*2800);}setTimeout(trigger,1400);}
function start(){cancelAnimationFrame(raf);settleStart=0;createLetters();sizeCanvas();buildParticles();runReveal();raf=requestAnimationFrame(renderParticles);}
window.addEventListener("resize",()=>{sizeCanvas();buildParticles();});
start();
})();
</script>
""", height=260)
