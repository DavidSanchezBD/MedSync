from fastapi import APIRouter, Depends, HTTPException

from api.deps import obter_usuario_id
from database.db import obter_conexao
from models.schemas import LoginRequest, RegistroRequest
from services.auth import criar_token, hash_senha, verificar_senha
from services.perfil import buscar_perfil

router = APIRouter()


@router.post("/registro")
def registrar(dados: RegistroRequest):
    senha_hash = hash_senha(dados.senha)
    try:
        with obter_conexao() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO usuarios (nome, email, senha_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, nome, email
                    """,
                    (dados.nome, dados.email, senha_hash),
                )
                usuario = cur.fetchone()
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="E-mail já cadastrado.") from e
        raise HTTPException(status_code=500, detail="Erro ao criar conta.") from e

    uid = str(usuario["id"])
    token = criar_token(uid, usuario["email"])
    return {
        "status": "sucesso",
        "token": token,
        "usuario": {"id": uid, "nome": usuario["nome"], "email": usuario["email"]},
        "tem_perfil": False,
    }


@router.post("/login")
def login(dados: LoginRequest):
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = %s",
                (dados.email,),
            )
            usuario = cur.fetchone()

    if not usuario or not verificar_senha(dados.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    uid = str(usuario["id"])
    perfil = buscar_perfil(uid)
    token = criar_token(uid, usuario["email"])
    return {
        "status": "sucesso",
        "token": token,
        "usuario": {"id": uid, "nome": usuario["nome"], "email": usuario["email"]},
        "tem_perfil": perfil is not None,
    }


@router.get("/me")
def me(usuario_id: str = Depends(obter_usuario_id)):
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email FROM usuarios WHERE id = %s",
                (usuario_id,),
            )
            usuario = cur.fetchone()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    perfil = buscar_perfil(usuario_id)
    return {
        "usuario": {
            "id": str(usuario["id"]),
            "nome": usuario["nome"],
            "email": usuario["email"],
        },
        "tem_perfil": perfil is not None,
        "perfil": perfil,
    }
