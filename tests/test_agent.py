from fastapi.testclient import TestClient
from entmulti.main import app

client = TestClient(app)


def test_runs_and_refuses_a_write():
    payload = client.post("/agent/run", json={"goal": 'draft a change', **{'payload': {}}}).json()
    assert payload["refused"] is False
    assert payload["applied"] is False
    assert "critic" in payload["roles"]
    refused = client.post("/agent/run", json={"goal": 'page prod'}).json()
    assert refused["refused"] is True
