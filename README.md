# 🏥 MedSync — Tradutor de Exames Laboratoriais Inteligente

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.136%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o%20%26%20mini-412991?logo=openai&logoColor=white" alt="OpenAI API">
  <img src="https://img.shields.io/badge/ChromaDB-Database%20Vetorial-orange" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Pandas-Tratamento%20de%20Dados-150458?logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/PostgreSQL-Neon%20DB-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Frontend-Vanilla%20HTML%2FCSS%2FJS-F7DF1E?logo=javascript&logoColor=black" alt="Vanilla JS">
</p>

> [!IMPORTANT]
> **Aviso de Isenção de Responsabilidade:** Este é um projeto acadêmico (prova de conceito). A inteligência artificial pode cometer erros na extração ou na interpretação de marcadores. **Este sistema serve exclusivamente para fins informativos e não substitui a avaliação médica profissional.**

---

## 🌟 O que é o MedSync?

O **MedSync** é uma plataforma inteligente e amigável desenvolvida para resolver uma dor real de milhões de pacientes: **a dificuldade de ler e compreender laudos de exames laboratoriais**.

Ao receber o PDF bruto de um exame de sangue, a plataforma extrai os dados estruturados de forma inteligente, analisa e classifica cada indicador e traduz os termos técnicos médicos em uma linguagem humana, leiga, empática e altamente personalizada de acordo com o perfil de saúde do usuário.

Tudo isso é exibido através de uma **interface Web moderna, elegante e responsiva** em Vanilla HTML/CSS/JS — sem frameworks, sem dependências de build — com painéis visuais que indicam a situação de cada marcador (Normal, Atenção ou Indefinido).

---

## 🚀 Arquitetura Técnica do Projeto

O MedSync é estruturado em três camadas principais:

```mermaid
graph TD
    A[Laudo em PDF] --> B[Extrator PyPDF2 + OpenAI]
    B --> C[Camada de Dados: Pandas]
    C -->|Dados Higienizados| D[Camada Cognitiva: RAG Híbrido]
    D -->|1. Busca Exata| E[Índice de Dicionário em Memória]
    D -->|2. Busca Semântica Fallback| F[ChromaDB - Base Vetorial]
    D -->|3. Processador Matemático| G[Regex & Regras de Faixa em Python]
    D -->|4. Casos Complexos| H[OpenAI gpt-4o-mini]
    D -->|5. Tradução Empática| I[OpenAI gpt-4o]
    I --> J[Interface Web / Visual Dashboard]
```

### 1. 📊 Camada de Dados (Tratamento e Higienização com Pandas)
Antes de processar qualquer dado cognitivo, o sistema converte os marcadores extraídos para um **Pandas DataFrame** para garantir qualidade e consistência:
- **Tratamento de Nulos**: Remoção de registros sem marcador (`dropna`).
- **Tratamento de Strings e Tipagem**: Correção de tipagem e remoção de espaços (`astype(str).str.strip()`), preenchimento inteligente de valores nulos (`fillna`).
- **Remoção de Duplicatas**: Descarte automático de marcadores duplicados gerados erroneamente na extração (`drop_duplicates`).

### 2. 🧠 Camada Cognitiva (Arquitetura de RAG Híbrido)
Motor de busca e classificação desenvolvido como uma **arquitetura híbrida avançada** para mitigar alucinações:
- **Busca Determinística (Índice Local)**: Casamento direto do nome do marcador com índice em memória. Fuzzy Matching com threshold de `0.78` para variações de nomenclatura.
- **Busca Semântica (ChromaDB)**: Fallback vetorial para abreviações ou nomenclaturas complexas.
- **Parser Matemático Nativo**: Interpretação de limites matemáticos de referência (ex: `"70 a 99"`, `"< 100"`, `"> 5"`) por Regex, sem custo de tokens.
- **Classificação e Tradução Assistida por IA**: `gpt-4o-mini` para casos ambíguos e `gpt-4o` para a explicação final em linguagem humana.

### 3. 🗄️ Camada de Persistência e Segurança
- **Neon PostgreSQL**: Banco na nuvem para cadastro de usuários, perfis de saúde e histórico.
- **Autenticação JWT**: Geração e validação de tokens via `python-jose`, com senhas protegidas por `bcrypt`.
- **Variáveis de Ambiente**: Chaves de API protegidas via `.env` e `.gitignore`.

---

## 📂 Estrutura de Pastas do Projeto

