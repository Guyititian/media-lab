from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router

app = FastAPI()

# =====================================================
# CORS (FIXES "LOAD FAILED" FROM FRONTEND)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://guyititian.github.io",
        "https://guyititian.github.io/media-lab",
        "https://guyititian.github.io/media-tiles"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# API ROUTES
# =====================================================
app.include_router(router)

# =====================================================
# STATIC FILES (DOWNLOAD OUTPUTS)
# =====================================================
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/")
def root():
    return {"status": "media-lab online"}
