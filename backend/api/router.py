from fastapi import APIRouter

from api.routes import auth, exames, perfil

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(perfil.router, prefix="/perfil", tags=["Perfil"])
api_router.include_router(exames.router, tags=["Exames"])