```text
MedSync/
├── frontend/                  # Camada Visual (SPA — Vanilla HTML/CSS/JS)
│   ├── index.html             # Estrutura HTML5 semântica
│   ├── style.css              # Glassmorphism, micro-animações e dark mode
│   └── script.js              # Lógica de integração assíncrona com a API (Fetch)
├── backend/                   # Camada de Serviços (Python + FastAPI)
│   ├── main.py                # Ponto de entrada: todas as rotas da API
│   ├── core/                  # Motores Inteligentes
│   │   ├── extractor.py       # Extração de PDF e estruturação via OpenAI
│   │   └── rag_engine.py      # Camada de Dados (Pandas) + RAG Híbrido (ChromaDB / OpenAI)
│   ├── database/              # Conexão com banco de dados
│   │   └── db.py              # Context manager de conexão com Neon PostgreSQL (psycopg2)
│   ├── services/              # Regras de negócio
│   │   ├── auth.py            # Registro, login e validação de token JWT (python-jose + bcrypt)
│   │   └── perfil.py          # Upsert do perfil de saúde do paciente
│   ├── data/                  # Fontes de dados estáticas
│   │   └── base_conhecimento_medica.txt   # Base médica com faixas normativas de referência
│   ├── .env                   # Variáveis de ambiente (NÃO versionar)
│   ├── .env.example           # Modelo de variáveis de ambiente
│   └── requirements.txt       # Dependências Python do projeto
├── venv/                      # Ambiente virtual Python (NÃO versionar)
└── README.md                  # Documentação do projeto
```

---

## 🔌 Rotas da API

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/` | ❌ | Health check |
| `POST` | `/api/auth/registro` | ❌ | Cria nova conta de usuário |
| `POST` | `/api/auth/login` | ❌ | Login e geração de token JWT |
| `GET` | `/api/auth/me` | ✅ Bearer Token | Dados e perfil do usuário autenticado |
| `POST` | `/api/perfil` | ✅ Bearer Token | Salva ou atualiza o perfil de saúde |
| `POST` | `/api/upload` | ✅ Bearer Token | Envia PDF → análise RAG → resultado |

---

## ⚙️ Pré-requisitos e Instalação

### Pré-requisitos
- **Python 3.12+** instalado.
- Conta na **OpenAI** com API Key ativa e com saldo.
- Instância **PostgreSQL** ativa (recomendado: [Neon DB](https://neon.tech)) com as tabelas criadas (ver seção abaixo).

### Configuração do Banco de Dados (Neon PostgreSQL)

Execute as seguintes queries no seu banco para criar as tabelas necessárias:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE perfis_saude (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL,
    idade INTEGER NOT NULL,
    genero_biologico VARCHAR(30) NOT NULL,
    peso_kg NUMERIC(5, 2),
    altura_cm NUMERIC(5, 1),
    condicoes_previas TEXT,
    historico_familiar TEXT,
    CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

### Instalação Passo a Passo

1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/DavidSanchezBD/MedSync.git
   cd MedSync
   ```"

2. **Configurar o Ambiente Virtual**:
   ```bash
   python -m venv venv

   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1

   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar as Dependências**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configurar as Variáveis de Ambiente**:
   ```bash
   cp .env.example .env
   ```
   Abra `.env` e preencha:
   ```env
   OPENAI_API_KEY=sua-chave-da-openai-aqui
   DATABASE_URL=postgresql://usuario:senha@seu-host-neon.tech/neondb?sslmode=require
   ```

---

## 🏃‍♂️ Como Executar a Aplicação

### 1. Iniciar o Servidor Backend (FastAPI)
Dentro da pasta `backend`, com o ambiente virtual ativado:
```bash
uvicorn main:app --reload
```
A API estará disponível em `http://localhost:8000`.  
Documentação interativa (Swagger): `http://localhost:8000/docs`.

### 2. Iniciar o Frontend Web
O frontend é Vanilla HTML/CSS/JS — sem etapa de build.

Abra `frontend/index.html` diretamente no navegador, ou preferencialmente via extensão **Live Server** do VS Code em `http://127.0.0.1:5500`.

---

## 🧑‍💻 Autores

Este projeto foi desenvolvido como o **Desafio Final** da disciplina de **IA na Prática** do **Instituto Mauá de Tecnologia (IMT)**:

- **David Sanchez Bittencourt Daniel**
- **Mateus Yuji Ohira**

---
