from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from api.routes import router

app = FastAPI()

# -------------------------
# API ROUTES
# -------------------------
app.include_router(router)

# -------------------------
# OUTPUT FILE STORAGE
# -------------------------
os.makedirs("outputs", exist_ok=True)

app.mount(
    "/outputs",
    StaticFiles(directory="outputs"),
    name="outputs"
)
