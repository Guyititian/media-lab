from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router
from core.cleanup import run_cleanup
from core.config import OUTPUT_DIR
from core.jobs import job_counts

app = FastAPI(title="Media-Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://guyititian.github.io",
        "https://guyititian.github.io/media-lab",
        "https://guyititian.github.io/media-tiles",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.on_event("startup")
def startup_cleanup():
    run_cleanup()


@app.get("/")
def root():
    return {
        "status": "media-lab online",
        "docs": "/docs"
    }


@app.head("/")
def root_head():
    return {}


@app.get("/health")
def health():
    return {
        "success": True,
        "status": "healthy",
        "jobs": job_counts()
    }
