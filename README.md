# MedSync — Tradutor de Exames Laboratoriais

> **Aviso:** Projeto acadêmico (prova de conceito). A IA pode errar na extração ou interpretação. **Não substitua** avaliação médica profissional.

## O que é

O **MedSync** recebe um PDF de exame laboratorial, extrai os marcadores com IA, compara com uma base de referências médicas e exibe uma explicação em linguagem leiga — com painel visual de métricas (normal / atenção / sem referência).

## Estrutura do projeto

```
MedSync/
├── frontend/          # HTML, CSS, JS (interface)
├── backend/
│   ├── main.py        # Entrada FastAPI
│   ├── api/           # Rotas HTTP
│   │   ├── deps.py
│   │   ├── router.py
│   │   └── routes/    # auth, perfil, exames
│   ├── core/          # Extração PDF + RAG
│   ├── services/      # Auth JWT, perfil de saúde
│   ├── models/        # Schemas Pydantic
│   ├── database/      # Conexão Neon + migrations SQL
│   ├── data/          # base_conhecimento_medica.txt
│   └── scripts/       # Utilitários (testar conexão)
└── README.md
```

## Pré-requisitos

- Python 3.9+
- Conta OpenAI (API key)
- Banco PostgreSQL (ex.: Neon) com tabelas `usuarios`, `perfis_saude`, `exames_metadados`

## Configuração

```bash
cd backend
python -m venv ../venv
..\venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env     # preencha as variáveis
```

Variáveis em `backend/.env`:

```env
OPENAI_API_KEY=...
DATABASE_URL=postgresql://...
```
## Executar

**API** (pasta `backend`):

```bash
uvicorn main:app --reload
```

**Frontend:** abra `frontend/index.html` com Live Server (ex.: `http://127.0.0.1:5500`) — a API deve estar em `http://localhost:8000`.

**Testar banco:**

```bash
python scripts/testar_conexao.py
```

## Autores

Instituto Mauá de Tecnologia — David Sanchez Bittencourt Daniel, Mateus Yuji Ohira.
