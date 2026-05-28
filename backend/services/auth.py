import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "medsync-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "72"))


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            senha_plana.encode("utf-8"),
            senha_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def criar_token(usuario_id: str, email: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": usuario_id,
        "email": email,
        "exp": int(expira.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
