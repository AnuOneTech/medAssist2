# app.py

import streamlit as st

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-color: lightblue; /* Replace with your color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

from prompts import build_public_prompt, build_clinician_prompt
from safety import is_safe_for_public, is_safe_for_clinician
from utils import call_llm, log_interaction



st.set_page_config(page_title="MedAssist - Virtual Dr. Assistant", page_icon="🩺", layout="centered")


st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-color: #fafafa;        /* light grey */
        background-color: rgb(10,34,64);  /* navy */
        background-color: #ffefd5;        /* papayawhip */
        background-image: url('https://www.transparenttextures.com/patterns/blueprint.png'); /* Optional: add a subtle pattern */
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)


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
st.sidebar.header("Optional Vitals & Body Metrics:")

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

# default help text
default_prompt_text = (
    "For example:\n"
    "- Public: Why is sleep important for teenagers?\n"
    "- Clinician: Summarize educational context for these labs and fatigue.\n"
)

# initialize session state for question
if "question" not in st.session_state:
    st.session_state["question"] = ""

question = st.text_area("Type your question here:", height=120, help=default_prompt_text, value=st.session_state["question"])
# update session state whenever question changes
st.session_state["question"] = question

# optional image upload
st.subheader("Optional: Upload an Image")
st.caption("Images are sent to Gemini for analysis along with your question")
upload_col1, upload_col2 = st.columns([1, 2])
with upload_col1:
    uploaded_image = st.file_uploader("Choose an image (JPG, PNG, etc.)", type=["jpg", "jpeg", "png", "gif", "bmp"])
    if uploaded_image is not None:
        st.session_state["uploaded_image"] = uploaded_image
        st.success(f"✓ Image ready to send: {uploaded_image.name}")
with upload_col2:
    if "uploaded_image" in st.session_state and st.session_state["uploaded_image"]:
        st.image(st.session_state["uploaded_image"], width=150, caption="Current image")


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

        # Build prompt according to mode (even if unsafe, so we can log later)
        if mode == "General Public":
            prompt = build_public_prompt(question, category, vitals)
        else:
            prompt = build_clinician_prompt(question, category, vitals)

        if not safe:
            # log unsafe question with no response
            log_interaction(question=question, category=category, mode=mode, safe=safe, image_uploaded="yes" if st.session_state.get("uploaded_image") else "no")
            st.error(
                "This question may involve sensitive or unsafe content. "
                "Please talk to a trusted adult, healthcare professional, or local emergency service "
                "instead of relying on this tool."
            )
        else:
            with st.spinner("Thinking..."):
                try:
                    # pass uploaded image if present
                    uploaded_image = st.session_state.get("uploaded_image")
                    response = call_llm(prompt, image=uploaded_image)
                    st.markdown("### Assistant Response")
                    st.write(response)

                    # save for potential feedback and logging
                    st.session_state["last_question"] = question
                    st.session_state["last_category"] = category
                    st.session_state["last_mode"] = mode
                    st.session_state["last_safe"] = safe
                    st.session_state["last_response"] = response
                    st.session_state["last_image_uploaded"] = "yes" if uploaded_image else "no"

                    # log the interaction including response and image info
                    image_uploaded = "yes" if st.session_state.get("uploaded_image") else "no"
                    log_interaction(
                        question=question,
                        category=category,
                        mode=mode,
                        safe=safe,
                        response=response,
                        image_uploaded=image_uploaded,
                    )
                except Exception as e:
                    st.error(f"Error while calling the AI model: {e}")

# -------- Feedback section --------
if st.session_state.get("last_response"):
    st.markdown("---")
    st.subheader("Feedback")

    st.write("Was this answer helpful?")
    feedback_rating = st.radio("", ["Yes", "No"], key="fb_rating")
    feedback_comments = st.text_area("Additional comments (optional)", height=80, key="fb_comments")

    if st.button("Submit Feedback", key="submit_feedback"):
        log_interaction(
            question=st.session_state.get("last_question", ""),
            category=st.session_state.get("last_category", ""),
            mode=st.session_state.get("last_mode", ""),
            safe=st.session_state.get("last_safe", None),
            response=st.session_state.get("last_response", ""),
            rating=feedback_rating,
            comments=feedback_comments,
            image_uploaded=st.session_state.get("last_image_uploaded", "no"),
        )
        st.success("Thanks for your feedback!")
        # clear feedback-related session state to avoid duplicate logs
        for key in ["last_question", "last_category", "last_mode", "last_safe", "last_response"]:
            if key in st.session_state:
                del st.session_state[key]

