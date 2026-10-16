import json
import time

import streamlit as st
import streamlit.components.v1 as components

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

:root {
    --bg: #07070c;
    --orange: #ff8c32;
    --red: #ff4d1a;
    --green: #50c878;
    --text: #ece8df;
    --muted: #9a928a;
    --glass: rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.09);
    --sy: 0;
}

html { scroll-behavior: smooth; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--text); }

.stApp {
    background: var(--bg);
}

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 3rem 4rem; max-width: 1240px; position: relative; z-index: 2; }

/* ── Fixed animated background ── */
.bg-layer { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.orb {
    position: absolute; border-radius: 50%; filter: blur(90px); opacity: .55;
    will-change: transform;
}
.orb.o1 { width: 520px; height: 520px; left: -140px; top: -120px;
    background: radial-gradient(circle, rgba(255,140,50,.55), transparent 70%);
    transform: translateY(calc(var(--sy) * 0.25px));
    animation: float1 14s ease-in-out infinite alternate; }
.orb.o2 { width: 460px; height: 460px; right: -120px; top: 30vh;
    background: radial-gradient(circle, rgba(255,70,30,.40), transparent 70%);
    transform: translateY(calc(var(--sy) * -0.18px));
    animation: float2 18s ease-in-out infinite alternate; }
.orb.o3 { width: 420px; height: 420px; left: 35vw; bottom: -160px;
    background: radial-gradient(circle, rgba(120,90,255,.30), transparent 70%);
    transform: translateY(calc(var(--sy) * -0.1px));
    animation: float1 20s ease-in-out infinite alternate-reverse; }
@keyframes float1 { to { margin-left: 70px; margin-top: 50px; } }
@keyframes float2 { to { margin-left: -80px; margin-top: -40px; } }
.grid-bg {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: radial-gradient(ellipse 70% 60% at 50% 20%, #000 20%, transparent 75%);
    -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 20%, #000 20%, transparent 75%);
    transform: translateY(calc(var(--sy) * 0.08px));
}

/* ── Scroll progress + cursor glow (injected by JS) ── */
#rm-progress {
    position: fixed; top: 0; left: 0; height: 3px; width: 0%; z-index: 9999;
    background: linear-gradient(90deg, #ff8c32, #ff4d1a, #a855f7);
    box-shadow: 0 0 14px rgba(255,140,50,.8);
}
#rm-glow {
    position: fixed; width: 380px; height: 380px; border-radius: 50%;
    pointer-events: none; z-index: 1; left: 0; top: 0;
    background: radial-gradient(circle, rgba(255,140,50,.10), transparent 65%);
    transform: translate(-50%, -50%); transition: opacity .3s; opacity: 0;
}

/* ── Reveal on scroll ── */
.rv { opacity: 0; transform: translateY(38px) scale(.985); filter: blur(6px);
      transition: opacity .8s cubic-bezier(.2,.7,.2,1), transform .8s cubic-bezier(.2,.7,.2,1), filter .8s; }
.rv.rv-in { opacity: 1; transform: none; filter: none; }

/* ── Nav ── */
.nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: .9rem 1.4rem; margin: .5rem 0 0;
    background: rgba(12,12,18,.55); border: 1px solid var(--glass-border);
    border-radius: 100px; backdrop-filter: blur(16px);
}
.nav-logo { font-family: 'Syne'; font-weight: 800; font-size: 1.05rem; letter-spacing: -.01em; }
.nav-logo b { color: var(--orange); }
.nav-links { display: flex; gap: 1.6rem; font-family: 'DM Mono'; font-size: .7rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.nav-pill { font-family: 'DM Mono'; font-size: .66rem; letter-spacing: .12em; padding: .35rem .8rem; border-radius: 100px;
    border: 1px solid rgba(80,200,120,.35); color: var(--green); display: flex; align-items: center; gap: .45rem; }
.nav-pill i { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); animation: pulse 1.8s infinite; }
@keyframes pulse { 50% { opacity: .35; transform: scale(.7); } }

