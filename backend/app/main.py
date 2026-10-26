from fastapi import FastAPI

from app.api import health, uploads

app = FastAPI(title="Spendsense AI", version="0.1.0")
app.include_router(health.router)
app.include_router(uploads.router)
