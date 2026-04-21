from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Media Lab")

app.include_router(router)
