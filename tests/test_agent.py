import pytest
from httpx import ASGITransport, AsyncClient
from src.agent.main import app

@pytest.mark.asyncio
async def test_readiness_probe():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ready"

@pytest.mark.asyncio
async def test_responses_endpoint_valid_turn():
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, agent!"}
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/responses", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "content" in data["response"]
    assert len(data["response"]["content"]) > 0

@pytest.mark.asyncio
async def test_responses_endpoint_empty_messages():
    payload = {"messages": []}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/responses", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
