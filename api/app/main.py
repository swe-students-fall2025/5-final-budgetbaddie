from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from .ai_routes import router as ai_router

app = FastAPI(title="Budget Baddie API")
app.include_router(ai_router)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api"}



