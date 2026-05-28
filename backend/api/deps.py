from fastapi import Header, HTTPException

from services.auth import decodificar_token


def obter_usuario_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticação ausente.")
    token = authorization.split(" ", 1)[1]
    payload = decodificar_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
    return payload["sub"]
