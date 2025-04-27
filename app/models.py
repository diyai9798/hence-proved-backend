import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Text, JSON, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from .database import Base

roles = ('staff', 'teacher', 'student')
enquiry_status = ('open', 'scheduled', 'closed')
batch_status = ('planned', 'active', 'completed')
test_types = ('classroom', 'custom')
attendance_status = ('present', 'absent')

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(*roles, name='role'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Enquiry(Base):
    __tablename__ = 'enquiries'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_name = Column(String, nullable=False)
    contact_info = Column(String, nullable=False)
    details = Column(Text)
    status = Column(Enum(*enquiry_status, name='enquiry_status'), default='open')
    scheduled_demo_at = Column(DateTime, nullable=True)
    created_by = Column(String, ForeignKey('users.id'))
    creator = relationship('User')

class Batch(Base):
    __tablename__ = 'batches'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum(*batch_status, name='batch_status'), default='planned')

class ClassSession(Base):
    __tablename__ = 'class_sessions'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, ForeignKey('batches.id'))
    teacher_id = Column(String, ForeignKey('users.id'))
    topic = Column(String)
    starts_at = Column(DateTime)
    batch = relationship('Batch')
    teacher = relationship('User')

class Note(Base):
    __tablename__ = 'notes'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('class_sessions.id'))
    teacher_id = Column(String, ForeignKey('users.id'))
    file_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship('ClassSession')
    teacher = relationship('User')

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(String, ForeignKey('users.id'))
    creator = relationship('User')

class Test(Base):
    __tablename__ = 'tests'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    creator_id = Column(String, ForeignKey('users.id'))
    type = Column(Enum(*test_types, name='test_type'))
    context_json = Column(JSON)
    topic_distribution = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator = relationship('User')

class Question(Base):
    __tablename__ = 'questions'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String, ForeignKey('tests.id'))
    text = Column(Text)
    options_json = Column(JSON)
    answer_key = Column(Text)
    test = relationship('Test')

class QuestionTopic(Base):
    __tablename__ = 'question_topics'
    question_id = Column(String, ForeignKey('questions.id'), primary_key=True)
    topic_id = Column(String, ForeignKey('topics.id'), primary_key=True)

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('class_sessions.id'))
    student_id = Column(String, ForeignKey('users.id'))
    status = Column(Enum(*attendance_status, name='attendance_status'))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    session = relationship('ClassSession')
    student = relationship('User')

class TestAttempt(Base):
    __tablename__ = 'test_attempts'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String, ForeignKey('tests.id'))
    student_id = Column(String, ForeignKey('users.id'))
    answers_json = Column(JSON)
    score = Column(Float)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    test = relationship('Test')
    student = relationship('User')