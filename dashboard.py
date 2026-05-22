import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import joblib
import shap
import os
import re
import io
import base64
import time
import random
import math
import string
from datetime import datetime, timedelta
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

# ── Gemini AI Import ─────────────────────────────────────
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    pass

st.set_page_config(
    page_title="Cyber Sentinel AI — Intrusion Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Login ─────────────────────────────────────────────────
USERNAME = "admin"
PASSWORD = "cyber2024"

def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 40%, #1b2838 70%, #0a0e1a 100%);
            font-family: 'Inter', sans-serif;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .block-container {
            padding-top: 1rem !important;
        }
        h1, h2, h3 { color: #00d4ff !important; font-family: 'Inter', sans-serif; }
        .stTextInput input {
            background-color: rgba(26, 31, 53, 0.8) !important;
            border: 1px solid rgba(0, 212, 255, 0.4) !important;
            color: white !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px);
            padding: 12px !important;
            font-family: 'Inter', sans-serif;
        }
        .stTextInput input:focus {
            border-color: #00d4ff !important;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3) !important;
        }
        .stButton button {
            background: linear-gradient(135deg, #00d4ff, #0099cc) !important;
            color: #0a0e1a !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            width: 100%;
            padding: 12px !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            font-family: 'Inter', sans-serif;
        }
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4) !important;
        }
        .login-container {
            background: rgba(13, 17, 23, 0.7);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 24px;
            padding: 40px;
            margin-top: 10px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        .login-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .login-subtitle {
            text-align: center;
            color: #8899aa;
            font-size: 1rem;
            margin-bottom: 30px;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        .shield-icon {
            text-align: center;
            font-size: 4rem;
            animation: float 3s ease-in-out infinite;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            # BMSIT College Branding (text-based)
            st.markdown("""
            <div style='text-align:center;margin-bottom:20px;'>
                <div style='font-size:2rem;font-weight:800;color:#00d4ff;letter-spacing:3px;
                            text-shadow:0 0 20px rgba(0,212,255,0.3);'>
                    BMS
                </div>
                <div style='color:#c0ccdd;font-size:0.75rem;font-weight:600;letter-spacing:2.5px;
                            margin-top:2px;line-height:1.5;'>
                    INSTITUTE OF TECHNOLOGY<br>& MANAGEMENT
                </div>
                <div style='color:#556677;font-size:0.65rem;margin-top:6px;letter-spacing:1.5px;'>
                    BENGALURU • AUTONOMOUS • NAAC 'A' GRADE
                </div>
                <div style='width:60px;height:2px;background:linear-gradient(90deg,transparent,#00d4ff,transparent);
                            margin:16px auto 0 auto;border-radius:2px;'></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="shield-icon">🛡️</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-title">Cyber Sentinel AI</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Advanced Intrusion Detection System</div>', unsafe_allow_html=True)
            st.markdown("---")
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            if st.button("🔐 Login"):
                if username == USERNAME and password == PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.section = "overview"
                    st.rerun()
                else:
                    st.error("❌ Wrong username or password!")
            st.markdown(
                "<p style='text-align:center;color:#556677;font-size:12px;margin-top:20px'>"
                "Default credentials: admin / cyber2024</p>",
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

check_login()

# ── Main App Styling ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 40%, #1b2838 70%, #0a0e1a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Title */
    h1 {
        background: linear-gradient(135deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        text-align: center;
        padding: 20px 0;
        margin-bottom: 10px;
        font-family: 'Inter', sans-serif;
    }
    h2, h3 {
        color: #00d4ff !important;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism cards */
    [data-testid="metric-container"] {
        background: rgba(26, 31, 53, 0.6);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    [data-testid="metric-container"]:hover {
        border-color: rgba(0, 212, 255, 0.6);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
        transform: translateY(-4px);
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8899aa !important;
        font-weight: 500 !important;
    }

    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(26, 31, 53, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        color: white !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #0a0e1a 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    section[data-testid="stSidebar"] .stButton button {
        background: transparent !important;
        color: #8899aa !important;
        border: none !important;
        text-align: left !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        width: 100%;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif;
        font-size: 14px !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(0, 212, 255, 0.1) !important;
        color: #00d4ff !important;
        border-left: 3px solid #00d4ff !important;
    }

    /* Main buttons */
    .stButton button {
        background: linear-gradient(135deg, #00d4ff, #0099cc) !important;
        color: #0a0e1a !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 10px 28px !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif;
    }
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(13, 17, 23, 0.5);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #8899aa;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 212, 255, 0.15) !important;
        color: #00d4ff !important;
    }

    /* Custom glass card */
    .glass-card {
        background: rgba(26, 31, 53, 0.5);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .glass-card-green {
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
    }
    .glass-card-red {
        background: rgba(255, 68, 68, 0.05);
        border: 1px solid rgba(255, 68, 68, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
    }
    .glass-card-yellow {
        background: rgba(255, 170, 0, 0.05);
        border: 1px solid rgba(255, 170, 0, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
    }

    /* Section header */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00d4ff;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-description {
        color: #8899aa;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    /* Status indicator */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .status-live {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00ff88;
        animation: pulse 2s ease-in-out infinite;
        margin-right: 6px;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }

    /* Severity badges */
    .badge-high {
        background: rgba(255, 68, 68, 0.2);
        color: #ff4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(255, 68, 68, 0.3);
    }
    .badge-medium {
        background: rgba(255, 170, 0, 0.2);
        color: #ffaa00;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(255, 170, 0, 0.3);
    }
    .badge-low {
        background: rgba(0, 212, 255, 0.2);
        color: #00d4ff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    .badge-safe {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(0, 255, 136, 0.3);
    }

    /* Chat messages */
    .chat-bot {
        background: rgba(0, 212, 255, 0.08);
        border-left: 3px solid #00d4ff;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 8px 0;
        color: #e0e0e0;
    }
    .chat-user {
        background: rgba(0, 255, 136, 0.08);
        border-right: 3px solid #00ff88;
        border-radius: 12px 0 0 12px;
        padding: 16px 20px;
        margin: 8px 0;
        color: #e0e0e0;
        text-align: right;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Divider */
    hr {
        border-color: rgba(0, 212, 255, 0.15) !important;
        margin: 20px 0 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(26, 31, 53, 0.5) !important;
        border-radius: 10px !important;
        color: #00d4ff !important;
        font-family: 'Inter', sans-serif;
    }

    /* Knowledge base cards */
    .kb-card {
        background: rgba(26, 31, 53, 0.5);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    .kb-card:hover {
        border-color: rgba(0, 212, 255, 0.4);
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
    }
    .kb-title {
        color: #00d4ff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .kb-desc {
        color: #8899aa;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Risk gauge */
    .risk-gauge {
        text-align: center;
        padding: 20px;
    }
    .risk-score-big {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 10px 0;
    }
    .risk-label {
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #445566;
        font-size: 12px;
        padding: 20px;
        font-family: 'Inter', sans-serif;
    }

    /* Password strength meter */
    .strength-meter {
        height: 8px;
        border-radius: 4px;
        margin: 8px 0;
        transition: all 0.5s ease;
    }
    .strength-label {
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 1px;
    }

    /* Active nav highlight */
    .nav-active {
        background: rgba(0, 212, 255, 0.12) !important;
        border-left: 3px solid #00d4ff !important;
        color: #00d4ff !important;
        font-weight: 600 !important;
    }

    /* Architecture diagram */
    .arch-box {
        background: rgba(26, 31, 53, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.25);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        color: #ccc;
        transition: all 0.3s ease;
    }
    .arch-box:hover {
        border-color: #00d4ff;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15);
    }
    .arch-arrow {
        color: #00d4ff;
        font-size: 1.5rem;
        text-align: center;
        padding: 4px 0;
    }

    /* Live monitor */
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    .live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #ff4444;
        animation: blink 1s ease-in-out infinite;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ───────────────────────────────────
if 'section' not in st.session_state:
    st.session_state.section = "overview"

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px 0;'>
        <div style='font-size:2rem;margin-bottom:5px;'>🛡️</div>
        <div style='font-size:1.1rem;font-weight:700;
            background:linear-gradient(135deg,#00d4ff,#00ff88);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            Cyber Sentinel AI
        </div>
        <div style='color:#556677;font-size:0.75rem;margin-top:4px;'>v2.0 — IDS Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # User info
    st.markdown(f"""
    <div style='background:rgba(0,212,255,0.05);border-radius:10px;padding:12px;margin-bottom:10px;'>
        <div style='color:#8899aa;font-size:0.8rem;'>Logged in as</div>
        <div style='color:#fff;font-weight:600;'>👤 admin</div>
        <div style='margin-top:8px;'>
            <span class='status-live'></span>
            <span style='color:#00ff88;font-size:0.85rem;font-weight:500;'>System Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<div style='color:#556677;font-size:0.75rem;font-weight:600;letter-spacing:1px;margin-bottom:8px;'>NAVIGATION</div>", unsafe_allow_html=True)

    nav_items = {
        "📊 Overview": "overview",
        "📡 Live Monitor": "live_monitor",
        "⚔️ Attack Analysis": "analysis",
        "🧠 XAI Explanation": "xai",
        "🚨 Recent Alerts": "alerts",
        "🍯 Honeypot Log": "honeypot",
        "📁 File Upload Analyzer": "file_upload",
        "🔍 URL Scanner": "url",
        "🔑 Password Checker": "password",
        "📚 Threat Knowledge": "knowledge",
        "🤖 AI Chatbot": "chatbot",
        "🧪 Packet Tester": "packet_tester",
        "📋 Audit Log": "audit_log",
        "🏆 Security Score": "security_score",
        "🧠 Security Quiz": "quiz",
        "#️⃣ Hash Checker": "hash_checker",
        "🌐 Port Scanner": "port_scanner",
        "🔐 Encryption Tool": "encryption",
        "ℹ️ About Project": "about",
    }

    for label, key in nav_items.items():
        is_active = st.session_state.section == key
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, use_container_width=True, key=f"nav_{key}", type=btn_type):
            st.session_state.section = key
            st.rerun()

    st.markdown("---")

    # Gemini API key config
    st.markdown("<div style='color:#556677;font-size:0.75rem;font-weight:600;letter-spacing:1px;margin-bottom:8px;'>AI SETTINGS</div>", unsafe_allow_html=True)
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="Enter key for AI chatbot", key="gemini_key_input", help="Get free at aistudio.google.com/apikey")
    if gemini_key:
        st.session_state.gemini_api_key = gemini_key
        st.markdown("<span style='color:#00ff88;font-size:0.8rem;'>✅ API Key Set</span>", unsafe_allow_html=True)
    elif 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

    st.markdown("---")

    # ── Beginner Mode Toggle ──
    st.markdown("<div style='color:#556677;font-size:0.75rem;font-weight:600;letter-spacing:1px;margin-bottom:8px;'>DISPLAY MODE</div>", unsafe_allow_html=True)
    beginner_mode = st.toggle("🎓 Beginner Mode", value=st.session_state.get('beginner_mode', False), key="beginner_mode_toggle", help="Simplifies labels and adds explanations throughout the dashboard")
    st.session_state.beginner_mode = beginner_mode
    if beginner_mode:
        st.markdown("<span style='color:#00ff88;font-size:0.8rem;'>✅ Simplified view active</span>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

# ── Audit Log init ───────────────────────────────────────
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []

def log_action(action, detail=""):
    st.session_state.audit_log.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'action': action,
        'detail': detail,
        'section': st.session_state.get('section', 'overview')
    })

log_action("Page Load", f"Section: {st.session_state.get('section','overview')}")

# ── Load Model ────────────────────────────────────────────
st.title("🛡️ Cyber Sentinel AI — Intrusion Detection System")
st.markdown("<p style='text-align:center;color:#556677;margin-top:-10px;margin-bottom:20px;'>Advanced AI-Powered Network Security Monitoring & Threat Intelligence</p>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_resource
def load_model():
    model = joblib.load('model/ids_model.pkl')
    feature_names = joblib.load('model/feature_names.pkl')
    return model, feature_names

model, feature_names = load_model()

@st.cache_data
def load_data_and_predict(_model):
    X_test = pd.read_csv('model/X_test.csv')
    y_test = pd.read_csv('model/y_test.csv').squeeze()
    y_pred = _model.predict(X_test)
    total = len(y_pred)
    attacks = sum(1 for p in y_pred if p == 'attack')
    normal = total - attacks
    accuracy = sum(1 for p, a in zip(y_pred, y_test) if p == a) / total * 100
    precision = precision_score(y_test, y_pred, pos_label='attack', zero_division=0) * 100
    recall = recall_score(y_test, y_pred, pos_label='attack', zero_division=0) * 100
    f1 = f1_score(y_test, y_pred, pos_label='attack', zero_division=0) * 100
    return X_test, y_test, y_pred, total, attacks, normal, accuracy, precision, recall, f1

X_test, y_test, y_pred, total, attacks, normal, accuracy, precision, recall, f1 = load_data_and_predict(model)

# ══════════════════════════════════════════════════════════
#                       OVERVIEW
# ══════════════════════════════════════════════════════════
if st.session_state.section == "overview":
    st.markdown("<div class='section-header'>📊 System Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Real-time monitoring dashboard showing network traffic analysis and threat detection metrics.</div>", unsafe_allow_html=True)

    # ── Key Metrics ──
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Packets Analyzed", f"{total:,}", help="Total network packets processed by the IDS model")
    col2.metric("⚠️ Attacks Detected", f"{attacks:,}", delta=f"{attacks/total*100:.1f}%", delta_color="inverse")
    col3.metric("✅ Normal Traffic", f"{normal:,}", delta=f"{normal/total*100:.1f}%")
    col4.metric("🎯 Model Accuracy", f"{accuracy:.2f}%")

    # ── Risk Score Banner ──
    risk_score = (attacks / total) * 100
    if risk_score < 30:
        risk_color = "#00ff88"
        risk_bg    = "rgba(0, 255, 136, 0.07)"
        risk_border= "rgba(0, 255, 136, 0.3)"
        risk_icon  = "🟢"
        risk_status= "LOW RISK"
    elif risk_score < 70:
        risk_color = "#ffaa00"
        risk_bg    = "rgba(255, 170, 0, 0.07)"
        risk_border= "rgba(255, 170, 0, 0.3)"
        risk_icon  = "🟡"
        risk_status= "MEDIUM RISK"
    else:
        risk_color = "#ff4444"
        risk_bg    = "rgba(255, 68, 68, 0.07)"
        risk_border= "rgba(255, 68, 68, 0.3)"
        risk_icon  = "🔴"
        risk_status= "HIGH RISK"

    st.markdown(f"""
    <div style='background:{risk_bg};border:1.5px solid {risk_border};border-radius:16px;
                padding:20px 28px;margin:16px 0;display:flex;align-items:center;
                justify-content:space-between;flex-wrap:wrap;gap:16px;
                box-shadow:0 4px 24px rgba(0,0,0,0.2);'>
        <div style='display:flex;align-items:center;gap:14px;'>
            <div style='font-size:2.4rem;line-height:1;'>{risk_icon}</div>
            <div>
                <div style='color:#8899aa;font-size:0.75rem;font-weight:600;
                            letter-spacing:1.5px;text-transform:uppercase;'>System Risk Level</div>
                <div style='color:{risk_color};font-size:1.8rem;font-weight:800;
                            letter-spacing:1px;margin-top:2px;'>{risk_status}</div>
            </div>
        </div>
        <div style='flex:1;min-width:220px;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
                <span style='color:#8899aa;font-size:0.8rem;'>Risk Score</span>
                <span style='color:{risk_color};font-weight:700;font-size:0.95rem;'>{risk_score:.2f}%</span>
            </div>
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;height:10px;overflow:hidden;'>
                <div style='width:{risk_score:.1f}%;height:100%;
                            background:linear-gradient(90deg,{risk_color}88,{risk_color});
                            border-radius:8px;transition:width 0.6s ease;'></div>
            </div>
            <div style='display:flex;justify-content:space-between;margin-top:4px;'>
                <span style='color:#556677;font-size:0.7rem;'>0%</span>
                <span style='color:#556677;font-size:0.7rem;'>100%</span>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:#8899aa;font-size:0.75rem;'>Attack Ratio</div>
            <div style='color:#ffffff;font-weight:700;font-size:1.1rem;'>
                {attacks:,} / {total:,}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── System Status & Model Performance ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
        <div class='glass-card'>
            <div style='color:#00d4ff;font-weight:700;font-size:1.1rem;margin-bottom:16px;'>
                ⚡ System Status
            </div>
            <table style='width:100%;color:#ccc;'>
                <tr><td style='padding:8px 0;color:#8899aa;'>Status</td>
                    <td style='text-align:right;'><span class='status-live'></span> <span style='color:#00ff88;font-weight:600;'>Online</span></td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Model</td>
                    <td style='text-align:right;font-weight:500;'>Random Forest (100 trees)</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Dataset</td>
                    <td style='text-align:right;font-weight:500;'>NSL-KDD</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Features</td>
                    <td style='text-align:right;font-weight:500;'>""" + str(len(feature_names)) + """ features</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Classification</td>
                    <td style='text-align:right;font-weight:500;'>Binary (Normal / Attack)</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Last Updated</td>
                    <td style='text-align:right;font-weight:500;'>""" + datetime.now().strftime('%Y-%m-%d %H:%M') + """</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class='glass-card'>
            <div style='color:#00d4ff;font-weight:700;font-size:1.1rem;margin-bottom:16px;'>
                📈 Model Performance
            </div>
        </div>
        """, unsafe_allow_html=True)
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        perf_col1.metric("Precision", f"{precision:.1f}%", help="How many detected attacks are real attacks")
        perf_col2.metric("Recall", f"{recall:.1f}%", help="How many real attacks were detected")
        perf_col3.metric("F1 Score", f"{f1:.1f}%", help="Harmonic mean of precision and recall")

    st.markdown("---")

    # ── Traffic Summary & Security Tips ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🔥 Threat Summary")
        # Attack severity breakdown
        attack_indices = [i for i, p in enumerate(y_pred) if p == 'attack']
        high_sev = sum(1 for i in attack_indices if X_test.iloc[i]['src_bytes'] > 5000)
        med_sev = sum(1 for i in attack_indices if 500 < X_test.iloc[i]['src_bytes'] <= 5000)
        low_sev = len(attack_indices) - high_sev - med_sev

        fig_threat, ax_threat = plt.subplots(figsize=(5, 3.5))
        fig_threat.patch.set_facecolor('#0d1117')
        ax_threat.set_facecolor('#0d1117')

        categories = ['HIGH', 'MEDIUM', 'LOW']
        values = [high_sev, med_sev, low_sev]
        colors = ['#ff4444', '#ffaa00', '#00d4ff']
        bars = ax_threat.barh(categories, values, color=colors, height=0.5, edgecolor='none')
        for bar, val in zip(bars, values):
            ax_threat.text(bar.get_width() + max(values)*0.02, bar.get_y() + bar.get_height()/2,
                          f'{val:,}', ha='left', va='center', color='white', fontsize=11, fontweight='bold')
        ax_threat.set_xlabel('Count', color='#8899aa', fontsize=10)
        ax_threat.tick_params(colors='#8899aa')
        ax_threat.spines['top'].set_visible(False)
        ax_threat.spines['right'].set_visible(False)
        ax_threat.spines['bottom'].set_color('#2a3040')
        ax_threat.spines['left'].set_color('#2a3040')
        ax_threat.set_xlim(0, max(values)*1.25)
        plt.tight_layout()
        st.pyplot(fig_threat)

    with col_b:
        st.markdown("#### 🔒 Security Tips")
        tips = [
            "🔑 **Use Strong Passwords** — Minimum 12 characters with mixed case, numbers, and symbols. Consider a password manager.",
            "🛡️ **Enable 2FA** — Two-factor authentication blocks 99.9% of automated attacks even if passwords are compromised.",
            "📧 **Beware of Phishing** — Never click links in unexpected emails. Always verify the sender before opening attachments.",
            "🔄 **Keep Software Updated** — Security patches fix known vulnerabilities. Enable auto-updates on all devices.",
            "📡 **Avoid Public WiFi** — Use a VPN when connecting to public networks. Attackers can intercept unencrypted data.",
            "💾 **Regular Backups** — Follow the 3-2-1 rule: 3 copies, 2 different media, 1 offsite backup.",
            "🔍 **Monitor Network Traffic** — Unusual spikes in traffic can indicate DDoS attacks or data exfiltration.",
            "🚫 **Principle of Least Privilege** — Only give users the minimum access they need to do their job.",
        ]
        for tip in random.sample(tips, 4):
            st.markdown(f"""<div class='glass-card' style='padding:14px 18px;margin:6px 0;'>
                <span style='color:#ccc;font-size:0.9rem;'>{tip}</span>
            </div>""", unsafe_allow_html=True)

    # ── Recent Activity Feed ──
    st.markdown("---")
    st.markdown("#### 📋 Recent Detection Activity")
    recent_attacks = [i for i, p in enumerate(y_pred) if p == 'attack'][:5]
    recent_normal = [i for i, p in enumerate(y_pred) if p == 'normal'][:3]

    activity_items = []
    for i in recent_attacks:
        row = X_test.iloc[i]
        sev = "HIGH" if row['src_bytes'] > 5000 else ("MEDIUM" if row['src_bytes'] > 500 else "LOW")
        badge_class = f"badge-{'high' if sev == 'HIGH' else 'medium' if sev == 'MEDIUM' else 'low'}"
        activity_items.append(f"""
        <div class='glass-card' style='padding:12px 18px;margin:5px 0;display:flex;justify-content:space-between;align-items:center;'>
            <div>
                <span style='color:#ff4444;font-weight:600;'>⚠️ Attack Detected</span>
                <span style='color:#556677;margin-left:10px;'>src_bytes: {int(row['src_bytes'])} | duration: {int(row['duration'])}s | connections: {int(row['count'])}</span>
            </div>
            <span class='{badge_class}'>{sev}</span>
        </div>
        """)

    for i in recent_normal[:2]:
        activity_items.append(f"""
        <div class='glass-card' style='padding:12px 18px;margin:5px 0;'>
            <span style='color:#00ff88;font-weight:600;'>✅ Normal Traffic</span>
            <span style='color:#556677;margin-left:10px;'>Packet #{i+1} cleared</span>
        </div>
        """)

    for item in activity_items:
        st.markdown(item, unsafe_allow_html=True)

    # ── Simulate Attack ──
    st.markdown("---")
    st.markdown("#### 🚨 Attack Simulation")
    st.markdown("<div class='section-description'>Inject a synthetic DDoS packet to test the dashboard's detection response.</div>", unsafe_allow_html=True)

    sim_col, _ = st.columns([1, 3])
    with sim_col:
        if st.button("🚨 Simulate Attack", key="simulate_attack_btn", use_container_width=True):
            fake_attack = {
                'src_bytes': random.randint(6000, 20000),
                'dst_bytes': random.randint(0, 1000),
                'duration': random.randint(1, 10),
                'count': random.randint(100, 500)
            }
            st.session_state.simulated_attack = fake_attack

    if 'simulated_attack' in st.session_state:
        fa = st.session_state.simulated_attack
        st.warning("⚠️ Simulated DDoS Attack Triggered!")
        st.markdown(f"""
        <div class='glass-card-red' style='margin-top:10px;'>
            <div style='color:#ff4444;font-weight:700;font-size:1.05rem;margin-bottom:12px;'>
                🔴 SIMULATED ATTACK PACKET — HIGH SEVERITY
            </div>
            <div style='display:flex;gap:32px;flex-wrap:wrap;'>
                <div>
                    <div style='color:#8899aa;font-size:0.8rem;'>SRC BYTES</div>
                    <div style='color:#ffffff;font-weight:700;font-size:1.3rem;'>{fa['src_bytes']:,}</div>
                </div>
                <div>
                    <div style='color:#8899aa;font-size:0.8rem;'>DST BYTES</div>
                    <div style='color:#ffffff;font-weight:700;font-size:1.3rem;'>{fa['dst_bytes']:,}</div>
                </div>
                <div>
                    <div style='color:#8899aa;font-size:0.8rem;'>DURATION</div>
                    <div style='color:#ffffff;font-weight:700;font-size:1.3rem;'>{fa['duration']}s</div>
                </div>
                <div>
                    <div style='color:#8899aa;font-size:0.8rem;'>CONNECTIONS</div>
                    <div style='color:#ffffff;font-weight:700;font-size:1.3rem;'>{fa['count']}</div>
                </div>
                <div>
                    <div style='color:#8899aa;font-size:0.8rem;'>VERDICT</div>
                    <div style='color:#ff4444;font-weight:700;font-size:1.3rem;'>⚠️ ATTACK</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🧹 Clear Simulation", key="clear_sim_btn"):
            del st.session_state.simulated_attack
            st.rerun()

    # ── Attack Trend Chart ──
    st.markdown("---")
    st.markdown("#### 📈 Live Attack Trend")
    st.markdown("<div class='section-description'>Simulated rolling window of attack vs normal traffic over time.</div>", unsafe_allow_html=True)

    if 'trend_data' not in st.session_state:
        st.session_state.trend_data = []

    # Add new data point each render
    now_str = datetime.now().strftime('%H:%M:%S')
    window_attacks = sum(1 for p in y_pred[random.randint(0, max(1, total-200)):random.randint(1, total)] if p == 'attack')
    new_point = {
        'time': now_str,
        'attacks': random.randint(int(attacks/total*180), int(attacks/total*220)),
        'normal': random.randint(int(normal/total*180), int(normal/total*220))
    }
    st.session_state.trend_data.append(new_point)
    if len(st.session_state.trend_data) > 20:
        st.session_state.trend_data = st.session_state.trend_data[-20:]

    trend_df = pd.DataFrame(st.session_state.trend_data)
    fig_trend, ax_trend = plt.subplots(figsize=(12, 3))
    fig_trend.patch.set_facecolor('#0d1117')
    ax_trend.set_facecolor('#0d1117')
    if len(trend_df) > 1:
        ax_trend.plot(trend_df['time'], trend_df['attacks'], color='#ff4444', linewidth=2,
                      marker='o', markersize=4, label='Attacks')
        ax_trend.fill_between(range(len(trend_df)), trend_df['attacks'],
                              alpha=0.15, color='#ff4444')
        ax_trend.plot(trend_df['time'], trend_df['normal'], color='#00d4ff', linewidth=2,
                      marker='o', markersize=4, label='Normal')
        ax_trend.fill_between(range(len(trend_df)), trend_df['normal'],
                              alpha=0.1, color='#00d4ff')
        ax_trend.set_xticks(range(len(trend_df)))
        ax_trend.set_xticklabels(trend_df['time'], rotation=30, ha='right', fontsize=7)
    ax_trend.tick_params(colors='#8899aa')
    ax_trend.spines['top'].set_visible(False)
    ax_trend.spines['right'].set_visible(False)
    ax_trend.spines['bottom'].set_color('#2a3040')
    ax_trend.spines['left'].set_color('#2a3040')
    ax_trend.legend(facecolor='#1a1f35', edgecolor='#2a3040', labelcolor='white', fontsize=9)
    ax_trend.set_ylabel('Packets', color='#8899aa', fontsize=9)
    plt.tight_layout()
    st.pyplot(fig_trend)

    # ── Live Auto-Refresh ──
    st.markdown("---")
    st.markdown("#### ⚡ Live Mode")
    rf_col1, rf_col2 = st.columns([1, 3])
    with rf_col1:
        auto_refresh = st.toggle("🔴 Auto-Refresh", value=st.session_state.get('auto_refresh', False), key="auto_refresh_toggle")
        st.session_state.auto_refresh = auto_refresh
    with rf_col2:
        refresh_interval = st.select_slider("Refresh every", options=[2, 3, 5, 10, 15, 30],
                                             value=st.session_state.get('refresh_interval', 5),
                                             key="refresh_interval_slider",
                                             format_func=lambda x: f"{x}s")
        st.session_state.refresh_interval = refresh_interval

    if auto_refresh:
        st.markdown(f"""<div style='display:flex;align-items:center;gap:8px;color:#00ff88;font-size:0.9rem;'>
            <span class='live-dot'></span> Live — refreshing every {refresh_interval}s
        </div>""", unsafe_allow_html=True)
        log_action("Auto-Refresh", f"Interval: {refresh_interval}s")
        time.sleep(refresh_interval)
        st.rerun()
    else:
        st.markdown("<span style='color:#556677;font-size:0.85rem;'>⏸ Auto-refresh is off — toggle to enable live updates</span>", unsafe_allow_html=True)


    # ── Security Score Card ──
    st.markdown("---")
    st.markdown("#### 🏆 System Security Score Card")

    # Calculate score (0-100, higher = more secure)
    attack_ratio = attacks / total * 100
    sec_score = max(0, min(100, int(
        (accuracy * 0.35) +
        ((100 - attack_ratio) * 0.25) +
        (precision * 0.20) +
        (f1 * 0.20)
    )))

    if sec_score >= 90:   grade, g_color, g_desc = "A+", "#00ff88", "Excellent — System is highly secure"
    elif sec_score >= 80: grade, g_color, g_desc = "A",  "#00ff88", "Very Good — Strong protection active"
    elif sec_score >= 70: grade, g_color, g_desc = "B",  "#00d4ff", "Good — Minor vulnerabilities present"
    elif sec_score >= 60: grade, g_color, g_desc = "C",  "#ffaa00", "Average — Attention recommended"
    elif sec_score >= 50: grade, g_color, g_desc = "D",  "#ff8800", "Poor — Multiple threats detected"
    else:                 grade, g_color, g_desc = "F",  "#ff4444", "Critical — Immediate action required"

    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    categories = [
        ("Accuracy",  f"{accuracy:.1f}%",  "#00ff88" if accuracy > 90 else "#ffaa00"),
        ("Precision", f"{precision:.1f}%", "#00ff88" if precision > 90 else "#ffaa00"),
        ("Recall",    f"{recall:.1f}%",    "#00ff88" if recall > 90 else "#ffaa00"),
        ("F1 Score",  f"{f1:.1f}%",        "#00ff88" if f1 > 90 else "#ffaa00"),
        ("Threat Level", f"{attack_ratio:.1f}%", "#ff4444" if attack_ratio > 50 else "#ffaa00"),
    ]
    for col, (label, val, col_c) in zip([sc1,sc2,sc3,sc4,sc5], categories):
        col.markdown(f"<div style='background:rgba(26,31,53,0.6);border:1px solid rgba(0,212,255,0.2);"
                     f"border-radius:12px;padding:14px;text-align:center;'>"
                     f"<div style='color:#8899aa;font-size:0.75rem;'>{label}</div>"
                     f"<div style='color:{col_c};font-size:1.3rem;font-weight:700;'>{val}</div>"
                     f"</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:rgba(26,31,53,0.6);border:2px solid {g_color}44;
                border-radius:18px;padding:22px 30px;margin:16px 0;
                display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;'>
        <div style='display:flex;align-items:center;gap:20px;'>
            <div style='font-size:4rem;font-weight:900;color:{g_color};
                        text-shadow:0 0 30px {g_color}66;'>{grade}</div>
            <div>
                <div style='color:#8899aa;font-size:0.75rem;letter-spacing:2px;'>SECURITY GRADE</div>
                <div style='color:{g_color};font-size:1.3rem;font-weight:700;'>{g_desc}</div>
            </div>
        </div>
        <div style='min-width:220px;flex:1;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
                <span style='color:#8899aa;font-size:0.8rem;'>Overall Score</span>
                <span style='color:{g_color};font-weight:700;'>{sec_score}/100</span>
            </div>
            <div style='background:rgba(255,255,255,0.07);border-radius:8px;height:14px;overflow:hidden;'>
                <div style='width:{sec_score}%;height:100%;
                            background:linear-gradient(90deg,{g_color}88,{g_color});
                            border-radius:8px;'></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                    ATTACK ANALYSIS
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "analysis":
    st.markdown("<div class='section-header'>⚔️ Attack Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Comprehensive visualization of network traffic patterns, attack distribution, and model prediction performance.</div>", unsafe_allow_html=True)

    # ── Traffic Distribution & Count ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### 🥧 Traffic Distribution")
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        fig1.patch.set_facecolor('#0d1117')
        ax1.set_facecolor('#0d1117')
        wedges, texts, autotexts = ax1.pie(
            [normal, attacks],
            labels=['Normal', 'Attack'],
            colors=['#00d4ff', '#ff4444'],
            autopct='%1.1f%%', startangle=90,
            textprops={'color': 'white', 'fontsize': 12},
            wedgeprops={'edgecolor': '#0d1117', 'linewidth': 2},
            shadow=False
        )
        for t in autotexts:
            t.set_fontweight('bold')
        ax1.axis('equal')
        st.pyplot(fig1)

    with col_right:
        st.markdown("##### 📊 Normal vs Attack Count")
        pred_series = pd.Series(y_pred)
        counts = pred_series.value_counts()
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor('#0d1117')
        ax2.set_facecolor('#0d1117')
        bars = ax2.bar(counts.index, counts.values, color=['#00d4ff', '#ff4444'],
                       edgecolor='none', width=0.5)
        ax2.set_ylabel("Count", color='#8899aa', fontsize=11)
        ax2.tick_params(colors='#8899aa')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color('#2a3040')
        ax2.spines['left'].set_color('#2a3040')
        for bar, val in zip(bars, counts.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts.values)*0.02,
                     f'{val:,}', ha='center', fontsize=12, color='white', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig2)

    st.markdown("---")

    # ── Confusion Matrix & Attack Severity ──
    col_cm, col_sev = st.columns(2)

    with col_cm:
        st.markdown("##### 🎯 Confusion Matrix")
        cm = confusion_matrix(y_test, y_pred, labels=['normal', 'attack'])
        fig_cm, ax_cm = plt.subplots(figsize=(5, 4))
        fig_cm.patch.set_facecolor('#0d1117')
        ax_cm.set_facecolor('#0d1117')

        im = ax_cm.imshow(cm, cmap='Blues', alpha=0.8)
        ax_cm.set_xticks([0, 1])
        ax_cm.set_yticks([0, 1])
        ax_cm.set_xticklabels(['Normal', 'Attack'], color='#8899aa', fontsize=11)
        ax_cm.set_yticklabels(['Normal', 'Attack'], color='#8899aa', fontsize=11)
        ax_cm.set_xlabel('Predicted', color='#8899aa', fontsize=12)
        ax_cm.set_ylabel('Actual', color='#8899aa', fontsize=12)

        for i in range(2):
            for j in range(2):
                color = 'white' if cm[i, j] > cm.max()/2 else '#00d4ff'
                ax_cm.text(j, i, f'{cm[i, j]:,}', ha='center', va='center',
                          color=color, fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig_cm)

        st.markdown(f"""
        <div class='glass-card' style='padding:14px;'>
            <div style='color:#8899aa;font-size:0.85rem;'>
                ✅ <b>True Positives</b> (correctly detected attacks): <span style='color:#00ff88;'>{cm[1,1]:,}</span><br>
                ❌ <b>False Positives</b> (false alarms): <span style='color:#ffaa00;'>{cm[0,1]:,}</span><br>
                ✅ <b>True Negatives</b> (correctly cleared): <span style='color:#00ff88;'>{cm[0,0]:,}</span><br>
                ❌ <b>False Negatives</b> (missed attacks): <span style='color:#ff4444;'>{cm[1,0]:,}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_sev:
        st.markdown("##### 🚦 Attack Severity Distribution")
        attack_idx = [i for i, p in enumerate(y_pred) if p == 'attack']
        high = sum(1 for i in attack_idx if X_test.iloc[i]['src_bytes'] > 5000)
        med = sum(1 for i in attack_idx if 500 < X_test.iloc[i]['src_bytes'] <= 5000)
        low = len(attack_idx) - high - med

        fig_sev, ax_sev = plt.subplots(figsize=(5, 4))
        fig_sev.patch.set_facecolor('#0d1117')
        ax_sev.set_facecolor('#0d1117')
        sizes = [high, med, low]
        labels_sev = [f'High\n{high:,}', f'Medium\n{med:,}', f'Low\n{low:,}']
        colors_sev = ['#ff4444', '#ffaa00', '#00d4ff']
        explode = (0.05, 0.02, 0)
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax_sev.pie(
                sizes, labels=labels_sev, colors=colors_sev,
                autopct='%1.1f%%', startangle=140, explode=explode,
                textprops={'color': 'white', 'fontsize': 10},
                wedgeprops={'edgecolor': '#0d1117', 'linewidth': 2}
            )
            for t in autotexts:
                t.set_fontweight('bold')
        ax_sev.axis('equal')
        plt.tight_layout()
        st.pyplot(fig_sev)

        st.markdown(f"""
        <div class='glass-card' style='padding:14px;'>
            <div style='color:#8899aa;font-size:0.85rem;'>
                <b>Severity Criteria (by src_bytes):</b><br>
                🔴 <b>High</b>: > 5,000 bytes — Major data transfer floods<br>
                🟡 <b>Medium</b>: 500–5,000 bytes — Suspicious activity<br>
                🔵 <b>Low</b>: < 500 bytes — Minor probing attempts
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Feature Distribution Comparison ──
    st.markdown("##### 📊 Feature Distribution: Normal vs Attack")
    feature_to_compare = st.selectbox("Select feature to compare:", feature_names[:15], index=0)
    if feature_to_compare:
        normal_vals = X_test[y_pred == 'normal'][feature_to_compare]
        attack_vals = X_test[y_pred == 'attack'][feature_to_compare]

        fig_dist, ax_dist = plt.subplots(figsize=(10, 3.5))
        fig_dist.patch.set_facecolor('#0d1117')
        ax_dist.set_facecolor('#0d1117')
        ax_dist.hist(normal_vals, bins=50, alpha=0.6, color='#00d4ff', label='Normal', density=True, edgecolor='none')
        ax_dist.hist(attack_vals, bins=50, alpha=0.6, color='#ff4444', label='Attack', density=True, edgecolor='none')
        ax_dist.legend(facecolor='#1a1f35', edgecolor='#2a3040', labelcolor='white')
        ax_dist.set_xlabel(feature_to_compare, color='#8899aa')
        ax_dist.set_ylabel('Density', color='#8899aa')
        ax_dist.tick_params(colors='#8899aa')
        ax_dist.spines['top'].set_visible(False)
        ax_dist.spines['right'].set_visible(False)
        ax_dist.spines['bottom'].set_color('#2a3040')
        ax_dist.spines['left'].set_color('#2a3040')
        plt.tight_layout()
        st.pyplot(fig_dist)


# ══════════════════════════════════════════════════════════
#                    XAI EXPLANATION
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "xai":
    st.markdown("<div class='section-header'>🧠 Explainable AI (XAI)</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Understand why the AI model flags certain traffic as attacks using SHAP (SHapley Additive exPlanations) — a game-theory approach to explain ML predictions.</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Global Feature Importance", "🔍 Individual Prediction Explorer"])

    with tab1:
        with st.spinner("Calculating SHAP values... please wait"):
            try:
                sample = X_test.head(200)
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(sample)

                if isinstance(shap_values, list):
                    sv = np.array(shap_values[1])
                elif hasattr(shap_values, 'values'):
                    sv = np.array(shap_values.values)
                    if sv.ndim == 3:
                        sv = sv[:, :, 1]
                else:
                    sv = np.array(shap_values)
                    if sv.ndim == 3:
                        sv = sv[:, :, 1]

                mean_shap = np.abs(sv).mean(axis=0)
                min_len = min(len(feature_names), len(mean_shap))
                shap_df = pd.DataFrame({
                    'Feature': feature_names[:min_len],
                    'Importance': mean_shap[:min_len]
                }).sort_values('Importance', ascending=False).head(10)

                fig3, ax3 = plt.subplots(figsize=(10, 5))
                fig3.patch.set_facecolor('#0d1117')
                ax3.set_facecolor('#0d1117')

                colors = ['#ff4444' if v > shap_df['Importance'].median() else '#00d4ff'
                          for v in shap_df['Importance'][::-1]]
                bars = ax3.barh(shap_df['Feature'][::-1], shap_df['Importance'][::-1],
                               color=colors, edgecolor='none', height=0.6)
                ax3.set_xlabel("Mean |SHAP Value|", color='#8899aa', fontsize=12)
                ax3.set_title("Top 10 Features Influencing Attack Detection",
                             color='white', fontsize=14, fontweight='bold', pad=15)
                ax3.tick_params(colors='#8899aa')
                ax3.spines['top'].set_visible(False)
                ax3.spines['right'].set_visible(False)
                ax3.spines['bottom'].set_color('#2a3040')
                ax3.spines['left'].set_color('#2a3040')

                for bar in bars:
                    width = bar.get_width()
                    ax3.text(width + max(shap_df['Importance'])*0.02,
                            bar.get_y() + bar.get_height()/2,
                            f'{width:.4f}', ha='left', va='center',
                            color='white', fontsize=10)
                plt.tight_layout()
                st.pyplot(fig3)

                st.markdown("---")
                st.markdown("#### 📖 Feature Explanations")

                feature_explanations = {
                    'src_bytes': ('📤 Source Bytes', 'Amount of data sent from source — high values indicate flooding attacks like DDoS or data exfiltration attempts.'),
                    'dst_bytes': ('📥 Destination Bytes', 'Amount of data received at destination — unusual values indicate data theft, unauthorized downloads, or exfiltration.'),
                    'flag': ('🚩 Connection Flag', 'TCP connection status flag — abnormal flags (e.g., SYN floods, RST scans) indicate port scans or DoS attacks.'),
                    'logged_in': ('🔐 Login Status', 'Whether user was logged in — unauthorized login attempts and privilege escalation attacks.'),
                    'count': ('🔢 Connection Count', 'Number of connections to same host in last 2s — high count strongly indicates DoS/DDoS attack.'),
                    'same_srv_rate': ('📊 Same Service Rate', 'Rate of connections to same service — indicates targeted attacks on specific services.'),
                    'dst_host_srv_count': ('🏠 Dest Host Service Count', 'Number of connections to destination service — indicates systematic scanning behavior.'),
                    'dst_host_same_srv_rate': ('📈 Dest Host Same Service Rate', 'Rate of same service connections to destination host — reveals focused attack patterns.'),
                    'serror_rate': ('⚠️ SYN Error Rate', 'Rate of SYN errors — high rate indicates SYN flood attacks overwhelming the server.'),
                    'srv_serror_rate': ('⚠️ Service SYN Error Rate', 'SYN error rate for the service — indicates service-level SYN flood attacks.'),
                    'duration': ('⏱️ Connection Duration', 'Length of the connection — very long or very short connections can indicate anomalies.'),
                    'dst_host_count': ('🌐 Dest Host Count', 'Count of connections to the destination host — high values indicate scanning or flooding.'),
                    'srv_count': ('📡 Service Count', 'Number of connections to the same service in last 2s — high count means service flood.'),
                    'diff_srv_rate': ('🔀 Different Service Rate', 'Rate of connections to different services — high rate indicates port scanning.'),
                    'dst_host_diff_srv_rate': ('🔄 Dest Different Service Rate', 'Rate of different services to destination — indicates attacker probing multiple services.'),
                }

                for feat in shap_df['Feature'].head(5):
                    if feat in feature_explanations:
                        name, desc = feature_explanations[feat]
                        st.markdown(f"""
                        <div class='glass-card' style='padding:14px 18px;margin:6px 0;'>
                            <div style='color:#00d4ff;font-weight:600;'>{name} ({feat})</div>
                            <div style='color:#aabbcc;font-size:0.9rem;margin-top:4px;'>{desc}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='glass-card' style='padding:14px 18px;margin:6px 0;'>
                            <div style='color:#00d4ff;font-weight:600;'>{feat}</div>
                            <div style='color:#aabbcc;font-size:0.9rem;margin-top:4px;'>Network feature contributing to attack detection.</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Store for tab2
                st.session_state._shap_explainer = explainer
                st.session_state._shap_sv = sv
                st.session_state._shap_sample = sample

            except Exception as e:
                st.error(f"SHAP error: {e}")

    with tab2:
        st.markdown("#### 🔍 Explore Individual Predictions")
        st.markdown("Select a specific packet to understand why the model classified it as normal or attack.")

        sample_idx = st.slider("Select Packet Index", 0, min(199, len(X_test)-1), 0)
        sample_row = X_test.iloc[sample_idx]
        prediction = y_pred[sample_idx]
        actual = y_test.iloc[sample_idx] if sample_idx < len(y_test) else "Unknown"

        pred_color = "#ff4444" if prediction == "attack" else "#00ff88"
        actual_color = "#ff4444" if actual == "attack" else "#00ff88"
        match = "✅ Correct" if prediction == actual else "❌ Incorrect"

        st.markdown(f"""
        <div class='glass-card'>
            <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;'>
                <div>
                    <span style='color:#8899aa;'>Packet #{sample_idx + 1}</span>
                    <span style='margin-left:20px;color:#8899aa;'>Prediction: </span>
                    <span style='color:{pred_color};font-weight:700;font-size:1.1rem;'>{prediction.upper()}</span>
                    <span style='margin-left:20px;color:#8899aa;'>Actual: </span>
                    <span style='color:{actual_color};font-weight:700;'>{actual.upper()}</span>
                    <span style='margin-left:20px;'>{match}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Auto Response System ──
        if prediction == "attack":
            action_icon = "🔒"
            action_text = "IP Blocked Automatically"
            action_color = "#ff4444"
            action_bg = "rgba(255,68,68,0.08)"
            action_border = "rgba(255,68,68,0.3)"
            action_steps = [
                "🚫 Source IP flagged and added to blocklist",
                "📡 Traffic rate limiting applied to connection",
                "📧 Security team alert dispatched",
                "📝 Incident logged for forensic review",
            ]
        else:
            action_icon = "✅"
            action_text = "No Action Needed"
            action_color = "#00ff88"
            action_bg = "rgba(0,255,136,0.06)"
            action_border = "rgba(0,255,136,0.25)"
            action_steps = [
                "✅ Packet cleared as normal traffic",
                "📊 Flow logged for baselining",
            ]

        steps_html = "".join(f"<div style='margin:4px 0;color:#aabbcc;font-size:0.88rem;'>• {s}</div>" for s in action_steps)
        st.markdown(f"""
        <div style='background:{action_bg};border:1.5px solid {action_border};border-radius:14px;
                    padding:16px 22px;margin:14px 0;'>
            <div style='color:{action_color};font-weight:700;font-size:1.05rem;margin-bottom:10px;'>
                {action_icon} Auto-Response: {action_text}
            </div>
            {steps_html}
        </div>
        """, unsafe_allow_html=True)

        # Show key features for this packet
        col_feat1, col_feat2 = st.columns(2)
        key_features = ['duration', 'src_bytes', 'dst_bytes', 'count', 'flag', 'logged_in',
                       'same_srv_rate', 'serror_rate', 'srv_count', 'dst_host_srv_count']
        available_features = [f for f in key_features if f in sample_row.index]

        half = len(available_features) // 2
        with col_feat1:
            for feat in available_features[:half]:
                st.metric(feat, f"{sample_row[feat]:.2f}" if isinstance(sample_row[feat], float) else str(sample_row[feat]))
        with col_feat2:
            for feat in available_features[half:]:
                st.metric(feat, f"{sample_row[feat]:.2f}" if isinstance(sample_row[feat], float) else str(sample_row[feat]))

        # SHAP explanation for this specific sample
        if hasattr(st.session_state, '_shap_sv') and sample_idx < len(st.session_state._shap_sv):
            individual_sv = st.session_state._shap_sv[sample_idx]
            min_l = min(len(feature_names), len(individual_sv))
            ind_df = pd.DataFrame({
                'Feature': feature_names[:min_l],
                'SHAP': individual_sv[:min_l]
            })
            ind_df['Abs'] = np.abs(ind_df['SHAP'])
            ind_df = ind_df.sort_values('Abs', ascending=False).head(8)

            st.markdown("##### 🎯 Why This Classification?")
            fig_ind, ax_ind = plt.subplots(figsize=(10, 4))
            fig_ind.patch.set_facecolor('#0d1117')
            ax_ind.set_facecolor('#0d1117')
            colors_ind = ['#ff4444' if v > 0 else '#00d4ff' for v in ind_df['SHAP'][::-1]]
            ax_ind.barh(ind_df['Feature'][::-1], ind_df['SHAP'][::-1], color=colors_ind, edgecolor='none', height=0.6)
            ax_ind.axvline(x=0, color='#445566', linestyle='-', linewidth=0.8)
            ax_ind.set_xlabel("SHAP Value (→ pushes to Attack | ← pushes to Normal)", color='#8899aa')
            ax_ind.tick_params(colors='#8899aa')
            ax_ind.spines['top'].set_visible(False)
            ax_ind.spines['right'].set_visible(False)
            ax_ind.spines['bottom'].set_color('#2a3040')
            ax_ind.spines['left'].set_color('#2a3040')
            plt.tight_layout()
            st.pyplot(fig_ind)

            # Plain English explanation
            top_attack = ind_df[ind_df['SHAP'] > 0].head(3)
            top_normal = ind_df[ind_df['SHAP'] < 0].head(3)

            explanation = f"**📝 Plain English Summary:** This packet was classified as **{prediction.upper()}**. "
            if len(top_attack) > 0:
                feats = ', '.join(top_attack['Feature'].tolist())
                explanation += f"The features pushing toward ATTACK are: **{feats}**. "
            if len(top_normal) > 0:
                feats = ', '.join(top_normal['Feature'].tolist())
                explanation += f"The features pushing toward NORMAL are: **{feats}**."

            st.info(explanation)


# ══════════════════════════════════════════════════════════
#                     RECENT ALERTS
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "alerts":
    st.markdown("<div class='section-header'>🚨 Recent Alerts</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Detected threats with severity classification, detailed packet information, and recommended response actions.</div>", unsafe_allow_html=True)

    attack_indices = [i for i, p in enumerate(y_pred) if p == 'attack'][:50]

    if attack_indices:
        # Severity counts
        high_alerts = [i for i in attack_indices if X_test.iloc[i]['src_bytes'] > 5000]
        med_alerts = [i for i in attack_indices if 500 < X_test.iloc[i]['src_bytes'] <= 5000]
        low_alerts = [i for i in attack_indices if X_test.iloc[i]['src_bytes'] <= 500]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔴 High Severity", len(high_alerts))
        col2.metric("🟡 Medium Severity", len(med_alerts))
        col3.metric("🔵 Low Severity", len(low_alerts))
        col4.metric("📋 Total Alerts", len(attack_indices))

        st.markdown("---")

        # Filter
        severity_filter = st.selectbox("Filter by severity:", ["All", "High", "Medium", "Low"])

        if severity_filter == "High":
            display_indices = high_alerts
        elif severity_filter == "Medium":
            display_indices = med_alerts
        elif severity_filter == "Low":
            display_indices = low_alerts
        else:
            display_indices = attack_indices

        st.markdown(f"**Showing {len(display_indices)} alerts:**")

        for idx, i in enumerate(display_indices[:20]):
            row = X_test.iloc[i]
            src_b = row['src_bytes']
            if src_b > 5000:
                severity = "HIGH"
                icon = "🔴"
                badge = "badge-high"
                response = "**Immediate Action Required:** Block source IP, enable DDoS mitigation, notify security team."
            elif src_b > 500:
                severity = "MEDIUM"
                icon = "🟡"
                badge = "badge-medium"
                response = "**Investigation Needed:** Monitor traffic pattern, review firewall logs, consider temporary rate limiting."
            else:
                severity = "LOW"
                icon = "🔵"
                badge = "badge-low"
                response = "**Monitor:** Log for analysis, check for repeated patterns, update IDS signatures."

            with st.expander(f"{icon} Alert #{idx+1} — {severity} Severity | src_bytes: {int(src_b)} | duration: {int(row['duration'])}s"):
                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.markdown(f"""
                    **📦 Packet Details:**
                    - **Source Bytes:** {int(row['src_bytes'])}
                    - **Dest Bytes:** {int(row['dst_bytes'])}
                    - **Duration:** {int(row['duration'])}s
                    - **Connection Count:** {int(row['count'])}
                    - **Service Count:** {int(row['srv_count'])}
                    """)
                with detail_col2:
                    st.markdown(f"""
                    **📊 Connection Features:**
                    - **Same Service Rate:** {row['same_srv_rate']:.2f}
                    - **Serror Rate:** {row['serror_rate']:.2f}
                    - **Dst Host Count:** {int(row['dst_host_count'])}
                    - **Dst Host Srv Count:** {int(row['dst_host_srv_count'])}
                    - **Logged In:** {'Yes' if row['logged_in'] else 'No'}
                    """)
                st.markdown(f"---\n🛡️ **Recommended Response:** {response}")

        # CSV Report Download
        st.markdown("---")
        st.markdown("##### 📥 Export Alert Report")
        report_data = []
        for i in display_indices[:20]:
            row = X_test.iloc[i]
            src_b = row['src_bytes']
            sev = "HIGH" if src_b > 5000 else ("MEDIUM" if src_b > 500 else "LOW")
            report_data.append({
                'Alert_ID': len(report_data) + 1,
                'Severity': sev,
                'Source_Bytes': int(row['src_bytes']),
                'Dest_Bytes': int(row['dst_bytes']),
                'Duration_Sec': int(row['duration']),
                'Connection_Count': int(row['count']),
                'Service_Count': int(row['srv_count']),
                'Same_Srv_Rate': round(row['same_srv_rate'], 4),
                'Serror_Rate': round(row['serror_rate'], 4),
                'Dst_Host_Count': int(row['dst_host_count']),
                'Logged_In': 'Yes' if row['logged_in'] else 'No',
                'Generated_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        report_df = pd.DataFrame(report_data)
        csv_data = report_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Alert Report (CSV)",
            data=csv_data,
            file_name=f"cyber_sentinel_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_alerts_csv"
        )
    else:
        st.markdown("""
        <div class='glass-card-green' style='text-align:center;padding:40px;'>
            <div style='font-size:3rem;margin-bottom:10px;'>✅</div>
            <div style='color:#00ff88;font-size:1.3rem;font-weight:700;'>All Clear!</div>
            <div style='color:#8899aa;margin-top:8px;'>No attacks detected in the current dataset.</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                       HONEYPOT
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "honeypot":
    import csv
    st.markdown("<div class='section-header'>🍯 Honeypot Activity Log</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Monitor attackers who connected to our decoy servers. Honeypot traps simulate vulnerable services to attract and log malicious activity.</div>", unsafe_allow_html=True)

    # Beginner mode explanation
    if st.session_state.get('beginner_mode', False):
        st.info("🎓 **Beginner Tip:** A honeypot is a fake computer service set up to lure hackers. When they try to break in, we record everything about them — like catching a thief in a trap!")

    # ── Upgraded log_connection function ──
    LOG_FILE = 'logs/honeypot_log.csv'
    os.makedirs('logs', exist_ok=True)

    def log_connection(ip, port, status="connected"):
        if port == 2222:
            attack_type = "SSH Brute Force"
        elif port == 8021:
            attack_type = "FTP Attack"
        elif port == 8082:
            attack_type = "Web Attack"
        else:
            attack_type = "Unknown"

        file_exists = os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'ip_address', 'port', 'attack_type', 'status', 'action'])
            action = "🔒 IP Blocked" if attack_type != "Unknown" else "⚠️ Monitored"
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                ip, port, attack_type, status, action
            ])

    # ── Honeypot Configuration Card ──
    st.markdown("""
    <div class='glass-card'>
        <div style='color:#00d4ff;font-weight:700;margin-bottom:12px;'>🏗️ Honeypot Configuration</div>
        <div style='color:#aabbcc;'>
            <table style='width:100%;'>
                <tr><td style='padding:6px 0;color:#8899aa;'>Port 2222</td><td style='color:#ffaa00;'>Fake SSH Server</td><td style='color:#ff4444;font-weight:600;'>SSH Brute Force</td><td style='color:#556677;'>Attracts brute force SSH attacks</td></tr>
                <tr><td style='padding:6px 0;color:#8899aa;'>Port 8021</td><td style='color:#ffaa00;'>Fake FTP Server</td><td style='color:#ff4444;font-weight:600;'>FTP Attack</td><td style='color:#556677;'>Attracts file transfer exploits</td></tr>
                <tr><td style='padding:6px 0;color:#8899aa;'>Port 8082</td><td style='color:#ffaa00;'>Fake HTTP Server</td><td style='color:#ff4444;font-weight:600;'>Web Attack</td><td style='color:#556677;'>Attracts web-based attacks</td></tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Simulate Connection Button ──
    st.markdown("---")
    st.markdown("#### 🧪 Simulate Honeypot Connection")
    sim_hp_col1, sim_hp_col2, sim_hp_col3 = st.columns(3)
    PORTS = {"SSH (2222)": 2222, "FTP (8021)": 8021, "HTTP (8082)": 8082}
    FAKE_IPS = [f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(1,254)}" for _ in range(5)]
    with sim_hp_col1:
        sim_port_label = st.selectbox("Select Port", list(PORTS.keys()), key="hp_port_sel")
    with sim_hp_col2:
        sim_ip = st.text_input("Source IP (or leave random)", value="", placeholder="e.g. 192.168.1.99", key="hp_ip_input")
    with sim_hp_col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🎣 Simulate Connection", use_container_width=True, key="hp_sim_btn"):
            chosen_port = PORTS[sim_port_label]
            chosen_ip = sim_ip.strip() if sim_ip.strip() else random.choice(FAKE_IPS)
            log_connection(chosen_ip, chosen_port)
            attack_label = {2222: "SSH Brute Force", 8021: "FTP Attack", 8082: "Web Attack"}.get(chosen_port, "Unknown")
            st.success(f"✅ Connection logged — IP: `{chosen_ip}` | Port: `{chosen_port}` | Type: **{attack_label}**")

    # ── Log Display ──
    st.markdown("---")
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        honey_df = pd.read_csv(LOG_FILE)
        if len(honey_df) > 0:
            hcol1, hcol2, hcol3 = st.columns(3)
            hcol1.metric("🕷️ Total Connections Trapped", len(honey_df))
            hcol2.metric("📍 Unique IPs", honey_df['ip_address'].nunique() if 'ip_address' in honey_df.columns else 0)
            hcol3.metric("🔴 Blocked", honey_df['action'].str.contains('Blocked').sum() if 'action' in honey_df.columns else 0)

            # ── Auto Response per log entry ──
            st.markdown("---")
            st.markdown("##### 🤖 Auto Response System")
            if 'action' in honey_df.columns:
                last = honey_df.iloc[-1]
                at = last.get('attack_type', 'Unknown')
                ip_last = last.get('ip_address', 'N/A')
                action_last = last.get('action', 'N/A')
                resp_color = "#ff4444" if "Blocked" in str(action_last) else "#ffaa00"
                st.markdown(f"""
                <div style='background:rgba(255,68,68,0.07);border:1.5px solid rgba(255,68,68,0.3);
                            border-radius:14px;padding:16px 22px;margin:10px 0;'>
                    <div style='color:{resp_color};font-weight:700;font-size:1rem;margin-bottom:8px;'>
                        🤖 Last Auto-Response
                    </div>
                    <div style='color:#aabbcc;font-size:0.9rem;'>
                        • Attack Type: <b style='color:#ffaa00;'>{at}</b><br>
                        • Source IP: <b style='color:#fff;'>{ip_last}</b><br>
                        • Action Taken: <b style='color:{resp_color};'>{action_last}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("##### 📋 Full Connection Log")
            st.dataframe(honey_df[::-1].reset_index(drop=True), use_container_width=True)

            # Download log
            csv_honey = honey_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Honeypot Log (CSV)", csv_honey,
                               file_name=f"honeypot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                               mime="text/csv", key="hp_download")
    else:
        st.markdown("""
        <div class='glass-card-yellow' style='text-align:center;padding:30px;'>
            <div style='font-size:2rem;'>🍯</div>
            <div style='color:#ffaa00;font-weight:600;margin-top:8px;'>No Honeypot Activity Yet</div>
            <div style='color:#8899aa;margin-top:4px;'>Use the <b>Simulate Connection</b> button above or run <code>python honeypot.py</code> to start logging.</div>
        </div>
        """, unsafe_allow_html=True)

    # ── How Honeypots Work ──
    st.markdown("---")
    st.markdown("##### 📖 How Honeypots Work")
    st.markdown("""
    <div class='glass-card'>
        <div style='color:#aabbcc;font-size:0.9rem;line-height:1.8;'>
            <b>1. Deployment</b> — Fake servers are set up mimicking real services (SSH, FTP, HTTP)<br>
            <b>2. Attraction</b> — Attackers scan the network and find these "vulnerable" services<br>
            <b>3. Trapping</b> — When they connect, their IP, port, and timestamp are logged<br>
            <b>4. Intelligence</b> — Collected data reveals attack patterns, source IPs, and methods<br>
            <b>5. Auto-Response</b> — The system automatically blocks attacker IPs and logs the incident
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                     FILE UPLOAD ANALYZER
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "file_upload":
    st.markdown("<div class='section-header'>📁 File Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Upload CSV data for IDS threat detection, or upload images and PDFs for secure viewing and logging.</div>", unsafe_allow_html=True)

    if st.session_state.get('beginner_mode', False):
        st.info("🎓 **Beginner Tip:** Upload a CSV file to scan for attacks, an image (PNG/JPG) to view it, or a PDF document to log it!")

    uploaded_file = st.file_uploader(
        "📂 Upload a File (CSV, PDF, PNG, JPG)",
        type=["csv", "pdf", "png", "jpg", "jpeg"],
        help="CSV: IDS threat analysis | Images: display & metadata | PDF: document viewer",
        key="file_upload_input"
    )

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        file_size_kb = uploaded_file.size / 1024
        file_size_mb = file_size_kb / 1024

        # ══ UNIVERSAL FILE SAFETY SCANNER ══
        def scan_file(name, ext, size_kb, extra_flags=None):
            warnings = []
            risk = 0

            SUSPICIOUS_NAMES = ['invoice', 'urgent', 'password', 'bank', 'free', 'win',
                                 'hack', 'crack', 'exploit', 'virus', 'trojan', 'malware',
                                 'phish', 'ransom', 'keylog', 'payload', 'shell', 'rootkit']
            DOUBLE_EXT = ['.pdf.exe', '.jpg.exe', '.png.exe', '.doc.exe',
                          '.pdf.bat', '.jpg.bat', '.docx.exe']

            name_lower = name.lower()

            # Check suspicious keywords in filename
            hits = [k for k in SUSPICIOUS_NAMES if k in name_lower]
            if hits:
                warnings.append(f"⚠️ Suspicious keyword(s) in filename: **{', '.join(hits)}**")
                risk += 25 * len(hits)

            # Check double extension
            if any(name_lower.endswith(de) for de in DOUBLE_EXT):
                warnings.append("🚨 **Double extension detected** — classic malware disguise technique!")
                risk += 60

            # Check oversized
            if ext == 'pdf' and size_kb > 15 * 1024:
                warnings.append(f"⚠️ PDF is very large ({size_kb/1024:.1f} MB) — could contain embedded malicious payloads")
                risk += 20
            elif ext in ['png', 'jpg', 'jpeg'] and size_kb > 10 * 1024:
                warnings.append(f"⚠️ Image is unusually large ({size_kb/1024:.1f} MB) — may contain hidden data (steganography)")
                risk += 20
            elif ext == 'csv' and size_kb > 50 * 1024:
                warnings.append(f"⚠️ CSV is extremely large ({size_kb/1024:.1f} MB) — verify source before processing")
                risk += 10

            # Special character in filename
            special_chars = set(name) - set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- ()')
            if special_chars:
                warnings.append(f"⚠️ Unusual characters in filename: `{''.join(special_chars)}` — could be obfuscation")
                risk += 15

            # Check very small PDF (could be dropper)
            if ext == 'pdf' and size_kb < 5:
                warnings.append("⚠️ PDF is suspiciously small — may be a dropper or decoy file")
                risk += 20

            # Extra flags from content analysis
            if extra_flags:
                for flag, pts in extra_flags:
                    warnings.append(flag)
                    risk += pts

            risk = min(risk, 100)
            return warnings, risk

        st.markdown("---")
        st.markdown("#### 🔍 File Safety Scan")

        scan_warnings, risk_score = scan_file(uploaded_file.name, file_ext, file_size_kb)

        # Verdict
        if risk_score == 0:
            verdict_icon = "🟢"
            verdict_label = "SAFE"
            verdict_color = "#00ff88"
            verdict_bg = "rgba(0,255,136,0.07)"
            verdict_border = "rgba(0,255,136,0.3)"
        elif risk_score < 40:
            verdict_icon = "🟡"
            verdict_label = "LOW RISK"
            verdict_color = "#ffaa00"
            verdict_bg = "rgba(255,170,0,0.07)"
            verdict_border = "rgba(255,170,0,0.3)"
        elif risk_score < 70:
            verdict_icon = "🟠"
            verdict_label = "SUSPICIOUS"
            verdict_color = "#ff8800"
            verdict_bg = "rgba(255,136,0,0.08)"
            verdict_border = "rgba(255,136,0,0.35)"
        else:
            verdict_icon = "🔴"
            verdict_label = "DANGEROUS"
            verdict_color = "#ff4444"
            verdict_bg = "rgba(255,68,68,0.09)"
            verdict_border = "rgba(255,68,68,0.4)"

        findings_html = "".join(
            f"<div style='margin:5px 0;color:#ffcc44;font-size:0.88rem;'>{w}</div>"
            for w in scan_warnings
        ) if scan_warnings else "<div style='color:#00ff88;font-size:0.88rem;'>✅ No suspicious indicators found</div>"

        st.markdown(f"""
        <div style='background:{verdict_bg};border:1.5px solid {verdict_border};
                    border-radius:16px;padding:20px 26px;margin:10px 0;'>
            <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;'>
                <div style='display:flex;align-items:center;gap:14px;'>
                    <div style='font-size:2.8rem;'>{verdict_icon}</div>
                    <div>
                        <div style='color:#8899aa;font-size:0.75rem;letter-spacing:1.5px;text-transform:uppercase;'>Scan Verdict</div>
                        <div style='color:{verdict_color};font-size:1.8rem;font-weight:800;letter-spacing:1px;'>{verdict_label}</div>
                    </div>
                </div>
                <div style='min-width:200px;flex:1;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
                        <span style='color:#8899aa;font-size:0.8rem;'>Risk Score</span>
                        <span style='color:{verdict_color};font-weight:700;'>{risk_score}/100</span>
                    </div>
                    <div style='background:rgba(255,255,255,0.07);border-radius:8px;height:10px;overflow:hidden;'>
                        <div style='width:{risk_score}%;height:100%;
                                    background:linear-gradient(90deg,{verdict_color}88,{verdict_color});
                                    border-radius:8px;'></div>
                    </div>
                </div>
                <div style='text-align:right;'>
                    <div style='color:#8899aa;font-size:0.75rem;'>File</div>
                    <div style='color:#fff;font-weight:600;font-size:0.9rem;'>{uploaded_file.name}</div>
                    <div style='color:#8899aa;font-size:0.75rem;margin-top:4px;'>{file_size_kb:.1f} KB &bull; {file_ext.upper()}</div>
                </div>
            </div>
            <div style='margin-top:14px;border-top:1px solid {verdict_border};padding-top:12px;'>
                <div style='color:#8899aa;font-size:0.75rem;font-weight:600;letter-spacing:1px;margin-bottom:6px;'>FINDINGS</div>
                {findings_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── IMAGE HANDLER ──
        if file_ext in ['png', 'jpg', 'jpeg']:
            from PIL import Image
            img = Image.open(uploaded_file)
            img_c1, img_c2 = st.columns([2, 1])
            with img_c1:
                st.markdown("##### 🖼️ Image Preview")
                st.image(img, use_column_width=True)
            with img_c2:
                st.markdown("##### 📊 Image Metadata")
                st.markdown(f"""
                <div class='glass-card'>
                    <div style='color:#8899aa;font-size:0.8rem;'>File Name</div>
                    <div style='color:#fff;font-weight:600;margin-bottom:10px;'>{uploaded_file.name}</div>
                    <div style='color:#8899aa;font-size:0.8rem;'>Format</div>
                    <div style='color:#00d4ff;font-weight:600;margin-bottom:10px;'>{img.format or file_ext.upper()}</div>
                    <div style='color:#8899aa;font-size:0.8rem;'>Dimensions</div>
                    <div style='color:#fff;font-weight:600;margin-bottom:10px;'>{img.width} × {img.height} px</div>
                    <div style='color:#8899aa;font-size:0.8rem;'>Mode</div>
                    <div style='color:#fff;font-weight:600;margin-bottom:10px;'>{img.mode}</div>
                    <div style='color:#8899aa;font-size:0.8rem;'>File Size</div>
                    <div style='color:#fff;font-weight:600;'>{file_size_kb:.1f} KB</div>
                </div>
                """, unsafe_allow_html=True)

        # ── PDF HANDLER ──
        elif file_ext == 'pdf':
            pdf_meta_c1, pdf_meta_c2 = st.columns(2)
            pdf_meta_c1.metric("📄 File Name", uploaded_file.name)
            pdf_meta_c2.metric("💾 File Size", f"{file_size_kb:.1f} KB")
            st.markdown("""
            <div class='glass-card' style='text-align:center;padding:20px;'>
                <div style='font-size:3rem;'>📄</div>
                <div style='color:#00d4ff;font-weight:700;font-size:1.1rem;margin-top:10px;'>PDF Document Received</div>
                <div style='color:#8899aa;margin-top:8px;font-size:0.9rem;'>
                    File scanned and securely logged for review.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.info("💡 To enable full PDF text extraction & deeper scan, run: `pip install PyPDF2`")

        # ── CSV HANDLER ──
        else:
          try:
            df_upload = pd.read_csv(uploaded_file)
            st.success(f"✅ File loaded: **{uploaded_file.name}** — {len(df_upload):,} rows, {len(df_upload.columns)} columns")
            st.markdown("---")

            # Preview
            st.markdown("##### 👀 Data Preview (first 10 rows)")
            st.dataframe(df_upload.head(10), use_container_width=True)

            st.markdown("---")
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            col_stat1.metric("📋 Total Rows", f"{len(df_upload):,}")
            col_stat2.metric("📊 Columns", len(df_upload.columns))
            col_stat3.metric("🔢 Numeric Cols", len(df_upload.select_dtypes(include='number').columns))
            col_stat4.metric("🔤 Text Cols", len(df_upload.select_dtypes(include='object').columns))

            st.markdown("---")
            st.markdown("##### 📈 Column Statistics")
            st.dataframe(df_upload.describe(), use_container_width=True)

            # Try to run IDS model if columns match
            matching_cols = [c for c in feature_names if c in df_upload.columns]
            st.markdown("---")
            if len(matching_cols) == len(feature_names):
                st.markdown("##### 🤖 IDS Model Prediction on Uploaded Data")
                try:
                    upload_preds = model.predict(df_upload[feature_names])
                    n_attacks = sum(1 for p in upload_preds if p == 'attack')
                    n_normal = len(upload_preds) - n_attacks
                    risk_pct = n_attacks / len(upload_preds) * 100

                    up_c1, up_c2, up_c3 = st.columns(3)
                    up_c1.metric("⚠️ Attacks Detected", f"{n_attacks:,}")
                    up_c2.metric("✅ Normal Traffic", f"{n_normal:,}")
                    up_c3.metric("🔴 Risk Score", f"{risk_pct:.1f}%")

                    df_upload['IDS_Prediction'] = upload_preds
                    st.markdown("##### 📋 Prediction Results")
                    st.dataframe(df_upload[['IDS_Prediction'] + feature_names[:8]].head(50), use_container_width=True)

                    # Auto Response summary
                    if n_attacks > 0:
                        st.markdown(f"""
                        <div style='background:rgba(255,68,68,0.08);border:1.5px solid rgba(255,68,68,0.3);
                                    border-radius:14px;padding:16px 22px;margin:12px 0;'>
                            <div style='color:#ff4444;font-weight:700;font-size:1rem;margin-bottom:8px;'>
                                🔒 Auto-Response: {n_attacks:,} IPs Flagged for Blocking
                            </div>
                            <div style='color:#aabbcc;font-size:0.88rem;'>
                                • {n_attacks:,} attack packets detected in uploaded data<br>
                                • Risk Level: {'🔴 HIGH' if risk_pct >= 70 else '🟡 MEDIUM' if risk_pct >= 30 else '🟢 LOW'} ({risk_pct:.1f}%)<br>
                                • Recommended: Review flagged rows and block source IPs
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("✅ Auto-Response: No Action Needed — all traffic appears normal.")

                    # Download predictions
                    csv_pred = df_upload.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Predictions (CSV)", csv_pred,
                                       file_name=f"ids_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                       mime="text/csv", key="upload_pred_download")
                except Exception as e:
                    st.error(f"Model prediction error: {e}")
            else:
                missing = set(feature_names) - set(df_upload.columns)
                st.warning(f"⚠️ **{len(matching_cols)}/{len(feature_names)}** required features found. Missing: {', '.join(list(missing)[:5])}{'...' if len(missing) > 5 else ''}")
                st.info("💡 The IDS model requires NSL-KDD format features. Your file can still be explored above.")

          except Exception as e:
              st.error(f"❌ Error reading CSV: {e}")

    else:
        st.markdown("""
        <div class='glass-card' style='text-align:center;padding:40px;'>
            <div style='font-size:3rem;margin-bottom:12px;'>📂</div>
            <div style='color:#00d4ff;font-size:1.2rem;font-weight:700;'>Upload a File to Begin</div>
            <div style='color:#8899aa;margin-top:8px;font-size:0.9rem;'>
                <b style='color:#00d4ff;'>📊 CSV</b> — IDS threat detection & model analysis<br>
                <b style='color:#00d4ff;'>🖼️ PNG / JPG</b> — Image preview with metadata<br>
                <b style='color:#00d4ff;'>📄 PDF</b> — Document logging & review
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                      URL SCANNER
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "url":
    st.markdown("<div class='section-header'>🔍 URL Safety Scanner</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Advanced URL threat analysis engine. Checks for phishing indicators, malware links, encryption status, and domain reputation.</div>", unsafe_allow_html=True)

    if 'url_history' not in st.session_state:
        st.session_state.url_history = []

    SUSPICIOUS_KEYWORDS = [
        'free', 'win', 'prize', 'click', 'verify', 'login', 'secure', 'update',
        'account', 'bank', 'paypal', 'confirm', 'password', 'lucky', 'offer',
        'deal', 'urgent', 'alert', 'suspended', 'unusual', 'activity', 'limited',
        'bonus', 'gift', 'reward', 'casino', 'lottery', 'inheritance', 'prince',
        'wire', 'transfer', 'congratulations', 'selected', 'won', 'claim'
    ]
    MALICIOUS_EXTENSIONS = ['.exe', '.bat', '.cmd', '.vbs', '.ps1', '.msi', '.dll', '.scr', '.jar', '.apk']
    TRUSTED_DOMAINS = [
        'google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'github.com',
        'wikipedia.org', 'youtube.com', 'linkedin.com', 'twitter.com', 'facebook.com',
        'instagram.com', 'reddit.com', 'stackoverflow.com', 'python.org', 'streamlit.io',
        'mozilla.org', 'cloudflare.com', 'aws.amazon.com', 'azure.microsoft.com'
    ]

    def analyze_url(url):
        url_lower = url.strip().lower()
        threats = []
        risk_score = 0
        categories = {'security': [], 'privacy': [], 'trust': []}

        if not url_lower.startswith('http'):
            threats.append("No HTTP/HTTPS — not a valid URL format")
            categories['security'].append("Missing protocol scheme")
            risk_score += 20

        if url_lower.startswith('http://'):
            threats.append("Uses HTTP not HTTPS — connection not encrypted")
            categories['privacy'].append("Unencrypted connection")
            risk_score += 25

        found_keywords = [k for k in SUSPICIOUS_KEYWORDS if k in url_lower]
        if found_keywords:
            threats.append(f"Suspicious keywords: {', '.join(found_keywords[:5])}")
            categories['trust'].append(f"Found {len(found_keywords)} suspicious keyword(s)")
            risk_score += min(len(found_keywords) * 10, 40)

        found_ext = [e for e in MALICIOUS_EXTENSIONS if url_lower.endswith(e)]
        if found_ext:
            threats.append(f"Dangerous file: {', '.join(found_ext)} — may contain malware")
            categories['security'].append("Malicious file extension detected")
            risk_score += 40

        ip_pattern = re.compile(r'https?://(\d{1,3}\.){3}\d{1,3}')
        if ip_pattern.match(url_lower):
            threats.append("IP address used instead of domain — common in phishing")
            categories['trust'].append("Raw IP address instead of domain name")
            risk_score += 35

        try:
            domain_part = url_lower.split('/')[2]
            if domain_part.count('.') > 3:
                threats.append("Too many subdomains — common phishing technique")
                categories['trust'].append("Excessive subdomains")
                risk_score += 20
        except:
            pass

        if len(url) > 100:
            threats.append(f"Very long URL ({len(url)} chars) — may hide malicious content")
            categories['trust'].append("Unusually long URL")
            risk_score += 15

        special_chars = ['@', '..', '--', '%00', '%0d', '%0a']
        found_special = [c for c in special_chars if c in url_lower]
        if found_special:
            threats.append(f"Suspicious characters: {', '.join(found_special)}")
            categories['security'].append("Suspicious special characters")
            risk_score += 15

        # Check for homograph attacks
        if any(ord(c) > 127 for c in url):
            threats.append("Contains non-ASCII characters — possible homograph attack")
            categories['security'].append("Potential IDN homograph attack")
            risk_score += 30

        is_trusted = any(d in url_lower for d in TRUSTED_DOMAINS)
        if is_trusted and risk_score < 30:
            risk_score = 0
            threats = []
            categories = {'security': [], 'privacy': [], 'trust': []}

        risk_score = min(risk_score, 100)

        if risk_score == 0:
            status = "SAFE"
        elif risk_score < 30:
            status = "LOW RISK"
        elif risk_score < 60:
            status = "MEDIUM RISK"
        else:
            status = "DANGEROUS"

        return status, risk_score, threats, categories

    # Quick scan suggestions
    st.markdown("##### 🔗 Quick Test URLs")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    with qcol1:
        if st.button("✅ google.com", key="q1"):
            st.session_state.test_url = "https://www.google.com"
            st.rerun()
    with qcol2:
        if st.button("⚠️ Suspicious", key="q2"):
            st.session_state.test_url = "http://free-prize-winner-click-now.com/claim-reward"
            st.rerun()
    with qcol3:
        if st.button("🔴 Malware", key="q3"):
            st.session_state.test_url = "http://192.168.1.100/download/update.exe"
            st.rerun()
    with qcol4:
        if st.button("🟡 HTTP Site", key="q4"):
            st.session_state.test_url = "http://example-shopping-deals.com/login"
            st.rerun()

    default_url = st.session_state.get('test_url', '')
    url_input = st.text_input("Enter URL to scan:", value=default_url, placeholder="https://example.com", key="url_scan_input")

    if st.button("🔍 Scan URL", key="scan_btn") and url_input.strip():
        with st.spinner("Scanning URL..."):
            time.sleep(0.8)
            status, score, threats, categories = analyze_url(url_input)

        # Visual risk gauge
        if status == "SAFE":
            gauge_color = "#00ff88"
        elif status == "LOW RISK":
            gauge_color = "#00d4ff"
        elif status == "MEDIUM RISK":
            gauge_color = "#ffaa00"
        else:
            gauge_color = "#ff4444"

        st.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:30px;'>
            <div style='color:#8899aa;font-size:0.9rem;text-transform:uppercase;letter-spacing:2px;'>Risk Assessment</div>
            <div class='risk-score-big' style='color:{gauge_color};'>{score}/100</div>
            <div class='risk-label' style='color:{gauge_color};'>{status}</div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(score)

        if threats:
            st.markdown("---")
            # Categorized findings
            cat_col1, cat_col2, cat_col3 = st.columns(3)
            with cat_col1:
                st.markdown(f"""
                <div class='glass-card-red' style='padding:16px;'>
                    <div style='color:#ff4444;font-weight:600;margin-bottom:8px;'>🔒 Security</div>
                    <div style='color:#aabbcc;font-size:0.85rem;'>
                        {'<br>'.join(f"• {c}" for c in categories['security']) if categories['security'] else '✅ No security issues'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cat_col2:
                st.markdown(f"""
                <div class='glass-card-yellow' style='padding:16px;'>
                    <div style='color:#ffaa00;font-weight:600;margin-bottom:8px;'>🔓 Privacy</div>
                    <div style='color:#aabbcc;font-size:0.85rem;'>
                        {'<br>'.join(f"• {c}" for c in categories['privacy']) if categories['privacy'] else '✅ No privacy issues'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cat_col3:
                st.markdown(f"""
                <div class='glass-card' style='padding:16px;'>
                    <div style='color:#00d4ff;font-weight:600;margin-bottom:8px;'>🤝 Trust</div>
                    <div style='color:#aabbcc;font-size:0.85rem;'>
                        {'<br>'.join(f"• {c}" for c in categories['trust']) if categories['trust'] else '✅ No trust issues'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**⚠️ Detailed Threats:**")
            for i, threat in enumerate(threats, 1):
                st.markdown(f"{i}. ⚠️ {threat}")

            # Contextual warnings
            if any('malware' in t.lower() or 'exe' in t.lower() for t in threats):
                st.error("🦠 **Malware Risk** — This URL may download harmful software. Never run unknown executables!")
            if any('phishing' in t.lower() or 'ip address' in t.lower() for t in threats):
                st.error("🎣 **Phishing Risk** — This URL may steal your login credentials or financial information.")
            if any('encrypted' in t.lower() or 'http' in t.lower() for t in threats):
                st.warning("🔓 **Privacy Risk** — Your data is transmitted in plain text and visible to network eavesdroppers.")
            if any('keyword' in t.lower() for t in threats):
                st.warning("🎭 **Social Engineering** — Uses psychological tricks to lure you into clicking.")
        else:
            st.success("✅ No threats found! This URL appears to be safe.")

        st.session_state.url_history.append({
            'Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'URL': url_input[:60] + ('...' if len(url_input) > 60 else ''),
            'Status': status,
            'Risk Score': score,
            'Threats': len(threats)
        })
        # Clear test URL
        if 'test_url' in st.session_state:
            del st.session_state['test_url']

    if st.session_state.url_history:
        st.markdown("---")
        st.markdown("##### 📜 Scan History")
        history_df = pd.DataFrame(st.session_state.url_history)

        def color_status(val):
            colors = {
                'SAFE': 'background-color:#0a3a0a;color:#00ff88',
                'LOW RISK': 'background-color:#0a1a3a;color:#00d4ff',
                'MEDIUM RISK': 'background-color:#3a2a0a;color:#ffaa00',
                'DANGEROUS': 'background-color:#3a0a0a;color:#ff4444'
            }
            return colors.get(val, '')

        styled_df = history_df.style.map(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)

        if st.button("🗑️ Clear URL History", key="clear_url_hist"):
            st.session_state.url_history = []
            st.rerun()


# ══════════════════════════════════════════════════════════
#                  THREAT KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "knowledge":
    st.markdown("<div class='section-header'>📚 Threat Knowledge Base</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Comprehensive cybersecurity encyclopedia covering attack types, defense strategies, and security frameworks.</div>", unsafe_allow_html=True)

    kb_tab1, kb_tab2, kb_tab3 = st.tabs(["🗡️ Attack Types", "🛡️ Defense Strategies", "📋 Security Frameworks"])

    with kb_tab1:
        attacks_kb = {
            "DDoS Attack (Distributed Denial of Service)": {
                "icon": "🌊",
                "severity": "HIGH",
                "description": "Overwhelms a server with traffic from thousands of compromised machines (botnet), making it unavailable to legitimate users.",
                "how_it_works": "1. Attacker infects thousands of computers with malware to create a botnet\n2. All bots simultaneously send requests to the target server\n3. Server cannot handle the volume and crashes or becomes extremely slow\n4. Legitimate users are denied access to the service",
                "real_example": "**Mirai Botnet (2016)** — Infected 600,000 IoT devices and attacked Dyn DNS, taking down Twitter, Netflix, Reddit, and GitHub for hours.",
                "prevention": "• Use DDoS protection services (Cloudflare, AWS Shield)\n• Implement rate limiting and traffic filtering\n• Use Content Delivery Networks (CDNs)\n• Have an incident response plan ready"
            },
            "SQL Injection": {
                "icon": "💉",
                "severity": "HIGH",
                "description": "Attacker inserts malicious SQL code into input fields to manipulate the database — steal data, delete records, or gain admin access.",
                "how_it_works": "1. Attacker finds a web form connected to a database (login, search)\n2. Instead of normal input, they type SQL commands like ' OR 1=1 --\n3. The application executes this as part of the database query\n4. Attacker gains unauthorized access to the entire database",
                "real_example": "**Heartland Payment Systems (2008)** — SQL injection led to theft of 134 million credit card numbers, costing $140 million.",
                "prevention": "• Use parameterized queries / prepared statements\n• Input validation and sanitization\n• Web Application Firewall (WAF)\n• Principle of least privilege for database accounts"
            },
            "Phishing": {
                "icon": "🎣",
                "severity": "HIGH",
                "description": "Fake emails, websites, or messages that impersonate trusted entities to trick victims into revealing passwords, credit card numbers, or personal data.",
                "how_it_works": "1. Attacker creates a convincing fake email/website mimicking a trusted brand\n2. Email contains urgent message (account suspended, verify identity)\n3. Victim clicks link and enters credentials on the fake site\n4. Attacker captures the credentials and accesses the real account",
                "real_example": "**Google & Facebook (2013-2015)** — Lithuanian hacker phished both companies for $100 million by impersonating a hardware vendor.",
                "prevention": "• Employee security awareness training\n• Email filtering and anti-phishing tools\n• Multi-factor authentication (MFA)\n• Verify URLs before entering credentials"
            },
            "Ransomware": {
                "icon": "🔒",
                "severity": "CRITICAL",
                "description": "Malware that encrypts all files on a system and demands payment (usually cryptocurrency) for the decryption key.",
                "how_it_works": "1. Victim opens infected email attachment or visits compromised website\n2. Ransomware silently encrypts all files on the computer and network\n3. A ransom note appears demanding Bitcoin payment\n4. Even after payment, decryption is not guaranteed",
                "real_example": "**WannaCry (2017)** — Infected 200,000+ computers in 150 countries including NHS hospitals. Exploited Windows SMB vulnerability.",
                "prevention": "• Regular offline backups (3-2-1 backup rule)\n• Keep all systems patched and updated\n• Email filtering to block malicious attachments\n• Network segmentation to limit spread"
            },
            "Man-in-the-Middle (MITM)": {
                "icon": "👤",
                "severity": "HIGH",
                "description": "Attacker secretly intercepts and potentially modifies communication between two parties who believe they are communicating directly.",
                "how_it_works": "1. Attacker positions themselves between victim and server (e.g., on public WiFi)\n2. All traffic passes through the attacker's system\n3. Attacker can read, modify, or inject data into the communication\n4. Neither party knows the communication is compromised",
                "real_example": "**DigiNotar (2011)** — Attackers obtained fraudulent SSL certificates to intercept 300,000 Iranian Gmail users' communications.",
                "prevention": "• Use HTTPS for all web traffic\n• VPN on untrusted networks\n• Certificate pinning\n• Avoid public WiFi for sensitive transactions"
            },
            "Cross-Site Scripting (XSS)": {
                "icon": "📜",
                "severity": "MEDIUM",
                "description": "Injecting malicious JavaScript into web pages that executes in victims' browsers, stealing cookies, session tokens, or redirecting to malicious sites.",
                "how_it_works": "1. Attacker finds a web page that displays user input without sanitization\n2. Injects JavaScript code (e.g., in comments, search fields)\n3. When other users view the page, the malicious script executes\n4. Script can steal cookies, capture keystrokes, or redirect users",
                "real_example": "**MySpace Samy Worm (2005)** — XSS worm that added 1 million friends to Samy's profile in under 24 hours.",
                "prevention": "• Input validation and output encoding\n• Content Security Policy (CSP) headers\n• HttpOnly and Secure cookie flags\n• Web Application Firewall (WAF)"
            },
            "Brute Force Attack": {
                "icon": "🔨",
                "severity": "MEDIUM",
                "description": "Systematically trying every possible password combination until finding the correct one. Can be automated to test millions of combinations.",
                "how_it_works": "1. Attacker targets a login page or authentication system\n2. Uses automated tools to try passwords from dictionaries or generate combinations\n3. Tries thousands/millions of attempts per second\n4. Eventually finds the correct password if it is weak",
                "real_example": "**iCloud Celebrity Hack (2014)** — Brute force on iCloud accounts led to private photo leaks of celebrities.",
                "prevention": "• Account lockout after failed attempts\n• CAPTCHA on login pages\n• Rate limiting\n• Strong, unique passwords + MFA"
            },
            "ARP Spoofing": {
                "icon": "🔄",
                "severity": "MEDIUM",
                "description": "Attacker sends fake ARP messages to link their MAC address with a legitimate IP address, intercepting traffic on the local network.",
                "how_it_works": "1. Attacker sends forged ARP replies to the network\n2. Devices update their ARP table with attacker's MAC address\n3. Traffic meant for the gateway now goes through the attacker\n4. Attacker can sniff, modify, or block the traffic",
                "real_example": "Commonly used in corporate espionage and public WiFi attacks to intercept unencrypted traffic.",
                "prevention": "• Static ARP entries for critical devices\n• ARP inspection on managed switches\n• VPN for all network traffic\n• Network segmentation"
            },
            "DNS Poisoning": {
                "icon": "☠️",
                "severity": "HIGH",
                "description": "Corrupting a DNS server's cache to redirect domain lookups to malicious IP addresses, sending users to fake websites.",
                "how_it_works": "1. Attacker sends forged DNS responses to a DNS resolver\n2. The resolver caches the incorrect IP address for a domain\n3. All users querying that resolver are sent to the attacker's server\n4. Users see a convincing fake site and enter credentials",
                "real_example": "**Brazilian Bank Attack (2017)** — Attackers hijacked all 36 bank domains for 5 hours, capturing customer credentials.",
                "prevention": "• DNSSEC (DNS Security Extensions)\n• DNS over HTTPS (DoH) or DNS over TLS (DoT)\n• Regular DNS cache flushing\n• Multiple DNS providers"
            },
            "Zero-Day Exploit": {
                "icon": "💀",
                "severity": "CRITICAL",
                "description": "An attack exploiting a previously unknown software vulnerability before the vendor releases a patch. Called 'zero-day' because developers have zero days to fix it.",
                "how_it_works": "1. Researcher or attacker discovers unknown vulnerability\n2. Exploit code is developed before vendor knows about it\n3. Attack is launched while no patch exists\n4. Organizations are defenseless until vendor releases fix",
                "real_example": "**Stuxnet (2010)** — Used 4 zero-day exploits to destroy Iranian nuclear centrifuges, the first known cyber weapon.",
                "prevention": "• Defense in depth strategy\n• Behavior-based detection systems\n• Regular security audits\n• Bug bounty programs to find vulnerabilities first"
            },
        }

        for attack_name, data in attacks_kb.items():
            sev_badge = f"badge-{'high' if data['severity'] in ['HIGH', 'CRITICAL'] else 'medium'}"
            with st.expander(f"{data['icon']} {attack_name}"):
                st.markdown(f"<span class='{sev_badge}'>{data['severity']}</span>", unsafe_allow_html=True)
                st.markdown(f"**📝 Description:** {data['description']}")
                st.markdown(f"**⚙️ How It Works:**\n{data['how_it_works']}")
                st.markdown(f"**📰 Real-World Example:** {data['real_example']}")
                st.markdown(f"**🛡️ Prevention:**\n{data['prevention']}")

    with kb_tab2:
        st.markdown("#### 🛡️ Defense Strategies & Best Practices")

        defenses = [
            ("🔥 Firewalls", "Network firewalls filter incoming and outgoing traffic based on security rules. Next-gen firewalls (NGFW) add deep packet inspection, intrusion prevention, and application awareness.", "• Configure deny-by-default rules\n• Regular rule review and cleanup\n• Enable logging for all denied traffic\n• Use application-layer filtering"),
            ("🔍 IDS/IPS Systems", "Intrusion Detection Systems (IDS) monitor and alert on threats. Intrusion Prevention Systems (IPS) actively block them. This project demonstrates an IDS using ML.", "• Signature-based + anomaly-based detection\n• Regular signature updates\n• Tune to reduce false positives\n• Place at network choke points"),
            ("🔐 Multi-Factor Authentication", "Requires 2+ verification methods: something you know (password), something you have (phone), something you are (biometric). Blocks 99.9% of automated attacks.", "• Enforce MFA for all accounts\n• Use authenticator apps over SMS\n• Hardware security keys for admins\n• Backup codes stored securely"),
            ("🌐 Zero Trust Architecture", "\"Never trust, always verify.\" Every access request is fully authenticated and authorized regardless of network location. No implicit trust zones.", "• Verify every user and device\n• Least-privilege access\n• Micro-segmentation\n• Continuous monitoring and validation"),
            ("📊 SIEM (Security Information & Event Management)", "Aggregates and analyzes security logs from across the organization in real-time. Uses correlation rules and ML to detect complex attack patterns.", "• Centralize all security logs\n• Create custom correlation rules\n• Automate incident response workflows\n• Regular tuning and optimization"),
            ("💾 Backup & Recovery", "Regular, tested backups are the last line of defense against ransomware and data loss. Follow the 3-2-1 rule: 3 copies, 2 different media, 1 offsite.", "• Automate daily backups\n• Test restoration regularly\n• Air-gapped backup copies\n• Encrypt backup data"),
        ]

        for name, desc, practices in defenses:
            with st.expander(name):
                st.markdown(f"**Overview:** {desc}")
                st.markdown(f"**Best Practices:**\n{practices}")

    with kb_tab3:
        st.markdown("#### 📋 Security Frameworks & Concepts")

        frameworks = [
            ("🔺 CIA Triad", "The three pillars of information security:\n- **Confidentiality** — Only authorized users can access data\n- **Integrity** — Data is accurate and unaltered\n- **Availability** — Systems and data are accessible when needed"),
            ("🏗️ MITRE ATT&CK", "A globally-accessible knowledge base of adversary tactics and techniques based on real-world observations. Used to plan defenses and evaluate security posture.\n\nKey Tactics: Initial Access → Execution → Persistence → Privilege Escalation → Defense Evasion → Credential Access → Discovery → Lateral Movement → Collection → Exfiltration → Impact"),
            ("📏 NIST Cybersecurity Framework", "Five core functions:\n1. **Identify** — Know your assets and risks\n2. **Protect** — Implement safeguards\n3. **Detect** — Find security events\n4. **Respond** — Take action on threats\n5. **Recover** — Restore normal operations"),
            ("🔐 OWASP Top 10", "The 10 most critical web application security risks:\n1. Broken Access Control\n2. Cryptographic Failures\n3. Injection\n4. Insecure Design\n5. Security Misconfiguration\n6. Vulnerable Components\n7. Authentication Failures\n8. Data Integrity Failures\n9. Logging & Monitoring Failures\n10. Server-Side Request Forgery"),
            ("🔑 Encryption: Symmetric vs Asymmetric", "**Symmetric** (AES, DES): Same key encrypts and decrypts. Fast but key distribution is a challenge.\n\n**Asymmetric** (RSA, ECC): Public key encrypts, private key decrypts. Slower but solves key distribution. Used in HTTPS, digital signatures, and secure email."),
            ("🔢 Hashing", "One-way function that converts data into a fixed-length fingerprint. Cannot be reversed.\n\n**Common Algorithms:** MD5 (broken), SHA-1 (deprecated), SHA-256 (current standard), bcrypt (passwords)\n\n**Uses:** Password storage, file integrity verification, digital signatures"),
        ]

        for name, content in frameworks:
            with st.expander(name):
                st.markdown(content)


# ══════════════════════════════════════════════════════════
#                       AI CHATBOT
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "chatbot":
    st.markdown("<div class='section-header'>🤖 AI Security Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Ask any cybersecurity question. Powered by Google Gemini AI for intelligent, context-aware responses.</div>", unsafe_allow_html=True)

    # ── Expanded Fallback Responses ──
    fallback_responses = {
        "ddos": {
            "answer": "**DDoS (Distributed Denial of Service) Attack**\n\nA DDoS attack floods your server with millions of fake requests from thousands of compromised computers (botnet), making it crash or become extremely slow.\n\n**How to respond:**\n1. Contact your hosting provider immediately\n2. Enable DDoS protection (Cloudflare, AWS Shield)\n3. Block malicious IPs at the firewall\n4. Implement rate limiting\n5. Use CDN to absorb traffic\n\n**Real Example:** The 2016 Mirai Botnet attack on Dyn DNS used 600,000 IoT devices to take down Twitter, Netflix, Reddit, and GitHub.",
        },
        "dos": {
            "answer": "**DoS (Denial of Service) Attack**\n\nA DoS attack floods your server with fake traffic from a single source to make it unavailable.\n\n**How to respond:**\n1. Block the source IP immediately\n2. Enable rate limiting on your server\n3. Contact your ISP for upstream filtering\n4. Document everything for forensics\n5. Review and harden server configuration",
        },
        "port scan": {
            "answer": "**Port Scanning**\n\nPort scanning is reconnaissance — attackers probe your system to find open ports (services) they can exploit.\n\n**How to respond:**\n1. Block the scanning IP at the firewall\n2. Close all unnecessary ports\n3. Enable Intrusion Prevention System (IPS)\n4. Monitor logs for follow-up attacks\n5. Use port knocking for sensitive services\n\n**Common tools:** Nmap, Masscan, Zmap\n**Commonly targeted ports:** 22 (SSH), 80 (HTTP), 443 (HTTPS), 3389 (RDP), 3306 (MySQL)",
        },
        "brute force": {
            "answer": "**Brute Force Attack**\n\nAutomated trial of thousands/millions of password combinations to find the correct one.\n\n**How to respond:**\n1. Lock the affected account immediately\n2. Enable Multi-Factor Authentication (MFA)\n3. Implement account lockout policies\n4. Add CAPTCHA to login forms\n5. Use rate limiting (max 5 attempts/minute)\n6. Change all potentially compromised passwords\n\n**Real Example:** The 2014 iCloud celebrity photo leak used brute force attacks on Apple accounts.",
        },
        "ransomware": {
            "answer": "**Ransomware**\n\nMalware that encrypts all your files and demands cryptocurrency payment for the decryption key.\n\n**How to respond:**\n1. Disconnect from network IMMEDIATELY (pull Ethernet, disable WiFi)\n2. Do NOT pay the ransom (no guarantee of decryption)\n3. Preserve the system for forensics\n4. Report to law enforcement and cybercrime authorities\n5. Restore from clean, offline backups\n6. Identify and patch the entry point\n\n**Real Example:** WannaCry (2017) infected 200,000+ computers in 150 countries, including NHS hospitals. Demanded Bitcoin payments.",
        },
        "phishing": {
            "answer": "**Phishing**\n\nFake emails, websites, or messages impersonating trusted companies to steal your credentials, financial information, or install malware.\n\n**How to respond:**\n1. Do NOT click any suspicious links\n2. If you clicked — change passwords immediately\n3. Enable Multi-Factor Authentication\n4. Report the phishing email to your IT team\n5. Check for unauthorized account activity\n6. Run a full antivirus scan\n\n**Types:** Spear phishing (targeted), Whaling (executives), Vishing (voice), Smishing (SMS)",
        },
        "malware": {
            "answer": "**Malware (Malicious Software)**\n\nUmbrella term for viruses, trojans, worms, spyware, ransomware, and other harmful software.\n\n**How to respond:**\n1. Isolate the infected machine from the network\n2. Run a full antivirus/anti-malware scan\n3. Remove identified malicious files\n4. Update all software and patch vulnerabilities\n5. Change all passwords from a clean device\n6. Monitor for persistence mechanisms\n\n**Types:** Virus, Trojan, Worm, Spyware, Adware, Rootkit, Keylogger, Ransomware",
        },
        "hacked": {
            "answer": "**What to do if you've been hacked:**\n\n**Immediate Steps:**\n1. Disconnect from the network immediately\n2. Preserve all logs and evidence\n3. Notify your security team / IT department\n4. Change ALL passwords from a clean device\n5. Enable MFA on all accounts\n\n**Investigation:**\n6. Identify the attack vector (how they got in)\n7. Check for backdoors and persistence\n8. Review all user accounts for unauthorized changes\n9. Scan all systems for malware\n\n**Recovery:**\n10. Restore from clean backups\n11. Patch the vulnerability that was exploited\n12. Report to law enforcement if required",
        },
        "sql injection": {
            "answer": "**SQL Injection**\n\nInserting malicious SQL code into input fields to manipulate the database — steal data, delete records, or gain admin access.\n\n**How to respond:**\n1. Take the affected application offline\n2. Patch using parameterized queries / prepared statements\n3. Audit the database for unauthorized changes\n4. Enable Web Application Firewall (WAF)\n5. Review all input fields for vulnerabilities\n\n**Example:** Typing `' OR 1=1 --` in a login form to bypass authentication and access all accounts.",
        },
        "mitm": {
            "answer": "**Man-in-the-Middle (MITM) Attack**\n\nAttacker secretly intercepts communication between two parties, reading or modifying data in transit.\n\n**How to respond:**\n1. Use HTTPS for ALL web connections\n2. Enable VPN on public/untrusted networks\n3. Verify SSL certificates (look for padlock icon)\n4. Avoid public WiFi for banking and sensitive tasks\n5. Use certificate pinning in applications\n\n**Example:** On cafe WiFi, an attacker intercepts your banking session and steals credentials.",
        },
        "xss": {
            "answer": "**Cross-Site Scripting (XSS)**\n\nInjecting malicious JavaScript into web pages that executes in other users' browsers.\n\n**Types:**\n- **Stored XSS:** Malicious script stored on the server (in database/comments)\n- **Reflected XSS:** Script included in URL and reflected back\n- **DOM-based XSS:** Manipulates the page's DOM directly\n\n**Prevention:**\n1. Input validation and output encoding\n2. Content Security Policy (CSP) headers\n3. HttpOnly and Secure cookie flags\n4. Web Application Firewall (WAF)\n5. Use modern frameworks with XSS protection built-in",
        },
        "csrf": {
            "answer": "**Cross-Site Request Forgery (CSRF)**\n\nTricks a logged-in user into unknowingly submitting a malicious request (e.g., transferring money, changing email).\n\n**How it works:**\n1. Victim is logged into their bank account\n2. Victim visits attacker's website\n3. Attacker's site sends hidden request to bank\n4. Bank thinks it's the victim's request and processes it\n\n**Prevention:**\n1. Anti-CSRF tokens in all forms\n2. SameSite cookie attribute\n3. Verify Referer/Origin headers\n4. Re-authenticate for sensitive actions",
        },
        "firewall": {
            "answer": "**Firewalls**\n\nA firewall filters incoming and outgoing network traffic based on predefined security rules.\n\n**Types:**\n- **Packet Filtering:** Examines packet headers (IP, port) — fastest but least secure\n- **Stateful Inspection:** Tracks connection state — better security\n- **Application Layer (WAF):** Inspects content of web traffic — detects SQL injection, XSS\n- **Next-Gen Firewall (NGFW):** Combines all above + IPS + deep packet inspection\n\n**Best Practices:**\n1. Default deny (block everything, allow specific)\n2. Regular rule review\n3. Enable logging\n4. Keep firmware updated",
        },
        "vpn": {
            "answer": "**VPN (Virtual Private Network)**\n\nEncrypts all internet traffic between your device and the VPN server, hiding your activity from eavesdroppers.\n\n**How it works:**\n1. Your device creates encrypted tunnel to VPN server\n2. All traffic passes through this encrypted tunnel\n3. Your real IP is hidden; VPN server's IP is shown\n4. ISP and network admins can't see your activity\n\n**When to use:**\n- Public WiFi networks\n- Accessing company resources remotely\n- Bypassing geo-restrictions\n- Protecting privacy from ISP monitoring\n\n**Protocols:** WireGuard (fastest), OpenVPN (most reliable), IKEv2 (mobile-friendly)",
        },
        "encryption": {
            "answer": "**Encryption**\n\nProcess of converting readable data (plaintext) into unreadable data (ciphertext) using a key.\n\n**Symmetric Encryption (Same key):**\n- AES-256 — Current gold standard\n- Used for: File encryption, disk encryption, VPNs\n- Fast but key distribution is challenging\n\n**Asymmetric Encryption (Public/Private keys):**\n- RSA, ECC — Public key encrypts, private key decrypts\n- Used for: HTTPS, email encryption, digital signatures\n- Slower but solves key distribution\n\n**Hashing (One-way):**\n- SHA-256, bcrypt — Cannot be reversed\n- Used for: Password storage, file integrity",
        },
        "ids": {
            "answer": "**IDS (Intrusion Detection System)**\n\nMonitors network traffic and system activity for suspicious behavior or known attack patterns.\n\n**This project IS an IDS!** It uses a Random Forest ML model trained on the NSL-KDD dataset to classify network traffic as normal or attack.\n\n**Types:**\n- **Signature-based:** Matches known attack patterns (like antivirus)\n- **Anomaly-based:** Detects deviations from normal behavior (like this project)\n- **NIDS:** Network-based (monitors network traffic)\n- **HIDS:** Host-based (monitors single system)\n\n**IDS vs IPS:**\n- IDS = Detection only (alerts)\n- IPS = Prevention (blocks automatically)",
        },
        "ips": {
            "answer": "**IPS (Intrusion Prevention System)**\n\nLike an IDS but actively blocks detected threats instead of just alerting.\n\n**Comparison:**\n| Feature | IDS | IPS |\n|---------|-----|-----|\n| Detection | ✅ | ✅ |\n| Alerting | ✅ | ✅ |\n| Blocking | ❌ | ✅ |\n| Inline | ❌ | ✅ |\n| Latency | None | Some |\n\n**Best practice:** Use both — IDS for monitoring + IPS for critical protection.",
        },
        "zero trust": {
            "answer": "**Zero Trust Architecture**\n\n\"Never trust, always verify.\" Every user, device, and network flow is authenticated and authorized, regardless of location.\n\n**Core Principles:**\n1. Verify explicitly — Always authenticate and authorize\n2. Least privilege access — Give minimum necessary permissions\n3. Assume breach — Design as if attackers are already inside\n\n**Implementation:**\n- Multi-factor authentication everywhere\n- Micro-segmentation of networks\n- Continuous monitoring and validation\n- Encrypt all data in transit and at rest",
        },
        "social engineering": {
            "answer": "**Social Engineering**\n\nManipulating people into breaking security procedures or revealing confidential information.\n\n**Types:**\n- **Phishing:** Fake emails/messages\n- **Pretexting:** Creating a fabricated scenario\n- **Baiting:** Leaving infected USB drives\n- **Tailgating:** Following authorized person through secure door\n- **Quid pro quo:** Offering something in exchange for info\n- **Vishing:** Voice-based phishing (phone calls)\n\n**Defense:** Security awareness training, verify requests through separate channel, healthy skepticism",
        },
        "cia triad": {
            "answer": "**CIA Triad — The Three Pillars of Information Security**\n\n🔐 **Confidentiality:** Only authorized users can access data\n- Encryption, access controls, authentication\n\n✅ **Integrity:** Data is accurate and hasn't been tampered with\n- Hashing, digital signatures, checksums\n\n⚡ **Availability:** Systems and data are accessible when needed\n- Redundancy, backups, DDoS protection\n\nEvery security decision should protect at least one of these pillars.",
        },
        "nmap": {
            "answer": "**Nmap (Network Mapper)**\n\nThe most popular network scanning tool used by both security professionals and attackers.\n\n**Common Scans:**\n- `nmap -sS target` — SYN scan (stealth)\n- `nmap -sV target` — Version detection\n- `nmap -O target` — OS detection\n- `nmap -A target` — Aggressive scan (all info)\n- `nmap -p- target` — Scan all 65535 ports\n\n**Detection:** This IDS can detect nmap scans through unusual connection patterns, high port scan rates, and SYN flood indicators.",
        },
        "password": {
            "answer": "**Password Security Best Practices**\n\n**Creating Strong Passwords:**\n- Minimum 12 characters (16+ recommended)\n- Mix uppercase, lowercase, numbers, symbols\n- Don't use dictionary words or personal info\n- Use passphrases: \"correct horse battery staple\"\n\n**Management:**\n- Use a password manager (Bitwarden, 1Password)\n- Unique password for every account\n- Enable MFA on all important accounts\n- Never share passwords\n\n**Storage (for developers):**\n- Never store plaintext passwords\n- Use bcrypt, Argon2, or scrypt for hashing\n- Add unique salt per user\n- Use pepper (server-side secret)",
        },
        "siem": {
            "answer": "**SIEM (Security Information and Event Management)**\n\nAggregates security logs from across the organization and uses correlation rules + ML to detect complex attacks.\n\n**Core Functions:**\n1. Log collection from all sources\n2. Real-time event correlation\n3. Threat detection and alerting\n4. Incident investigation tools\n5. Compliance reporting\n\n**Popular SIEM Tools:** Splunk, IBM QRadar, Microsoft Sentinel, Elastic SIEM, AlienVault\n\n**How it helps:** A single failed login is normal. SIEM correlates 100 failed logins from different sources to detect a brute force campaign.",
        },
        "owasp": {
            "answer": "**OWASP Top 10 — Web Application Security Risks**\n\n1. **A01: Broken Access Control** — Users access unauthorized data\n2. **A02: Cryptographic Failures** — Weak or missing encryption\n3. **A03: Injection** — SQL, NoSQL, OS command injection\n4. **A04: Insecure Design** — Missing security architecture\n5. **A05: Security Misconfiguration** — Default settings, open cloud storage\n6. **A06: Vulnerable Components** — Using outdated libraries\n7. **A07: Authentication Failures** — Weak login mechanisms\n8. **A08: Data Integrity Failures** — Unverified updates, CI/CD issues\n9. **A09: Logging & Monitoring Failures** — No audit trail\n10. **A10: SSRF** — Server makes requests to unintended locations",
        },
        "help": {
            "answer": "**🤖 I can help with these cybersecurity topics:**\n\n**🗡️ Attacks:** DDoS, DoS, Phishing, Ransomware, SQL Injection, XSS, CSRF, Brute Force, MITM, Port Scan, ARP Spoofing, DNS Poisoning, Social Engineering, Zero-Day\n\n**🛡️ Defense:** Firewall, IDS, IPS, VPN, Encryption, Password Security, SIEM, Zero Trust, MFA\n\n**📋 Frameworks:** CIA Triad, OWASP Top 10, MITRE ATT&CK, NIST\n\n**🔧 Tools:** Nmap, Wireshark\n\n**Try asking:**\n- \"What is a DDoS attack?\"\n- \"How to prevent SQL injection?\"\n- \"Explain zero trust\"\n- \"What is the CIA triad?\"",
        },
    }

    # Gemini AI function
    def get_gemini_response(user_msg, chat_history):
        """Get response from Google Gemini AI"""
        api_key = st.session_state.get('gemini_api_key', '')
        if not api_key or not GEMINI_AVAILABLE:
            return None

        try:
            genai.configure(api_key=api_key)
            model_ai = genai.GenerativeModel('gemini-2.0-flash')

            system_prompt = """You are Cyber Sentinel AI, an expert cybersecurity assistant integrated into an Intrusion Detection System (IDS) dashboard. 

Your role:
- Answer ANY cybersecurity question clearly and thoroughly
- Provide practical, actionable advice
- Use real-world examples when helpful
- Explain technical concepts in simple terms
- Stay focused on cybersecurity topics
- If asked about non-cybersecurity topics, politely redirect to security topics

Format your responses with:
- Bold headers for sections
- Numbered steps for procedures
- Bullet points for lists
- Clear, concise language

Context: You are part of a university major project IDS built with Random Forest ML model on NSL-KDD dataset, using SHAP for explainability, with a honeypot, URL scanner, and this chatbot."""

            # Build conversation context
            messages = [system_prompt + "\n\n"]
            for msg in chat_history[-6:]:  # Last 6 messages for context
                role = "User" if msg['role'] == 'user' else "Assistant"
                messages.append(f"{role}: {msg['text']}\n")
            messages.append(f"User: {user_msg}\nAssistant:")

            response = model_ai.generate_content(''.join(messages))
            return response.text
        except Exception as e:
            return None

    def get_fallback_response(user_msg):
        """Enhanced keyword-based fallback"""
        msg = user_msg.lower().strip()
        sorted_keys = sorted(fallback_responses.keys(), key=len, reverse=True)

        # Check for topic matches
        for key in sorted_keys:
            if key in msg:
                return fallback_responses[key]['answer']

        # Pattern matching for common questions
        if any(w in msg for w in ['what is', 'explain', 'define', 'tell me about']):
            for key in sorted_keys:
                if key in msg:
                    return fallback_responses[key]['answer']

        if any(w in msg for w in ['how to protect', 'how to prevent', 'how to stop', 'how to defend']):
            return fallback_responses.get('help', {}).get('answer', "Type 'help' to see available topics.")

        if any(w in msg for w in ['hello', 'hi', 'hey', 'greetings']):
            return "👋 Hello! I'm **Cyber Sentinel AI**, your cybersecurity assistant.\n\nI can help you with questions about:\n- 🗡️ **Cyber attacks** (DDoS, phishing, ransomware, etc.)\n- 🛡️ **Defense strategies** (firewalls, encryption, VPN)\n- 📋 **Security frameworks** (OWASP, CIA Triad)\n\nType **'help'** for a full list of topics, or just ask any cybersecurity question!"

        if any(w in msg for w in ['thank', 'thanks', 'thx']):
            return "You're welcome! 😊 Feel free to ask more cybersecurity questions anytime. Stay safe! 🛡️"

        if any(w in msg for w in ['who are you', 'what are you', 'what can you do']):
            return "I'm **Cyber Sentinel AI** 🛡️, an AI-powered cybersecurity assistant.\n\nI'm part of an Intrusion Detection System (IDS) dashboard that uses Machine Learning to detect network attacks.\n\n**My capabilities:**\n- Answer cybersecurity questions\n- Explain attack types and defenses\n- Provide incident response guidance\n- Explain security frameworks and best practices\n\nType **'help'** to see all topics I can discuss!"

        return "🤔 I'm not sure about that specific topic. Here are some things I can help with:\n\n- **\"What is DDoS?\"** — Learn about DDoS attacks\n- **\"How to prevent SQL injection?\"** — Defense strategies\n- **\"Explain phishing\"** — Understanding social engineering\n- **\"What is the CIA triad?\"** — Security fundamentals\n\nType **'help'** for a complete list of topics, or try rephrasing your question!"

    def get_response(user_msg):
        """Main function: tries Gemini first, falls back to hardcoded"""
        # Try Gemini first
        chat_history = st.session_state.get('chat_history', [])
        gemini_resp = get_gemini_response(user_msg, chat_history)
        if gemini_resp:
            return gemini_resp
        # Fallback
        return get_fallback_response(user_msg)

    # AI status indicator
    has_api_key = bool(st.session_state.get('gemini_api_key', ''))
    if has_api_key and GEMINI_AVAILABLE:
        st.markdown("""
        <div class='glass-card-green' style='padding:10px 16px;display:flex;align-items:center;gap:10px;'>
            <span class='status-live'></span>
            <span style='color:#00ff88;font-weight:600;'>Gemini AI Connected</span>
            <span style='color:#8899aa;font-size:0.85rem;'>— Can answer any cybersecurity question</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='glass-card-yellow' style='padding:10px 16px;'>
            <span style='color:#ffaa00;font-weight:600;'>⚠️ Running in Offline Mode</span>
            <span style='color:#8899aa;font-size:0.85rem;'>— Using built-in knowledge base (30+ topics). Add a Gemini API key in the sidebar for unlimited AI responses.</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Suggested questions
    st.markdown("##### 💡 Quick Questions")
    sq_col1, sq_col2, sq_col3, sq_col4 = st.columns(4)
    with sq_col1:
        if st.button("What is DDoS?", key="sq1"):
            st.session_state.quick_q = "What is a DDoS attack?"
            st.rerun()
    with sq_col2:
        if st.button("Prevent ransomware?", key="sq2"):
            st.session_state.quick_q = "How to prevent ransomware?"
            st.rerun()
    with sq_col3:
        if st.button("Explain phishing", key="sq3"):
            st.session_state.quick_q = "Explain phishing attacks"
            st.rerun()
    with sq_col4:
        if st.button("What is CIA Triad?", key="sq4"):
            st.session_state.quick_q = "What is the CIA triad?"
            st.rerun()

    st.markdown("---")

    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{
            "role": "bot",
            "text": "👋 Hello! I'm **Cyber Sentinel AI**, your cybersecurity assistant.\n\nI can answer questions about cyber attacks, defense strategies, security frameworks, and more.\n\nType **'help'** for a list of topics, or just ask any cybersecurity question!"
        }]

    # Handle quick questions
    if 'quick_q' in st.session_state:
        quick = st.session_state.pop('quick_q')
        st.session_state.chat_history.append({"role": "user", "text": quick})
        response = get_response(quick)
        st.session_state.chat_history.append({"role": "bot", "text": response})

    # Display chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'bot':
                st.markdown(f"<div class='chat-bot'>🤖 {msg['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-user'>👤 {msg['text']}</div>", unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ask any cybersecurity question...")

    if user_input and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        with st.spinner("Thinking..."):
            response = get_response(user_input)
        st.session_state.chat_history.append({"role": "bot", "text": response})
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_history = [{
            "role": "bot",
            "text": "👋 Hello! I'm **Cyber Sentinel AI**, your cybersecurity assistant.\n\nI can answer questions about cyber attacks, defense strategies, security frameworks, and more.\n\nType **'help'** for a list of topics, or just ask any cybersecurity question!"
        }]
        st.rerun()


# ══════════════════════════════════════════════════════════
#                   LIVE NETWORK MONITOR
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "live_monitor":
    st.markdown("<div class='section-header'>📡 Live Network Traffic Monitor</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'><span class='live-dot'></span> Simulated real-time network traffic analysis showing packet flow, threat detection rates, and protocol distribution.</div>", unsafe_allow_html=True)

    # Generate simulated live data
    if 'monitor_data' not in st.session_state:
        st.session_state.monitor_data = []
        st.session_state.monitor_threats = []

    # Simulate new data points
    now = datetime.now()
    np.random.seed(int(now.timestamp()) % 10000)
    time_points = [now - timedelta(seconds=i*5) for i in range(30, 0, -1)]
    traffic_values = [max(0, int(300 + 150 * np.sin(i/4) + np.random.normal(0, 40))) for i in range(30)]
    threat_values = [max(0, int(15 + 10 * np.sin(i/3 + 2) + np.random.normal(0, 8))) for i in range(30)]

    # Live metrics
    current_traffic = traffic_values[-1]
    current_threats = threat_values[-1]
    avg_traffic = int(np.mean(traffic_values))
    peak_traffic = max(traffic_values)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Current Packets/s", f"{current_traffic}", delta=f"{current_traffic - traffic_values[-2]:+d}")
    col2.metric("⚠️ Active Threats", f"{current_threats}", delta=f"{current_threats - threat_values[-2]:+d}", delta_color="inverse")
    col3.metric("📊 Avg Traffic", f"{avg_traffic}/s")
    col4.metric("🔺 Peak Traffic", f"{peak_traffic}/s")

    st.markdown("---")

    # Traffic and threats chart
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("##### 📈 Network Traffic Flow")
        fig_live, ax_live = plt.subplots(figsize=(6, 3.5))
        fig_live.patch.set_facecolor('#0d1117')
        ax_live.set_facecolor('#0d1117')
        time_labels = [t.strftime('%H:%M:%S') for t in time_points]
        ax_live.fill_between(range(30), traffic_values, alpha=0.3, color='#00d4ff')
        ax_live.plot(range(30), traffic_values, color='#00d4ff', linewidth=2)
        ax_live.set_ylabel('Packets/sec', color='#8899aa', fontsize=10)
        ax_live.set_xticks([0, 9, 19, 29])
        ax_live.set_xticklabels([time_labels[0], time_labels[9], time_labels[19], time_labels[29]], fontsize=8)
        ax_live.tick_params(colors='#8899aa')
        ax_live.spines['top'].set_visible(False)
        ax_live.spines['right'].set_visible(False)
        ax_live.spines['bottom'].set_color('#2a3040')
        ax_live.spines['left'].set_color('#2a3040')
        plt.tight_layout()
        st.pyplot(fig_live)

    with col_chart2:
        st.markdown("##### 🚨 Threat Detection Rate")
        fig_threat_live, ax_tl = plt.subplots(figsize=(6, 3.5))
        fig_threat_live.patch.set_facecolor('#0d1117')
        ax_tl.set_facecolor('#0d1117')
        ax_tl.fill_between(range(30), threat_values, alpha=0.3, color='#ff4444')
        ax_tl.plot(range(30), threat_values, color='#ff4444', linewidth=2)
        ax_tl.set_ylabel('Threats/min', color='#8899aa', fontsize=10)
        ax_tl.set_xticks([0, 9, 19, 29])
        ax_tl.set_xticklabels([time_labels[0], time_labels[9], time_labels[19], time_labels[29]], fontsize=8)
        ax_tl.tick_params(colors='#8899aa')
        ax_tl.spines['top'].set_visible(False)
        ax_tl.spines['right'].set_visible(False)
        ax_tl.spines['bottom'].set_color('#2a3040')
        ax_tl.spines['left'].set_color('#2a3040')
        plt.tight_layout()
        st.pyplot(fig_threat_live)

    st.markdown("---")

    # Protocol distribution and connection stats
    col_proto, col_stats = st.columns(2)

    with col_proto:
        st.markdown("##### 🌐 Protocol Distribution")
        fig_proto, ax_proto = plt.subplots(figsize=(5, 3.5))
        fig_proto.patch.set_facecolor('#0d1117')
        ax_proto.set_facecolor('#0d1117')
        protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'DNS', 'SSH']
        proto_vals = [45, 22, 8, 15, 7, 3]
        colors_proto = ['#00d4ff', '#00ff88', '#ffaa00', '#ff4444', '#aa66ff', '#ff66aa']
        wedges, texts, autotexts = ax_proto.pie(
            proto_vals, labels=protocols, colors=colors_proto,
            autopct='%1.0f%%', startangle=90,
            textprops={'color': 'white', 'fontsize': 9},
            wedgeprops={'edgecolor': '#0d1117', 'linewidth': 1.5}
        )
        for t in autotexts:
            t.set_fontweight('bold')
            t.set_fontsize(8)
        ax_proto.axis('equal')
        plt.tight_layout()
        st.pyplot(fig_proto)

    with col_stats:
        st.markdown("##### 📋 Connection Statistics")
        st.markdown(f"""
        <div class='glass-card' style='padding:16px;'>
            <table style='width:100%;color:#ccc;font-size:0.9rem;'>
                <tr><td style='padding:8px 0;color:#8899aa;'>Active Connections</td>
                    <td style='text-align:right;font-weight:600;color:#00d4ff;'>{random.randint(120, 250)}</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Blocked IPs (today)</td>
                    <td style='text-align:right;font-weight:600;color:#ff4444;'>{random.randint(5, 30)}</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Bandwidth Usage</td>
                    <td style='text-align:right;font-weight:600;color:#00ff88;'>{random.randint(40, 85)}%</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Avg Response Time</td>
                    <td style='text-align:right;font-weight:600;'>{random.randint(12, 45)}ms</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Uptime</td>
                    <td style='text-align:right;font-weight:600;color:#00ff88;'>99.97%</td></tr>
                <tr><td style='padding:8px 0;color:#8899aa;'>Last Scan</td>
                    <td style='text-align:right;font-weight:500;'>{datetime.now().strftime('%H:%M:%S')}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # Auto-refresh
    st.markdown("---")
    auto_refresh = st.checkbox("🔄 Auto-refresh every 10 seconds", value=False)
    if auto_refresh:
        time.sleep(10)
        st.rerun()


# ══════════════════════════════════════════════════════════
#                   PASSWORD STRENGTH CHECKER
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "password":
    st.markdown("<div class='section-header'>🔑 Password Strength Checker</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Test how strong your passwords are. We analyze length, complexity, patterns, and common vulnerabilities. Nothing is stored or sent anywhere.</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='glass-card-green' style='padding:12px 18px;'>
        <span style='color:#00ff88;font-weight:600;'>🔒 Privacy Notice:</span>
        <span style='color:#aabbcc;'> Your password is analyzed locally in your browser session. It is never stored, logged, or transmitted.</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    pwd_input = st.text_input("Enter a password to test:", type="password", placeholder="Type a password...", key="pwd_check")

    if pwd_input:
        # Analysis
        length = len(pwd_input)
        has_upper = bool(re.search(r'[A-Z]', pwd_input))
        has_lower = bool(re.search(r'[a-z]', pwd_input))
        has_digit = bool(re.search(r'\d', pwd_input))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:",./<>?|\\~`]', pwd_input))
        has_space = ' ' in pwd_input

        # Common passwords check
        common_passwords = [
            'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey', 'master',
            'dragon', 'login', 'princess', 'admin', 'welcome', 'letmein', 'football',
            'shadow', 'sunshine', 'trustno1', 'iloveyou', 'batman', 'password1',
            'password123', '1234567890', '000000', '111111', 'donald', 'computer',
        ]
        is_common = pwd_input.lower() in common_passwords

        # Sequential / repeated patterns
        has_sequential = bool(re.search(r'(012|123|234|345|456|567|678|789|abc|bcd|cde|def)', pwd_input.lower()))
        has_repeated = bool(re.search(r'(.)\1{2,}', pwd_input))

        # Calculate score
        score = 0
        checks = []

        # Length scoring
        if length >= 16:
            score += 30
            checks.append(("✅", "Length: Excellent", f"{length} characters — very strong"))
        elif length >= 12:
            score += 25
            checks.append(("✅", "Length: Good", f"{length} characters — solid length"))
        elif length >= 8:
            score += 15
            checks.append(("⚠️", "Length: Acceptable", f"{length} characters — could be longer"))
        else:
            score += 5
            checks.append(("❌", "Length: Too Short", f"{length} characters — minimum 8 recommended"))

        # Character variety
        if has_upper:
            score += 10
            checks.append(("✅", "Uppercase Letters", "Contains A-Z"))
        else:
            checks.append(("❌", "No Uppercase Letters", "Add A-Z for stronger password"))

        if has_lower:
            score += 10
            checks.append(("✅", "Lowercase Letters", "Contains a-z"))
        else:
            checks.append(("❌", "No Lowercase Letters", "Add a-z for stronger password"))

        if has_digit:
            score += 10
            checks.append(("✅", "Numbers", "Contains 0-9"))
        else:
            checks.append(("❌", "No Numbers", "Add 0-9 for stronger password"))

        if has_special:
            score += 15
            checks.append(("✅", "Special Characters", "Contains !@#$% etc."))
        else:
            checks.append(("⚠️", "No Special Characters", "Add !@#$%^&* for much stronger password"))

        # Penalty scoring
        if is_common:
            score = max(5, score - 40)
            checks.append(("❌", "Common Password!", "This is in the top 25 most common passwords"))

        if has_sequential:
            score = max(5, score - 15)
            checks.append(("⚠️", "Sequential Pattern", "Contains sequential characters like 123 or abc"))

        if has_repeated:
            score = max(5, score - 10)
            checks.append(("⚠️", "Repeated Characters", "Contains repeated characters like aaa or 111"))

        # Unique characters bonus
        unique_ratio = len(set(pwd_input)) / max(length, 1)
        if unique_ratio > 0.8:
            score += 10
            checks.append(("✅", "High Variety", f"{len(set(pwd_input))} unique characters — excellent diversity"))

        score = min(100, max(0, score))

        # Determine strength
        if score >= 80:
            strength = "VERY STRONG"
            color = "#00ff88"
            emoji = "🏆"
        elif score >= 60:
            strength = "STRONG"
            color = "#00d4ff"
            emoji = "💪"
        elif score >= 40:
            strength = "MODERATE"
            color = "#ffaa00"
            emoji = "⚠️"
        elif score >= 20:
            strength = "WEAK"
            color = "#ff8800"
            emoji = "😟"
        else:
            strength = "VERY WEAK"
            color = "#ff4444"
            emoji = "🚨"

        # Crack time estimation
        charset_size = 0
        if has_lower: charset_size += 26
        if has_upper: charset_size += 26
        if has_digit: charset_size += 10
        if has_special: charset_size += 32
        if has_space: charset_size += 1
        if charset_size == 0: charset_size = 26

        combinations = charset_size ** length
        guesses_per_sec = 10_000_000_000  # 10 billion (GPU-accelerated)
        seconds_to_crack = combinations / guesses_per_sec / 2  # average case

        if seconds_to_crack < 1:
            crack_time = "Instantly"
        elif seconds_to_crack < 60:
            crack_time = f"{int(seconds_to_crack)} seconds"
        elif seconds_to_crack < 3600:
            crack_time = f"{int(seconds_to_crack/60)} minutes"
        elif seconds_to_crack < 86400:
            crack_time = f"{int(seconds_to_crack/3600)} hours"
        elif seconds_to_crack < 86400 * 365:
            crack_time = f"{int(seconds_to_crack/86400)} days"
        elif seconds_to_crack < 86400 * 365 * 1000:
            crack_time = f"{int(seconds_to_crack/(86400*365))} years"
        elif seconds_to_crack < 86400 * 365 * 1_000_000:
            crack_time = f"{int(seconds_to_crack/(86400*365*1000))}K years"
        else:
            crack_time = "Millions of years"

        # Display results
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:30px;'>
            <div style='font-size:2.5rem;'>{emoji}</div>
            <div class='strength-label' style='color:{color};margin-top:8px;'>{strength}</div>
            <div style='background:rgba(255,255,255,0.1);border-radius:4px;height:10px;margin:16px auto;max-width:400px;'>
                <div style='background:{color};height:10px;border-radius:4px;width:{score}%;transition:all 0.5s ease;'></div>
            </div>
            <div style='color:#8899aa;font-size:1.1rem;'>Score: <span style='color:{color};font-weight:700;'>{score}/100</span></div>
            <div style='color:#8899aa;margin-top:12px;'>⏱️ Estimated crack time (GPU): <span style='color:{color};font-weight:600;'>{crack_time}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Detailed checks
        st.markdown("##### 📋 Detailed Analysis")
        for icon, title, desc in checks:
            bg = 'rgba(0,255,136,0.05)' if icon == '✅' else ('rgba(255,170,0,0.05)' if icon == '⚠️' else 'rgba(255,68,68,0.05)')
            st.markdown(f"""
            <div style='background:{bg};border-radius:10px;padding:10px 16px;margin:4px 0;'>
                <span style='font-size:1.1rem;'>{icon}</span>
                <span style='color:#ddd;font-weight:600;margin:0 8px;'>{title}</span>
                <span style='color:#8899aa;'>— {desc}</span>
            </div>
            """, unsafe_allow_html=True)

        # Tips
        st.markdown("---")
        st.markdown("##### 💡 Password Tips")
        st.markdown("""
        <div class='glass-card'>
            <div style='color:#aabbcc;font-size:0.9rem;line-height:1.8;'>
                <b>Creating an uncrackable password:</b><br>
                🔹 Use a <b>passphrase</b>: "correct horse battery staple" is stronger than "P@ssw0rd!"<br>
                🔹 Make it <b>16+ characters</b> — length beats complexity every time<br>
                🔹 Use a <b>password manager</b> (Bitwarden, 1Password) to generate and store unique passwords<br>
                🔹 <b>Never reuse</b> passwords across accounts<br>
                🔹 Enable <b>2FA/MFA</b> — even if password is stolen, attacker can't log in<br>
                🔹 <b>Avoid</b>: birthdays, pet names, dictionary words, keyboard patterns (qwerty)
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Show example before user types
        st.markdown("""
        <div class='glass-card' style='text-align:center;padding:40px;'>
            <div style='font-size:3rem;'>🔑</div>
            <div style='color:#8899aa;margin-top:12px;font-size:1.1rem;'>Type a password above to see its strength analysis</div>
            <div style='color:#556677;margin-top:8px;font-size:0.85rem;'>We'll check length, complexity, common patterns, and estimate crack time</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                     ABOUT PROJECT
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "about":
    st.markdown("<div class='section-header'>ℹ️ About This Project</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Cyber Sentinel AI — Major Project 2026, BMS Institute of Technology and Management, Bengaluru.</div>", unsafe_allow_html=True)

    # Project overview
    st.markdown("""
    <div class='glass-card'>
        <div style='color:#00d4ff;font-weight:700;font-size:1.2rem;margin-bottom:12px;'>🛡️ Project Overview</div>
        <div style='color:#aabbcc;font-size:0.95rem;line-height:1.8;'>
            <b>Cyber Sentinel AI</b> is an advanced AI-powered <b>Intrusion Detection System (IDS)</b> that uses Machine Learning
            to detect network intrusions in real-time. The system analyzes network traffic patterns and classifies them
            as <span style='color:#00ff88;font-weight:600;'>Normal</span> or
            <span style='color:#ff4444;font-weight:600;'>Attack</span> using a Random Forest classifier trained on the
            industry-standard NSL-KDD dataset.
            <br><br>
            The dashboard provides comprehensive security monitoring with explainable AI (XAI) using SHAP values,
            a honeypot trap system, URL safety scanner, password strength checker, threat knowledge base, and an
            AI-powered chatbot for cybersecurity guidance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Architecture
    st.markdown("##### 🏗️ System Architecture")
    arch_col1, arch_col2, arch_col3, arch_col4, arch_col5 = st.columns(5)
    with arch_col1:
        st.markdown("""
        <div class='arch-box'>
            <div style='font-size:1.8rem;'>📡</div>
            <div style='font-weight:600;color:#00d4ff;margin-top:8px;'>Data Source</div>
            <div style='font-size:0.75rem;color:#8899aa;margin-top:4px;'>NSL-KDD Dataset<br>Network Traffic</div>
        </div>
        """, unsafe_allow_html=True)
    with arch_col2:
        st.markdown("""
        <div class='arch-box'>
            <div style='font-size:1.8rem;'>⚙️</div>
            <div style='font-weight:600;color:#00d4ff;margin-top:8px;'>Preprocessing</div>
            <div style='font-size:0.75rem;color:#8899aa;margin-top:4px;'>Label Encoding<br>Feature Selection</div>
        </div>
        """, unsafe_allow_html=True)
    with arch_col3:
        st.markdown("""
        <div class='arch-box'>
            <div style='font-size:1.8rem;'>🧠</div>
            <div style='font-weight:600;color:#00d4ff;margin-top:8px;'>ML Model</div>
            <div style='font-size:0.75rem;color:#8899aa;margin-top:4px;'>Random Forest<br>100 Decision Trees</div>
        </div>
        """, unsafe_allow_html=True)
    with arch_col4:
        st.markdown("""
        <div class='arch-box'>
            <div style='font-size:1.8rem;'>🔍</div>
            <div style='font-weight:600;color:#00d4ff;margin-top:8px;'>XAI Engine</div>
            <div style='font-size:0.75rem;color:#8899aa;margin-top:4px;'>SHAP Values<br>Feature Impact</div>
        </div>
        """, unsafe_allow_html=True)
    with arch_col5:
        st.markdown("""
        <div class='arch-box'>
            <div style='font-size:1.8rem;'>📊</div>
            <div style='font-weight:600;color:#00d4ff;margin-top:8px;'>Dashboard</div>
            <div style='font-size:0.75rem;color:#8899aa;margin-top:4px;'>Streamlit UI<br>Real-time Viz</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Tech stack
    st.markdown("---")
    st.markdown("##### 🛠️ Technology Stack")

    tech_col1, tech_col2 = st.columns(2)
    with tech_col1:
        st.markdown("""
        <div class='glass-card'>
            <div style='color:#00d4ff;font-weight:700;margin-bottom:12px;'>🐍 Backend & ML</div>
            <table style='width:100%;color:#ccc;font-size:0.9rem;'>
                <tr><td style='padding:6px 0;'>Python 3.x</td><td style='color:#8899aa;'>Core programming language</td></tr>
                <tr><td style='padding:6px 0;'>Scikit-learn</td><td style='color:#8899aa;'>Random Forest classifier</td></tr>
                <tr><td style='padding:6px 0;'>SHAP</td><td style='color:#8899aa;'>Explainable AI framework</td></tr>
                <tr><td style='padding:6px 0;'>Pandas / NumPy</td><td style='color:#8899aa;'>Data processing</td></tr>
                <tr><td style='padding:6px 0;'>Joblib</td><td style='color:#8899aa;'>Model serialization</td></tr>
                <tr><td style='padding:6px 0;'>Google Gemini</td><td style='color:#8899aa;'>AI chatbot engine</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with tech_col2:
        st.markdown("""
        <div class='glass-card'>
            <div style='color:#00d4ff;font-weight:700;margin-bottom:12px;'>🎨 Frontend & Tools</div>
            <table style='width:100%;color:#ccc;font-size:0.9rem;'>
                <tr><td style='padding:6px 0;'>Streamlit</td><td style='color:#8899aa;'>Web dashboard framework</td></tr>
                <tr><td style='padding:6px 0;'>Matplotlib</td><td style='color:#8899aa;'>Data visualization</td></tr>
                <tr><td style='padding:6px 0;'>Custom CSS</td><td style='color:#8899aa;'>Glassmorphism UI design</td></tr>
                <tr><td style='padding:6px 0;'>Socket (Python)</td><td style='color:#8899aa;'>Honeypot server</td></tr>
                <tr><td style='padding:6px 0;'>Regex</td><td style='color:#8899aa;'>URL threat analysis</td></tr>
                <tr><td style='padding:6px 0;'>HTML/JS</td><td style='color:#8899aa;'>Interactive components</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Dataset info
    st.markdown("##### 📦 Dataset — NSL-KDD")
    st.markdown("""
    <div class='glass-card'>
        <div style='color:#aabbcc;font-size:0.9rem;line-height:1.8;'>
            The <b>NSL-KDD</b> dataset is an improved version of the original KDD Cup 1999 dataset,
            widely used for benchmarking intrusion detection systems.
            <br><br>
            <b>Key Facts:</b><br>
            🔹 <b>125,973</b> records in training set<br>
            🔹 <b>41 features</b> per connection record (duration, protocol, bytes, flags, etc.)<br>
            🔹 <b>Binary classification:</b> Normal vs Attack<br>
            🔹 <b>Attack categories:</b> DoS, Probe, R2L, U2R<br>
            🔹 Addresses issues of redundant records in original KDD'99
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Features table
    st.markdown("##### 📊 Key Model Metrics")
    st.markdown(f"""
    <div class='glass-card'>
        <table style='width:100%;color:#ccc;font-size:0.95rem;text-align:center;'>
            <tr style='color:#00d4ff;font-weight:600;border-bottom:1px solid rgba(0,212,255,0.2);'>
                <td style='padding:12px;'>Metric</td>
                <td style='padding:12px;'>Value</td>
                <td style='padding:12px;'>Meaning</td>
            </tr>
            <tr><td style='padding:10px;'>Accuracy</td>
                <td style='color:#00ff88;font-weight:700;'>{accuracy:.2f}%</td>
                <td style='color:#8899aa;'>Overall correct predictions</td></tr>
            <tr><td style='padding:10px;'>Precision</td>
                <td style='color:#00ff88;font-weight:700;'>{precision:.1f}%</td>
                <td style='color:#8899aa;'>True attacks / all flagged attacks</td></tr>
            <tr><td style='padding:10px;'>Recall</td>
                <td style='color:#00ff88;font-weight:700;'>{recall:.1f}%</td>
                <td style='color:#8899aa;'>Detected attacks / all real attacks</td></tr>
            <tr><td style='padding:10px;'>F1 Score</td>
                <td style='color:#00ff88;font-weight:700;'>{f1:.1f}%</td>
                <td style='color:#8899aa;'>Balance of precision & recall</td></tr>
            <tr><td style='padding:10px;'>Features</td>
                <td style='color:#00d4ff;font-weight:700;'>{len(feature_names)}</td>
                <td style='color:#8899aa;'>Network connection attributes</td></tr>
            <tr><td style='padding:10px;'>Test Samples</td>
                <td style='color:#00d4ff;font-weight:700;'>{total:,}</td>
                <td style='color:#8899aa;'>Size of test dataset</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Project info
    st.markdown("""
    <div class='glass-card' style='text-align:center;'>
        <div style='color:#00d4ff;font-weight:700;font-size:1.1rem;margin-bottom:12px;'>🎓 Academic Details</div>
        <div style='color:#aabbcc;line-height:2;'>
            <b>Project Title:</b> Cyber Sentinel AI — AI-Powered Intrusion Detection System<br>
            <b>Institution:</b> BMS Institute of Technology and Management, Bengaluru<br>
            <b>Year:</b> 2026 — Major Project<br>
            <b>Domain:</b> Cybersecurity & Machine Learning<br>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                  MANUAL PACKET TESTER
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "packet_tester":
    log_action("Visited", "Packet Tester")
    st.markdown("<div class='section-header'>🧪 Manual Packet Tester</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Enter custom network packet values and get an instant AI-powered IDS prediction in real time.</div>", unsafe_allow_html=True)

    if st.session_state.get('beginner_mode', False):
        st.info("🎓 **Beginner Tip:** Fill in the packet details below and click **Run IDS Prediction** to see if the AI thinks it's an attack or normal traffic!")

    st.markdown("---")
    st.markdown("#### ⚙️ Configure Packet Features")

    # Preset buttons
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
    preset = None
    with preset_col1:
        if st.button("🌐 Normal Web", use_container_width=True, key="preset_normal"):
            preset = 'normal'
    with preset_col2:
        if st.button("💥 DDoS Attack", use_container_width=True, key="preset_ddos"):
            preset = 'ddos'
    with preset_col3:
        if st.button("🔓 Port Scan", use_container_width=True, key="preset_scan"):
            preset = 'scan'
    with preset_col4:
        if st.button("🎲 Random", use_container_width=True, key="preset_random"):
            preset = 'random'

    PRESETS = {
        'normal': {'duration': 5,    'src_bytes': 500,   'dst_bytes': 2000, 'count': 5,   'srv_count': 3,  'same_srv_rate': 0.95, 'serror_rate': 0.0,  'dst_host_count': 50,  'dst_host_srv_count': 40, 'logged_in': 1},
        'ddos':   {'duration': 0,    'src_bytes': 15000, 'dst_bytes': 0,    'count': 450, 'srv_count': 400,'same_srv_rate': 1.0,  'serror_rate': 0.9,  'dst_host_count': 255, 'dst_host_srv_count': 255,'logged_in': 0},
        'scan':   {'duration': 0,    'src_bytes': 0,     'dst_bytes': 0,    'count': 200, 'srv_count': 1,  'same_srv_rate': 0.01, 'serror_rate': 1.0,  'dst_host_count': 255, 'dst_host_srv_count': 1,  'logged_in': 0},
        'random': {'duration': random.randint(0,20), 'src_bytes': random.randint(0,20000), 'dst_bytes': random.randint(0,5000),
                   'count': random.randint(1,500), 'srv_count': random.randint(1,300), 'same_srv_rate': round(random.random(),2),
                   'serror_rate': round(random.random(),2), 'dst_host_count': random.randint(1,255),
                   'dst_host_srv_count': random.randint(1,255), 'logged_in': random.randint(0,1)},
    }

    defaults = PRESETS.get(preset, st.session_state.get('pkt_defaults', PRESETS['normal']))
    if preset:
        st.session_state.pkt_defaults = defaults

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        duration    = st.number_input("⏱ Duration (s)",        min_value=0,   max_value=10000, value=int(defaults['duration']),    step=1,    key="pt_dur")
        src_bytes   = st.number_input("📤 Source Bytes",        min_value=0,   max_value=99999, value=int(defaults['src_bytes']),   step=100,  key="pt_src")
        dst_bytes   = st.number_input("📥 Dest Bytes",          min_value=0,   max_value=99999, value=int(defaults['dst_bytes']),   step=100,  key="pt_dst")
    with c2:
        count       = st.number_input("🔢 Connection Count",    min_value=0,   max_value=512,   value=int(defaults['count']),       step=1,    key="pt_cnt")
        srv_count   = st.number_input("📡 Service Count",        min_value=0,   max_value=512,   value=int(defaults['srv_count']),   step=1,    key="pt_srv")
        logged_in   = st.selectbox("🔐 Logged In",              [0, 1],         index=int(defaults['logged_in']),                              key="pt_log")
    with c3:
        same_srv_rate      = st.slider("📊 Same Service Rate",   0.0, 1.0, float(defaults['same_srv_rate']),      0.01, key="pt_ssr")
        serror_rate        = st.slider("⚠️ SYN Error Rate",      0.0, 1.0, float(defaults['serror_rate']),        0.01, key="pt_ser")
        dst_host_count     = st.number_input("🌐 Dst Host Count", min_value=0, max_value=255, value=int(defaults['dst_host_count']),     step=1, key="pt_dhc")
        dst_host_srv_count = st.number_input("🏠 Dst Host Srv Count", min_value=0, max_value=255, value=int(defaults['dst_host_srv_count']), step=1, key="pt_dhs")

    st.markdown("---")
    run_col, _ = st.columns([1, 3])
    with run_col:
        run_predict = st.button("🤖 Run IDS Prediction", use_container_width=True, key="pt_run_btn")

    if run_predict:
        # Build full feature vector using defaults from X_test row 0 for missing features
        base_row = X_test.iloc[0].copy()
        base_row['duration']            = duration
        base_row['src_bytes']           = src_bytes
        base_row['dst_bytes']           = dst_bytes
        base_row['count']               = count
        base_row['srv_count']           = srv_count
        base_row['logged_in']           = logged_in
        base_row['same_srv_rate']       = same_srv_rate
        base_row['serror_rate']         = serror_rate
        base_row['dst_host_count']      = dst_host_count
        base_row['dst_host_srv_count']  = dst_host_srv_count

        import warnings as _w
        with _w.catch_warnings():
            _w.simplefilter('ignore')
            single_pred = model.predict(pd.DataFrame([base_row]))[0]
            try:
                single_proba = model.predict_proba(pd.DataFrame([base_row]))[0]
                attack_prob = single_proba[list(model.classes_).index('attack')] * 100 if 'attack' in model.classes_ else 50
            except Exception:
                attack_prob = 100 if single_pred == 'attack' else 5

        log_action("Packet Test", f"Prediction: {single_pred} | src_bytes: {src_bytes}")

        is_attack = single_pred == 'attack'
        p_color  = '#ff4444' if is_attack else '#00ff88'
        p_bg     = 'rgba(255,68,68,0.08)' if is_attack else 'rgba(0,255,136,0.06)'
        p_border = 'rgba(255,68,68,0.35)' if is_attack else 'rgba(0,255,136,0.3)'
        p_icon   = '⚠️' if is_attack else '✅'
        p_label  = 'ATTACK DETECTED' if is_attack else 'NORMAL TRAFFIC'
        action   = '🔒 IP Blocked Automatically' if is_attack else '✅ No Action Needed'

        st.markdown(f"""
        <div style='background:{p_bg};border:2px solid {p_border};border-radius:18px;
                    padding:24px 30px;margin:16px 0;'>
            <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;'>
                <div style='display:flex;align-items:center;gap:16px;'>
                    <div style='font-size:3rem;'>{p_icon}</div>
                    <div>
                        <div style='color:#8899aa;font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;'>IDS Verdict</div>
                        <div style='color:{p_color};font-size:2rem;font-weight:800;letter-spacing:1px;'>{p_label}</div>
                        <div style='color:#aabbcc;font-size:0.9rem;margin-top:4px;'>Action: <b style='color:{p_color};'>{action}</b></div>
                    </div>
                </div>
                <div style='min-width:180px;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
                        <span style='color:#8899aa;font-size:0.8rem;'>Attack Probability</span>
                        <span style='color:{p_color};font-weight:700;'>{attack_prob:.1f}%</span>
                    </div>
                    <div style='background:rgba(255,255,255,0.07);border-radius:8px;height:12px;overflow:hidden;'>
                        <div style='width:{attack_prob:.1f}%;height:100%;
                                    background:linear-gradient(90deg,{p_color}88,{p_color});
                                    border-radius:8px;'></div>
                    </div>
                </div>
            </div>
            <div style='margin-top:16px;border-top:1px solid {p_border};padding-top:12px;
                        display:flex;gap:24px;flex-wrap:wrap;'>
                <div><span style='color:#8899aa;font-size:0.75rem;'>SRC BYTES</span><br>
                     <span style='color:#fff;font-weight:700;'>{src_bytes:,}</span></div>
                <div><span style='color:#8899aa;font-size:0.75rem;'>DST BYTES</span><br>
                     <span style='color:#fff;font-weight:700;'>{dst_bytes:,}</span></div>
                <div><span style='color:#8899aa;font-size:0.75rem;'>DURATION</span><br>
                     <span style='color:#fff;font-weight:700;'>{duration}s</span></div>
                <div><span style='color:#8899aa;font-size:0.75rem;'>CONNECTIONS</span><br>
                     <span style='color:#fff;font-weight:700;'>{count}</span></div>
                <div><span style='color:#8899aa;font-size:0.75rem;'>SYN ERR RATE</span><br>
                     <span style='color:#fff;font-weight:700;'>{serror_rate:.2f}</span></div>
                <div><span style='color:#8899aa;font-size:0.75rem;'>LOGGED IN</span><br>
                     <span style='color:#fff;font-weight:700;'>{'Yes' if logged_in else 'No'}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # History
        if 'packet_history' not in st.session_state:
            st.session_state.packet_history = []
        st.session_state.packet_history.append({
            'Time': datetime.now().strftime('%H:%M:%S'),
            'src_bytes': src_bytes, 'dst_bytes': dst_bytes,
            'duration': duration, 'count': count,
            'serror_rate': serror_rate, 'Verdict': single_pred.upper(),
            'Attack Prob %': f"{attack_prob:.1f}"
        })

    if 'packet_history' in st.session_state and len(st.session_state.packet_history) > 0:
        st.markdown("---")
        st.markdown("##### 🕒 Prediction History")
        hist_df = pd.DataFrame(st.session_state.packet_history[::-1])
        st.dataframe(hist_df, use_container_width=True)
        if st.button("🗑️ Clear History", key="clear_hist_btn"):
            st.session_state.packet_history = []
            st.rerun()


# ══════════════════════════════════════════════════════════
#                      AUDIT LOG
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "audit_log":
    st.markdown("<div class='section-header'>📋 Audit Log</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Real-time log of all user actions and system events in this session.</div>", unsafe_allow_html=True)

    if st.session_state.get('beginner_mode', False):
        st.info("🎓 **Beginner Tip:** An audit log tracks every action taken on the system — like a security camera for your dashboard!")

    logs = st.session_state.get('audit_log', [])

    al_c1, al_c2, al_c3 = st.columns(3)
    al_c1.metric("📋 Total Events", len(logs))
    al_c2.metric("🕒 Session Start", logs[0]['time'] if logs else "—")
    al_c3.metric("⏱️ Last Event", logs[-1]['time'] if logs else "—")

    st.markdown("---")

    if logs:
        for entry in reversed(logs[-50:]):
            action_color = '#ff4444' if 'attack' in entry['action'].lower() or 'blocked' in entry['detail'].lower() else '#00d4ff'
            st.markdown(f"""
            <div style='background:rgba(26,31,53,0.5);border-left:3px solid {action_color};
                        border-radius:0 10px 10px 0;padding:10px 16px;margin:4px 0;
                        display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;'>
                <div>
                    <span style='color:{action_color};font-weight:600;'>{entry['action']}</span>
                    <span style='color:#8899aa;margin-left:12px;font-size:0.85rem;'>{entry['detail']}</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:#556677;font-size:0.8rem;'>🕒 {entry['time']}</span>
                    <span style='color:#445566;font-size:0.75rem;margin-left:10px;'>📍 {entry['section']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        log_export = pd.DataFrame(logs)
        csv_log = log_export.to_csv(index=False).encode('utf-8')
        col_dl, col_clr = st.columns(2)
        with col_dl:
            st.download_button("📥 Export Audit Log (CSV)", csv_log,
                               file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                               mime="text/csv", key="audit_download")
        with col_clr:
            if st.button("🗑️ Clear Log", use_container_width=True, key="audit_clear"):
                st.session_state.audit_log = []
                st.rerun()
    else:
        st.markdown("""
        <div class='glass-card' style='text-align:center;padding:40px;'>
            <div style='font-size:3rem;'>📋</div>
            <div style='color:#8899aa;margin-top:10px;'>No events logged yet. Use the dashboard to generate activity.</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                  SECURITY SCORE PAGE
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "security_score":
    log_action("Visited", "Security Score")
    st.markdown("<div class='section-header'>🏆 Security Score Card</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Comprehensive A–F security grade based on model performance, threat levels, and system health.</div>", unsafe_allow_html=True)

    attack_ratio = attacks / total * 100
    sec_score = max(0, min(100, int((accuracy*0.35)+((100-attack_ratio)*0.25)+(precision*0.20)+(f1*0.20))))
    if sec_score >= 90:   grade, g_color, g_desc, g_advice = "A+", "#00ff88", "Excellent", "System is operating at peak security. Continue monitoring regularly."
    elif sec_score >= 80: grade, g_color, g_desc, g_advice = "A",  "#00ff88", "Very Good", "Strong protection active. Review low-severity alerts periodically."
    elif sec_score >= 70: grade, g_color, g_desc, g_advice = "B",  "#00d4ff", "Good",      "Good security posture. Investigate medium-severity alerts."
    elif sec_score >= 60: grade, g_color, g_desc, g_advice = "C",  "#ffaa00", "Average",   "Several vulnerabilities detected. Tighten firewall rules."
    elif sec_score >= 50: grade, g_color, g_desc, g_advice = "D",  "#ff8800", "Poor",      "Multiple threats active. Immediate review of attack logs required."
    else:                 grade, g_color, g_desc, g_advice = "F",  "#ff4444", "Critical",  "System under active threat. Engage incident response team NOW."

    st.markdown(f"""
    <div style='background:rgba(26,31,53,0.7);border:2px solid {g_color}55;
                border-radius:20px;padding:36px;text-align:center;margin:16px 0;'>
        <div style='font-size:7rem;font-weight:900;color:{g_color};
                    text-shadow:0 0 60px {g_color}88;line-height:1;'>{grade}</div>
        <div style='color:{g_color};font-size:1.6rem;font-weight:700;margin-top:10px;'>{g_desc}</div>
        <div style='color:#8899aa;margin-top:8px;font-size:0.95rem;'>{g_advice}</div>
        <div style='margin-top:20px;'>
            <div style='display:flex;justify-content:center;gap:8px;margin-bottom:8px;'>
                <span style='color:#8899aa;font-size:0.85rem;'>Overall Security Score</span>
                <span style='color:{g_color};font-weight:700;'>{sec_score}/100</span>
            </div>
            <div style='background:rgba(255,255,255,0.07);border-radius:10px;height:16px;overflow:hidden;max-width:500px;margin:0 auto;'>
                <div style='width:{sec_score}%;height:100%;
                            background:linear-gradient(90deg,{g_color}66,{g_color});
                            border-radius:10px;'></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 Score Breakdown")
    breakdown = [
        ("🎯 Model Accuracy",  accuracy,  35, "Core detection reliability"),
        ("📋 Precision",       precision, 20, "False positive control"),
        ("🔁 F1 Score",        f1,        20, "Precision-recall balance"),
        ("🛡️ Threat Safety",  max(0, 100-attack_ratio), 25, "Proportion of clean traffic"),
    ]
    for label, val, weight, desc in breakdown:
        bar_color = "#00ff88" if val >= 90 else "#ffaa00" if val >= 70 else "#ff4444"
        st.markdown(f"""
        <div style='background:rgba(26,31,53,0.5);border:1px solid rgba(0,212,255,0.15);
                    border-radius:12px;padding:16px 20px;margin:8px 0;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:8px;'>
                <span style='color:#fff;font-weight:600;'>{label}</span>
                <span style='color:{bar_color};font-weight:700;'>{val:.1f}% <span style='color:#556677;font-size:0.8rem;'>(weight {weight}%)</span></span>
            </div>
            <div style='background:rgba(255,255,255,0.06);border-radius:6px;height:8px;overflow:hidden;'>
                <div style='width:{val:.1f}%;height:100%;background:{bar_color};border-radius:6px;'></div>
            </div>
            <div style='color:#8899aa;font-size:0.8rem;margin-top:4px;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎓 Grade Legend")
    grades_info = [("A+/A","90-100","#00ff88","Excellent — Minimal risk"),("B","70-89","#00d4ff","Good — Monitor regularly"),("C","60-69","#ffaa00","Average — Review alerts"),("D","50-59","#ff8800","Poor — Take action"),("F","<50","#ff4444","Critical — Emergency response")]
    gl_cols = st.columns(5)
    for col, (g, rng, gc, gdesc) in zip(gl_cols, grades_info):
        col.markdown(f"<div style='background:rgba(26,31,53,0.5);border:1px solid {gc}44;border-radius:12px;padding:12px;text-align:center;'>"
                     f"<div style='font-size:1.8rem;font-weight:900;color:{gc};'>{g}</div>"
                     f"<div style='color:#8899aa;font-size:0.75rem;'>{rng}</div>"
                     f"<div style='color:#aabbcc;font-size:0.75rem;margin-top:4px;'>{gdesc}</div>"
                     f"</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#                    SECURITY QUIZ
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "quiz":
    log_action("Visited", "Security Quiz")
    st.markdown("<div class='section-header'>🧠 Cybersecurity Quiz</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Test your cybersecurity knowledge with 10 questions. See how you score!</div>", unsafe_allow_html=True)

    QUESTIONS = [
        {"q": "What does DDoS stand for?",
         "opts": ["Direct Denial of Service", "Distributed Denial of Service", "Dynamic Data over SSL", "Device Detection over Socket"],
         "ans": 1, "exp": "DDoS = Distributed Denial of Service — floods a server from many sources."},
        {"q": "Which algorithm is used in this IDS project?",
         "opts": ["Neural Network", "K-Means Clustering", "Random Forest", "Linear Regression"],
         "ans": 2, "exp": "Random Forest is an ensemble learning method used for classification."},
        {"q": "What does SHAP stand for?",
         "opts": ["Secure Hash Algorithm Protocol", "SHapley Additive exPlanations", "Shared Host Access Protocol", "System Health Analysis Platform"],
         "ans": 1, "exp": "SHAP explains AI predictions by computing feature contributions."},
        {"q": "What is a honeypot in cybersecurity?",
         "opts": ["Encrypted storage", "A firewall rule", "A decoy system to attract attackers", "A type of malware"],
         "ans": 2, "exp": "Honeypots are fake systems designed to lure and study attackers."},
        {"q": "Which port does SSH use by default?",
         "opts": ["21", "80", "443", "22"],
         "ans": 3, "exp": "SSH uses port 22 for secure shell remote connections."},
        {"q": "What does XAI stand for?",
         "opts": ["Extra AI", "Explainable Artificial Intelligence", "Extended Algorithm Interface", "External Access Integration"],
         "ans": 1, "exp": "XAI makes AI decisions transparent and understandable to humans."},
        {"q": "What dataset is used to train this IDS?",
         "opts": ["MNIST", "CIFAR-10", "NSL-KDD", "ImageNet"],
         "ans": 2, "exp": "NSL-KDD is the benchmark dataset for intrusion detection systems."},
        {"q": "What does phishing primarily target?",
         "opts": ["Network bandwidth", "Credentials and personal data", "Hardware firmware", "DNS servers"],
         "ans": 1, "exp": "Phishing tricks users into revealing passwords and sensitive data."},
        {"q": "What is a False Positive in IDS?",
         "opts": ["Missed attack", "Correctly detected attack", "Normal traffic flagged as attack", "Attack disguised as normal"],
         "ans": 2, "exp": "A False Positive is when normal traffic is incorrectly classified as an attack."},
        {"q": "What does the 'F1 Score' measure?",
         "opts": ["Speed of detection", "Number of features", "Harmonic mean of Precision and Recall", "False negative rate"],
         "ans": 2, "exp": "F1 Score = 2 × (Precision × Recall) / (Precision + Recall)."},
    ]

    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = {'answers': {}, 'submitted': False}

    qs = st.session_state.quiz_state

    if not qs['submitted']:
        st.markdown(f"<div style='color:#8899aa;margin-bottom:16px;'>Answer all {len(QUESTIONS)} questions then click Submit.</div>", unsafe_allow_html=True)
        for i, q in enumerate(QUESTIONS):
            st.markdown(f"**Q{i+1}. {q['q']}**")
            choice = st.radio("", q['opts'], key=f"quiz_q{i}", index=None, label_visibility="collapsed")
            if choice is not None:
                qs['answers'][i] = q['opts'].index(choice)
            st.markdown("")

        answered = len(qs['answers'])
        st.markdown(f"<span style='color:#8899aa;'>{answered}/{len(QUESTIONS)} answered</span>", unsafe_allow_html=True)
        sub_col, reset_col = st.columns([1, 3])
        with sub_col:
            if st.button("✅ Submit Quiz", use_container_width=True, key="quiz_submit"):
                if answered == len(QUESTIONS):
                    qs['submitted'] = True
                    log_action("Quiz Submitted", f"Answered: {answered}/{len(QUESTIONS)}")
                    st.rerun()
                else:
                    st.warning(f"Please answer all {len(QUESTIONS)} questions first!")
    else:
        score = sum(1 for i, q in enumerate(QUESTIONS) if qs['answers'].get(i) == q['ans'])
        pct = score / len(QUESTIONS) * 100
        if pct >= 90:   qg, qc = "A+", "#00ff88"
        elif pct >= 70: qg, qc = "B",  "#00d4ff"
        elif pct >= 50: qg, qc = "C",  "#ffaa00"
        else:           qg, qc = "F",  "#ff4444"

        st.markdown(f"""
        <div style='background:rgba(26,31,53,0.7);border:2px solid {qc}55;
                    border-radius:18px;padding:28px;text-align:center;margin:16px 0;'>
            <div style='font-size:5rem;font-weight:900;color:{qc};'>{qg}</div>
            <div style='color:{qc};font-size:1.5rem;font-weight:700;'>Score: {score}/{len(QUESTIONS)} ({pct:.0f}%)</div>
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;height:12px;overflow:hidden;max-width:400px;margin:14px auto 0;'>
                <div style='width:{pct:.0f}%;height:100%;background:{qc};border-radius:8px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📝 Answer Review")
        for i, q in enumerate(QUESTIONS):
            user_ans = qs['answers'].get(i, -1)
            correct = user_ans == q['ans']
            icon = "✅" if correct else "❌"
            c = "#00ff88" if correct else "#ff4444"
            st.markdown(f"""
            <div style='background:rgba(26,31,53,0.5);border-left:3px solid {c};
                        border-radius:0 12px 12px 0;padding:12px 16px;margin:6px 0;'>
                <div style='color:#fff;font-weight:600;'>{icon} Q{i+1}: {q['q']}</div>
                <div style='color:{c};font-size:0.88rem;margin-top:4px;'>Your answer: {q['opts'][user_ans] if user_ans >= 0 else 'None'}</div>
                {f"<div style='color:#8899aa;font-size:0.85rem;'>Correct: {q['opts'][q['ans']]}</div>" if not correct else ""}
                <div style='color:#556677;font-size:0.82rem;margin-top:4px;'>💡 {q['exp']}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔄 Retake Quiz", key="quiz_retake"):
            st.session_state.quiz_state = {'answers': {}, 'submitted': False}
            st.rerun()


# ══════════════════════════════════════════════════════════
#                     HASH CHECKER
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "hash_checker":
    log_action("Visited", "Hash Checker")
    import hashlib
    st.markdown("<div class='section-header'>#️⃣ File Hash Checker</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Generate and verify MD5/SHA256 hashes. Check against known malware signatures.</div>", unsafe_allow_html=True)

    if st.session_state.get('beginner_mode', False):
        st.info("🎓 **Beginner Tip:** A hash is like a digital fingerprint for a file. If the hash matches a known malware hash, the file is dangerous!")

    # Known malware hashes (educational examples)
    KNOWN_MALWARE = {
        "44d88612fea8a8f36de82e1278abb02f": "EICAR Test File (Antivirus test)",
        "69630e4574ec6798239b091cda43dca0": "WannaCry Ransomware Sample",
        "84c82835a5d21bbcf75a61706d8ab549": "Mirai Botnet Variant",
        "e3b0c44298fc1c149afbf4c8996fb924": "Empty file — suspicious submission",
        "d41d8cd98f00b204e9800998ecf8427e": "Empty MD5 — likely obfuscated payload",
    }

    tab_text, tab_file = st.tabs(["📝 Hash Text/String", "📂 Hash Uploaded File"])

    with tab_text:
        st.markdown("##### Enter text or paste a hash to check")
        input_text = st.text_area("Input text or existing hash:", placeholder="Paste text to hash, or enter a hash to verify...", height=100, key="hash_input")
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            if st.button("🔢 Generate Hashes", use_container_width=True, key="gen_hash_btn") and input_text:
                md5  = hashlib.md5(input_text.encode()).hexdigest()
                sha1 = hashlib.sha1(input_text.encode()).hexdigest()
                sha256 = hashlib.sha256(input_text.encode()).hexdigest()
                log_action("Hash Generated", f"MD5: {md5[:16]}...")
                st.markdown(f"""
                <div class='glass-card'>
                    <div style='color:#00d4ff;font-weight:700;margin-bottom:12px;'>Generated Hashes</div>
                    <div style='color:#8899aa;font-size:0.78rem;'>MD5</div>
                    <div style='color:#fff;font-family:monospace;font-size:0.9rem;word-break:break-all;margin-bottom:10px;'>{md5}</div>
                    <div style='color:#8899aa;font-size:0.78rem;'>SHA-1</div>
                    <div style='color:#fff;font-family:monospace;font-size:0.9rem;word-break:break-all;margin-bottom:10px;'>{sha1}</div>
                    <div style='color:#8899aa;font-size:0.78rem;'>SHA-256</div>
                    <div style='color:#fff;font-family:monospace;font-size:0.9rem;word-break:break-all;'>{sha256}</div>
                </div>
                """, unsafe_allow_html=True)
                malware_hit = KNOWN_MALWARE.get(md5) or KNOWN_MALWARE.get(sha256)
                if malware_hit:
                    st.error(f"🚨 MALWARE MATCH: {malware_hit}")
                else:
                    st.success("✅ No known malware signature matches found.")
        with h_col2:
            if st.button("🔍 Check Against Malware DB", use_container_width=True, key="check_hash_btn") and input_text.strip():
                check = input_text.strip().lower()
                hit = KNOWN_MALWARE.get(check)
                if hit:
                    st.error(f"🚨 **MALWARE DETECTED:** {hit}")
                    log_action("Hash Flagged", f"Match: {hit}")
                else:
                    st.success("✅ Hash not found in malware database.")

    with tab_file:
        st.markdown("##### Upload a file to compute its hash")
        hash_file = st.file_uploader("Upload file for hashing", type=None, key="hash_file_upload")
        if hash_file:
            content = hash_file.read()
            md5_f   = hashlib.md5(content).hexdigest()
            sha256_f = hashlib.sha256(content).hexdigest()
            log_action("File Hashed", f"{hash_file.name} | MD5: {md5_f[:16]}...")
            st.markdown(f"""
            <div class='glass-card'>
                <div style='color:#00d4ff;font-weight:700;margin-bottom:12px;'>📁 {hash_file.name}</div>
                <div style='color:#8899aa;font-size:0.78rem;'>MD5</div>
                <div style='color:#fff;font-family:monospace;font-size:0.9rem;word-break:break-all;margin-bottom:10px;'>{md5_f}</div>
                <div style='color:#8899aa;font-size:0.78rem;'>SHA-256</div>
                <div style='color:#fff;font-family:monospace;font-size:0.9rem;word-break:break-all;'>{sha256_f}</div>
                <div style='color:#8899aa;font-size:0.78rem;margin-top:10px;'>File Size</div>
                <div style='color:#fff;font-weight:600;'>{len(content)/1024:.1f} KB</div>
            </div>
            """, unsafe_allow_html=True)
            malware_hit = KNOWN_MALWARE.get(md5_f) or KNOWN_MALWARE.get(sha256_f)
            if malware_hit:
                st.error(f"🚨 MALWARE MATCH: {malware_hit}")
            else:
                st.success("✅ No known malware signatures detected.")

    st.markdown("---")
    st.markdown("##### 🗃️ Known Malware Database (Educational)")
    db_df = pd.DataFrame([(h, n) for h, n in KNOWN_MALWARE.items()], columns=["Hash", "Malware Name"])
    st.dataframe(db_df, use_container_width=True)


# ══════════════════════════════════════════════════════════
#                    PORT SCANNER
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "port_scanner":
    log_action("Visited", "Port Scanner")
    import socket
    st.markdown("<div class='section-header'>🌐 Network Port Scanner</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Scan a target host for open ports and identify risky services.</div>", unsafe_allow_html=True)

    if st.session_state.get('beginner_mode', False):
        st.info("🎓 **Beginner Tip:** Open ports are like open doors on a computer. Too many open doors = more ways for attackers to get in!")

    RISKY_PORTS = {
        21: ("FTP", "🔴 HIGH", "Unencrypted file transfer — use SFTP instead"),
        22: ("SSH", "🟡 MEDIUM", "Secure but brute-force target — restrict access"),
        23: ("Telnet", "🔴 HIGH", "Completely unencrypted — disable immediately"),
        25: ("SMTP", "🟡 MEDIUM", "Mail server — may be abused for spam"),
        53: ("DNS", "🟡 MEDIUM", "DNS service — secure against amplification attacks"),
        80: ("HTTP", "🟢 LOW", "Unencrypted web — redirect to HTTPS (443)"),
        110:("POP3", "🔴 HIGH", "Unencrypted mail — use POP3S (995)"),
        135:("RPC",  "🔴 HIGH", "Windows RPC — common exploit target"),
        139:("NetBIOS","🔴 HIGH","Legacy Windows sharing — disable if unused"),
        143:("IMAP", "🟡 MEDIUM", "Mail access — use IMAPS (993)"),
        443:("HTTPS","🟢 LOW",  "Encrypted web — keep open"),
        445:("SMB",  "🔴 HIGH", "WannaCry vector — patch and restrict"),
        1433:("MSSQL","🔴 HIGH","Database — never expose to internet"),
        3306:("MySQL","🔴 HIGH","Database — restrict to local only"),
        3389:("RDP", "🔴 HIGH", "Remote Desktop — prime ransomware target"),
        5432:("PostgreSQL","🔴 HIGH","Database — restrict access"),
        6379:("Redis","🔴 HIGH","Often unauthenticated — restrict immediately"),
        8080:("HTTP-Alt","🟡 MEDIUM","Alt web port — ensure it's necessary"),
        8443:("HTTPS-Alt","🟢 LOW","Alt HTTPS — verify certificate"),
        27017:("MongoDB","🔴 HIGH","Often unauthenticated — secure immediately"),
    }

    ps_col1, ps_col2, ps_col3 = st.columns([2, 1, 1])
    with ps_col1:
        target_host = st.text_input("🎯 Target Host / IP", value="127.0.0.1", placeholder="e.g. 127.0.0.1 or localhost", key="ps_host")
    with ps_col2:
        port_start = st.number_input("Start Port", min_value=1, max_value=65535, value=20, key="ps_start")
    with ps_col3:
        port_end = st.number_input("End Port", min_value=1, max_value=65535, value=1000, key="ps_end")

    timeout = st.slider("Connection Timeout (seconds)", 0.1, 2.0, 0.3, 0.1, key="ps_timeout")

    scan_col, _ = st.columns([1, 3])
    with scan_col:
        run_scan = st.button("🔍 Start Port Scan", use_container_width=True, key="ps_run")

    if run_scan:
        if port_end - port_start > 500:
            st.warning("⚠️ Scanning more than 500 ports may take a while. Limiting to 500 ports.")
            port_end = port_start + 500

        log_action("Port Scan", f"{target_host}:{port_start}-{port_end}")
        open_ports = []
        progress = st.progress(0, text="Scanning...")
        total_ports = port_end - port_start + 1

        for idx, port in enumerate(range(int(port_start), int(port_end)+1)):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target_host, port))
                sock.close()
                if result == 0:
                    open_ports.append(port)
            except Exception:
                pass
            if idx % 50 == 0:
                progress.progress(idx / total_ports, text=f"Scanning port {port}...")
        progress.progress(1.0, text=f"✅ Scan complete — {len(open_ports)} open ports found")

        st.markdown(f"---")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("🔓 Open Ports", len(open_ports))
        sc2.metric("🔒 Closed Ports", total_ports - len(open_ports))
        risky = [p for p in open_ports if p in RISKY_PORTS and '🔴' in RISKY_PORTS[p][1]]
        sc3.metric("🔴 High-Risk Ports", len(risky))

        if open_ports:
            st.markdown("##### 🔓 Open Ports Found")
            for port in open_ports:
                if port in RISKY_PORTS:
                    svc, risk, advice = RISKY_PORTS[port]
                    risk_color = "#ff4444" if "🔴" in risk else "#ffaa00" if "🟡" in risk else "#00ff88"
                    st.markdown(f"""
                    <div style='background:rgba(26,31,53,0.6);border-left:3px solid {risk_color};
                                border-radius:0 12px 12px 0;padding:12px 18px;margin:5px 0;'>
                        <div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;'>
                            <div><b style='color:#fff;'>Port {port}</b> <span style='color:#00d4ff;margin-left:8px;'>{svc}</span></div>
                            <span style='color:{risk_color};font-weight:600;font-size:0.85rem;'>{risk}</span>
                        </div>
                        <div style='color:#8899aa;font-size:0.82rem;margin-top:4px;'>💡 {advice}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background:rgba(26,31,53,0.4);border-radius:10px;padding:10px 16px;margin:4px 0;'>"
                                f"<b style='color:#fff;'>Port {port}</b> <span style='color:#8899aa;margin-left:8px;'>Unknown service</span></div>",
                                unsafe_allow_html=True)
        else:
            st.success("✅ No open ports found in the specified range.")


# ══════════════════════════════════════════════════════════
#                   ENCRYPTION TOOL
# ══════════════════════════════════════════════════════════
elif st.session_state.section == "encryption":
    log_action("Visited", "Encryption Tool")
    import base64
    st.markdown("<div class='section-header'>🔐 Encryption Tool</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'>Encrypt and decrypt messages using classic and modern ciphers. Learn how encryption protects data.</div>", unsafe_allow_html=True)

    if st.session_state.get('beginner_mode', False):
        st.info("🎓 **Beginner Tip:** Encryption scrambles your message so only the intended recipient can read it. It's like a secret code!")

    enc_tab1, enc_tab2, enc_tab3 = st.tabs(["🔤 Caesar Cipher", "📦 Base64", "⚡ XOR Cipher"])

    with enc_tab1:
        st.markdown("##### Caesar Cipher — shifts each letter by a key")
        c_text = st.text_area("Enter message:", height=100, key="caesar_input", placeholder="Type your message here...")
        c_shift = st.slider("Shift Key (1–25)", 1, 25, 13, key="caesar_shift")
        c_col1, c_col2 = st.columns(2)
        def caesar(text, shift, decrypt=False):
            result = []
            shift = shift if not decrypt else -shift
            for ch in text:
                if ch.isalpha():
                    base = ord('A') if ch.isupper() else ord('a')
                    result.append(chr((ord(ch) - base + shift) % 26 + base))
                else:
                    result.append(ch)
            return ''.join(result)
        with c_col1:
            if st.button("🔒 Encrypt", use_container_width=True, key="caesar_enc") and c_text:
                enc = caesar(c_text, c_shift)
                log_action("Caesar Encrypt", f"Shift: {c_shift}")
                st.markdown(f"<div class='glass-card'><div style='color:#8899aa;font-size:0.8rem;'>ENCRYPTED</div>"
                            f"<div style='color:#00d4ff;font-family:monospace;word-break:break-all;'>{enc}</div></div>", unsafe_allow_html=True)
        with c_col2:
            if st.button("🔓 Decrypt", use_container_width=True, key="caesar_dec") and c_text:
                dec = caesar(c_text, c_shift, decrypt=True)
                log_action("Caesar Decrypt", f"Shift: {c_shift}")
                st.markdown(f"<div class='glass-card'><div style='color:#8899aa;font-size:0.8rem;'>DECRYPTED</div>"
                            f"<div style='color:#00ff88;font-family:monospace;word-break:break-all;'>{dec}</div></div>", unsafe_allow_html=True)
        st.info("💡 Caesar cipher shifts each letter by the key value. ROT13 uses shift=13. Used by Julius Caesar for secret messages!")

    with enc_tab2:
        st.markdown("##### Base64 — encodes binary/text as ASCII")
        b_text = st.text_area("Enter text or Base64 string:", height=100, key="b64_input", placeholder="Enter text to encode, or Base64 to decode...")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("🔒 Encode to Base64", use_container_width=True, key="b64_enc") and b_text:
                enc_b64 = base64.b64encode(b_text.encode()).decode()
                log_action("Base64 Encode", "")
                st.markdown(f"<div class='glass-card'><div style='color:#8899aa;font-size:0.8rem;'>BASE64 ENCODED</div>"
                            f"<div style='color:#00d4ff;font-family:monospace;word-break:break-all;'>{enc_b64}</div></div>", unsafe_allow_html=True)
        with b_col2:
            if st.button("🔓 Decode from Base64", use_container_width=True, key="b64_dec") and b_text:
                try:
                    dec_b64 = base64.b64decode(b_text.encode()).decode(errors='replace')
                    log_action("Base64 Decode", "")
                    st.markdown(f"<div class='glass-card'><div style='color:#8899aa;font-size:0.8rem;'>DECODED</div>"
                                f"<div style='color:#00ff88;font-family:monospace;word-break:break-all;'>{dec_b64}</div></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Invalid Base64: {e}")
        st.info("💡 Base64 is used to encode binary data (images, files) as plain text for safe transmission in emails and APIs.")

    with enc_tab3:
        st.markdown("##### XOR Cipher — combines each character with a key")
        x_text = st.text_input("Message:", placeholder="Enter plaintext or hex-encoded ciphertext...", key="xor_input")
        x_key  = st.text_input("Key:", placeholder="Any string key...", key="xor_key", value="secret")
        x_col1, x_col2 = st.columns(2)
        def xor_cipher(text, key):
            return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text)) if key else text
        with x_col1:
            if st.button("🔒 XOR Encrypt", use_container_width=True, key="xor_enc") and x_text and x_key:
                enc_x = xor_cipher(x_text, x_key)
                enc_hex = enc_x.encode('latin-1').hex()
                log_action("XOR Encrypt", f"Key: {x_key[:4]}...")
                st.markdown(f"<div class='glass-card'><div style='color:#8899aa;font-size:0.8rem;'>XOR CIPHERTEXT (hex)</div>"
                            f"<div style='color:#00d4ff;font-family:monospace;word-break:break-all;'>{enc_hex}</div></div>", unsafe_allow_html=True)
        with x_col2:
            if st.button("🔓 XOR Decrypt", use_container_width=True, key="xor_dec") and x_text and x_key:
                try:
                    decoded_bytes = bytes.fromhex(x_text)
                    dec_x = xor_cipher(decoded_bytes.decode('latin-1'), x_key)
                    log_action("XOR Decrypt", "")
                    st.markdown(f"<div class='glass-card'><div style='color:#8899aa;font-size:0.8rem;'>DECRYPTED</div>"
                                f"<div style='color:#00ff88;font-family:monospace;word-break:break-all;'>{dec_x}</div></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Decryption error: {e}")
        st.info("💡 XOR cipher is widely used in malware and CTF challenges. It's symmetric — the same key encrypts and decrypts.")


# ── Footer ────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class='footer-text'>
    🛡️ Cyber Sentinel AI v2.0 — Major Project 2026 — BMS Institute of Technology and Management<br>
    <span style='font-size:11px;'>Powered by Random Forest ML • SHAP Explainability • Google Gemini AI</span>
</div>
""", unsafe_allow_html=True)