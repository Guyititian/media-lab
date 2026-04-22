from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Media-Lab",
    description="Media processing toolkit (GIF Motion Engine + future tools)",
    version="1.0.0"
)

# Register API routes
app.include_router(router)


# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "media-lab",
        "message": "GIF Motion Engine running"
    }


# ----------------------------
# SIMPLE DEBUG ENDPOINT
# ----------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
