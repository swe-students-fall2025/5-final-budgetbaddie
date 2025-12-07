from fastapi import FastAPI
from .schemas import AdviceRequest, AdviceResponse
from .service import generate_advice

app = FastAPI(title="Budget Baddie AI Service")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-service"}


@app.post("/advice", response_model=AdviceResponse)
def get_advice(req: AdviceRequest):
    """
    Main AI endpoint: receives a budget snapshot + user question and
    returns structured budgeting advice.
    """
    return generate_advice(req)
