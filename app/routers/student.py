# app/routers/student.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

def get_current_student(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != 'student':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student privileges required"
        )
    return current_user

# ----- Session Notes -----
@router.get("/classes/{class_id}/notes", response_model=List[schemas.NoteOut])
def get_session_notes(
    class_id: str,
    db: Session = Depends(get_db),
    student: models.User = Depends(get_current_student)
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

# ----- Classroom Tests -----
@router.get("/tests/available", response_model=List[schemas.TestCreate])
def list_available_tests(
    db: Session = Depends(get_db),
    student: models.User = Depends(get_current_student)
):
    """
    List all classroom tests available.
    """
    tests = db.query(models.Test).filter(models.Test.type == 'classroom').all()
    # Use TestCreate schema to return only title, type, context_json, topic_distribution
    return tests

@router.post("/tests/{test_id}/attempt", response_model=schemas.TestAttemptOut, status_code=status.HTTP_201_CREATED)
def attempt_classroom_test(
    test_id: str,
    attempt: schemas.AttemptData,
    db: Session = Depends(get_db),
    student: models.User = Depends(get_current_student)
):
    """
    Student attempts a classroom test. Currently, score is defaulted to 0.0.
    """
    test = db.query(models.Test).filter(models.Test.id == test_id, models.Test.type == 'classroom').first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    new_attempt = models.TestAttempt(
        test_id=test_id,
        student_id=student.id,
        answers_json=attempt.answers_json,
        score=0.0  # TODO: compute actual score based on questions
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)
    return new_attempt

# ----- Custom Tests -----
@router.post("/custom-tests/", response_model=schemas.TestCreate, status_code=status.HTTP_201_CREATED)
def create_custom_test(
    test_in: schemas.TestCreate,
    db: Session = Depends(get_db),
    student: models.User = Depends(get_current_student)
):
    """
    Generate a custom test. The student provides the context and distribution,
    or you can extend this to auto-generate based on past attempts.
    """
    new_test = models.Test(
        title=test_in.title,
        creator_id=student.id,
        type='custom',
        context_json=test_in.context_json,
        topic_distribution=test_in.topic_distribution
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test

# ----- Results -----
@router.get("/results/tests/{test_id}", response_model=schemas.TestAttemptOut)
def get_test_result(
    test_id: str,
    db: Session = Depends(get_db),
    student: models.User = Depends(get_current_student)
):
    """
    View this student's result for a specific test.
    """
    attempt = (
        db.query(models.TestAttempt)
          .filter(
              models.TestAttempt.test_id == test_id,
              models.TestAttempt.student_id == student.id
          )
          .order_by(models.TestAttempt.submitted_at.desc())
          .first()
    )
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attempt found")
    return attempt

@router.get("/results/", response_model=List[schemas.TestAttemptOut])
def list_all_results(
    db: Session = Depends(get_db),
    student: models.User = Depends(get_current_student)
):
    """
    List all test results for the current student.
    """
    attempts = (
        db.query(models.TestAttempt)
          .filter(models.TestAttempt.student_id == student.id)
          .order_by(models.TestAttempt.submitted_at.desc())
          .all()
    )
    return attempts
