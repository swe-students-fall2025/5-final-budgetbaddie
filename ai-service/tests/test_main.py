# test

from fastapi.testclient import TestClient
from app.main import app
from app.schemas import AdviceResponse, BudgetSnapshot, BudgetItem, AdviceRequest

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "ai-service"


def test_advice_endpoint_uses_service(monkeypatch):
    """
    We don't want unit tests to call the real Gemini API, so we monkeypatch
    generate_advice to return a fake AdviceResponse and just verify that:
    - /advice accepts the expected JSON payload
    - the response schema matches what we expect
    """

    
    from app import service

    def fake_generate_advice(req: AdviceRequest) -> AdviceResponse:
        return AdviceResponse(
            recommendation="BUY",
            explanation="This is a fake explanation for testing.",
            top_categories=[],
            suggested_monthly_savings=100.0,
        )

    
    monkeypatch.setattr(service, "generate_advice", fake_generate_advice)

    payload = {
        "user_id": "user123",
        "question": "Can I buy a $200 coat this month?",
        "item_name": "Winter coat",
        "item_url": None,
        "snapshot": {
            "month": "2025-12",
            "income": 3000,
            "expenses": [
                {"category": "Rent", "amount": 1200, "is_recurring": True},
                {"category": "Food", "amount": 400, "is_recurring": True},
                {"category": "Shopping", "amount": 150, "is_recurring": False},
            ],
        },
    }

    resp = client.post("/advice", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["recommendation"] == "BUY"
    assert "explanation" in data
    assert data["suggested_monthly_savings"] == 100.0
