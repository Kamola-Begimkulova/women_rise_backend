"""Community router — posts, comments, mentors, stats. TO BE IMPLEMENTED.

Endpoints (prefix /api):
  GET   /api/community/posts?category=         -> List[PostOut]  (comment_count set)
  POST  /api/community/posts (auth) body=PostCreate -> PostOut
  GET   /api/community/posts/{id}              -> PostDetail     (with comments)
  POST  /api/community/posts/{id}/like         -> PostOut        (likes += 1)
  POST  /api/community/posts/{id}/comments (auth) body=CommentCreate -> CommentOut
  GET   /api/mentors                           -> List[MentorOut] (users with role=mentor)
  POST  /api/mentorship (auth) body=MentorshipCreate -> MentorshipOut
  GET   /api/mentorship (auth)                 -> List[MentorshipOut] (mentee = current user)
  GET   /api/stats                             -> StatsOut       (aggregate impact metrics)
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/api", tags=["community"])


def _post_to_out(post: models.Post) -> schemas.PostOut:
    """Build a PostOut with comment_count populated."""
    out = schemas.PostOut.model_validate(post)
    out.comment_count = len(post.comments)
    return out


@router.get("/community/posts", response_model=List[schemas.PostOut])
def list_posts(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Post)
    if category:
        query = query.filter(models.Post.category == category)
    posts = query.all()
    return [_post_to_out(p) for p in posts]


@router.post("/community/posts", response_model=schemas.PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    body: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = models.Post(
        author_id=current_user.id,
        title=body.title,
        body=body.body,
        category=body.category,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return _post_to_out(post)


@router.get("/community/posts/{post_id}", response_model=schemas.PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    detail = schemas.PostDetail.model_validate(post)
    detail.comment_count = len(post.comments)
    return detail


@router.post("/community/posts/{post_id}/like", response_model=schemas.PostOut)
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.likes = (post.likes or 0) + 1
    db.commit()
    db.refresh(post)
    return _post_to_out(post)


@router.post("/community/posts/{post_id}/comments", response_model=schemas.CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: int,
    body: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    comment = models.Comment(post_id=post_id, author_id=current_user.id, body=body.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/mentors", response_model=List[schemas.MentorOut])
def list_mentors(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == "mentor").all()


@router.post("/mentorship", response_model=schemas.MentorshipOut, status_code=status.HTTP_201_CREATED)
def create_mentorship(
    body: schemas.MentorshipCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    mentor = db.query(models.User).filter(models.User.id == body.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    if mentor.role != "mentor":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a mentor")

    mentorship = models.Mentorship(
        mentor_id=body.mentor_id,
        mentee_id=current_user.id,
        topic=body.topic,
        message=body.message,
    )
    db.add(mentorship)
    db.commit()
    db.refresh(mentorship)
    return mentorship


@router.get("/mentorship", response_model=List[schemas.MentorshipOut])
def my_mentorships(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Mentorship)
        .filter(models.Mentorship.mentee_id == current_user.id)
        .all()
    )


@router.get("/stats", response_model=schemas.StatsOut)
def get_stats(db: Session = Depends(get_db)):
    women_served = db.query(func.count(models.User.id)).scalar() or 0
    businesses_launched = db.query(func.count(distinct(models.Product.seller_id))).scalar() or 0
    courses_count = db.query(func.count(models.Course.id)).scalar() or 0
    products_count = db.query(func.count(models.Product.id)).scalar() or 0
    economic_impact = db.query(func.coalesce(func.sum(models.Order.total), 0.0)).scalar() or 0.0
    total_enrollments = db.query(func.count(models.Enrollment.id)).scalar() or 0

    return schemas.StatsOut(
        women_served=women_served,
        businesses_launched=businesses_launched,
        courses_count=courses_count,
        products_count=products_count,
        economic_impact=float(economic_impact),
        total_enrollments=total_enrollments,
    )
