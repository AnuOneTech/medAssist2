
import google.generativeai as genai
import os
from datetime import datetime
from pandas import pandas as pd
import base64

# Configure Gemini API with key from environment

# streamlit run App.py
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY environment variable not set. "
        "Please set it to your Google Gemini API key."
    )
genai.configure(api_key=api_key)

def call_llm(prompt, image=None):
    # Use a valid model ID
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    content = [prompt]
    
    if image is not None:
        try:
            image.seek(0)
            image_data = image.read()
            
            # The SDK can often wrap this automatically if you pass a dict
            image_part = {
                "mime_type": image.type, # Streamlit provides this automatically
                "data": image_data
            }
            content.append(image_part)
        except Exception as e:
            print(f"Warning: Could not process image: {e}")
    
    try:
        # Use stream=False if you want the whole response at once
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Gemini API error: {str(e)}"

def log_interaction(
    question: str,
    category: str = "",
    mode: str = "",
    safe: bool = None,
    response: str = "",
    rating: str = "",
    comments: str = "",
    image_uploaded: str = "no",
):
    """Logs activity to ``logs/interactions.csv``.

    The function is called for both the original user query and later when a
    piece of feedback is submitted.  All rows are appended; callers may choose
    to supply only a subset of the fields depending on context.  Missing values
    will result in empty cells in the CSV.
    """
    log_path = "logs/interactions.csv"
    row = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "category": category,
        "mode": mode,
        "safe": safe,
        "response": response,
        "rating": rating,
        "comments": comments,
        "image_uploaded": image_uploaded,
    }
    try:
        df_existing = pd.read_csv(log_path)
        df = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([row])
    df.to_csv(log_path, index=False)