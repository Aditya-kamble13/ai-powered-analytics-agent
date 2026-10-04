import os
import time
import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY missing hai! Local .env file check karein.")

client = genai.Client(api_key=api_key)

def ask_data_agent(df: pd.DataFrame, user_query: str) -> str:
    schema_info = f"""
    Columns: {list(df.columns)}
    Data Types: {df.dtypes.to_string()}
    Data Sample (head 3): {df.head(3).to_dict(orient='records')}
    """

    prompt = f"""
    You are an expert Python Data Analyst.
    Given Pandas DataFrame `df`:
    {schema_info}

    User Question: "{user_query}"

    Task:
    1. Write ONLY executable Python code using `df` to answer the question.
    2. Store output string in variable `result`.
    3. Do NOT include markdown blocks like ```python. Strictly raw code.
    """

    # 3 Times Auto-Retry Logic for 503 Server Overload
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )

            code_to_exec = response.text.strip().replace("```python", "").replace("```", "").strip()

            local_vars = {'df': df, 'pd': pd}
            exec(code_to_exec, {}, local_vars)

            return str(local_vars.get('result', 'Code executed without result output.'))

        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retry
                    continue
            return f"Error executing query: {str(e)}"