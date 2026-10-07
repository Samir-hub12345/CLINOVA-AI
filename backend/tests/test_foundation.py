"""CLINOVA AI — Clean Foundation Verification Tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_root_endpoint_and_safety_headers():
    """Verify root endpoint returns system identity and mandatory safety headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == settings.APP_NAME
        assert data["version"] == settings.APP_VERSION
        assert data["philosophy"] == "Continuous Care Intelligence"
        assert response.headers["X-Clinical-Safety"] == "Non-Diagnostic-Advisory-Only"
        assert response.headers["X-Human-In-The-Loop"] == "Required-Before-Action"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify system health endpoint returns healthy status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_status_and_safety():
    """Verify API v1 status reports clean foundation pillars and safety mandate."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_status = await client.get("/api/v1/status")
        assert res_status.status_code == 200
        status_data = res_status.json()
        assert "caregraph" in status_data["pillars"]
        assert "facilitygraph" in status_data["pillars"]
        assert "signalgraph" in status_data["pillars"]
        assert "orchestration_engine" in status_data["pillars"]

        res_safety = await client.get("/api/v1/safety")
        assert res_safety.status_code == 200
        safety_data = res_safety.json()
        assert safety_data["non_diagnostic_mandate"] is True
        assert safety_data["human_in_the_loop_required"] is True
        assert safety_data["autonomous_action_allowed"] is False
