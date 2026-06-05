"""Courses + enrollments router. TO BE IMPLEMENTED.

Endpoints (prefix /api):
  GET   /api/courses?category=        -> List[CourseOut]
  GET   /api/courses/{id}             -> CourseOut
  POST  /api/courses/{id}/enroll (auth) -> EnrollmentOut
  GET   /api/enrollments (auth)       -> List[EnrollmentOut]   (current user's)
  PATCH /api/enrollments/{id}/progress (auth) body=ProgressUpdate -> EnrollmentOut
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/api", tags=["courses"])


@router.get("/courses", response_model=List[schemas.CourseOut])
def list_courses(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Course)
    if category:
        query = query.filter(models.Course.category == category)
    return query.all()


@router.get("/courses/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("/courses/{course_id}/enroll", response_model=schemas.EnrollmentOut, status_code=status.HTTP_201_CREATED)
def enroll(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.user_id == current_user.id, models.Enrollment.course_id == course_id)
        .first()
    )
    if existing:
        return existing

    enrollment = models.Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(enrollment)
    course.students_count = (course.students_count or 0) + 1
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/enrollments", response_model=List[schemas.EnrollmentOut])
def my_enrollments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Enrollment)
        .filter(models.Enrollment.user_id == current_user.id)
        .all()
    )


@router.patch("/enrollments/{enrollment_id}/progress", response_model=schemas.EnrollmentOut)
def update_progress(
    enrollment_id: int,
    body: schemas.ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    if enrollment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your enrollment")

    enrollment.progress = body.progress
    if body.progress == 100:
        enrollment.completed = True
    db.commit()
    db.refresh(enrollment)
    return enrollment
