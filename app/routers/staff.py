# app/routers/staff.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()
batch_router = APIRouter()

def get_current_staff(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != 'staff':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    return current_user

# ----- Enquiry Management -----

@router.get("/", response_model=List[schemas.EnquiryOut])
def list_enquiries(
    db: Session = Depends(get_db),
    staff: models.User = Depends(get_current_staff)
):
    """
    List all enquiries.
    """
    enquiries = db.query(models.Enquiry).all()
    return enquiries

@router.post("/", response_model=schemas.EnquiryOut, status_code=status.HTTP_201_CREATED)
def create_enquiry(
    enquiry_in: schemas.EnquiryCreate,
    db: Session = Depends(get_db),
    staff: models.User = Depends(get_current_staff)
):
    """
    Create a new enquiry (status defaults to 'open').
    """
    new_enq = models.Enquiry(
        student_name=enquiry_in.student_name,
        contact_info=enquiry_in.contact_info,
        details=enquiry_in.details,
        created_by=staff.id
    )
    db.add(new_enq)
    db.commit()
    db.refresh(new_enq)
    return new_enq

@router.put("/{enquiry_id}/schedule", response_model=schemas.EnquiryOut)
def schedule_enquiry(
    enquiry_id: str,
    sched: schemas.EnquirySchedule,
    db: Session = Depends(get_db),
    staff: models.User = Depends(get_current_staff)
):
    """
    Schedule a demo for an existing enquiry.
    """
    enq = db.query(models.Enquiry).filter(models.Enquiry.id == enquiry_id).first()
    if not enq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found"
        )
    enq.scheduled_demo_at = sched.scheduled_demo_at
    enq.status = 'scheduled'
    db.commit()
    db.refresh(enq)
    return enq

# ----- Batch Management -----

@batch_router.get("/", response_model=List[schemas.BatchOut])
def list_batches(
    db: Session = Depends(get_db),
    staff: models.User = Depends(get_current_staff)
):
    """
    List all batches.
    """
    batches = db.query(models.Batch).all()
    return batches
