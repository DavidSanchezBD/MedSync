import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from jose import JWTError, jwt

from database.db import obter_conexao

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "medsync-secret-mvp-2024")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24 * 7  # 7 dias


def _hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def _verificar_senha(senha: str, hash_armazenado: str) -> bool:
    return bcrypt.checkpw(senha.encode(), hash_armazenado.encode())


def _criar_token(payload: dict) -> str:
    dados = payload.copy()
    dados["exp"] = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)


def _decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Token inválido ou expirado.")


def registrar_usuario(nome: str, email: str, senha: str) -> dict:
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cur.fetchone():
                raise ValueError("E-mail já cadastrado.")

            user_id = str(uuid.uuid4())
            senha_hash = _hash_senha(senha)
            cur.execute(
                "INSERT INTO usuarios (id, nome, email, senha_hash) VALUES (%s, %s, %s, %s)",
                (user_id, nome, email, senha_hash),
            )

    token = _criar_token({"sub": user_id, "email": email})
    return {
        "token": token,
        "usuario": {"id": user_id, "nome": nome, "email": email},
        "tem_perfil": False,
    }


def fazer_login(email: str, senha: str) -> dict:
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = %s",
                (email,),
            )
            usuario = cur.fetchone()
            if not usuario or not _verificar_senha(senha, usuario["senha_hash"]):
                raise ValueError("E-mail ou senha inválidos.")

            cur.execute(
                "SELECT id FROM perfis_saude WHERE usuario_id = %s", (str(usuario["id"]),)
            )
            tem_perfil = cur.fetchone() is not None

    token = _criar_token({"sub": str(usuario["id"]), "email": email})
    return {
        "token": token,
        "usuario": {
            "id": str(usuario["id"]),
            "nome": usuario["nome"],
            "email": usuario["email"],
        },
        "tem_perfil": tem_perfil,
    }


def obter_usuario_atual(token: str) -> dict:
    payload = _decodificar_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token inválido.")

    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email FROM usuarios WHERE id = %s", (user_id,)
            )
            usuario = cur.fetchone()
            if not usuario:
                raise ValueError("Usuário não encontrado.")

            cur.execute(
                """
                SELECT idade, genero_biologico, peso_kg, altura_cm,
                       condicoes_previas, historico_familiar
                FROM perfis_saude WHERE usuario_id = %s
                """,
                (user_id,),
            )
            perfil = cur.fetchone()

    return {
        "usuario": {
            "id": str(usuario["id"]),
            "nome": usuario["nome"],
            "email": usuario["email"],
        },
        "perfil": dict(perfil) if perfil else None,
        "tem_perfil": perfil is not None,
    }
