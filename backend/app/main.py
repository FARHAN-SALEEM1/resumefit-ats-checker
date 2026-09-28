from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import resumes, job_descriptions, analysis, feedback, export, history

# Creates resumefit.db and all tables on first run if they don't exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResumeFit API", version="1.0.0")

# Wide open for local dev — tighten this before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes.router)
app.include_router(job_descriptions.router)
app.include_router(analysis.router)
app.include_router(feedback.router)
app.include_router(export.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "ResumeFit API", "version": "1.0.0"}
