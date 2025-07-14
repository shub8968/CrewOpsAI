import logging
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.schemas import CrewMemberIn, RuleIn, ScheduleOut, FeedbackIn
from app.services.llm_client import call_llm
from .auth import verify_api_key
from .db import Base, engine, get_db
from .models import CrewMember, Rule, Feedback
from .modules.ai_scheduler import AIScheduler
from .modules.feedback_analyzer import FeedbackAnalyzer
from .modules.preference_analyzer import PreferenceAnalyzer
from .modules.rule_engine import RuleEngine

logging.basicConfig(level=logging.INFO)
Base.metadata.create_all(bind=engine)
app = FastAPI()

def reset_database():
    logging.info("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logging.info("Database reset complete.")

@app.on_event("startup")
def startup_event():
    reset_database()

@app.post("/admin/crew")
def add_crew(member: CrewMemberIn, db: Session = Depends(get_db)):
    try:
        prefs = member.preferences
        if isinstance(prefs, str):
            prefs = call_llm(f"Convert this into structured preferences: {prefs}")
        crew = CrewMember(name=member.name, preferences=prefs)
        db.add(crew)
        db.commit()
        db.refresh(crew)
        return {"id": crew.id, "name": crew.name}
    except Exception:
        return {"error": "An unexpected error occurred."}, 500

@app.post("/admin/rule", dependencies=[Depends(verify_api_key)])
def add_rule(rule: RuleIn, db=Depends(get_db)):
    db_obj = Rule(rule_text=rule.rule_text)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.post("/admin/rule_bulk", dependencies=[Depends(verify_api_key)])
def add_rule_bulk(rules: list[RuleIn], db: Session = Depends(get_db)):
    try:
        added_rules = []
        for rule in rules:
            db_obj = Rule(rule_text=rule.rule_text)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            added_rules.append({"id": db_obj.id, "rule_text": db_obj.rule_text})
        return {"status": "success", "added_rules": added_rules}
    except Exception:
        return {"error": "An unexpected error occurred."}, 500

@app.get("/schedule", response_model=ScheduleOut, dependencies=[Depends(verify_api_key)])
def get_schedule(db=Depends(get_db)):
    rules = RuleEngine(db).load_and_validate()
    prefs = PreferenceAnalyzer(db).get_all()
    sched = AIScheduler(rules, prefs).generate()
    return {"assignments": sched}

@app.post("/feedback", dependencies=[Depends(verify_api_key)])
def post_feedback(fb: FeedbackIn, db=Depends(get_db)):
    analysis = FeedbackAnalyzer().process(fb.feedback)
    db_obj = Feedback(crew_id=fb.crew_id, feedback=fb.feedback, analysis=analysis)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return {"status": "stored", "analysis": analysis}

@app.post("/admin/crew_bulk")
def add_crew_bulk(members: list[CrewMemberIn], db: Session = Depends(get_db)):
    try:
        added_crew = []
        for member in members:
            prefs = member.preferences
            if isinstance(prefs, str):
                prefs = call_llm(f"Convert this into structured preferences: {prefs}")
            crew = CrewMember(name=member.name, preferences=prefs)
            db.add(crew)
            db.commit()
            db.refresh(crew)
            added_crew.append({"id": crew.id, "name": crew.name})
        return {"status": "success", "added_crew": added_crew}
    except Exception:
        return {"error": "An unexpected error occurred."}, 500