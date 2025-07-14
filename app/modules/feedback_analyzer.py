import json

from app.services.llm_client import call_llm


class FeedbackAnalyzer:
    def process(self, feedback_json: dict) -> dict:
        prompt = f"Analyze this scheduling feedback:\n{feedback_json}"
        response = call_llm(prompt)
        if isinstance(response, str):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"error": "Invalid response from LLM"}
        return response
