# WomenRise — Backend

FastAPI backend for **WomenRise**, a digital ecosystem empowering women through
education, a handmade marketplace, and community/mentorship.

Frontend repo: https://github.com/ibragimovAzizbek/WOMENRISE-FRONT

## Stack
- FastAPI + Uvicorn
- SQLAlchemy 2 + SQLite
- JWT auth (PyJWT) + passlib password hashing

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The database is created and seeded automatically on first startup.
Interactive API docs: http://localhost:8000/docs

**Demo login:** `demo@womenrise.org` / `demo1234`

## API overview (prefix `/api`)
| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Courses | `GET /courses`, `GET /courses/{id}`, `POST /courses/{id}/enroll`, `GET /enrollments`, `PATCH /enrollments/{id}/progress` |
| Marketplace | `GET /products`, `GET /products/{id}`, `GET /products/mine`, `POST /products`, `POST /orders`, `GET /orders` |
| Community | `GET/POST /community/posts`, `GET /community/posts/{id}`, `POST .../like`, `POST .../comments` |
| Mentorship | `GET /mentors`, `POST /mentorship`, `GET /mentorship` |
| Stats | `GET /stats` |

## Project layout
```
app/
  main.py        # app + CORS + router wiring + startup seed
  config.py      # settings (secret, db url, CORS)
  database.py    # engine, session, Base, get_db
  models.py      # SQLAlchemy models
  schemas.py     # Pydantic request/response contract
  security.py    # hashing, JWT, current-user deps
  seed.py        # demo data
  routers/       # auth, courses, marketplace, community
```
