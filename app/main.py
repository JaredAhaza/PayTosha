from fastapi import FastAPI
from app.routes import pricing, users

app = FastAPI(title="PayTosha API")

app.include_router(pricing.router)
app.include_router(users.router)