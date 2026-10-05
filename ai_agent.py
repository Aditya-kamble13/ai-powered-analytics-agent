import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)

def ask_gemini_analyst(df, user_query):
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "❌ GEMINI_API_KEY is missing in .env file."
        
    try:
        client = genai.Client(api_key=api_key)
        
        # Prepare context from DataFrame summary
        dataset_summary = f"""
        Dataset Columns: {list(df.columns)}
        Total Rows: {len(df)}
        Sample Data (First 5 rows):
        {df.head(5).to_string()}
        """
        
        prompt = f"You are an expert AI Data Analyst. Analyze this dataset context:\n{dataset_summary}\n\nUser Question: {user_query}"
        
        # Updated active model names
        models_to_try = ['gemini-3.8-flash', 'gemini-3.5-flash-lite']
        
        for model_name in models_to_try:
            for attempt in range(2):  # Try twice per model with short delay
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    return response.text
                except Exception as err:
                    if "503" in str(err) or "UNAVAILABLE" in str(err) or "404" in str(err):
                        time.sleep(1)
                        continue
                    else:
                        raise err
                        
        return "⚠️ Gemini servers are currently busy. Please try again in a few seconds."
        
    except Exception as e:
        return f"❌ Gemini API Error: {e}"