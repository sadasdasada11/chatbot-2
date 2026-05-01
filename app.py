import streamlit as st
from openai import OpenAI

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Healthcare Assistant", page_icon="🏥", layout="wide")

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.main {
    background-color: #f4f6fb;
}
.block-container {
    padding-top: 2rem;
}
h1 {
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("🏥 AI Healthcare Assistant")
st.caption("AI-powered symptom checker & chatbot (Not medical advice)")

# =========================
# API (FIXED)
# =========================
import os

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ API key not found. Set it in environment variables.")
    st.stop()
client = OpenAI(api_key=api_key)

# =========================
# SIDEBAR
# =========================
mode = st.sidebar.radio("Select Mode", ["🤖 Chatbot", "📋 Symptom Checker"])
st.sidebar.warning("⚠️ Not a substitute for professional medical advice")

# =========================
# 🤖 CHATBOT
# =========================
if mode == "🤖 Chatbot":

    st.subheader("Healthcare Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Describe your symptoms...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional healthcare assistant. "
                            "You must NOT diagnose. "
                            "Provide:\n"
                            "1. Possible causes (general)\n"
                            "2. Self-care advice\n"
                            "3. When to seek help\n"
                        )
                    },
                    *st.session_state.messages
                ],
                temperature=0.3
            )

            reply = response.choices[0].message.content

        except Exception as e:
            reply = f"⚠️ AI error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# =========================
# 📋 QUESTIONNAIRE
# =========================
if mode == "📋 Symptom Checker":

    st.subheader("Symptom Assessment")

    if "step" not in st.session_state:
        st.session_state.step = 0
        st.session_state.data = {}

    st.progress((st.session_state.step + 1) / 5)

    # STEP 1
    if st.session_state.step == 0:
        symptom = st.selectbox("Main symptom", [
            "Fever", "Headache", "Cough", "Chest Pain",
            "Shortness of Breath", "Stomach Pain",
            "Nausea", "Fatigue", "Dizziness"
        ])

        if st.button("Next"):
            st.session_state.data["symptom"] = symptom
            st.session_state.step = 1
            st.rerun()

    # STEP 2
    elif st.session_state.step == 1:
        severity = st.select_slider("Severity", ["Mild", "Moderate", "Severe"])

        if st.button("Next"):
            st.session_state.data["severity"] = severity
            st.session_state.step = 2
            st.rerun()

    # STEP 3
    elif st.session_state.step == 2:
        duration = st.selectbox("Duration", [
            "<24 hours", "1-3 days", "4-7 days", "1-2 weeks", "2+ weeks"
        ])

        if st.button("Next"):
            st.session_state.data["duration"] = duration
            st.session_state.step = 3
            st.rerun()

    # STEP 4
    elif st.session_state.step == 3:

        red_flag = st.checkbox("Severe symptoms (e.g. chest pain, breathing difficulty)")
        worsening = st.checkbox("Symptoms getting worse")

        if st.button("See Results"):
            st.session_state.data["red_flag"] = red_flag
            st.session_state.data["worsening"] = worsening
            st.session_state.step = 4
            st.rerun()

    # RESULT
    elif st.session_state.step == 4:

        data = st.session_state.data
        score = 0

        if data["severity"] == "Severe":
            score += 3
        elif data["severity"] == "Moderate":
            score += 2
        else:
            score += 1

        if data["duration"] == "2+ weeks":
            score += 3
        elif data["duration"] == "1-2 weeks":
            score += 2

        if data["worsening"]:
            score += 2

        st.markdown("### 🧾 Result")

        if data["red_flag"]:
            st.error("🚨 EMERGENCY — Seek immediate medical help.")
        elif score >= 6:
            st.error("🔴 HIGH RISK — Urgent attention needed.")
        elif score >= 4:
            st.warning("🟠 MEDIUM RISK — Consult a GP.")
        else:
            st.success("🟢 LOW RISK — Monitor symptoms.")

        if st.button("Restart"):
            st.session_state.step = 0
            st.session_state.data = {}
            st.rerun()