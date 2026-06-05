"""SQLAlchemy ORM models — the single source of truth for the data layer.

Roles: a user can learn, sell, and mentor; `role` marks their primary identity.
Domains: Education (Course/Enrollment), Marketplace (Product/Order/OrderItem),
Community (Post/Comment, Mentorship).
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="learner")  # learner | seller | mentor | admin
    bio = Column(Text, default="")
    avatar_url = Column(String, default="")
    expertise = Column(String, default="")  # for mentors: comma-separated topics
    created_at = Column(DateTime, default=_now)

    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, index=True)  # coding | yoga | fitness | business
    level = Column(String, default="Beginner")  # Beginner | Intermediate | Advanced
    instructor_name = Column(String, default="")
    price = Column(Float, default=0.0)
    image_url = Column(String, default="")
    lessons_count = Column(Integer, default=0)
    duration_hours = Column(Float, default=0.0)
    rating = Column(Float, default=4.5)
    students_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress = Column(Integer, default=0)  # 0-100
    completed = Column(Boolean, default=False)
    enrolled_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, index=True)  # jewelry | textiles | art | beauty | home
    price = Column(Float, default=0.0)
    image_url = Column(String, default="")
    stock = Column(Integer, default=0)
    rating = Column(Float, default=4.8)
    created_at = Column(DateTime, default=_now)

    seller = relationship("User", back_populates="products")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total = Column(Float, default=0.0)
    status = Column(String, default="paid")  # pending | paid | shipped
    created_at = Column(DateTime, default=_now)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    title = Column(String, default="")  # snapshot of product title at purchase

    order = relationship("Order", back_populates="items")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, default="")
    category = Column(String, default="general")  # general | wins | questions | collab
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)

    post = relationship("Post", back_populates="comments")
    author = relationship("User")


class Mentorship(Base):
    __tablename__ = "mentorships"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, default="")
    message = Column(Text, default="")
    status = Column(String, default="requested")  # requested | accepted | declined
    created_at = Column(DateTime, default=_now)

    mentor = relationship("User", foreign_keys=[mentor_id])
    mentee = relationship("User", foreign_keys=[mentee_id])
