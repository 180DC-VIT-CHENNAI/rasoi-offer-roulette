"""ISSUE-05: /predict is a 501 shell and this test fails initially."""

from fastapi.testclient import TestClient

from rasoi.serve.api import app


def test_health():
    client = TestClient(app)
    assert client.get("/health").status_code == 200


def test_predict_returns_offer():
    client = TestClient(app)
    response = client.get("/predict/CU-000001")
    assert response.status_code == 200
    assert response.json()["offer"] in {"NONE", "OFFER_10", "OFFER_20"}
