import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

st.set_page_config(
    page_title="Verbatim — AI Meeting Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');


.main .block-container {
    padding-bottom: 0rem !important;
}
/* ══════════════ TOKENS ══════════════ */
:root {
    --bg:         #0D1117;
    --bg-2:       #161C26;
    --bg-3:       #1C2433;
    --bg-4:       #212B3C;
    --bd:         #21293A;
    --bd-2:       #2D3A50;
    --bd-3:       #3D4F6A;

    --blue:       #4F8EF7;
    --blue-2:     #3B7DE8;
    --blue-hi:    rgba(79,142,247,.15);
    --blue-ring:  rgba(79,142,247,.30);

    --green:      #34D399;
    --green-hi:   rgba(52,211,153,.12);
    --amber:      #FBBF24;
    --amber-hi:   rgba(251,191,36,.12);
    --rose:       #FB7185;
    --rose-hi:    rgba(251,113,133,.10);

    --tx:         #A8B4C8;
    --tx-2:       #D4DCE8;
    --tx-3:       #F0F4FA;
    --tx-lo:      #6B7FA0;

    --r:  8px;
    --rl: 14px;
    --rxl: 18px;
}

/* ══════════════ GLOBAL ══════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--tx) !important;
    font-size: 15px;
    line-height: 1.65;
}
.stApp { background: var(--bg) !important; min-height: 100vh; }
h1,h2,h3,h4,h5,h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--tx-3) !important;
    font-weight: 600 !important;
}

/* kill "Press Enter to apply" */
[data-testid="InputInstructions"],
.stTextInput div[data-baseweb="input"] ~ div,
small { display: none !important; }

/* ══════════════ PAGE TOP ACCENT LINE ══════════════ */
.stApp::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,
        transparent 0%, var(--blue) 30%, #93C5FD 60%, transparent 100%);
    background-size: 300% 100%;
    animation: scanLine 8s ease-in-out infinite alternate;
    z-index: 9999;
}
@keyframes scanLine {
    0%   { background-position: 0% 0%; opacity: .7; }
    100% { background-position: 100% 0%; opacity: 1; }
}

