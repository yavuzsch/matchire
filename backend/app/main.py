from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, skills, jobs, resumes, applications

import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Matchire API",
    description="AI-assisted recruitment platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(applications.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Matchire API is running"}