import os
import re
import json
import unicodedata
import chromadb
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
cliente_ia = OpenAI()

cliente_vetorial = chromadb.Client()
colecao_medica = cliente_vetorial.get_or_create_collection(name="referencias_medicas")

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_base = os.path.join(diretorio_atual, "..", "data", "base_conhecimento_medica.txt")

textos_referencia: list[str] = []
_indice_marcadores: dict[str, str] = {}


def _normalizar(texto: str) -> str:
    if not texto:
        return ""
    t = unicodedata.normalize("NFKD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def _extrair_nome_da_linha(linha: str) -> str:
    match = re.match(r"Marcador:\s*(.+?)\.\s*Valores", linha, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _construir_indice() -> None:
    global _indice_marcadores
    _indice_marcadores = {}
    for linha in textos_referencia:
        nome = _extrair_nome_da_linha(linha)
        if nome:
            _indice_marcadores[_normalizar(nome)] = linha


def _score_match(nome_norm: str, chave: str) -> float:
    """Pontuação 0–1; exige correspondência forte para evitar falso positivo."""
    if not nome_norm or not chave:
        return 0.0
    if nome_norm == chave:
        return 1.0

    if len(chave) >= 4 and len(nome_norm) >= 4:
        if chave in nome_norm:
            return len(chave) / len(nome_norm)
        if nome_norm in chave:
            return len(nome_norm) / len(chave)

    tokens_m = nome_norm.split()
    tokens_c = chave.split()
    if not tokens_m or not tokens_c:
        return 0.0

    # Todos os tokens do nome mais curto devem aparecer no mais longo
    curto, longo = (
        (tokens_m, tokens_c) if len(tokens_m) <= len(tokens_c) else (tokens_c, tokens_m)
    )
    if all(t in longo for t in curto):
        return len(curto) / len(longo)

    return 0.0


def _buscar_linha_referencia(nome_marcador: str, score_minimo: float = 0.78) -> str | None:
    if not nome_marcador or not textos_referencia:
        return None

    nome_norm = _normalizar(nome_marcador)
    if not nome_norm:
        return None

    if nome_norm in _indice_marcadores:
        return _indice_marcadores[nome_norm]

    melhor_linha = None
    melhor_score = 0.0

    for chave, linha in _indice_marcadores.items():
        score = _score_match(nome_norm, chave)
        if score > melhor_score:
            melhor_score = score
            melhor_linha = linha

    return melhor_linha if melhor_score >= score_minimo else None


def _parse_valor_numerico(valor) -> float | None:
    if valor is None:
        return None
    texto = str(valor).strip().replace(",", ".")
    match = re.search(r"(\d+(?:\.\d+)?)", texto)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _classificar_por_faixa(valor: float, linha_ref: str) -> str | None:
    """Retorna 'normal', 'atencao' ou None se a faixa for ambígua."""
    parte = linha_ref.split("(SI)")[0] if "(SI)" in linha_ref else linha_ref

    faixa = re.search(
        r"([\d]+(?:[,.]\d+)?)\s*a\s*([\d]+(?:[,.]\d+)?)",
        parte,
        re.IGNORECASE,
    )
    if faixa:
        minimo = float(faixa.group(1).replace(",", "."))
        maximo = float(faixa.group(2).replace(",", "."))
        if minimo <= valor <= maximo:
            return "normal"
        return "atencao"

    menor_que = re.search(r"<\s*([\d]+(?:[,.]\d+)?)", parte)
    if menor_que:
        limite = float(menor_que.group(1).replace(",", "."))
        return "normal" if valor < limite else "atencao"

    maior_que = re.search(r">\s*([\d]+(?:[,.]\d+)?)", parte)
    if maior_que:
        limite = float(maior_que.group(1).replace(",", "."))
        return "normal" if valor > limite else "atencao"

    return None


try:
    with open(caminho_base, "r", encoding="utf-8") as arquivo:
        textos_referencia = [linha.strip() for linha in arquivo.read().splitlines() if linha.strip()]

    _construir_indice()

    if colecao_medica.count() > 0:
        ids_existentes = colecao_medica.get()["ids"]
        colecao_medica.delete(ids=ids_existentes)

    colecao_medica.add(
        documents=textos_referencia,
        ids=[f"ref_{i}" for i in range(len(textos_referencia))],
    )
    print(f"[MedSync] Base de conhecimento carregada: {len(textos_referencia)} marcadores.")
except FileNotFoundError:
    print(f"[MedSync] ERRO: Arquivo nao encontrado em {caminho_base}.")


def _buscar_contexto(lista_marcadores: list[str]) -> str:
    if not lista_marcadores:
        return ""

    linhas: list[str] = []
    vistos: set[str] = set()

    for marcador in lista_marcadores:
        if not marcador:
            continue
        direta = _buscar_linha_referencia(marcador)
        if direta and direta not in vistos:
            linhas.append(direta)
            vistos.add(direta)

    if linhas:
        return "\n".join(linhas)

    if not textos_referencia:
        return ""

    pergunta_busca = f"Referências para: {', '.join(lista_marcadores)}"
    quantidade = max(1, min(len(lista_marcadores) * 2, len(textos_referencia)))
    resultados = colecao_medica.query(query_texts=[pergunta_busca], n_results=quantidade)
    docs = resultados.get("documents", [[]])
    return "\n".join(docs[0]) if docs and docs[0] else ""


def _formatar_perfil(perfil: dict | None) -> str:
    if not perfil:
        return "Perfil de saúde não informado."
    imc = None
    if perfil.get("peso_kg") and perfil.get("altura_cm"):
        altura_m = float(perfil["altura_cm"]) / 100
        imc = round(float(perfil["peso_kg"]) / (altura_m**2), 1)
    partes = [
        f"Idade: {perfil.get('idade')} anos",
        f"Gênero biológico: {perfil.get('genero_biologico')}",
        f"Peso: {perfil.get('peso_kg')} kg",
        f"Altura: {perfil.get('altura_cm')} cm",
    ]
    if imc:
        partes.append(f"IMC estimado: {imc}")
    if perfil.get("condicoes_previas"):
        partes.append(f"Condições pré-existentes: {perfil['condicoes_previas']}")
    if perfil.get("historico_familiar"):
        partes.append(f"Histórico familiar: {perfil['historico_familiar']}")
    return "\n".join(partes)


def classificar_metricas(metricas_json: dict) -> list[dict]:
    metricas = metricas_json.get("metricas") or []
    if not metricas:
        return []

    # --- CAMADA DE DADOS (PANDAS): Tratamento e Limpeza de Dados ---
    # Convertemos os marcadores extraídos para um DataFrame para realizar a limpeza necessária
    df = pd.DataFrame(metricas)
    
    # 1. Tratar nulos: remover registros que não possuem o nome do marcador
    if "marcador" in df.columns:
        df = df.dropna(subset=["marcador"])
        # Corrigir tipagem e padronizar (converter para string e remover espaços adicionais)
        df["marcador"] = df["marcador"].astype(str).str.strip()
    else:
        df["marcador"] = []

    # 2. Tratar nulos/vazios na coluna de 'valor'
    if "valor" in df.columns:
        df["valor"] = df["valor"].fillna("")
        df["valor"] = df["valor"].astype(str).str.strip()
    else:
        df["valor"] = ""

    # 3. Remover duplicatas: se a IA extrair o mesmo marcador mais de uma vez no mesmo exame, mantemos o primeiro
    df = df.drop_duplicates(subset=["marcador"], keep="first")

    # Reconverte para lista de dicionários para compatibilidade com o pipeline FastAPI
    metricas = df.to_dict(orient="records")
    # ---------------------------------------------------------------

    resultado: list[dict | None] = [None] * len(metricas)

    # Só envia à IA marcadores com referência confirmada na base (faixa ambígua).
    pendentes_llm: list[tuple[int, dict, str]] = []

    for i, item in enumerate(metricas):
        marcador = item.get("marcador", "")
        valor = item.get("valor")
        linha_ref = _buscar_linha_referencia(marcador)

        if not linha_ref:
            resultado[i] = {
                "marcador": marcador,
                "valor": valor,
                "status": "indefinido",
            }
            continue

        valor_num = _parse_valor_numerico(valor)
        if valor_num is not None:
            status_regra = _classificar_por_faixa(valor_num, linha_ref)
            if status_regra:
                resultado[i] = {
                    "marcador": marcador,
                    "valor": valor,
                    "status": status_regra,
                }
                continue

        pendentes_llm.append((i, item, linha_ref))

    if pendentes_llm:
        blocos_contexto = []
        metricas_llm = []
        for _, item, linha in pendentes_llm:
            metricas_llm.append(item)
            nome = item.get("marcador", "")
            blocos_contexto.append(f"[{nome}]\n{linha}")

        contexto = "\n\n".join(blocos_contexto)
        prompt = f"""
        Classifique marcadores de exames usando SOMENTE a referência fornecida para cada um.
        Retorne JSON com lista "classificacoes", cada item com:
        "marcador", "valor" (original), "status" ("normal" ou "atencao").

        Regras obrigatórias:
        - Use "normal" se o valor estiver dentro da faixa da referência.
        - Use "atencao" se estiver fora da faixa.
        - NÃO invente faixas. NÃO use conhecimento externo.
        - NÃO retorne "indefinido" (a referência já foi validada).

        CONTEXTO:
        {contexto}

        MÉTRICAS:
        {json.dumps(metricas_llm, ensure_ascii=False)}
        """

        resposta = cliente_ia.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=0,
            messages=[
                {"role": "system", "content": "Retorne apenas JSON válido."},
                {"role": "user", "content": prompt},
            ],
        )
        dados = json.loads(resposta.choices[0].message.content)
        classificacoes = dados.get("classificacoes", dados.get("metricas", []))

        for j, (idx, item, linha_ref) in enumerate(pendentes_llm):
            base = classificacoes[j] if j < len(classificacoes) else {}
            status = base.get("status", "indefinido")

            if status not in ("normal", "atencao"):
                valor_num = _parse_valor_numerico(item.get("valor"))
                status = (
                    _classificar_por_faixa(valor_num, linha_ref) if valor_num is not None else None
                ) or "indefinido"

            resultado[idx] = {
                "marcador": item.get("marcador"),
                "valor": item.get("valor"),
                "status": status,
            }

    return [
        r
        if r is not None
        else {
            "marcador": metricas[i].get("marcador"),
            "valor": metricas[i].get("valor"),
            "status": "indefinido",
        }
        for i, r in enumerate(resultado)
    ]


def gerar_traducao_amigavel(
    metricas_json: dict,
    perfil: dict | None = None,
    metricas_classificadas: list[dict] | None = None,
) -> str:
    if not metricas_json.get("metricas"):
        return "Não consegui identificar métricas claras no exame."

    metricas_entrada = metricas_json.get("metricas") or []

    if metricas_classificadas:
        em_atencao = [m for m in metricas_classificadas if m.get("status") == "atencao"]
        if not em_atencao:
            return (
                "Boa notícia: pelos marcadores identificados, não encontrei nenhum valor claramente fora "
                "da faixa de referência disponível. Se quiser, posso explicar o que cada marcador mede, "
                "mas para manter simples eu foquei apenas no que exigiria atenção."
                "\n\nAviso: esta análise é informativa e não substitui consulta médica."
            )
        metricas_entrada = [{"marcador": m.get("marcador"), "valor": m.get("valor")} for m in em_atencao]

    lista_marcadores = [item["marcador"] for item in metricas_entrada if item.get("marcador")]
    contexto_unido = _buscar_contexto(lista_marcadores)
    perfil_texto = _formatar_perfil(perfil)

    prompt_sistema = f"""
    Você é o assistente virtual do MedSync.
    Explique de forma amigável, leiga e reconfortante, focando em clareza e objetividade.
    Personalize levemente considerando o PERFIL DO PACIENTE (sem diagnosticar doenças).
    Use APENAS o CONTEXTO médico para faixas de referência. Não invente valores.

    FORMATAÇÃO (obrigatório):
    - Não use Markdown (nada de **, listas numeradas, headings ou bullets com asterisco).
    - Escreva em texto simples, com parágrafos curtos.
    - Para cada marcador, use o formato: "Marcador (valor): explicação... Situação: ...".
    - No final, inclua um aviso médico em texto simples.
    - Não use emojis.

    PERFIL DO PACIENTE:
    {perfil_texto}

    CONTEXTO DAS DIRETRIZES MÉDICAS:
    {contexto_unido}
    """

    dados_paciente = json.dumps(metricas_entrada, ensure_ascii=False)
    mensagem_usuario = (
        f"Marcadores que quero que você explique: {dados_paciente}. "
        f"Explique SOMENTE estes marcadores e diga se estão dentro do esperado com base no contexto."
    )

    resposta = cliente_ia.chat.completions.create(
        model="gpt-4o",
        temperature=0.2,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensagem_usuario},
        ],
    )
    return resposta.choices[0].message.content