/* ══════════════ SUBTLE GRID BG ══════════════ */
.stApp::after {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(79,142,247,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(79,142,247,.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ══════════════ SIDEBAR ══════════════ */
[data-testid="stSidebar"] {
    background: #0B1628 !important;
    border-right: 1px solid rgba(79,142,247,.14) !important;
    box-shadow: 6px 0 48px rgba(0,0,0,.7) !important;
    z-index: 10 !important;
}
/* Kill ALL Streamlit default top padding in sidebar */
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebar"] > div > div > div,
[data-testid="stSidebar"] section {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
[data-testid="stSidebarContent"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
[data-testid="stSidebar"] * { color: var(--tx) !important; }

/* ── SIDEBAR HERO ── */
.sb-hero {
    position: relative; overflow: hidden;
    padding: 1.75rem 1.25rem 1.4rem;
    background: linear-gradient(160deg, #101e36 0%, #0b1628 55%, #091220 100%);
    border-bottom: 2px solid rgba(79,142,247,.55);
}
/* blue ambient glow top-right */
.sb-hero::before {
    content: '';
    position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px; border-radius: 50%;
    background: radial-gradient(circle,
        rgba(79,142,247,.22) 0%, transparent 65%);
    pointer-events: none;
    animation: heroGlow 6s ease-in-out infinite;
}
@keyframes heroGlow {
    0%,100% { opacity:.7; transform:scale(1); }
    50%      { opacity:1;  transform:scale(1.12); }
}

/* ── Top row: icon + wordmark ── */
.sb-top-row {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 1rem;
}
/* Large mic icon chip */
.sb-icon-chip {
    flex-shrink: 0;
    width: 68px; height: 68px; border-radius: 18px;
    background: linear-gradient(145deg, #1A3060 0%, #0E2248 60%, #0B1A38 100%);
    border: 1.5px solid rgba(79,142,247,.45);
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem;
    box-shadow:
        0 0 0 5px rgba(79,142,247,.1),
        0 0 30px rgba(79,142,247,.2),
        0 8px 24px rgba(0,0,0,.6),
        inset 0 1px 0 rgba(255,255,255,.08);
    transition: transform .28s cubic-bezier(.34,1.56,.64,1),
                box-shadow .28s, border-color .28s;
    cursor: default;
}
.sb-icon-chip:hover {
    transform: rotate(-6deg) scale(1.1);
    border-color: rgba(79,142,247,.8);
    box-shadow:
        0 0 0 6px rgba(79,142,247,.18),
        0 0 40px rgba(79,142,247,.35),
        0 12px 30px rgba(0,0,0,.6);
}
/* Wordmark block */
.sb-wordmark-block {}
.sb-wordmark {
    font-size: 1.9rem; font-weight: 900;
    letter-spacing: -.04em; line-height: 1;
    margin-bottom: .35rem;
    color: #F0F4FA !important;
}
.sb-wordmark .blue {
    background: linear-gradient(90deg, #4F8EF7 0%, #7EB8FF 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
/* "AI MEETING INTELLIGENCE" pill badge */
.sb-tagpill {
    display: inline-block;
    font-size: .62rem; font-weight: 700;
    letter-spacing: .14em; text-transform: uppercase;
    color: #5DA8FF !important;
    background: rgba(79,142,247,.12);
    border: 1px solid rgba(79,142,247,.4);
    border-radius: 6px;
    padding: .22rem .65rem;
    line-height: 1;
}

/* ── Status row ── */
.sb-status-row {
    display: flex; align-items: center; gap: .5rem;
    margin-top: .1rem;
}
.sb-status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #34D399;
    box-shadow: 0 0 8px #34D399;
    flex-shrink: 0;
    animation: sPulse 2.2s ease-in-out infinite;
}
@keyframes sPulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.3;transform:scale(.75)} }
.sb-status-txt {
    font-size: .74rem; font-weight: 500;
    color: #5A7595 !important;
    letter-spacing: .02em;
}

/* ── SIDEBAR BODY ── */
.sb-body { padding: 1.1rem 1.1rem 0; }

/* Section labels */
.sb-label {
    display: flex; align-items: center; gap: .55rem;
    font-size: .7rem; font-weight: 700;
    letter-spacing: .16em; text-transform: uppercase;
    color: #7B90B8 !important;
    margin: 1.15rem 0 .5rem;
}
.sb-label-icon { font-size: .8rem; }
.sb-label::after {
    content: ''; flex:1; height:1px;
    background: linear-gradient(90deg, rgba(61,79,106,.5), transparent);
}

/* Format tag chips */
.sb-tags { display:flex; gap:.4rem; flex-wrap:wrap; margin:.5rem 0 .65rem; }
.sb-tag {
    font-size: .7rem; font-weight: 600;
    letter-spacing: .04em;
    padding: .28rem .75rem; border-radius: 8px;
    background: rgba(79,142,247,.08);
    border: 1px solid rgba(79,142,247,.28);
    color: #6BA4E0 !important;
    transition: background .18s, border-color .2s,
                color .18s, transform .2s cubic-bezier(.34,1.56,.64,1);
    cursor: default;
}
.sb-tag:hover {
    background: rgba(79,142,247,.2);
    border-color: rgba(79,142,247,.6);
    color: #A8D4FF !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(79,142,247,.2);
}
.sb-tag:active { transform: translateY(0) !important; }

/* Divider */
.sb-div {
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%, rgba(61,79,106,.5) 25%,
        rgba(61,79,106,.5) 75%, transparent 100%);
    margin: 1rem 0 .5rem;
}

/* Run Analysis button — vivid electric blue */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(180deg, #1E72FF 0%, #0F52F0 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: .85rem 1.5rem !important;
    letter-spacing: .03em !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,.2) inset,
        0 6px 24px rgba(15,82,240,.6),
        0 2px 8px rgba(0,0,0,.4) !important;
    transition: all .2s cubic-bezier(.34,1.2,.64,1) !important;
    transform: translateY(0) scale(1) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(180deg, #3D8AFF 0%, #1A62FF 100%) !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,.25) inset,
        0 12px 36px rgba(15,82,240,.75),
        0 2px 10px rgba(0,0,0,.4) !important;
    transform: translateY(-3px) scale(1.01) !important;
}
[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(1px) scale(.98) !important;
    box-shadow: 0 3px 10px rgba(15,82,240,.45) !important;
    transition: all .07s ease !important;
}

/* Footer */
.sb-footer {
    padding: 1rem 1.1rem 1.3rem;
    border-top: 1px solid rgba(33,41,58,.9);
    margin-top: 1.5rem;
}
.sb-footer-stack {
    display: flex; gap: .4rem; justify-content: center;
    flex-wrap: wrap;
}
.sb-badge {
    font-size: .66rem; font-weight: 600;
    letter-spacing: .05em;
    padding: .28rem .7rem; border-radius: 8px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(61,79,106,.4);
    color: #4A6080 !important;
    transition: border-color .18s, color .18s, background .18s, transform .18s;
    cursor: default;
}
.sb-badge:hover {
    border-color: rgba(79,142,247,.4);
    color: #7EB8FF !important;
    background: rgba(79,142,247,.1);
    transform: translateY(-1px);
}



/* ══════════════ INPUTS ══════════════ */
.stTextInput > div > div > input {
    background: var(--bg) !important;
    border: 1px solid var(--bd-2) !important;
    border-radius: var(--r) !important;
    color: var(--tx-3) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .92rem !important;
    padding: .65rem 1rem !important;
    transition: border-color .18s, box-shadow .18s, transform .15s !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,.25) !important;
}
.stTextInput > div > div > input:hover {
    border-color: var(--bd-3) !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,.25), 0 0 0 2px rgba(79,142,247,.08) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px var(--blue-ring),
                inset 0 1px 3px rgba(0,0,0,.25) !important;
    outline: none !important;
    transform: translateY(-1px) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--tx-lo) !important; }
.stSelectbox > div > div {
    background: var(--bg) !important;
    border: 1px solid var(--bd-2) !important;
    border-radius: var(--r) !important;
    color: var(--tx-3) !important;
    font-size: .92rem !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,.25) !important;
    transition: border-color .18s, box-shadow .18s !important;
}
.stSelectbox > div > div:hover {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(79,142,247,.12) !important;
}

/* ══════════════ RUN BUTTON ══════════════ */
.stButton > button {
    background: linear-gradient(180deg, var(--blue) 0%, var(--blue-2) 100%) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: var(--r) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: .92rem !important;
    padding: .68rem 1.25rem !important;
    margin-top: .8rem !important;
    transition: all .18s cubic-bezier(.34,1.56,.64,1) !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,.12) inset,
        0 4px 12px rgba(59,125,232,.35),
        0 1px 3px rgba(0,0,0,.3) !important;
    position: relative !important;
    top: 0 !important;
    letter-spacing: .02em !important;
    overflow: hidden !important;
    transform: translateY(0) scale(1) !important;
}

