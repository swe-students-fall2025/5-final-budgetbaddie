from fastapi import FastAPI

app = FastAPI(title="Budget Baddie API")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api"}