/* ── Hero ── */
.hero { text-align: center; padding: 5rem 0 3rem; position: relative; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: .6rem;
    font-family: 'DM Mono'; font-size: .7rem; letter-spacing: .25em; text-transform: uppercase;
    color: var(--orange); padding: .45rem 1rem; border-radius: 100px;
    border: 1px solid rgba(255,140,50,.3); background: rgba(255,140,50,.07);
    margin-bottom: 1.6rem;
}
.hero h1 {
    font-family: 'Syne'; font-weight: 800; letter-spacing: -.045em; line-height: .95;
    font-size: clamp(3.2rem, 8.5vw, 7rem); color: #f4efe4; margin: 0 0 1.4rem;
    transform: translateY(calc(var(--sy) * -0.06px));
}
.hero h1 .grad {
    background: linear-gradient(110deg, #ff8c32 0%, #ff4d1a 35%, #ffb36b 60%, #ff8c32 100%);
    background-size: 220% auto; -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; animation: shine 5s linear infinite;
}
@keyframes shine { to { background-position: 220% center; } }
.hero-sub { font-size: 1.12rem; font-weight: 300; color: var(--muted); max-width: 600px; margin: 0 auto; line-height: 1.7; }
.hero-sub strong { color: var(--text); font-weight: 500; }

.scroll-hint { margin-top: 2.6rem; display: inline-flex; flex-direction: column; align-items: center; gap: .5rem;
    font-family: 'DM Mono'; font-size: .62rem; letter-spacing: .25em; color: #6b645c; text-transform: uppercase; }
.mouse { width: 22px; height: 34px; border: 1.5px solid #6b645c; border-radius: 12px; position: relative; }
.mouse::after { content: ''; position: absolute; left: 50%; top: 7px; width: 3px; height: 7px; margin-left: -1.5px;
    background: var(--orange); border-radius: 3px; animation: wheel 1.6s infinite; }
@keyframes wheel { 0% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(12px); } }

/* ── Marquee ── */
.marquee { overflow: hidden; margin: 1rem -3rem 2.5rem; padding: 1rem 0;
    border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border);
    background: rgba(255,255,255,.02);
    mask-image: linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent);
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent); }
.marquee-track { display: flex; gap: 3rem; width: max-content; animation: scrollx 32s linear infinite; }
.marquee-track span { font-family: 'Syne'; font-weight: 700; font-size: 1.1rem; color: #4a443e; white-space: nowrap; text-transform: uppercase; letter-spacing: .08em; }
.marquee-track span em { color: var(--orange); font-style: normal; margin-right: 3rem; }
@keyframes scrollx { to { transform: translateX(-50%); } }

/* ── Section titles ── */
.eyebrow { font-family: 'DM Mono'; font-size: .68rem; letter-spacing: .25em; text-transform: uppercase; color: var(--orange); margin-bottom: .6rem; }
.section-heading { font-family: 'Syne'; font-size: clamp(1.6rem, 3.2vw, 2.4rem); font-weight: 800; letter-spacing: -.03em; color: #f4efe4; margin: 0 0 1.2rem; }

/* ── Input card ── */
.st-key-input_card {
    background: linear-gradient(145deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    border: 1px solid rgba(255,140,50,.22); border-radius: 22px; padding: 1.8rem 2rem 1.6rem;
    backdrop-filter: blur(14px); box-shadow: 0 20px 60px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.06);
    position: relative; overflow: hidden;
}
.st-key-input_card::before {
    content: ''; position: absolute; inset: -1px; border-radius: 22px; padding: 1px; pointer-events: none;
    background: conic-gradient(from var(--ang, 0deg), transparent 0 70%, rgba(255,140,50,.9) 85%, transparent 100%);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor;
    mask-composite: exclude; animation: spin 6s linear infinite;
}
@property --ang { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
@keyframes spin { to { --ang: 360deg; } }

.stTextInput > div > div > input {
    background: rgba(0,0,0,.35) !important; border: 1px solid rgba(255,140,50,.25) !important;
    border-radius: 14px !important; color: #f4efe4 !important; font-size: 1.05rem !important;
    padding: .95rem 1.1rem !important; transition: all .25s !important;
}
.stTextInput > div > div > input:focus { border-color: var(--orange) !important; box-shadow: 0 0 0 4px rgba(255,140,50,.14), 0 0 30px rgba(255,140,50,.15) !important; }
.stTextInput > label, .stTextInput label p {
    font-family: 'DM Mono' !important; font-size: .7rem !important; letter-spacing: .18em !important;
    text-transform: uppercase !important; color: var(--orange) !important; font-weight: 500 !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Syne' !important; font-weight: 700 !important; letter-spacing: .03em !important;
    border-radius: 12px !important; transition: all .25s cubic-bezier(.2,.7,.2,1) !important; width: 100%;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #ff9a42 0%, #ff4d1a 100%) !important; color: #0a0a0f !important;
    border: none !important; padding: .8rem 2rem !important; font-size: 1rem !important;
    box-shadow: 0 8px 30px rgba(255,100,30,.35) !important; position: relative; overflow: hidden;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-3px) scale(1.01) !important; box-shadow: 0 14px 40px rgba(255,100,30,.5) !important;
}
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"] {
    background: rgba(255,255,255,.04) !important; color: #b4aca2 !important;
    border: 1px solid rgba(255,255,255,.1) !important; font-family: 'DM Sans' !important;
    font-weight: 500 !important; font-size: .78rem !important; padding: .35rem .6rem !important;
}
.stButton > button[kind="secondary"]:hover, .stButton > button[data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--orange) !important; color: var(--orange) !important; background: rgba(255,140,50,.08) !important; transform: translateY(-2px) !important;
}
.stDownloadButton > button {
    background: rgba(80,200,120,.08) !important; border: 1px solid rgba(80,200,120,.4) !important;
    color: var(--green) !important; border-radius: 12px !important; font-family: 'Syne' !important; font-weight: 700 !important;
    padding: .65rem 1.6rem !important; transition: all .25s !important;
}
.stDownloadButton > button:hover { background: rgba(80,200,120,.16) !important; transform: translateY(-2px); box-shadow: 0 10px 30px rgba(80,200,120,.2); }

