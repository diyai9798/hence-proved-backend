# app/routers/teacher.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

def get_current_teacher(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != 'teacher':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher privileges required"
        )
    return current_user

# ----- Session Notes -----

@router.get("/classes/{class_id}/notes", response_model=List[schemas.NoteOut])
def download_session_notes(
    class_id: str,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(get_current_teacher)
):
    """
    Download notes for a given class session.
    """
    notes = (
        db.query(models.Note)
          .filter(models.Note.session_id == class_id)
          .all()
    )
    return notes

@router.post("/content/notes", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def upload_notes(
    note_in: schemas.NoteCreate,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(get_current_teacher)
):
    """
    Upload handwritten notes for a session.
    """
    # Verify session exists
    session = db.query(models.ClassSession).filter(models.ClassSession.id == note_in.session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class session not found")

    new_note = models.Note(
        session_id=note_in.session_id,
        teacher_id=teacher.id,
        file_url=note_in.file_url,
        created_at=datetime.utcnow()
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

# ----- Classroom Tests -----

@router.post("/tests/", response_model=schemas.TestCreate, status_code=status.HTTP_201_CREATED)
def generate_classroom_test(
    test_in: schemas.TestCreate,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(get_current_teacher)
):
    """
    Generate a new classroom test (AI-driven).
    """
    new_test = models.Test(
        title=test_in.title,
        creator_id=teacher.id,
        type='classroom',
        context_json=test_in.context_json,
        topic_distribution=test_in.topic_distribution,
        created_at=datetime.utcnow()
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return test_in  # returns title, type, context_json, topic_distribution

@router.get("/tests/{test_id}/questions", response_model=List[schemas.QuestionOut])
def view_test_questions(
    test_id: str,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(get_current_teacher)
):
    """
    View the questions for a given test.
    """
    questions = db.query(models.Question).filter(models.Question.test_id == test_id).all()
    if not questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questions not found for this test")
    return questions

@router.post("/tests/{test_id}/grade", response_model=schemas.TestAttemptOut)
def submit_grading(
    test_id: str,
    grade_in: schemas.GradeData,
    student_id: str,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(get_current_teacher)
):
    """
    Submit grading data for a student's test attempt.
    The student_id must be provided as a query parameter.
    """
    # Find the student's latest attempt (if any)
    attempt = (
        db.query(models.TestAttempt)
          .filter(
              models.TestAttempt.test_id == test_id,
              models.TestAttempt.student_id == student_id
          )
          .order_by(models.TestAttempt.submitted_at.desc())
          .first()
    )
    if not attempt:
        # Create a new attempt record if none exists
        attempt = models.TestAttempt(
            test_id=test_id,
            student_id=student_id,
            answers_json=grade_in.answers_json,
            score=grade_in.score,
            submitted_at=datetime.utcnow()
        )
        db.add(attempt)
    else:
        # Update existing attempt
        attempt.answers_json = grade_in.answers_json
        attempt.score = grade_in.score
        attempt.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(attempt)
    return attempt
