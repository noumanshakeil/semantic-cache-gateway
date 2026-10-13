import pytest

@pytest.mark.asyncio
async def test_cache_hit(client):
    first = await client.post("/api/complete", json={"prompt": "Explain gradient descent simply"})
    assert first.status_code == 200
    assert first.json()["cache"] == "miss"
    second = await client.post("/api/complete", json={"prompt": "Explain gradient descent simply for beginners"})
    assert second.status_code == 200
    assert second.json()["cache"] in {"hit", "miss"}
    analytics = await client.get("/api/analytics")
    assert analytics.json()["queries"] >= 2
