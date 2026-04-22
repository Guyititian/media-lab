from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI()

# =====================================================
# 🔥 CORS CONFIG (CRITICAL FOR GITHUB PAGES FRONTEND)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://guyititian.github.io",
        "http://localhost:3000",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROUTES
# =====================================================
app.include_router(router)


@app.get("/")
def root():
    return {
        "status": "media-lab online",
        "message": "API running"
    }
