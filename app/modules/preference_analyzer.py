import json
from ..models import CrewMember
from ..services.llm_client import call_llm

class PreferenceAnalyzer:
    def __init__(self, db):
        self.db = db

    def analyze_nl(self, text: str) -> dict:
        prompt = f"Extract and categorize crew scheduling preferences:\n{text}"
        return eval(call_llm(prompt))

    def get_all(self):
        crew_list = self.db.query(CrewMember).all()
        parsed = []
        for c in crew_list:
            if isinstance(c.preferences, dict):
                prefs = c.preferences
            else:
                try:
                    prefs = json.loads(c.preferences)
                except:
                    prefs = self.analyze_nl(str(c.preferences))
            parsed.append({"id": c.id, "name": c.name, **prefs})
        return parsed