/* Ripple pseudo-element on button */
.stButton > button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at var(--mx, 50%) var(--my, 50%),
        rgba(255,255,255,.28) 0%, transparent 60%);
    opacity: 0;
    transition: opacity .4s ease;
    border-radius: inherit;
    pointer-events: none;
}
.stButton > button:hover::after { opacity: 1; }

.stButton > button:hover {
    background: linear-gradient(180deg, #5F9EFF 0%, #4A8DEE 100%) !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,.20) inset,
        0 10px 28px rgba(59,125,232,.55),
        0 2px 8px rgba(0,0,0,.3) !important;
    transform: translateY(-3px) scale(1.015) !important;
    top: 0 !important;
}

.stButton > button:active {
    transform: translateY(1px) scale(0.975) !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,.08) inset,
        0 2px 6px rgba(59,125,232,.3) !important;
    transition: all .06s ease !important;
}

.stButton > button[kind="secondary"] {
    background: var(--bg-3) !important;
    border: 1px solid var(--bd-2) !important;
    color: var(--tx) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.2) !important;
    margin-top: 0 !important;
    top: 0 !important;
    transform: translateY(0) scale(1) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--bg-4) !important;
    border-color: var(--bd-3) !important;
    color: var(--tx-2) !important;
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 6px 16px rgba(0,0,0,.3) !important;
    top: 0 !important;
}
.stButton > button[kind="secondary"]:active {
    transform: translateY(0) scale(0.98) !important;
    transition: all .06s ease !important;
}

/* ══════════════ PIPELINE STEPS ══════════════ */
.p-step {
    display: flex; align-items: center; gap: .55rem;
    padding: .46rem .65rem; border-radius: 7px;
    margin-bottom: .2rem; font-size: .82rem; font-weight: 500;
    border: 1px solid transparent;
    transition: background .15s, border-color .15s, transform .18s, box-shadow .18s;
    cursor: default;
}
.p-step:hover {
    transform: translateX(3px);
}
.ps-done {
    background: var(--green-hi); border-color: rgba(52,211,153,.2);
    color: var(--green);
}
.ps-done:hover {
    box-shadow: 0 0 12px rgba(52,211,153,.15);
}
.ps-active {
    background: var(--blue-hi); border-color: var(--blue-ring);
    color: var(--blue); animation: stepGlow 2s ease-in-out infinite;
}
.ps-pending { color: var(--tx-lo); }
@keyframes stepGlow {
    0%,100% { border-color: var(--blue-ring); }
    50%      { border-color: var(--blue); }
}

.p-dot {
    width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
}
.pd-done    { background: var(--green); }
.pd-active  { background: var(--blue); box-shadow: 0 0 6px var(--blue);
              animation: dotPop 1s ease-in-out infinite; }
.pd-pending { background: var(--tx-lo); opacity: .4; }
@keyframes dotPop {
    0%,100% { opacity:1; transform:scale(1); }
    50%     { opacity:.4; transform:scale(.7); }
}

/* ══════════════ HERO ══════════════ */
.hero {
    position: relative; overflow: hidden;
    background: var(--bg-2);
    border: 1px solid var(--bd-2);
    border-radius: var(--rxl);
    padding: 2.5rem 2.75rem;
    margin-bottom: 1.5rem;
    box-shadow:
        0 0 0 1px rgba(255,255,255,.03) inset,
        0 1px 0 rgba(255,255,255,.04) inset,
        0 20px 60px rgba(0,0,0,.4);
    transition: border-color .3s, box-shadow .3s, transform .3s;
}
.hero:hover {
    border-color: var(--bd-3);
    box-shadow:
        0 0 0 1px rgba(255,255,255,.05) inset,
        0 1px 0 rgba(255,255,255,.06) inset,
        0 30px 80px rgba(0,0,0,.5),
        0 0 60px rgba(79,142,247,.06);
    transform: translateY(-2px);
}
/* top border glow */
.hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,
        transparent 0%, rgba(79,142,247,.6) 30%,
        rgba(147,197,253,.5) 60%, transparent 100%);
    transition: opacity .3s;
}
.hero:hover::before { opacity: 1.5; }

/* ambient glow top-right */
.hero-glow {
    position: absolute; top: -60px; right: -60px;
    width: 300px; height: 300px; border-radius: 50%;
    background: radial-gradient(circle,
        rgba(79,142,247,.10) 0%, transparent 65%);
    pointer-events: none;
    animation: glowBreath 6s ease-in-out infinite;
}
@keyframes glowBreath {
    0%,100% { transform: scale(1); opacity:.8; }
    50%      { transform: scale(1.15); opacity:1; }
}

