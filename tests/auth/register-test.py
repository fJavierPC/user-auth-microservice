import pytest
from fastapi.testclient import TestClient
from api.main import app
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from infrastructure.services.jwt_service import decode_token

client = TestClient(app)

@pytest.fixture
def mock_db():
    """
    Simula la base de datos con MagicMock para pruebas.
    """
    db = MagicMock(spec=Session)
    return db


def test_register_user(mock_db, monkeypatch):
    """
    Prueba para el registro de usuario.
    """
    def mock_add_user(self, user):
        return None

    monkeypatch.setattr("infrastructure.repositories.user_repository.UserRepository.add_user", mock_add_user)

    payload = {"username": "testuser", "password": "securepassword"}
    response = client.post("v1/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}


def test_login_success(mock_db, monkeypatch):
    """
    Prueba para login exitoso.
    """
    def mock_authenticate_user(usrname, password, repo):
        class MockUser:
            user_id = 1
            username = usrname

        return MockUser(), None

    def mock_create_access_token(data, expires_delta):
        return "mock_access_token"

    def mock_create_refresh_token(data):
        return "mock_refresh_token"

    def mock_log_user_login(user_id, ip_address, user_agent):
        return None

    monkeypatch.setattr("core.usecases.login.authenticate_user", mock_authenticate_user)
    monkeypatch.setattr("infrastructure.services.jwt_service.create_access_token", mock_create_access_token)
    monkeypatch.setattr("infrastructure.services.jwt_service.create_refresh_token", mock_create_refresh_token)
    monkeypatch.setattr("infrastructure.repositories.user_repository.UserRepository.log_user_login", mock_log_user_login)

    payload = {"username": "testuser", "password": "securepassword"}
    response = client.post("v1/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_refresh_token_success(mock_db, monkeypatch):
    """
    Prueba para la renovación exitosa del token de acceso.
    """
    def mock_decode_token(token):
        return {"sub": "testuser"}

    def mock_get_user_by_username(usrname):
        class MockUser:
            user_id = 1
            username = usrname

        return MockUser()

    def mock_create_access_token(data, expires_delta):
        return "mock_access_token"

    monkeypatch.setattr("infrastructure.services.jwt_service.decode_token", mock_decode_token)
    monkeypatch.setattr("infrastructure.repositories.user_repository.UserRepository.get_user_by_username", mock_get_user_by_username)
    monkeypatch.setattr("infrastructure.services.jwt_service.create_access_token", mock_create_access_token)

    token = "mock_refresh_token"
    response = client.post("v1/auth/refresh-token", json={"token": token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalid(mock_db, monkeypatch):
    """
    Prueba para un refresh token inválido.
    """
    def mock_decode_token(token):
        raise Exception("Invalid token")

    monkeypatch.setattr("infrastructure.services.jwt_service.decode_token", mock_decode_token)

    token = "invalid_refresh_token"
    response = client.post("v1/auth/refresh-token", json={"token": token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired refresh token"}


def test_revoke_token(mock_db, monkeypatch):
    """
    Prueba para revocar un token.
    """
    def mock_add_token_to_blacklist(token):
        return None

    monkeypatch.setattr("infrastructure.repositories.blacklist_repository.BlacklistRepository.add_token_to_blacklist", mock_add_token_to_blacklist)

    token = "mock_access_token"
    response = client.post("v1/auth/revoke-token", json={"token": token})
    assert response.status_code == 200
    assert response.json() == {"message": "Token has been revoked"}
