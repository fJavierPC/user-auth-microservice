from fastapi import APIRouter, Depends, Request, HTTPException, status
from api.schemas.user import UserPayloadParams
from api.schemas.login_history import LoginHistoryResponse

from core.usecases.register_user import register_user
from core.usecases.login import authenticate_user
from infrastructure.repositories.blacklist_repository import BlacklistRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.jwt_service import create_access_token, decode_token, get_current_user, \
    create_refresh_token
from infrastructure.config.db_config import get_db
from sqlalchemy.orm import Session
from datetime import timedelta

router = APIRouter()


@router.post("/register")
def register(user: UserPayloadParams, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    new_user = register_user(user_id=None, username=user.username, password=user.password)
    repo.add_user(new_user)
    return {"message": "User registered successfully"}


@router.post("/login")
def login(request: Request, user: UserPayloadParams, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    auth_user, error_message = authenticate_user(user.username, user.password, repo)
    if auth_user:
        access_token = create_access_token(data={"sub": auth_user.username}, expires_delta=timedelta(minutes=30))
        r_token = create_refresh_token(data={"sub": auth_user.username})

        # Registrar el inicio de sesión
        repo.log_user_login(
            user_id=auth_user.user_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent")
        )

        return {"access_token": access_token, "token_type": "bearer", "refresh_token": r_token}
    return {"error": error_message}


@router.post("/refresh-token")
def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Renueva el token de acceso basado en un refresh token válido.
    """
    try:
        payload = decode_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Validar que el usuario existe y está activo
    username = payload.get("sub")
    repo = UserRepository(db)
    user = repo.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Crear un nuevo token de acceso
    access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/revoke-token")
def revoke_token(token: str, db: Session = Depends(get_db)):
    """
    Revoca un token específico añadiéndolo al blacklist.
    """
    repo = BlacklistRepository(db)
    repo.add_token_to_blacklist(token)
    return {"message": "Token has been revoked"}
