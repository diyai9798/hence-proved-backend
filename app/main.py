from fastapi import FastAPI
from .database import engine, Base
from .auth import auth_router
from .routers import staff, teacher, student, analytics

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coaching Center Management System")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(staff.router, prefix="/enquiries", tags=["staff"])
app.include_router(staff.batch_router, prefix="/batches", tags=["staff"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(teacher.router, tags=["teacher"])
app.include_router(student.router, tags=["student"])