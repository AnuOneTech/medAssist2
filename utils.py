""" from openai import OpenAI

client = OpenAI()

def call_llm(prompt:str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"] """

from groq import Groq
import os
from datetime import datetime
from pandas import pandas as pd

client = Groq(api_key="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")

def call_llm(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages = [{"role": "user", "content": prompt}],
        temperature = 0.4
    )
    return response.choices[0].message.content

def log_interaction(question: str, category: str, mode: str, safe: bool): 
    """ Logs the interaction to logs/interactions.csv. Creates the file if it does not exist. """ 
    log_path = "logs/interactions.csv" 
    row = { "timestamp": datetime.now().isoformat(), "question": question, "category": category, "mode": mode, "safe": safe, } 
    try: 
        df_existing = pd.read_csv(log_path) 
        df = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True) 
    except FileNotFoundError: 
        df = pd.DataFrame([row]) 
        df.to_csv(log_path, index=False)