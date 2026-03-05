
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
    """
    Call Google Gemini with text and optional image support.
    
    Args:
        prompt (str): The text prompt
        image: Optional Streamlit UploadedFile object
    
    Returns:
        str: Response from Gemini
    """
    # Initialize model (use available Gemini version)
    # 'gemini-1.5' is currently supported; adjust if necessary.
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Build content list
    content = [prompt]
    
    # Add image if provided
    if image is not None:
        try:
            # Read image and encode as base64
            image_data = image.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine media type
            media_type = "image/jpeg"
            if image.type == "image/png":
                media_type = "image/png"
            elif image.type in ["image/gif", "image/bmp"]:
                media_type = image.type
            
            # Create image part for Gemini
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            image_part = genai.types.Part.from_data(
                data=image_data,
                mime_type=media_type
            )
            content.insert(0, image_part)
        except Exception as e:
            print(f"Warning: Could not process image: {e}")
    
    # Call Gemini API
    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

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