.hero-eyebrow {
    font-size: .68rem; font-weight: 700; letter-spacing: .18em;
    text-transform: uppercase; color: var(--blue);
    display: flex; align-items: center; gap: .5rem;
    margin-bottom: .6rem;
}
.hero-eyebrow::before {
    content: ''; width: 16px; height: 1px;
    background: var(--blue); opacity: .7;
}
.hero-h1 {
    font-size: clamp(1.6rem, 3vw, 2.4rem);
    font-weight: 700; letter-spacing: -.025em;
    color: var(--tx-3); line-height: 1.15;
    margin: 0 0 .55rem;
}
.hero-h1 em {
    font-style: normal;
    background: linear-gradient(90deg, var(--blue) 0%, #93C5FD 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-desc {
    font-size: .97rem; color: var(--tx); line-height: 1.7;
    max-width: 520px; margin-bottom: 1.75rem; font-weight: 400;
}

/* wave bars — blue only */
.wave { display:flex; align-items:center; gap:3px; height:28px; }
.wave s {
    display:block; width:3px; border-radius:3px;
    background: var(--blue); text-decoration: none;
    animation: wv 1.8s ease-in-out infinite;
}
.wave s:nth-child(1)  {height:5px;  animation-delay:.00s; opacity:.4;}
.wave s:nth-child(2)  {height:10px; animation-delay:.06s; opacity:.5;}
.wave s:nth-child(3)  {height:18px; animation-delay:.12s; opacity:.65;}
.wave s:nth-child(4)  {height:24px; animation-delay:.18s; opacity:.8;}
.wave s:nth-child(5)  {height:28px; animation-delay:.24s; opacity:1;}
.wave s:nth-child(6)  {height:22px; animation-delay:.30s; opacity:.85;}
.wave s:nth-child(7)  {height:16px; animation-delay:.36s; opacity:.7;}
.wave s:nth-child(8)  {height:26px; animation-delay:.42s; opacity:.9;}
.wave s:nth-child(9)  {height:20px; animation-delay:.48s; opacity:.75;}
.wave s:nth-child(10) {height:12px; animation-delay:.54s; opacity:.55;}
.wave s:nth-child(11) {height:7px;  animation-delay:.60s; opacity:.45;}
.wave s:nth-child(12) {height:14px; animation-delay:.66s; opacity:.6;}
@keyframes wv {
    0%,100% { transform:scaleY(.25); opacity:.2; }
    50%      { transform:scaleY(1);   opacity:1; }
}

.hero-pills { display:flex; gap:.4rem; flex-wrap:wrap; margin-top:.4rem; }
.pill {
    display: inline-flex; align-items: center; gap: .3rem;
    padding: .22rem .65rem; border-radius: 99px;
    font-size: .72rem; font-weight: 600;
    letter-spacing: .05em; text-transform: uppercase;
    background: rgba(79,142,247,.10);
    color: #93C5FD;
    border: 1px solid rgba(79,142,247,.22);
    transition: background .2s, border-color .2s, transform .2s cubic-bezier(.34,1.56,.64,1),
                box-shadow .2s;
    cursor: default;
    user-select: none;
}
.pill:hover {
    background: rgba(79,142,247,.22);
    border-color: rgba(79,142,247,.55);
    transform: translateY(-3px) scale(1.06);
    box-shadow: 0 6px 18px rgba(79,142,247,.25), 0 0 0 2px rgba(79,142,247,.12);
}
.pill:active {
    transform: translateY(-1px) scale(1.0) !important;
    transition: all .08s ease !important;
}

/* ══════════════ STAT ROW ══════════════ */
.stat-row {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: .75rem; margin-bottom: 1.25rem;
}
.stat-card {
    background: var(--bg-3);
    border: 1px solid var(--bd);
    border-radius: var(--rl); padding: 1rem 1.25rem;
    position: relative; overflow: hidden;
    transition: border-color .22s, transform .22s cubic-bezier(.34,1.2,.64,1),
                box-shadow .22s;
    cursor: default;
}
.stat-card:hover {
    border-color: var(--bd-3);
    transform: translateY(-5px) scale(1.012);
    box-shadow: 0 16px 40px rgba(0,0,0,.45), 0 0 0 1px rgba(255,255,255,.04);
}
.stat-card:active {
    transform: translateY(-2px) scale(1.005) !important;
    transition: all .08s ease !important;
}
.stat-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    opacity: 0; transition: opacity .22s;
    border-radius: var(--rl) var(--rl) 0 0;
}
.stat-card:hover::before { opacity: 1; }
.sc-blue::before  { background: linear-gradient(90deg, var(--blue), transparent); }
.sc-green::before { background: linear-gradient(90deg, var(--green), transparent); }
.sc-amber::before { background: linear-gradient(90deg, var(--amber), transparent); }
.sc-rose::before  { background: linear-gradient(90deg, var(--rose), transparent); }

/* Shimmer sweep on card hover */
.stat-card::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(
        105deg,
        transparent 40%,
        rgba(255,255,255,.04) 50%,
        transparent 60%
    );
    background-size: 200% 100%;
    background-position: -100% 0;
    transition: background-position .6s ease;
    pointer-events: none;
}
.stat-card:hover::after {
    background-position: 200% 0;
}

.stat-icon {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; margin-bottom: .65rem;
    transition: transform .2s cubic-bezier(.34,1.56,.64,1);
}
.stat-card:hover .stat-icon {
    transform: scale(1.18) rotate(-4deg);
}
.si-blue  { background: var(--blue-hi);  }
.si-green { background: var(--green-hi); }
.si-amber { background: var(--amber-hi); }
.si-rose  { background: var(--rose-hi);  }

.stat-lbl {
    font-size: .68rem; font-weight: 600;
    letter-spacing: .12em; text-transform: uppercase;
    color: var(--tx-lo); margin-bottom: .35rem;
}
.stat-body { font-size: .9rem; line-height: 1.75; color: var(--tx-2); }
.stat-title { font-size: 1.05rem; font-weight: 700; color: var(--tx-3); line-height:1.3; }

