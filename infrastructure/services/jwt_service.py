from typing import Dict
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from infrastructure.repositories.blacklist_repository import BlacklistRepository
from infrastructure.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from infrastructure.config.db_config import get_db

from dotenv import load_dotenv
import os
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: Dict, expires_delta: timedelta = None):
    """
        Genera un token de acceso con tiempo de expiración.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict, expires_delta: timedelta = timedelta(minutes=60)) -> str:
    """
    Genera un token de refresco con mayor tiempo de expiración.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def decode_token(token: str) -> Dict:
    """
    Decodifica un token JWT.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

def check_token_not_blacklisted(token: str, db: Session):
    """
        Comprueba si el token esta en lista negra
    """
    repo = BlacklistRepository(db)
    if repo.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Valida el token de acceso, verifica si expiró y extrae al usuario autenticado.
    Si el token expiró, lo revoca antes de lanzar un error.
    """
    check_token_not_blacklisted(token, db)  # Verificar si el token ya está en la blacklist.

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica el token (validando expiración)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError as e:
        # Validar si el error es por expiración
        if "Signature has expired" in str(e):
            # Si el token expiró, agregarlo a la lista negra
            blacklist_repo = BlacklistRepository(db)
            blacklist_repo.add_token_to_blacklist(token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired and has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            # Otros errores de token inválido
            raise credentials_exception

    # Si el token es válido, obtener el usuario
    repo = UserRepository(db)
    user = repo.get_user_by_username(username=username)
    if user is None:
        raise credentials_exception

    return {"user_id": user.user_id, "username": user.username, "is_admin": False}