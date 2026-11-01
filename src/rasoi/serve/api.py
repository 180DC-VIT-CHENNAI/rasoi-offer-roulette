from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Rasoi offer API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/predict/{customer_id}")
def predict(customer_id: str):
    # ISSUE-05: load the persisted model and return an offer for this customer.
    return JSONResponse(
        status_code=501,
        content={"detail": "GET /predict is not implemented yet", "customer_id": customer_id},
    )
