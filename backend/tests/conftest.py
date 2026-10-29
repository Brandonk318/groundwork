import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def settings():
    return Settings(jwt_secret="t" * 40)


@pytest.fixture
def db():
    return AsyncMongoMockClient()["groundwork_test"]


@pytest.fixture
def client(settings, db):
    with TestClient(create_app(settings, db=db)) as c:
        yield c
