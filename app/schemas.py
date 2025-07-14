import json
from typing import Union, Dict, Any
from pydantic import BaseModel, model_validator

class CrewMemberIn(BaseModel):
    name: str
    preferences: Union[str, Dict[str, Any]]

    @model_validator(mode="before")
    def validate_preferences(cls, values):
        prefs = values.get("preferences")
        if isinstance(prefs, str):
            prefs = prefs.strip()
            if prefs.startswith("{") and prefs.endswith("}"):
                try:
                    values["preferences"] = json.loads(prefs)
                except json.JSONDecodeError:
                    values["preferences"] = prefs
            else:
                values["preferences"] = prefs
        elif isinstance(prefs, dict):
            values["preferences"] = prefs
        else:
            raise ValueError("Preferences must be a valid JSON string or dictionary")
        return values

class RuleIn(BaseModel):
    rule_text: str

class ScheduleOut(BaseModel):
    assignments: Dict[str, Any]

class FeedbackIn(BaseModel):
    crew_id: int
    feedback: Union[Dict[str, Any], str]