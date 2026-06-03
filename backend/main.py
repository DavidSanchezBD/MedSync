import os
import tempfile

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.extractor import extrair_dados_exame
from core.rag_engine import classificar_metricas, gerar_traducao_amigavel
from services.auth import fazer_login, obter_usuario_atual, registrar_usuario
from services.perfil import salvar_perfil

app = FastAPI(title="MedSync API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helpers ────────────────────────────────────────────────────────────────

def _extrair_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticação ausente.")
    return authorization.split(" ", 1)[1]


def _usuario_da_requisicao(authorization: str | None) -> dict:
    token = _extrair_token(authorization)
    try:
        return obter_usuario_atual(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


# ─── Health ──────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    return {"status": "ok", "mensagem": "MedSync API online"}


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegistroPayload(BaseModel):
    nome: str
    email: str
    senha: str


class LoginPayload(BaseModel):
    email: str
    senha: str


@app.post("/api/auth/registro")
def registro(payload: RegistroPayload):
    try:
        return registrar_usuario(payload.nome, payload.email, payload.senha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
def login(payload: LoginPayload):
    try:
        return fazer_login(payload.email, payload.senha)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/auth/me")
def me(authorization: str | None = Header(default=None)):
    return _usuario_da_requisicao(authorization)


# ─── Perfil ──────────────────────────────────────────────────────────────────

class PerfilPayload(BaseModel):
    idade: int | None = None
    genero_biologico: str | None = None
    peso_kg: float | None = None
    altura_cm: float | None = None
    condicoes_previas: str | None = None
    historico_familiar: str | None = None


@app.post("/api/perfil")
def criar_perfil(
    payload: PerfilPayload,
    authorization: str | None = Header(default=None),
):
    dados_usuario = _usuario_da_requisicao(authorization)
    usuario_id = dados_usuario["usuario"]["id"]
    return salvar_perfil(usuario_id, payload.model_dump())


# ─── Upload / Análise ─────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_exame(
    arquivo: UploadFile = File(...),
    authorization: str | None = Header(default=None),
):
    dados_usuario = _usuario_da_requisicao(authorization)
    perfil = dados_usuario.get("perfil")  # pode ser None se não preencheu

    # Salva o PDF em arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await arquivo.read())
        caminho_tmp = tmp.name

    try:
        # 1. Extrai métricas do PDF via OpenAI
        metricas_json = extrair_dados_exame(caminho_tmp)

        # 2. Classifica cada métrica (normal / atenção / indefinido)
        metricas_classificadas = classificar_metricas(metricas_json)

        # 3. Gera a explicação amigável via RAG + OpenAI
        traducao = gerar_traducao_amigavel(
            metricas_json,
            perfil=perfil,
            metricas_classificadas=metricas_classificadas,
        )

        return {
            "dados_extraidos": {
                "nome_paciente": metricas_json.get("nome_paciente"),
                "data_exame": metricas_json.get("data_exame"),
                "metricas": metricas_json.get("metricas", []),
            },
            "metricas_classificadas": metricas_classificadas,
            "traducao_leiga": traducao,
        }
    finally:
        os.unlink(caminho_tmp)
