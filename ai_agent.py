import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiBIAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    def explain_root_cause(self, dataset_summary_str, issues_list):
        """Generates a natural language executive summary & root-cause analysis."""
        if not self.client:
            return "⚠️ Gemini API Key not found in .env. Showing standard summary."

        prompt = f"""
        You are an expert AI Data Auditor and Business Intelligence Agent.
        Analyze the following dataset context and detected anomalies, then provide a concise executive root-cause analysis.

        DATASET CONTEXT SUMMARY:
        {dataset_summary_str}

        DETECTED ANOMALIES & ISSUES:
        {issues_list}

        Your output should include:
        1. Executive Narrative (2-3 sentences explaining what went wrong and potential root cause).
        2. Actionable Business Recommendation.
        """

        try:
            # Updated model name here
            response = self.client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Error generating AI narrative: {str(e)}"

    def evaluate_custom_rule(self, df_sample_str, user_query):
        """Interprets natural language custom audit rules from user."""
        if not self.client:
            return "API Key missing."

        prompt = f"""
        Given the following pandas dataframe preview:
        {df_sample_str}

        User Request / Custom Rule: "{user_query}"

        Convert this custom audit request into a clear logical condition or explanation.
        State which columns need to be checked and what threshold or value indicates an anomaly/issue.
        Keep the response brief (max 3 sentences).
        """

        try:
            # Updated model name here
            response = self.client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Error executing AI rule: {str(e)}"