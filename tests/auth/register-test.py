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
    ## WBRR468GBW-eyJsaWNlbnNlSWQiOiJXQlJSNDY4R0JXIiwibGljZW5zZWVOYW1lIjoiSm9yZ2UgTHVpcyBPcnRpeiBHb21leiIsImxpY2Vuc2VlVHlwZSI6IlBFUlNPTkFMIiwiYXNzaWduZWVOYW1lIjoiIiwiYXNzaWduZWVFbWFpbCI6IiIsImxpY2Vuc2VSZXN0cmljdGlvbiI6IiIsImNoZWNrQ29uY3VycmVudFVzZSI6ZmFsc2UsInByb2R1Y3RzIjpbeyJjb2RlIjoiR08iLCJmYWxsYmFja0RhdGUiOiIyMDI1LTAyLTEwIiwicGFpZFVwVG8iOiIyMDI2LTAyLTA5IiwiZXh0ZW5kZWQiOmZhbHNlfSx7ImNvZGUiOiJSUzAiLCJmYWxsYmFja0RhdGUiOiIyMDI1LTAyLTEwIiwicGFpZFVwVG8iOiIyMDI2LTAyLTA5IiwiZXh0ZW5kZWQiOmZhbHNlfSx7ImNvZGUiOiJETSIsImZhbGxiYWNrRGF0ZSI6IjIwMjUtMDItMTAiLCJwYWlkVXBUbyI6IjIwMjYtMDItMDkiLCJleHRlbmRlZCI6ZmFsc2V9LHsiY29kZSI6IkNMIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiUlNVIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiUlNDIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJQQyIsImZhbGxiYWNrRGF0ZSI6IjIwMjUtMDItMTAiLCJwYWlkVXBUbyI6IjIwMjYtMDItMDkiLCJleHRlbmRlZCI6ZmFsc2V9LHsiY29kZSI6IkRTIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiUkQiLCJmYWxsYmFja0RhdGUiOiIyMDI1LTAyLTEwIiwicGFpZFVwVG8iOiIyMDI2LTAyLTA5IiwiZXh0ZW5kZWQiOmZhbHNlfSx7ImNvZGUiOiJRQSIsImZhbGxiYWNrRGF0ZSI6IjIwMjUtMDItMTAiLCJwYWlkVXBUbyI6IjIwMjYtMDItMDkiLCJleHRlbmRlZCI6ZmFsc2V9LHsiY29kZSI6IlJDIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiUlNGIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJSTSIsImZhbGxiYWNrRGF0ZSI6IjIwMjUtMDItMTAiLCJwYWlkVXBUbyI6IjIwMjYtMDItMDkiLCJleHRlbmRlZCI6ZmFsc2V9LHsiY29kZSI6IklJIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiRFBOIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiREIiLCJmYWxsYmFja0RhdGUiOiIyMDI1LTAyLTEwIiwicGFpZFVwVG8iOiIyMDI2LTAyLTA5IiwiZXh0ZW5kZWQiOmZhbHNlfSx7ImNvZGUiOiJEQyIsImZhbGxiYWNrRGF0ZSI6IjIwMjUtMDItMTAiLCJwYWlkVXBUbyI6IjIwMjYtMDItMDkiLCJleHRlbmRlZCI6ZmFsc2V9LHsiY29kZSI6IlBTIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiUlIiLCJmYWxsYmFja0RhdGUiOiIyMDI1LTAyLTEwIiwicGFpZFVwVG8iOiIyMDI2LTAyLTA5IiwiZXh0ZW5kZWQiOmZhbHNlfSx7ImNvZGUiOiJSU1YiLCJmYWxsYmFja0RhdGUiOiIyMDI1LTAyLTEwIiwicGFpZFVwVG8iOiIyMDI2LTAyLTA5IiwiZXh0ZW5kZWQiOnRydWV9LHsiY29kZSI6IldTIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjpmYWxzZX0seyJjb2RlIjoiUFNJIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJQQ1dNUCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJBSUwiLCJwYWlkVXBUbyI6IjIwMjYtMDItMDkiLCJleHRlbmRlZCI6ZmFsc2V9LHsiY29kZSI6IlJTIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJEUCIsImZhbGxiYWNrRGF0ZSI6IjIwMjUtMDItMTAiLCJwYWlkVXBUbyI6IjIwMjYtMDItMDkiLCJleHRlbmRlZCI6dHJ1ZX0seyJjb2RlIjoiUERCIiwiZmFsbGJhY2tEYXRlIjoiMjAyNS0wMi0xMCIsInBhaWRVcFRvIjoiMjAyNi0wMi0wOSIsImV4dGVuZGVkIjp0cnVlfSx7ImNvZGUiOiJQUlIiLCJmYWxsYmFja0RhdGUiOiIyMDI1LTAyLTEwIiwicGFpZFVwVG8iOiIyMDI2LTAyLTA5IiwiZXh0ZW5kZWQiOnRydWV9XSwibWV0YWRhdGEiOiIwMjIwMjUwMjAzUFBBQTAxMDAwOUEiLCJoYXNoIjoiNjYwNDc5NTEvMDoxMzE3ODY5ODI3IiwiZ3JhY2VQZXJpb2REYXlzIjo3LCJhdXRvUHJvbG9uZ2F0ZWQiOnRydWUsImlzQXV0b1Byb2xvbmdhdGVkIjp0cnVlLCJ0cmlhbCI6ZmFsc2UsImFpQWxsb3dlZCI6dHJ1ZX0=-EfHMU45ZuEj679wSghbGUJL+/qK7UFvh248OF4JB438HajcF+x/I1n6V8SGIfiLbI+WFlY70CjFk1xU8hfeedRYWDyfFpEMnKPmZvHR1Z4F7FMR8IQLfKldYdGztEj9VP35B1NfT7dDoMtxXPo3OQZ/9E9s5zrQBevQ4xupedHlhO4CFn/0JWZ2rNkbTeDNRaRKrZv+z98FomXLp0quL+fPFnd/640GPGrdN1Ed57dhZWOifKAKp2eB+cgdt9V07AcQdndtXudtXX8oIxqi6PV6NpmVQjiEAGbuYkygcooJmdo9i/JMI6dFsSwjMYKaS00+Mvvvekzv4EXM1jMF+yw==-MIIETDCCAjSgAwIBAgIBETANBgkqhkiG9w0BAQsFADAYMRYwFAYDVQQDDA1KZXRQcm9maWxlIENBMB4XDTI0MDkyMDEyMTEyN1oXDTI2MDkyMjEyMTEyN1owHzEdMBsGA1UEAwwUcHJvZDJ5LWZyb20tMjAyNDA5MjAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7SH/XcUoMwkDi8JJPzXWWHWFdOZdrP2Dqkz2W8iUi650cwz2vdPEd0tMzosLAj7ifkFEHUyiuEcL//q9d9Op7ZsV23lpPXX8tFMLFwugoQ9D8jDLT/XP9pp/YukWkKF5jpNbaCvsVQkDdYkArBkYvhH3aN4v9BkEsXahfgLLOPe4IG2FDJNf9R4to9V1vt+m2UVJB0zV4a/sVMKUZLgqKmKKKOKoLrE3OjBlZlb+Q0z2N5dsW0hDEVRFGmBUAbHN/mp44MMMvEIFKfoLIGpgic92P2O6uFh75PI7mcultL6yuR48ajErx8CjjQEGOSnoq/8hD+yVE+6GW2gJa2CPvAgMBAAGjgZkwgZYwCQYDVR0TBAIwADAdBgNVHQ4EFgQUb5NERj05GyNerQ/Mjm9XH8HXtLIwSAYDVR0jBEEwP4AUo562SGdCEjZBvW3gubSgUouX8bOhHKQaMBgxFjAUBgNVBAMMDUpldFByb2ZpbGUgQ0GCCQDSbLGDsoN54TATBgNVHSUEDDAKBggrBgEFBQcDATALBgNVHQ8EBAMCBaAwDQYJKoZIhvcNAQELBQADggIBALq6VfVUjmPI3N/w0RYoPGFYUieCfRO0zVvD1VYHDWsN3F9buVsdudhxEsUb8t7qZPkDKTOB6DB+apgt2ZdKwok8S0pwifwLfjHAhO3b+LUQaz/VmKQW8gTOS5kTVcpM0BY7UPF8cRBqxMsdUfm5ejYk93lBRPBAqntznDY+DNc9aXOldFiACyutB1/AIh7ikUYPbpEIPZirPdAahroVvfp2tr4BHgCrk9z0dVi0tk8AHE5t7Vk4OOaQRJzy3lST4Vv6Mc0+0z8lNa+Sc3SVL8CrRtnTAs7YpD4fpI5AFDtchNrgFalX+BZ9GLu4FDsshVI4neqV5Jd5zwWPnwRuKLxsCO/PB6wiBKzdapQBG+P9z74dQ0junol+tqxd7vUV/MFsR3VwVMTndyapIS+fMoe+ZR5g+y44R8C7fXyVE/geg+JXQKvRwS0C5UpnS5FcGk+61b0e4U7pwO20RlwhEFHLSaP61p2TaVGo/TQtT/fWmrtV+HegAv9P3X3Se+xIVtJzQsk8QrB/w52IB3FKiAKl/KRn1egbMIs4uoNAkqNZ9Ih2P1NpiQnONFmkiAgeynJ+0FPykKdJQbV3Mx44jkaHIif4aFReTsYX1WUBNu/QerZRjn4FVSHRaZPSR5Oi82Wz0Nj7IY9ocTpLnXFrqkb

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
