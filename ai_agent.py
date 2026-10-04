import pandas as pd
from google import genai
import os

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_data_agent(df: pd.DataFrame, user_query: str) -> str:
    """
    User ke natural language query se Pandas python code generate karke
    dataframe par execute karta hai aur accurate math/analysis answer deta hai.
    """
    try:
        # Dataframe schema aur column types extract karo
        schema_info = f"""
        Columns: {list(df.columns)}
        Data Types:
        {df.dtypes.to_string()}
        Data Sample (head 3):
        {df.head(3).to_dict(orient='records')}
        """

        # System prompt Gemini ko Pandas code generator banane ke liye
        prompt = f"""
        You are an expert Python Data Analyst.
        You are given a Pandas DataFrame named `df`.
        
        DataFrame Info:
        {schema_info}

        User Question: "{user_query}"

        Task:
        1. Write ONLY the executable Python code using `df` to calculate or find the exact answer to the user's question.
        2. Assign the final answer or output string to a variable named `result`.
        3. Do NOT include markdown code blocks (like ```python), explanations, or extra text. Output strictly raw executable Python code only.

        Example 1:
        User: "Employee table me kitne employees hain?"
        Code:
        result = f"Total employees: {{len(df)}}"

        Example 2:
        User: "Unki sabki salary ki Total batao and null kahan hai?"
        Code:
        total_sal = df['Salary'].sum() if 'Salary' in df.columns else 'N/A'
        null_counts = df.isnull().sum().to_dict()
        result = f"Total Salary: {{total_sal}}\\nNull values per column: {{null_counts}}"
        """

        # Gemini se Pandas Code Generate karwao
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        code_to_exec = response.text.strip().replace("```python", "").replace("```", "").strip()

        # Code ko safely local scope mein execute karo
        local_vars = {'df': df, 'pd': pd}
        exec(code_to_exec, {}, local_vars)

        # Execution ka output return karo
        output = local_vars.get('result', 'Code executed, but no `result` variable was set.')
        return str(output)

    except Exception as e:
        # Fallback: Agar code execution fail ho, toh direct LLM text analysis use karo
        fallback_prompt = f"Data Summary:\n{df.describe(include='all').to_string()}\n\nQuestion: {user_query}\nAnswer directly based on data:"
        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=fallback_prompt
        )
        return res.text