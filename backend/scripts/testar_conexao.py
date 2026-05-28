"""Testa conexão com o banco Neon. Uso: python -m scripts.testar_conexao (a partir de backend/)"""

import os
import sys

import psycopg2
from dotenv import load_dotenv

# Garante imports quando executado como script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

URL_DO_BANCO = os.getenv("DATABASE_URL")


def main():
    try:
        print("Tentando conectar ao banco de dados Neon...")
        conexao = psycopg2.connect(URL_DO_BANCO)
        print("Conexao com PostgreSQL estabelecida com sucesso.")
        conexao.close()
    except Exception as e:
        print(f"Erro ao conectar:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
