from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Enquiry
class EnquiryCreate(BaseModel):
    student_name: str
    contact_info: str
    details: Optional[str]

class EnquiryOut(BaseModel):
    id: str
    student_name: str
    contact_info: str
    details: Optional[str]
    status: str
    scheduled_demo_at: Optional[datetime]
    created_by: Optional[str]

    class Config:
        orm_mode = True

class EnquirySchedule(BaseModel):
    scheduled_demo_at: datetime

# Batch
class BatchOut(BaseModel):
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    status: str

    class Config:
        orm_mode = True

# Notes
class NoteOut(BaseModel):
    id: str
    session_id: str
    teacher_id: str
    file_url: str
    created_at: datetime

    class Config:
        orm_mode = True

class NoteCreate(BaseModel):
    session_id: str
    file_url: str

# Test & Questions
class QuestionOut(BaseModel):
    id: str
    text: str
    options_json: Dict[str, Any]

    class Config:
        orm_mode = True

class TestCreate(BaseModel):
    title: str
    type: str
    context_json: Dict[str, Any]
    topic_distribution: Dict[str, float]

class GradeData(BaseModel):
    answers_json: Dict[str, Any]
    score: float

class AttemptData(BaseModel):
    answers_json: Dict[str, Any]

class TestAttemptOut(BaseModel):
    id: str
    test_id: str
    student_id: str
    answers_json: Dict[str, Any]
    score: float
    submitted_at: datetime

    class Config:
        orm_mode = True

# Analytics
class AttendanceOut(BaseModel):
    session_id: str
    student_id: str
    status: str
    recorded_at: datetime

    class Config:
        orm_mode = True

class ResultOut(BaseModel):
    test_id: str
    student_id: str
    score: float
    submitted_at: datetime

    class Config:
        orm_mode = True