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


@pytest.mark.asyncio
async def test_liveness_probes():
    """Verify that both root and API v1 liveness probes return 200 and alive status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for path in ["/health/live", "/api/v1/health/live"]:
            res = await client.get(path)
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "healthy"
            assert data["liveness"] == "alive"
            assert data["app"] == settings.APP_NAME


@pytest.mark.asyncio
async def test_readiness_probe_success():
    """Verify that readiness probes return 200 and connected status when DB is available."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for path in ["/health/ready", "/api/v1/health/ready"]:
            res = await client.get(path)
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ready"
            assert data["database"] == "connected"
            assert "password" not in str(data).lower()
            assert "sqlite" not in str(data).lower()


@pytest.mark.asyncio
async def test_readiness_probe_failure(monkeypatch):
    """Verify that readiness probes return 503 unready when DB connectivity fails, without disclosing secrets."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def broken_session():
        raise ConnectionError("Simulated database cluster unreachable")
        yield

    monkeypatch.setattr("app.db.session.async_session_factory", broken_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health/ready")
        assert res.status_code == 503
        data = res.json()
        assert data["status"] == "unready"
        assert data["database"] == "unavailable"
        assert "Simulated database cluster unreachable" not in str(data)
        assert "traceback" not in str(data).lower()


def test_production_config_validation():
    """Verify that production mode enforces strict security invariants."""
    from app.core.config import Settings
    from pydantic import ValidationError

    # In production, default dev key must be rejected
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="clinova-native-dev-secret-key-32chars-minimum-2026!",
        )

    # In production, key shorter than 32 chars must be rejected
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short-secret",
        )

    # In production with valid key, dev debug & auth bypass flags are forced off
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="high-entropy-production-secret-key-32chars!",
        DEBUG=True,
        ALLOW_LEGACY_ACTOR_HEADERS=True,
        ALLOW_LEGACY_ANONYMOUS_FALLBACK=True,
    )
    assert prod_settings.DEBUG is False
    assert prod_settings.ALLOW_LEGACY_ACTOR_HEADERS is False
    assert prod_settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK is False
    assert prod_settings.BACKEND_HOST == "0.0.0.0"


def test_database_url_dialect_adaptation():
    """Verify that PostgreSQL URLs are normalized for SQLAlchemy asyncpg engine."""
    from app.core.config import Settings

    s1 = Settings(DATABASE_URL="postgres://user:pass@host:5432/db")
    assert s1.DATABASE_URL.startswith("postgresql+asyncpg://")

    s2 = Settings(DATABASE_URL="postgresql://user:pass@host:5432/db")
    assert s2.DATABASE_URL.startswith("postgresql+asyncpg://")


@pytest.mark.asyncio
async def test_alembic_schema_version_at_head():
    """Verify that database initialization stamps alembic_version at current head."""
    from sqlalchemy import text
    from app.db.session import async_session_factory

    async with async_session_factory() as session:
        res = await session.execute(text("SELECT version_num FROM alembic_version"))
        version = res.scalar()
        assert version == "b84f3782910c"

