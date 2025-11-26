from fastapi import FastAPI

app = FastAPI(title="Budget Baddie AI Service")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-service"}