/* ══════════════ SUMMARY CARD ══════════════ */
.sum-card {
    background: var(--bg-3);
    border: 1px solid var(--bd);
    border-radius: var(--rl); padding: 1.35rem 1.5rem;
    margin-bottom: 1rem; position: relative; overflow: hidden;
    transition: border-color .22s, box-shadow .22s, transform .22s cubic-bezier(.34,1.2,.64,1);
}
.sum-card:hover {
    border-color: var(--bd-3);
    box-shadow: 0 12px 32px rgba(0,0,0,.4);
    transform: translateY(-2px);
}
.sum-card::before {
    content: ''; position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    background: linear-gradient(180deg, var(--blue), transparent);
    border-radius: var(--rl) 0 0 var(--rl);
    transition: width .2s;
}
.sum-card:hover::before { width: 4px; }

/* Shimmer on summary card */
.sum-card::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(
        105deg,
        transparent 40%,
        rgba(255,255,255,.03) 50%,
        transparent 60%
    );
    background-size: 200% 100%;
    background-position: -100% 0;
    transition: background-position .7s ease;
    pointer-events: none;
}
.sum-card:hover::after { background-position: 200% 0; }

.sum-lbl {
    font-size: .68rem; font-weight: 700; letter-spacing: .16em;
    text-transform: uppercase; color: var(--tx-lo); margin-bottom: .6rem;
}
.sum-body { font-size: .92rem; line-height: 1.78; color: var(--tx-2); }

/* ══════════════ SECTION TITLE ══════════════ */
.sec-head {
    display: flex; align-items: center; gap: .6rem;
    margin: 1.5rem 0 .85rem;
}
.sec-head-title {
    font-size: .88rem; font-weight: 700;
    color: var(--tx-2); letter-spacing: -.01em;
}
.sec-head-line {
    flex: 1; height: 1px; background: var(--bd);
}

/* ══════════════ TRANSCRIPT BOX ══════════════ */
.tx-box {
    font-family: 'JetBrains Mono', monospace;
    font-size: .75rem; line-height: 1.85;
    color: var(--tx); background: var(--bg);
    border: 1px solid var(--bd); border-radius: var(--r);
    padding: 1rem 1.2rem; max-height: 280px; overflow-y: auto;
    white-space: pre-wrap; word-break: break-word;
    box-shadow: inset 0 1px 3px rgba(0,0,0,.3);
    transition: border-color .18s;
}
.tx-box:hover { border-color: var(--bd-2); }

/* ══════════════ CHAT ══════════════ */
.chat-shell {
    background: var(--bg-2);
    border: 1px solid var(--bd-2);
    border-radius: var(--rl);
    overflow: hidden;
    margin-bottom: .75rem;
    box-shadow: 0 4px 20px rgba(0,0,0,.3);
    transition: border-color .22s, box-shadow .22s;
}
.chat-shell:hover {
    border-color: var(--bd-3);
    box-shadow: 0 8px 32px rgba(0,0,0,.4);
}
.chat-topbar {
    background: var(--bg-3);
    border-bottom: 1px solid var(--bd);
    padding: .7rem 1.1rem;
    display: flex; align-items: center; gap: .5rem;
}
.chat-topbar-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
    animation: livePulse 2s ease-in-out infinite;
}
@keyframes livePulse {
    0%,100% { opacity:1; } 50% { opacity:.3; }
}
.chat-topbar-lbl {
    font-size: .8rem; font-weight: 600;
    color: var(--tx-2); letter-spacing: .02em;
}
.chat-topbar-badge {
    margin-left: auto;
    font-size: .65rem; font-weight: 700;
    letter-spacing: .1em; text-transform: uppercase;
    background: var(--blue-hi); color: var(--blue);
    border: 1px solid var(--blue-ring);
    padding: .15rem .55rem; border-radius: 99px;
    transition: background .18s, box-shadow .18s;
    cursor: default;
}
.chat-topbar-badge:hover {
    background: rgba(79,142,247,.25);
    box-shadow: 0 0 10px rgba(79,142,247,.2);
}
.chat-msgs {
    padding: 1rem 1.1rem;
    max-height: 360px; overflow-y: auto;
    display: flex; flex-direction: column; gap: .85rem;
}
.c-msg  { display:flex; flex-direction:column; gap:.18rem; }
.c-role {
    font-size: .65rem; font-weight: 700;
    letter-spacing: .14em; text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.cr-u { color: var(--blue); }
.cr-b { color: var(--green); }
.c-bbl {
    padding: .65rem .95rem; border-radius: 10px;
    font-size: .9rem; line-height: 1.68; max-width: 88%;
    transition: box-shadow .18s, transform .18s;
}
.c-bbl:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,.3);
    transform: translateY(-1px);
}
.bu {
    background: var(--bg-4);
    border: 1px solid var(--bd-2);
    align-self: flex-end; border-bottom-right-radius: 3px;
    color: var(--tx-2);
}
.bb {
    background: var(--bg-3);
    border: 1px solid var(--bd);
    align-self: flex-start; border-bottom-left-radius: 3px;
    color: var(--tx-2);
}