/* ── Pipeline ── */
div[data-testid="stColumn"]:last-child { position: sticky; top: 1.2rem; align-self: flex-start; }
.pipe-wrap { position: relative; padding-left: 0; }
.step-card {
    background: var(--glass); border: 1px solid var(--glass-border); border-radius: 16px;
    padding: 1.1rem 1.4rem; margin-bottom: .9rem; position: relative; overflow: hidden;
    transition: all .4s cubic-bezier(.2,.7,.2,1); backdrop-filter: blur(10px);
}
.step-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: rgba(255,255,255,.07); transition: background .3s; }
.step-card.active { border-color: rgba(255,140,50,.5); background: rgba(255,140,50,.06); transform: translateX(6px); box-shadow: 0 10px 40px rgba(255,120,30,.15); }
.step-card.active::before { background: var(--orange); box-shadow: 0 0 14px var(--orange); }
.step-card.active::after { content: ''; position: absolute; inset: 0; background: linear-gradient(100deg, transparent 30%, rgba(255,140,50,.14) 50%, transparent 70%); animation: sweep 1.6s infinite; }
@keyframes sweep { from { transform: translateX(-100%); } to { transform: translateX(100%); } }
.step-card.done { border-color: rgba(80,200,120,.35); background: rgba(80,200,120,.04); }
.step-card.done::before { background: var(--green); }
.step-card.error { border-color: rgba(255,80,80,.45); background: rgba(255,80,80,.05); }
.step-card.error::before { background: #ff5050; }
.step-header { display: flex; align-items: center; gap: .8rem; }
.step-icon { width: 38px; height: 38px; display: grid; place-items: center; font-size: 1.15rem; border-radius: 11px; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08); }
.step-num { font-family: 'DM Mono'; font-size: .62rem; letter-spacing: .15em; color: var(--orange); opacity: .8; display: block; }
.step-title { font-family: 'Syne'; font-size: .95rem; font-weight: 700; color: #f4efe4; }
.step-status { margin-left: auto; font-family: 'DM Mono'; font-size: .64rem; letter-spacing: .1em; padding: .25rem .6rem; border-radius: 100px; border: 1px solid transparent; }
.status-waiting { color: #6b645c; border-color: rgba(255,255,255,.07); }
.status-running { color: var(--orange); border-color: rgba(255,140,50,.4); background: rgba(255,140,50,.08); animation: pulse 1.2s infinite; }
.status-done { color: var(--green); border-color: rgba(80,200,120,.35); background: rgba(80,200,120,.08); }
.status-error { color: #ff6b6b; border-color: rgba(255,80,80,.4); }
.step-desc { font-size: .8rem; color: #78706a; margin: .55rem 0 0 3.1rem; }

.pbar { height: 4px; border-radius: 4px; background: rgba(255,255,255,.06); overflow: hidden; margin: .4rem 0 1rem; }
.pbar > div { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #ff8c32, #ff4d1a); box-shadow: 0 0 12px rgba(255,120,30,.7); transition: width .6s cubic-bezier(.2,.7,.2,1); }

/* ── Chips label ── */
.try-label { font-family: 'DM Mono'; font-size: .64rem; letter-spacing: .18em; color: #6b645c; margin: .9rem 0 .35rem; text-transform: uppercase; }

/* ── Result panels ── */
.result-panel { background: rgba(255,255,255,.025); border: 1px solid var(--glass-border); border-radius: 14px; padding: 1.4rem 1.6rem; }
.result-panel-title { font-family: 'DM Mono'; font-size: .68rem; letter-spacing: .2em; text-transform: uppercase; color: var(--orange); margin-bottom: .9rem; padding-bottom: .6rem; border-bottom: 1px solid rgba(255,140,50,.15); }
.result-content { font-size: .9rem; line-height: 1.8; color: #cdc8bf; white-space: pre-wrap; }

.st-key-report_panel, .st-key-feedback_panel {
    border-radius: 22px; padding: 2.2rem 2.6rem; margin-top: 1rem; backdrop-filter: blur(12px);
    background: linear-gradient(160deg, rgba(255,255,255,.045), rgba(255,255,255,.015));
    box-shadow: 0 30px 80px rgba(0,0,0,.35);
}
.st-key-report_panel { border: 1px solid rgba(255,140,50,.28); }
.st-key-feedback_panel { border: 1px solid rgba(80,200,120,.28); }
.st-key-report_panel h1, .st-key-report_panel h2, .st-key-report_panel h3 { font-family: 'Syne'; letter-spacing: -.02em; color: #f4efe4; }
.st-key-report_panel h2 { border-bottom: 1px solid rgba(255,140,50,.18); padding-bottom: .4rem; margin-top: 1.8rem; }
.st-key-report_panel p, .st-key-report_panel li, .st-key-feedback_panel p, .st-key-feedback_panel li { line-height: 1.85; color: #d4cfc5; font-size: 1rem; }
.st-key-report_panel a { color: var(--orange); }
.panel-label { font-family: 'DM Mono'; font-size: .7rem; letter-spacing: .2em; text-transform: uppercase; margin-bottom: 1rem; padding-bottom: .7rem; }
.panel-label.orange { color: var(--orange); border-bottom: 1px solid rgba(255,140,50,.18); }
.panel-label.green { color: var(--green); border-bottom: 1px solid rgba(80,200,120,.18); }

/* ── Expander ── */
[data-testid="stExpander"] { border: 1px solid var(--glass-border) !important; border-radius: 14px !important; background: var(--glass) !important; margin-bottom: .8rem; }
[data-testid="stExpander"] summary { font-family: 'DM Mono' !important; font-size: .75rem !important; color: #a09890 !important; letter-spacing: .1em !important; }

.stSpinner > div { color: var(--orange) !important; }
.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,140,50,.4), transparent); margin: 3rem 0 2.2rem; }

/* ── Feature cards (how it works) ── */
.feat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.1rem; margin: 1rem 0 2rem; }
.feat {
    position: relative; padding: 1.7rem 1.4rem; border-radius: 20px; overflow: hidden;
    background: var(--glass); border: 1px solid var(--glass-border); backdrop-filter: blur(10px);
    transition: transform .4s cubic-bezier(.2,.7,.2,1), border-color .3s, box-shadow .4s;
}
.feat::before { content: ''; position: absolute; inset: 0; background: radial-gradient(400px circle at var(--mx, 50%) var(--my, 0%), rgba(255,140,50,.14), transparent 45%); opacity: 0; transition: opacity .3s; }
.feat:hover { transform: translateY(-8px); border-color: rgba(255,140,50,.4); box-shadow: 0 24px 60px rgba(0,0,0,.45); }
.feat:hover::before { opacity: 1; }
.feat .big { font-family: 'Syne'; font-weight: 800; font-size: 3.2rem; line-height: 1; letter-spacing: -.05em; color: rgba(255,140,50,.18); }
.feat .ico { font-size: 1.8rem; margin: .8rem 0 .6rem; display: block; }
.feat h4 { font-family: 'Syne'; font-size: 1.05rem; margin: 0 0 .4rem; color: #f4efe4; }
.feat p { font-size: .85rem; color: var(--muted); line-height: 1.6; margin: 0; }
.feat:nth-child(2) { transition-delay: .08s; } .feat:nth-child(3) { transition-delay: .16s; } .feat:nth-child(4) { transition-delay: .24s; }

.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1rem 0 2rem; }
.stat { text-align: center; padding: 1.6rem 1rem; border-radius: 18px; border: 1px solid var(--glass-border); background: var(--glass); }
.stat b { display: block; font-family: 'Syne'; font-size: 2.4rem; font-weight: 800; letter-spacing: -.04em;
    background: linear-gradient(120deg, #ff8c32, #ff4d1a); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.stat span { font-family: 'DM Mono'; font-size: .66rem; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); }

.notice { font-family: 'DM Mono'; font-size: .7rem; color: #5b544c; text-align: center; margin-top: 3rem; letter-spacing: .08em; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 10px; } ::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: linear-gradient(#ff8c32, #ff4d1a); border-radius: 10px; border: 2px solid #0a0a0f; }

@media (max-width: 900px) {
    .block-container { padding: 1rem 1.2rem 3rem; }
    .nav-links { display: none; }
    .feat-grid { grid-template-columns: 1fr 1fr; }
    .stats { grid-template-columns: 1fr; }
    .marquee { margin: 1rem -1.2rem 2rem; }
    div[data-testid="stColumn"]:last-child { position: static; }
}
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } .rv { opacity: 1; transform: none; filter: none; } }
</style>
<div class="bg-layer"><div class="grid-bg"></div><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div></div>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── JS: scroll progress, reveal-on-scroll, parallax, cursor glow ─────────────
PARENT_JS = r"""
(function () {
  if (window.__rmInit) return; window.__rmInit = true;
  var doc = document;
  var bar = doc.createElement('div'); bar.id = 'rm-progress'; doc.body.appendChild(bar);
  var glow = doc.createElement('div'); glow.id = 'rm-glow'; doc.body.appendChild(glow);

  doc.addEventListener('scroll', function (e) {
    var t = e.target === doc ? doc.documentElement : e.target;
    if (!t || t.scrollHeight === undefined) return;
    var max = t.scrollHeight - t.clientHeight;
    if (max < 50) return;
    var y = t.scrollTop;
    bar.style.width = Math.min(100, (y / max) * 100) + '%';
    doc.documentElement.style.setProperty('--sy', y);
  }, true);

  doc.addEventListener('mousemove', function (e) {
    glow.style.opacity = 1;
    glow.style.left = e.clientX + 'px'; glow.style.top = e.clientY + 'px';
    var f = e.target.closest ? e.target.closest('.feat') : null;
    if (f) { var r = f.getBoundingClientRect();
      f.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      f.style.setProperty('--my', (e.clientY - r.top) + 'px'); }
  });

  var SEL = '.reveal, .feat, .stat, [data-testid="stExpander"], .st-key-report_panel, .st-key-feedback_panel, .st-key-input_card, .hero > *, .section-block';
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('rv-in'); io.unobserve(en.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });

  function scan() {
    doc.querySelectorAll(SEL).forEach(function (el) {
      if (el.__rv) return; el.__rv = 1;
      el.classList.add('rv');
      // stagger hero children
      if (el.parentElement && el.parentElement.classList.contains('hero')) {
        var i = Array.prototype.indexOf.call(el.parentElement.children, el);
        el.style.transitionDelay = (i * 0.12) + 's';
      }
      io.observe(el);
    });
  }
  scan();
  new MutationObserver(function () { scan(); }).observe(doc.body, { childList: true, subtree: true });

  // animated counters
  var cio = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return; cio.unobserve(en.target);
      var el = en.target, end = parseFloat(el.dataset.count), suf = el.dataset.suffix || '', t0 = null;
      function step(ts) { t0 = t0 || ts; var p = Math.min(1, (ts - t0) / 1400);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))) + suf; if (p < 1) requestAnimationFrame(step); }
      requestAnimationFrame(step);
    });
  }, { threshold: 0.6 });
  setInterval(function () { doc.querySelectorAll('[data-count]').forEach(function (el) { if (!el.__c) { el.__c = 1; cio.observe(el); } }); }, 800);
})();
"""
inject = f"""
<script>
(function() {{
  try {{
    var pd = window.parent.document;
    if (pd.getElementById('rm-script')) return;
    var s = pd.createElement('script'); s.id = 'rm-script';
    s.textContent = {json.dumps(PARENT_JS)};
    pd.body.appendChild(s);
  }} catch (e) {{ console.log('ResearchMind JS inject failed', e); }}
}})();
</script>
"""
components.html(inject, height=0)


# ── Pipeline config / helpers ─────────────────────────────────────────────────
STEPS = [
    ("search", "01", "🔍", "Search Agent", "Gathers recent web information"),
    ("reader", "02", "📄", "Reader Agent", "Scrapes & extracts deep content"),
    ("writer", "03", "✍️", "Writer Chain", "Drafts the full research report"),
    ("critic", "04", "🧐", "Critic Chain", "Reviews & scores the report"),
]
LABELS = {
    "waiting": ("WAITING", "status-waiting", ""),
    "running": ("● RUNNING", "status-running", "active"),
    "done": ("✓ DONE", "status-done", "done"),
    "error": ("✕ FAILED", "status-error", "error"),
}


def render_pipeline(states: dict) -> str:
    done_n = sum(1 for v in states.values() if v == "done")
    pct = int(done_n / len(STEPS) * 100)
    out = f'<div class="pipe-wrap"><div class="pbar"><div style="width:{pct}%"></div></div>'
    for key, num, icon, title, desc in STEPS:
        label, cls, card = LABELS[states.get(key, "waiting")]
        out += (
            f'<div class="step-card {card}"><div class="step-header">'
            f'<div class="step-icon">{icon}</div>'
            f'<div><span class="step-num">STEP {num}</span><span class="step-title">{title}</span></div>'
            f'<span class="step-status {cls}">{label}</span></div>'
            f'<div class="step-desc">{desc}</div></div>'
        )
    return out + "</div>"


def states_from(results: dict, running_key: str | None = None, error_key: str | None = None) -> dict:
    s = {}
    for key, *_ in STEPS:
        if key == error_key:
            s[key] = "error"
        elif key in results:
            s[key] = "done"
        elif key == running_key:
            s[key] = "running"
        else:
            s[key] = "waiting"
    return s


def set_example(text: str):
    st.session_state.topic_input = text


# ── Session state ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = {}
if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""


# ── Nav + Hero ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav">
    <div class="nav-logo">🔬 Research<b>Mind</b></div>
    <div class="nav-links"><span>Pipeline</span><span>Results</span><span>How it works</span></div>
    <div class="nav-pill"><i></i>AGENTS ONLINE</div>
</div>

<div class="hero">
    <div class="hero-eyebrow">✦ Multi-Agent AI System</div>
    <h1>Research<br><span class="grad">at the speed of thought</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — <strong>searching, scraping, writing</strong>
        and <strong>critiquing</strong> — to deliver a polished research report on any topic.
    </p>
    <div class="scroll-hint"><div class="mouse"></div>Scroll</div>
</div>

<div class="marquee"><div class="marquee-track">
    <span><em>✦</em>Web Search</span><span><em>✦</em>Deep Scraping</span><span><em>✦</em>Report Writing</span>
    <span><em>✦</em>Critical Review</span><span><em>✦</em>LangChain Agents</span><span><em>✦</em>Markdown Export</span>
    <span><em>✦</em>Web Search</span><span><em>✦</em>Deep Scraping</span><span><em>✦</em>Report Writing</span>
    <span><em>✦</em>Critical Review</span><span><em>✦</em>LangChain Agents</span><span><em>✦</em>Markdown Export</span>
</div></div>
""", unsafe_allow_html=True)


# ── Input + pipeline ──────────────────────────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.4, 4])

with col_input:
    st.markdown('<div class="eyebrow">Start here</div><div class="section-heading">What should we research?</div>',
                unsafe_allow_html=True)
    with st.container(key="input_card"):
        topic = st.text_input(
            "Research Topic",
            placeholder="e.g. Quantum computing breakthroughs in 2025",
            key="topic_input",
        )
        run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True, type="primary")
        st.markdown('<div class="try-label">Try an example →</div>', unsafe_allow_html=True)
        ex_cols = st.columns(3)
        for col, ex in zip(ex_cols, ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]):
            col.button(ex, key=f"ex_{ex}", on_click=set_example, args=(ex,), use_container_width=True)

with col_pipeline:
    st.markdown('<div class="eyebrow">Live status</div><div class="section-heading">Pipeline</div>',
                unsafe_allow_html=True)
    pipeline_slot = st.empty()
    pipeline_slot.markdown(render_pipeline(states_from(st.session_state.results)), unsafe_allow_html=True)


# ── Run pipeline (live updates) ───────────────────────────────────────────────
if run_btn:
    topic_val = (topic or "").strip()
    if not topic_val:
        st.warning("Please enter a research topic first.")
    else:
        results: dict = {}
        st.session_state.results = {}

        def update(running=None, error=None):
            pipeline_slot.markdown(render_pipeline(states_from(results, running, error)), unsafe_allow_html=True)

        current = "search"
        try:
            # Step 1: Search
            update("search")
            with st.spinner("🔍  Search Agent is working…"):
                sr = build_search_agent().invoke({
                    "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
                })
                results["search"] = sr["messages"][-1].content

            # Step 2: Reader
            current = "reader"
            update("reader")
            with st.spinner("📄  Reader Agent is scraping top resources…"):
                rr = build_reader_agent().invoke({
                    "messages": [("user",
                        f"Based on the following search results about '{topic_val}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{results['search'][:800]}"
                    )]
                })
                results["reader"] = rr["messages"][-1].content

            # Step 3: Writer
            current = "writer"
            update("writer")
            with st.spinner("✍️  Writer is drafting the report…"):
                research_combined = (
                    f"SEARCH RESULTS:\n{results['search']}\n\n"
                    f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
                )
                results["writer"] = writer_chain.invoke({"topic": topic_val, "research": research_combined})

            # Step 4: Critic
            current = "critic"
            update("critic")
            with st.spinner("🧐  Critic is reviewing the report…"):
                results["critic"] = critic_chain.invoke({"report": results["writer"]})

            update()
            st.toast("Research report ready!", icon="✅")
        except Exception as exc:  # noqa: BLE001
            update(error=current)
            st.error(f"The {current} step failed: {exc}")
        finally:
            st.session_state.results = dict(results)


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Output</div><div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "writer" in r:
        with st.container(key="report_panel"):
            st.markdown('<div class="panel-label orange">📝 Final Research Report</div>', unsafe_allow_html=True)
            st.markdown(r["writer"])
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        with st.container(key="feedback_panel"):
            st.markdown('<div class="panel-label green">🧐 Critic Feedback</div>', unsafe_allow_html=True)
            st.markdown(r["critic"])


# ── How it works (scroll section) ─────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section-block">
    <div class="eyebrow">Under the hood</div>
    <div class="section-heading">How it works</div>
</div>

<div class="feat-grid">
    <div class="feat"><div class="big">01</div><span class="ico">🔍</span><h4>Search</h4>
        <p>An agent queries the web for fresh, reliable sources on your topic.</p></div>
    <div class="feat"><div class="big">02</div><span class="ico">📄</span><h4>Read</h4>
        <p>The best link is scraped to pull out deep, detailed content.</p></div>
    <div class="feat"><div class="big">03</div><span class="ico">✍️</span><h4>Write</h4>
        <p>A writer chain turns raw research into a structured report.</p></div>
    <div class="feat"><div class="big">04</div><span class="ico">🧐</span><h4>Critique</h4>
        <p>A critic reviews and scores the draft so you know its quality.</p></div>
</div>

<div class="stats">
    <div class="stat"><b data-count="4">4</b><span>Specialized agents</span></div>
    <div class="stat"><b data-count="1">1</b><span>Click to run</span></div>
    <div class="stat"><b data-count="100" data-suffix="%">100%</b><span>Markdown export</span></div>
</div>

<div class="notice">ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit</div>
""", unsafe_allow_html=True)