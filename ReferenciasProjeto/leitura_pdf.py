import os
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
cliente_ia = OpenAI()

# ====================================================================
# TODO 1: LEITURA DO "PDF" (Lendo o texto sujo)
# ====================================================================
# Leia o arquivo 'fatura_suja_01.txt' e guarde todo o conteúdo 
# em uma variável chamada 'texto_bruto'.

caminho_arquivo = 'C:/Users/24.00752-8/Documents/Chat_bot/dev/exemplos/nota-fiscal-notebook-dell.pdf'

with open(caminho_arquivo, 'rb') as arquivo:
    leitor_pdf = PdfReader(arquivo)
    texto_bruto = ''
    for pagina in leitor_pdf.pages:
        texto_bruto += pagina.extract_text()



# ====================================================================
# TODO 2: EXTRAÇÃO INTELIGENTE COM IA (Structured Output)
# ====================================================================
# Use a API da OpenAI para analisar o 'texto_bruto'.
# CRIE UM SYSTEM PROMPT EXTREMAMENTE RÍGIDO pedindo que a IA 
# devolva a resposta NO FORMATO JSON com as chaves:
# "nome_empresa", "data_vencimento", "valor" (só os números).

prompt_sistema = resposta = cliente_ia.chat.completions.create(
            model="gpt-4o-mini", 
            response_format={"type": "json_object"},
            temperature=0.1,
            messages=[
                {"role": "system", "content": 'Você é um assistente especializado em extrair informações de faturas. '
                '                              Receberá um texto bruto extraído de um PDF de fatura e deve retornar APENAS UM JSON com as seguintes chaves:'
                '                               "nome_empresa", "data_vencimento", "valor". '
                '                               O valor deve conter apenas os números, sem símbolos ou texto adicional. '
                '                               Se alguma informação não puder ser encontrada, '
                '                               retorne null para aquela chave.'},
                {"role": "user", "content": texto_bruto}
                ]
            )
resposta = resposta.choices[0].message.content
print(resposta)

# ====================================================================
# TODO 3: CONSOLIDANDO NO PANDAS
# ====================================================================
# 1. Pegue a resposta em JSON gerada pela IA (que é uma string).
# 2. Converta ela em um dicionário Python (use a biblioteca 'json').
# 3. Transforme esse dicionário em uma linha de um DataFrame do Pandas.

import json
json_extraido = json.loads(resposta)
df_resultado = pd.DataFrame([json_extraido])
print("\n📊 Dado Extraído e Estruturado:")
print(df_resultado)