/* ══════════════ EMPTY STATE ══════════════ */
.empty-wrap {
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    padding:5rem 2rem; text-align:center;
}
.empty-icon {
    width:80px; height:80px; border-radius:22px;
    background: var(--bg-3);
    border: 1px solid var(--bd-2);
    display:flex; align-items:center; justify-content:center;
    font-size:2rem; margin:0 auto 1.5rem;
    box-shadow: 0 0 0 8px rgba(79,142,247,.06),
                0 12px 32px rgba(0,0,0,.4);
    animation: floatIcon 4s ease-in-out infinite;
    transition: border-color .22s, box-shadow .22s, transform .22s;
    cursor: default;
}
.empty-icon:hover {
    border-color: var(--blue);
    box-shadow: 0 0 0 10px rgba(79,142,247,.12),
                0 16px 40px rgba(0,0,0,.5),
                0 0 30px rgba(79,142,247,.2);
    animation-play-state: paused;
    transform: scale(1.1) rotate(5deg);
}
@keyframes floatIcon {
    0%,100% { transform:translateY(0); }
    50%      { transform:translateY(-8px); }
}
.empty-title {
    font-size:1.2rem; font-weight:700;
    color:var(--tx-3); margin-bottom:.45rem;
}
.empty-desc {
    font-size:.92rem; color:var(--tx); line-height:1.7;
    max-width:380px; margin:0 auto 2rem;
}
.empty-features {
    display:grid; grid-template-columns:repeat(3,1fr);
    gap:.55rem; max-width:480px; margin:0 auto;
}
.ef-card {
    background: var(--bg-3);
    border: 1px solid var(--bd);
    border-radius: var(--rl); padding: .85rem 1rem;
    transition: border-color .22s, transform .22s cubic-bezier(.34,1.56,.64,1),
                box-shadow .22s, background .22s;
    cursor: default; text-align: center;
    position: relative; overflow: hidden;
}
.ef-card::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(
        135deg,
        transparent 40%,
        rgba(79,142,247,.06) 50%,
        transparent 60%
    );
    background-size: 200% 200%;
    background-position: -100% -100%;
    transition: background-position .5s ease;
    pointer-events: none;
}
.ef-card:hover::after { background-position: 100% 100%; }
.ef-card:hover {
    border-color: var(--blue);
    background: rgba(79,142,247,.06);
    transform: translateY(-5px) scale(1.04);
    box-shadow: 0 0 0 2px var(--blue-ring),
                0 12px 28px rgba(0,0,0,.35),
                0 0 20px rgba(79,142,247,.1);
}
.ef-card:active {
    transform: translateY(-2px) scale(1.01) !important;
    transition: all .08s ease !important;
}
.ef-icon {
    font-size:1.4rem; margin-bottom:.4rem;
    display: block;
    transition: transform .22s cubic-bezier(.34,1.56,.64,1);
}
.ef-card:hover .ef-icon { transform: scale(1.25) translateY(-2px); }
.ef-name {
    font-size:.8rem; font-weight:600;
    color:var(--tx-2); letter-spacing:.01em;
    transition: color .18s;
}
.ef-card:hover .ef-name { color: var(--tx-3); }

/* ══════════════ EXPANDER ══════════════ */
.stExpander {
    background: var(--bg-3) !important;
    border: 1px solid var(--bd) !important;
    border-radius: var(--r) !important;
    transition: border-color .2s, box-shadow .2s !important;
}
.stExpander:hover {
    border-color: var(--bd-2) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,.25) !important;
}
summary, [data-testid="stExpanderToggleIcon"] {
    transition: color .18s !important;
}
.stExpander summary:hover {
    color: var(--tx-3) !important;
}

/* ══════════════ MISC ══════════════ */
hr { border:none !important; border-top:1px solid var(--bd) !important; margin:1.5rem 0 !important; }
.stProgress > div > div > div {
    background:linear-gradient(90deg,var(--blue),#93C5FD) !important;
    transition: width .3s ease !important;
}
.stSpinner > div { border-top-color:var(--blue) !important; }
[data-testid="stMarkdownContainer"] p { color:var(--tx) !important; }
label { color:var(--tx) !important; font-size:.82rem !important; }
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--bd-2); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--blue); }

/* ══════════════ CLICK RIPPLE (JS-enhanced) ══════════════ */
@keyframes rippleOut {
    0%   { transform: scale(0); opacity: .6; }
    100% { transform: scale(4); opacity: 0; }
}
.ripple-circle {
    position: absolute;
    border-radius: 50%;
    width: 60px; height: 60px;
    background: rgba(255,255,255,.25);
    transform: scale(0);
    pointer-events: none;
    animation: rippleOut .55s ease-out forwards;
}

/* ══════════════ FOCUS-VISIBLE ACCESSIBILITY ══════════════ */
*:focus-visible {
    outline: 2px solid var(--blue) !important;
    outline-offset: 2px !important;
}
</style>

