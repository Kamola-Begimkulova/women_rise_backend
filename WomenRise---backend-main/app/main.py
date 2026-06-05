"""WomenRise API — FastAPI application entrypoint.

Run from the backend/ directory:
    uvicorn app.main:app --reload --port 8000
Interactive docs at http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import Base, engine, SessionLocal
from .routers import auth, courses, marketplace, community
from .seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed demo data on startup.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="WomenRise API",
    description="Empowering Women Through Digital Innovation — education, marketplace, community.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_origin_regex=config.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(marketplace.router)
app.include_router(community.router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "service": "WomenRise API"}
