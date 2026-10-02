import os
# Only default to SQLite if no external DATABASE_URL is provided.
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DEBUG"] = "false"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["GEMINI_API_KEY"] = ""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.main import app
import app.main as main_module
import app.services.audit as audit_module
from app.db.base import Base
from app.db.session import get_db
from app.db.migrations import upgrade_ownership
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole

import app.db.session as session_module

@pytest_asyncio.fixture(autouse=True)
async def database(tmp_path, monkeypatch):
    if "sqlite" in os.environ.get("DATABASE_URL", ""):
        engine = create_async_engine("sqlite+aiosqlite:///" + str(tmp_path / "test.db"))
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(upgrade_ownership)
        monkeypatch.setattr(session_module, "async_session_factory", sessions)
        monkeypatch.setattr(session_module, "engine", engine)
        monkeypatch.setattr(main_module, "async_session_factory", sessions)
        monkeypatch.setattr(audit_module, "async_session_factory", sessions)
        await main_module.seed_initial_data()
        async with sessions() as db:
            db.add_all([
                User(email="nurse@test.invalid", full_name="Test Nurse", role=UserRole.NURSE, hashed_password=get_password_hash("TestPassword123!")),
                User(email="second.doctor@test.invalid", full_name="Second Doctor", role=UserRole.DOCTOR, hashed_password=get_password_hash("TestPassword123!")),
            ])
            await db.commit()
        async def test_db():
            async with sessions() as db:
                yield db
        app.dependency_overrides[get_db] = test_db
        yield sessions
        app.dependency_overrides.clear()
        await engine.dispose()
    else:
        async with main_module.async_session_factory() as db:
            for email, role, name in [
                ("nurse@test.invalid", UserRole.NURSE, "Test Nurse"),
                ("second.doctor@test.invalid", UserRole.DOCTOR, "Second Doctor"),
            ]:
                res = await db.execute(select(User).where(User.email == email))
                if not res.scalar_one_or_none():
                    db.add(User(email=email, full_name=name, role=role, hashed_password=get_password_hash("TestPassword123!")))
            await db.commit()
        yield main_module.async_session_factory

@pytest_asyncio.fixture
async def async_client(database):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def doctor_auth_headers():
    return {"Authorization": "Bearer " + create_access_token(subject="doctor-test-id", role="doctor")}

@pytest.fixture
def patient_auth_headers():
    return {"Authorization": "Bearer " + create_access_token(subject="patient-test-id", role="patient")}