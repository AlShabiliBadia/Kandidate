from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import engine, Base
from services.shared import setup_logging
from .api.routes import (
    auth_router,
    users_router,
    settings_router,
    pipelines_router,
    jobs_router,
    applications_router,
    public_router,
)

logger = setup_logging("backend")

app = FastAPI(
    title="Kandidate ATS",
    description="Applicant Tracking System with AI-powered CV analysis",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(settings_router)
app.include_router(pipelines_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(public_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    logger.info("Kandidate Backend started successfully")


@app.get("/health")
async def health_check():
    return {
        "service": "kandidate-backend",
        "status": "healthy",
        "version": "2.0.0"
    }
