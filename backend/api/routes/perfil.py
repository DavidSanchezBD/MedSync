from fastapi import APIRouter, Depends

from api.deps import obter_usuario_id
from models.schemas import PerfilRequest
from services.perfil import buscar_perfil, salvar_perfil

router = APIRouter()


@router.get("")
def obter_perfil(usuario_id: str = Depends(obter_usuario_id)):
    perfil = buscar_perfil(usuario_id)
    if not perfil:
        return {"status": "ok", "perfil": None}
    return {"status": "ok", "perfil": perfil}


@router.post("")
def criar_ou_atualizar_perfil(
    dados: PerfilRequest,
    usuario_id: str = Depends(obter_usuario_id),
):
    perfil = salvar_perfil(usuario_id, dados)
    return {"status": "sucesso", "perfil": perfil}
