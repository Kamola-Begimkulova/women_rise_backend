from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Dependency to require admin role
def get_current_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ---------- Schemas for Admin Operations ----------
class UserRoleUpdate(BaseModel):
    role: str

class CourseCreateUpdate(BaseModel):
    title: str
    description: str = ""
    category: str
    level: str = "Beginner"
    instructor_name: str = ""
    price: float = 0.0
    image_url: str = ""
    lessons_count: int = 0
    duration_hours: float = 0.0

class OrderStatusUpdate(BaseModel):
    status: str

# ---------- User Management ----------
@router.get("/users", response_model=List[schemas.UserOut])
def list_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.order_by(models.User.created_at.desc()).all()

@router.patch("/users/{user_id}/role", response_model=schemas.UserOut)
def update_user_role(
    user_id: int,
    body: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    if body.role not in ["learner", "seller", "mentor", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be learner, seller, mentor, or admin")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-demotion
    if user.id == admin.id and body.role != "admin":
        raise HTTPException(status_code=400, detail="Admins cannot demote themselves")
        
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot delete their own account")
        
    db.delete(user)
    db.commit()
    return {"message": f"User {user.name} successfully deleted"}

# ---------- Course Management ----------
@router.post("/courses", response_model=schemas.CourseOut, status_code=201)
def create_course(
    body: CourseCreateUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    course = models.Course(
        title=body.title,
        description=body.description,
        category=body.category,
        level=body.level,
        instructor_name=body.instructor_name,
        price=body.price,
        image_url=body.image_url,
        lessons_count=body.lessons_count,
        duration_hours=body.duration_hours,
        rating=4.5,
        students_count=0
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.put("/courses/{course_id}", response_model=schemas.CourseOut)
def update_course(
    course_id: int,
    body: CourseCreateUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course.title = body.title
    course.description = body.description
    course.category = body.category
    course.level = body.level
    course.instructor_name = body.instructor_name
    course.price = body.price
    if body.image_url:
        course.image_url = body.image_url
    course.lessons_count = body.lessons_count
    course.duration_hours = body.duration_hours
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    db.delete(course)
    db.commit()
    return {"message": f"Course '{course.title}' successfully deleted"}

# ---------- Order Management ----------
@router.get("/orders")
def list_all_orders(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    results = []
    for order in orders:
        # Get buyer details manually as relationship is not defined directly
        buyer = db.query(models.User).filter(models.User.id == order.buyer_id).first()
        buyer_name = buyer.name if buyer else "Unknown Buyer"
        buyer_email = buyer.email if buyer else "unknown@womenrise.org"
        
        items = []
        for item in order.items:
            items.append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "title": item.title
            })
            
        results.append({
            "id": order.id,
            "total": order.total,
            "status": order.status,
            "created_at": order.created_at,
            "buyer": {
                "id": order.buyer_id,
                "name": buyer_name,
                "email": buyer_email
            },
            "items": items
        })
    return results

@router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    if body.status not in ["pending", "paid", "shipped"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be pending, paid, or shipped")
        
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = body.status
    db.commit()
    return {"id": order.id, "status": order.status}

# ---------- Moderation ----------
@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post successfully deleted"}

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return {"message": "Comment successfully deleted"}

# ---------- Detailed Analytics Stats ----------
@router.get("/stats/breakdown")
def get_stats_breakdown(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    # User breakdowns
    total_users = db.query(models.User).count()
    learners = db.query(models.User).filter(models.User.role == "learner").count()
    sellers = db.query(models.User).filter(models.User.role == "seller").count()
    mentors = db.query(models.User).filter(models.User.role == "mentor").count()
    admins = db.query(models.User).filter(models.User.role == "admin").count()
    
    # Revenue / Sales
    economic_impact = db.query(func.coalesce(func.sum(models.Order.total), 0.0)).scalar() or 0.0
    orders_count = db.query(models.Order).count()
    
    # Courses
    total_courses = db.query(models.Course).count()
    total_enrollments = db.query(models.Enrollment).count()
    
    # Products
    total_products = db.query(models.Product).count()
    
    # Course categories breakdown
    course_cats = db.query(models.Course.category, func.count(models.Course.id)).group_by(models.Course.category).all()
    course_categories = {cat: count for cat, count in course_cats}
    
    # Product categories breakdown
    prod_cats = db.query(models.Product.category, func.count(models.Product.id)).group_by(models.Product.category).all()
    product_categories = {cat: count for cat, count in prod_cats}
    
    # Enrollments over time (or grouped by course)
    course_enrollments = db.query(
        models.Course.title, 
        func.count(models.Enrollment.id)
    ).join(
        models.Enrollment, models.Enrollment.course_id == models.Course.id
    ).group_by(models.Course.id).order_by(desc(func.count(models.Enrollment.id))).limit(5).all()
    
    top_courses = [{"title": r[0], "enrollments": r[1]} for r in course_enrollments]
    
    # Recent orders
    recent_orders_raw = db.query(models.Order).order_by(models.Order.created_at.desc()).limit(5).all()
    recent_orders = []
    for order in recent_orders_raw:
        buyer = db.query(models.User).filter(models.User.id == order.buyer_id).first()
        recent_orders.append({
            "id": order.id,
            "total": order.total,
            "status": order.status,
            "created_at": order.created_at,
            "buyer_name": buyer.name if buyer else "Unknown User"
        })
        
    return {
        "users": {
            "total": total_users,
            "learner": learners,
            "seller": sellers,
            "mentor": mentors,
            "admin": admins
        },
        "sales": {
            "total_revenue": float(economic_impact),
            "orders_count": orders_count,
            "average_order_value": float(economic_impact / orders_count) if orders_count > 0 else 0.0
        },
        "courses": {
            "total": total_courses,
            "enrollments": total_enrollments,
            "categories": course_categories,
            "top_courses": top_courses
        },
        "products": {
            "total": total_products,
            "categories": product_categories
        },
        "recent_orders": recent_orders
    }
