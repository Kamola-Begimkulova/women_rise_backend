"""Pydantic v2 schemas — the API request/response contract.

The frontend api client (frontend/src/api/client.js) is built against these shapes.
Keep field names in sync on both sides.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth / Users ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "learner"  # learner | seller | mentor
    bio: str = ""
    expertise: str = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORMModel):
    id: int
    name: str
    email: EmailStr
    role: str
    bio: str = ""
    avatar_url: str = ""
    expertise: str = ""
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Courses ----------
class CourseOut(ORMModel):
    id: int
    title: str
    description: str
    category: str
    level: str
    instructor_name: str
    price: float
    image_url: str
    lessons_count: int
    duration_hours: float
    rating: float
    students_count: int


class EnrollmentOut(ORMModel):
    id: int
    progress: int
    completed: bool
    enrolled_at: datetime
    course: CourseOut


class ProgressUpdate(BaseModel):
    progress: int = Field(ge=0, le=100)


# ---------- Marketplace ----------
class ProductCreate(BaseModel):
    title: str
    description: str = ""
    category: str
    price: float = Field(ge=0)
    image_url: str = ""
    stock: int = Field(default=10, ge=0)


class SellerLite(ORMModel):
    id: int
    name: str
    avatar_url: str = ""


class ProductOut(ORMModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    image_url: str
    stock: int
    rating: float
    seller: SellerLite


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class OrderCreate(BaseModel):
    items: List[OrderItemIn]


class OrderItemOut(ORMModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    title: str


class OrderOut(ORMModel):
    id: int
    total: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]


# ---------- Community ----------
class AuthorLite(ORMModel):
    id: int
    name: str
    avatar_url: str = ""
    role: str = "learner"


class PostCreate(BaseModel):
    title: str
    body: str = ""
    category: str = "general"


class CommentCreate(BaseModel):
    body: str


class CommentOut(ORMModel):
    id: int
    body: str
    created_at: datetime
    author: AuthorLite


class PostOut(ORMModel):
    id: int
    title: str
    body: str
    category: str
    likes: int
    created_at: datetime
    author: AuthorLite
    comment_count: int = 0


class PostDetail(PostOut):
    comments: List[CommentOut] = []


# ---------- Mentorship ----------
class MentorOut(ORMModel):
    id: int
    name: str
    bio: str = ""
    avatar_url: str = ""
    expertise: str = ""


class MentorshipCreate(BaseModel):
    mentor_id: int
    topic: str = ""
    message: str = ""


class MentorshipOut(ORMModel):
    id: int
    topic: str
    message: str
    status: str
    created_at: datetime
    mentor: MentorOut


# ---------- Stats (dashboard / impact) ----------
class StatsOut(BaseModel):
    women_served: int
    businesses_launched: int
    courses_count: int
    products_count: int
    economic_impact: float
    total_enrollments: int
