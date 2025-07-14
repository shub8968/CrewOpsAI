from ..models import Rule
from ..services.llm_client import call_llm
import json

class RuleEngine:
    def __init__(self, db):
        self.db = db

    def validate_rule(self, rule_text: str) -> bool:
        prompt = f"Validate this scheduling rule for compliance and clarity:\n{rule_text}"
        response = call_llm(prompt)

        if isinstance(response, dict):
            response_text = json.dumps(response).lower()
        elif isinstance(response, str):
            response_text = response.lower()
        else:
            response_text = str(response).lower()

        return 'valid' in response_text

    def load_and_validate(self):
        rules = self.db.query(Rule).all()
        valid_rules = [rule.rule_text for rule in rules if self.validate_rule(rule.rule_text)]
        return valid_rules