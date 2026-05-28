import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@contextmanager
def obter_conexao():
    conexao = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
