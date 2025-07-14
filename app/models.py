from sqlalchemy import Column, Integer, String, JSON, Text
from .db import Base

class CrewMember(Base):
    __tablename__ = "crew_members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    preferences = Column(JSON, nullable=True)

class Rule(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True, index=True)
    rule_text = Column(Text)
    validated = Column(String)

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer)
    feedback = Column(JSON)
    analysis = Column(JSON)