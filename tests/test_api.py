import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app

os.environ["TESTING"] = "True"


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def test_db():
    TEST_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


def test_deposit(test_client, test_db):
    response = test_client.post("/api/v1/wallets/test_wallet/operation", json={
        "operation_type": "DEPOSIT",
        "amount": 1000
    })
    assert response.status_code == 200
    assert response.json() == {"message": "DEPOSIT successful"}


def test_withdraw(test_client, test_db):
    # Сначала депонируем средства
    test_client.post("/api/v1/wallets/test_wallet/operation", json={
        "operation_type": "DEPOSIT",
        "amount": 1500
    })
    # Теперь пытаемся снять деньги
    response = test_client.post("/api/v1/wallets/test_wallet/operation", json={
        "operation_type": "WITHDRAW",
        "amount": 500
    })
    assert response.status_code == 200
    assert response.json() == {"message": "WITHDRAW successful"}


def test_insufficient_funds(test_client, test_db):
    # Сначала депонируем средства
    test_client.post("/api/v1/wallets/test_wallet/operation", json={
        "operation_type": "DEPOSIT",
        "amount": 1000
    })
    # Теперь пытаемся снять больше денег, чем есть
    response = test_client.post("/api/v1/wallets/test_wallet/operation", json={
        "operation_type": "WITHDRAW",
        "amount": 1500
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Insufficient funds"}


def test_get_balance(test_client, test_db):
    # Сначала депонируем средства
    test_client.post("/api/v1/wallets/test_wallet/operation", json={
        "operation_type": "DEPOSIT",
        "amount": 1000
    })
    # Проверяем баланс
    response = test_client.get("/api/v1/wallets/test_wallet")
    assert response.status_code == 200
    assert response.json() == {"balance": 1000}