<!-- Ripple JS — injects a ripple circle on every button click -->
<script>
(function(){
  function addRipple(btn) {
    btn.addEventListener('click', function(e) {
      var rect = btn.getBoundingClientRect();
      var r = document.createElement('span');
      r.className = 'ripple-circle';
      r.style.left = (e.clientX - rect.left - 30) + 'px';
      r.style.top  = (e.clientY - rect.top  - 30) + 'px';
      btn.appendChild(r);
      setTimeout(function(){ if(r.parentNode) r.parentNode.removeChild(r); }, 600);
    });
  }
  function initRipples() {
    document.querySelectorAll('.stButton > button:not([data-ripple])').forEach(function(btn){
      btn.setAttribute('data-ripple','1');
      addRipple(btn);
    });
  }
  var obs = new MutationObserver(initRipples);
  obs.observe(document.body, {childList:true, subtree:true});
  initRipples();
})();
</script>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────────
for k, v in {
    "result": None, "chat_history": [],
    "processing": False, "pipeline_done": False, "pipeline_steps": {},
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

STEPS = [
    ("audio",      "🔊", "Audio extraction"),
    ("transcript", "📝", "Transcription"),
    ("title",      "🏷️",  "Title generation"),
    ("summary",    "📋", "Summarisation"),
    ("extract",    "🔍", "Signal extraction"),
    ("rag",        "🧠", "RAG index"),
]

def render_step(icon, label, key):
    s  = st.session_state.pipeline_steps.get(key, "pending")
    sc = {"done":"ps-done","active":"ps-active","pending":"ps-pending"}[s]
    dc = {"done":"pd-done","active":"pd-active","pending":"pd-pending"}[s]
    st.markdown(
        f'<div class="p-step {sc}">'
        f'<div class="p-dot {dc}"></div>{icon} {label}</div>',
        unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Hero banner ──
    st.markdown("""
    <div class="sb-hero">
        <div class="sb-top-row">
            <div class="sb-icon-chip">🎙️</div>
            <div class="sb-wordmark-block">
                <div class="sb-wordmark">Verba<span class="blue">tim</span></div>
                <span class="sb-tagpill">AI Meeting Intelligence</span>
            </div>
        </div>
        <div class="sb-status-row">
            <div class="sb-status-dot"></div>
            <span class="sb-status-txt">Ready · Whisper · LangChain · FAISS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Body ──
    st.markdown('<div class="sb-body">', unsafe_allow_html=True)

    # Source
    st.markdown("""
    <div class="sb-label">
        <span class="sb-label-icon">🔗</span> Source
    </div>
    """, unsafe_allow_html=True)

    source = st.text_input("_src", label_visibility="collapsed",
        placeholder="Paste YouTube URL or /path/to/file")

    st.markdown("""
    <div class="sb-tags">
        <span class="sb-tag">YouTube</span>
        <span class="sb-tag">MP4</span>
        <span class="sb-tag">WAV</span>
        <span class="sb-tag">MP3</span>
    </div>
    """, unsafe_allow_html=True)

    # Language
    st.markdown("""
    <div class="sb-label">
        <span class="sb-label-icon">🌐</span> Language
    </div>
    """, unsafe_allow_html=True)

    language = st.selectbox("_lang", ["english", "hinglish"],
        label_visibility="collapsed", format_func=lambda x: x.capitalize())

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # Run Analysis button
    run_btn = st.button("⚡  Run Analysis", use_container_width=True)
    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

    # Pipeline steps (shown after run)
    if st.session_state.pipeline_done or st.session_state.pipeline_steps:
        st.markdown("""
        <div class="sb-label" style="margin-top:.8rem">
            <span class="sb-label-icon">⚙️</span> Pipeline
        </div>
        """, unsafe_allow_html=True)
        for key, icon, label in STEPS:
            render_step(icon, label, key)

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="sb-footer">
        <div class="sb-footer-stack">
            <span class="sb-badge">Whisper</span>
            <span class="sb-badge">LangChain</span>
            <span class="sb-badge">FAISS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-glow"></div>
    <div class="hero-eyebrow">AI Meeting Intelligence</div>
    <div class="hero-h1">Turn recordings into<br><em>structured insight</em></div>
    <div class="hero-desc">
        Drop a YouTube link or a local file. Verbatim transcribes the audio,
        generates a clear summary, mines key decisions and action items —
        then lets you interrogate every detail with natural language.
    </div>
    <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">
        <div class="wave">
            <s></s><s></s><s></s><s></s><s></s>
            <s></s><s></s><s></s><s></s><s></s>
            <s></s><s></s>
        </div>
        <div class="hero-pills">
            <span class="pill">Transcription</span>
            <span class="pill">Summarisation</span>
            <span class="pill">Action Items</span>
            <span class="pill">RAG Chat</span>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

# ── PIPELINE RUN ─────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("⚠️  Add a YouTube URL or file path in the sidebar first.")
    else:
        st.session_state.update(pipeline_done=False, result=None,
                                chat_history=[], pipeline_steps={})
        prog = st.empty()
        def tick(k, s): st.session_state.pipeline_steps[k] = s
        try:
            prog.info("Running pipeline — see sidebar for live progress…")
            tick("audio","active");      chunks=process_input(source);               tick("audio","done")
            tick("transcript","active"); transcript=transcribe_all(chunks,language); tick("transcript","done")
            tick("title","active");      title=generate_title(transcript);           tick("title","done")
            tick("summary","active");    summary=summarize(transcript);              tick("summary","done")
            tick("extract","active")
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            tick("extract","done")
            tick("rag","active");        rag_chain=build_rag_chain(transcript);      tick("rag","done")
            st.session_state.result = dict(
                title=title, transcript=transcript, summary=summary,
                action_items=action_items, key_decisions=decisions,
                open_questions=questions, rag_chain=rag_chain,
            )
            st.session_state.pipeline_done = True
            prog.success("✅  Analysis complete!")
            time.sleep(0.6); prog.empty(); st.rerun()
        except Exception as e:
            for k,_,_ in STEPS:
                if st.session_state.pipeline_steps.get(k)=="active":
                    st.session_state.pipeline_steps[k]="pending"
            prog.error(f"Error: {e}")

# ── RESULTS ───────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # ── Session title ──
    st.markdown(f"""
    <div class="sum-card sc-blue" style="margin-bottom:1.25rem">
        <div class="sum-lbl">📌 Session Title</div>
        <div style="font-size:1.1rem;font-weight:700;color:var(--tx-3);line-height:1.3">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Summary + Transcript ──
    col_s, col_t = st.columns([3,2], gap="medium")
    with col_s:
        st.markdown(f"""
        <div class="sum-card" style="height:100%;margin-bottom:0">
            <div class="sum-lbl">📋 Summary</div>
            <div class="sum-body">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)
    with col_t:
        with st.expander("📝  Full Transcript", expanded=False):
            st.markdown(f'<div class="tx-box">{r["transcript"]}</div>',
                unsafe_allow_html=True)

    # ── Intelligence cards ──
    st.markdown("""
    <div class="sec-head">
        <span class="sec-head-title">Intelligence Extraction</span>
        <div class="sec-head-line"></div>
    </div>""", unsafe_allow_html=True)

    ca, cb, cc = st.columns(3, gap="medium")
    cards = [
        (ca, "sc-green", "si-green", "✅", "Action Items",   r["action_items"]),
        (cb, "sc-blue",  "si-blue",  "🔑", "Key Decisions",  r["key_decisions"]),
        (cc, "sc-amber", "si-amber", "❓", "Open Questions", r["open_questions"]),
    ]
    for col, sc, si, icon, lbl, content in cards:
        with col:
            st.markdown(f"""
            <div class="stat-card {sc}">
                <div class="stat-icon {si}">{icon}</div>
                <div class="stat-lbl">{lbl}</div>
                <div class="stat-body">{content}</div>
            </div>""", unsafe_allow_html=True)

    # ── RAG Chat ──
    st.markdown("""
    <div class="sec-head" style="margin-top:1.75rem">
        <span class="sec-head-title">Ask your meeting</span>
        <div class="sec-head-line"></div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.chat_history:
        msgs_html = ""
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                msgs_html += (
                    f'<div class="c-msg" style="align-items:flex-end">'
                    f'<span class="c-role cr-u">You</span>'
                    f'<div class="c-bbl bu">{m["content"]}</div></div>')
            else:
                msgs_html += (
                    f'<div class="c-msg" style="align-items:flex-start">'
                    f'<span class="c-role cr-b">Verbatim AI</span>'
                    f'<div class="c-bbl bb">{m["content"]}</div></div>')

        st.markdown(f"""
        <div class="chat-shell">
            <div class="chat-topbar">
                <div class="chat-topbar-dot"></div>
                <span class="chat-topbar-lbl">Live session</span>
                <span class="chat-topbar-badge">RAG-powered</span>
            </div>
            <div class="chat-msgs">{msgs_html}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chat-shell">
            <div class="chat-topbar">
                <div class="chat-topbar-dot"></div>
                <span class="chat-topbar-lbl">Ready to answer</span>
                <span class="chat-topbar-badge">RAG-powered</span>
            </div>
            <div style="padding:2.25rem 1.25rem;text-align:center">
                <div style="font-size:1.5rem;margin-bottom:.5rem">💬</div>
                <div style="font-size:.9rem;font-weight:600;color:var(--tx-2);margin-bottom:.3rem">
                    Ask anything about your meeting
                </div>
                <div style="font-size:.8rem;color:var(--tx)">
                    Decisions · Follow-ups · Timelines · Owners · Open questions
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    qi, send_col = st.columns([5,1], gap="small")
    with qi:
        user_input = st.text_input("q",
            placeholder="e.g.  What action items were assigned to the engineering team?",
            label_visibility="collapsed")
    with send_col:
        send = st.button("Send →", use_container_width=True)

    if send and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history += [
            {"role":"user","content":user_input.strip()},
            {"role":"assistant","content":answer},
        ]
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️  Clear chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

# ── EMPTY STATE ───────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="empty-wrap">
        <div class="empty-icon">🎙️</div>
        <div class="empty-title">No session loaded</div>
        <div class="empty-desc">
            Paste a YouTube URL or local file path in the sidebar,
            choose a language, and click
            <strong style="color:var(--tx-3)">Run Analysis</strong> to begin.
        </div>
        <div class="empty-features">
            <div class="ef-card">
                <div class="ef-icon">🎧</div>
                <div class="ef-name">Transcription</div>
            </div>
            <div class="ef-card">
                <div class="ef-icon">📋</div>
                <div class="ef-name">Summarisation</div>
            </div>
            <div class="ef-card">
                <div class="ef-icon">✅</div>
                <div class="ef-name">Action Items</div>
            </div>
            <div class="ef-card">
                <div class="ef-icon">🔑</div>
                <div class="ef-name">Key Decisions</div>
            </div>
            <div class="ef-card">
                <div class="ef-icon">❓</div>
                <div class="ef-name">Open Questions</div>
            </div>
            <div class="ef-card">
                <div class="ef-icon">💬</div>
                <div class="ef-name">RAG Chat</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


st.markdown("""
<div style="
    margin-top: 180px;
    padding: -120px 0;
    text-align: center;
    border-top: 1px solid rgba(79,142,247,0.15);
">
    <span style="color:#7B90B8;font-size:14px;">
        🚀 Developed with ❤️ by
    </span>
    <span style="
        color:#4F8EF7;
        font-weight:700;
        font-size:14px;
    ">
        Akansha Kumari
    </span>
</div>
""", unsafe_allow_html=True)