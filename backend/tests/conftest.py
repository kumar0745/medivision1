import os
import tempfile
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-thirty-two-characters-long")
os.environ.setdefault("STORAGE_BACKEND", "local")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.core.database import Base, get_db
from app.core import file_storage
from app.core.config import settings
from app.models.user import User

@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(settings, "frontend_origins", "http://testserver")
    monkeypatch.setattr(settings, "malware_scanner_url", "")
    monkeypatch.setattr(settings, "malware_scanner_token", "")
    app.dependency_overrides[get_db] = override_get_db
    with tempfile.TemporaryDirectory() as directory:
        monkeypatch.setattr(file_storage.settings, "upload_dir", directory)
        with TestClient(app) as test_client:
            yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
