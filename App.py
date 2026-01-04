# app.py

import streamlit as st

from prompts import build_public_prompt, build_clinician_prompt
from safety import is_safe_for_public, is_safe_for_clinician
from utils import call_llm, log_interaction


st.set_page_config(page_title="MedAssist - Virtual Dr. Assistant", page_icon="🩺", layout="centered")

st.title("🩺 MedAssist - Virtual Dr. Assistant")
st.caption("Use case for AI as Health Educator and Clinician Assistant (Non-diagnostic)")


# -------- Mode selection --------
st.sidebar.header("Mode & Settings")

mode = st.sidebar.radio(
    "Assistant Mode:",
    ["General Public", "Clinician Assistant"]
)

category = st.sidebar.selectbox(
    "Category:",
    ["General Health", "Nutrition", "Sleep", "Exercise", "Symptoms", "Labs & Vitals", "Other1"]
)


# -------- Optional vitals & body metrics --------
st.sidebar.header("Optional Vitals & Body Metrics")

heart_rate = st.sidebar.text_input("Heart Rate (bpm) — optional")
temperature = st.sidebar.text_input("Body Temperature (°F) — optional")
sleep_hours = st.sidebar.text_input("Sleep (hours per day) — optional")
steps = st.sidebar.text_input("Steps Today — optional")

height_cm = st.sidebar.text_input("Height (cm) — optional")
weight_kg = st.sidebar.text_input("Weight (kg) — optional")

bmi = None
try:
    if height_cm.strip() and weight_kg.strip():
        h = float(height_cm)
        w = float(weight_kg)
        if h > 0:
            bmi = round(w / ((h / 100) ** 2), 2)
except ValueError:
    # Ignore invalid input; we won't calculate BMI in that case.
    bmi = None


# -------- Optional common lab values --------
st.sidebar.header("Optional Common Lab Values")

hemoglobin = st.sidebar.text_input("Hemoglobin (g/dL) — optional")
wbc = st.sidebar.text_input("WBC Count — optional")
platelets = st.sidebar.text_input("Platelets — optional")
glucose = st.sidebar.text_input("Blood Glucose (mg/dL) — optional")
cholesterol = st.sidebar.text_input("Total Cholesterol (mg/dL) — optional")
vitamin_d = st.sidebar.text_input("Vitamin D — optional")
ferritin = st.sidebar.text_input("Ferritin — optional")


# -------- Build vitals/labs dictionary if provided --------
vitals = {}

def add_if_present(key_label: str, value: str):
    if value and value.strip():
        vitals[key_label] = value.strip()

add_if_present("Heart rate (bpm)", heart_rate)
add_if_present("Body temperature (°F)", temperature)
add_if_present("Sleep (hours)", sleep_hours)
add_if_present("Steps today", steps)
add_if_present("Height (cm)", height_cm)
add_if_present("Weight (kg)", weight_kg)
if bmi is not None:
    vitals["BMI (calculated)"] = str(bmi)

add_if_present("Hemoglobin (g/dL)", hemoglobin)
add_if_present("WBC count", wbc)
add_if_present("Platelets", platelets)
add_if_present("Blood glucose (mg/dL)", glucose)
add_if_present("Total cholesterol (mg/dL)", cholesterol)
add_if_present("Vitamin D", vitamin_d)
add_if_present("Ferritin", ferritin)


# -------- Main question input --------
st.subheader("Ask a Question")

default_prompt_text = (
    "For example:\n"
    "- Public: Why is sleep important for teenagers?\n"
    "- Clinician: Summarize educational context for these labs and fatigue.\n"
)

question = st.text_area("Type your question here:", height=120, help=default_prompt_text)


# -------- Disclaimer --------
if mode == "General Public":
    st.info(
        "This assistant is for general health education only. "
        "It does not diagnose, treat, or replace a doctor."
    )
else:
    st.info(
        "Clinician Assistant Mode: For educational and organizational support only. "
        "Not for diagnosis, treatment, or clinical decision-making."
    )


# -------- Handle submission --------
if st.button("Get Response"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # Safety check based on mode
        if mode == "General Public":
            safe = is_safe_for_public(question)
        else:
            safe = is_safe_for_clinician(question)

        # Log the interaction (even if unsafe)
        log_interaction(question=question, category=category, mode=mode, safe=safe)

        if not safe:
            st.error(
                "This question may involve sensitive or unsafe content. "
                "Please talk to a trusted adult, healthcare professional, or local emergency service "
                "instead of relying on this tool."
            )
        else:
            # Build prompt according to mode
            if mode == "General Public":
                prompt = build_public_prompt(question, category, vitals)
            else:
                prompt = build_clinician_prompt(question, category, vitals)

            with st.spinner("Thinking..."):
                try:
                    response = call_llm(prompt)
                    st.markdown("### Assistant Response")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error while calling the AI model: {e}")
