import os
import shutil
import tempfile
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.deps import obter_usuario_id
from core.extractor import extrair_dados_exame
from core.rag_engine import classificar_metricas, gerar_traducao_amigavel
from database.db import obter_conexao
from services.perfil import buscar_perfil

router = APIRouter()


@router.post("/upload")
async def processar_exame(
    arquivo: UploadFile = File(...),
    usuario_id: str = Depends(obter_usuario_id),
):
    if not arquivo.filename or not arquivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie apenas arquivos PDF.")

    perfil = buscar_perfil(usuario_id)
    if not perfil:
        raise HTTPException(
            status_code=400,
            detail="Complete seu perfil de saúde antes de enviar exames.",
        )

    ref_arquivo = f"exames/{uuid.uuid4().hex}/{arquivo.filename}"
    caminho_temp = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(arquivo.file, tmp)
            caminho_temp = tmp.name

        json_estruturado = extrair_dados_exame(caminho_temp)
        metricas_classificadas = classificar_metricas(json_estruturado)
        texto_amigavel = gerar_traducao_amigavel(
            json_estruturado,
            perfil,
            metricas_classificadas=metricas_classificadas,
        )

        with obter_conexao() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO exames_metadados (usuario_id, caminho_arquivo, status_processamento)
                    VALUES (%s, %s, %s)
                    """,
                    (usuario_id, ref_arquivo, "Processado"),
                )

        return {
            "status": "sucesso",
            "arquivo_processado": arquivo.filename,
            "dados_extraidos": json_estruturado,
            "metricas_classificadas": metricas_classificadas,
            "traducao_leiga": texto_amigavel,
        }
    except HTTPException:
        raise
    except Exception as erro:
        with obter_conexao() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO exames_metadados (usuario_id, caminho_arquivo, status_processamento)
                    VALUES (%s, %s, %s)
                    """,
                    (usuario_id, ref_arquivo, "Falhou"),
                )
        raise HTTPException(status_code=500, detail=str(erro)) from erro
    finally:
        if caminho_temp and os.path.exists(caminho_temp):
            try:
                os.remove(caminho_temp)
            except OSError:
                pass
