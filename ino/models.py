from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
import datetime


Base = declarative_base()


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    student_name = Column(String(200))
    question_id = Column(String(100))
    student_text = Column(Text)
    teacher_text = Column(Text)
    similarity = Column(Float)
    grade = Column(String(4))
    marks = Column(Integer)
    matched_keywords = Column(Text)
    missing_keywords = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)