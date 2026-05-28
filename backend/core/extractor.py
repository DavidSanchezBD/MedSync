import json

from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

load_dotenv()
cliente_ia = OpenAI()


def extrair_dados_exame(caminho_pdf: str) -> dict:
    print("[MedSync] Iniciando leitura do PDF...")

    texto_bruto = ""
    with open(caminho_pdf, "rb") as arquivo:
        leitor_pdf = PdfReader(arquivo)
        for pagina in leitor_pdf.pages:
            texto_bruto += pagina.extract_text() or ""

    print("[MedSync] Enviando para a OpenAI...")
    prompt_sistema = """
    Você é um assistente especializado em extrair informações de laudos de exames laboratoriais.
    Receberá um texto bruto extraído de um PDF e deve retornar APENAS UM JSON com as seguintes chaves:
    "nome_paciente", "data_exame" e "metricas".
    A chave "metricas" deve ser uma lista de objetos, onde cada objeto tem "marcador" (ex: Glicose, Colesterol Total) e "valor".
    Se alguma informação não puder ser encontrada, retorne null.
    """

    resposta = cliente_ia.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0.1,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": texto_bruto},
        ],
    )

    return json.loads(resposta.choices[0].message.content)
