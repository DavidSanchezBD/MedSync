# 🏥 MedSync — Tradutor de Exames Laboratoriais Inteligente

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.100.0%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o%20%26%20mini-412991?logo=openai&logoColor=white" alt="OpenAI API">
  <img src="https://img.shields.io/badge/ChromaDB-Database%20Vetorial-orange" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Pandas-Tratamento%20de%20Dados-150458?logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/PostgreSQL-Neon%20DB-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
</p>

> [!IMPORTANT]
> **Aviso de Isenção de Responsabilidade:** Este é um projeto acadêmico (prova de conceito). A inteligência artificial pode cometer erros na extração ou na interpretação de marcadores. **Este sistema serve exclusivamente para fins informativos e não substitui a avaliação médica profissional.**

---

## 🌟 O que é o MedSync?

O **MedSync** é uma plataforma inteligente e amigável desenvolvida para resolver uma dor real de milhões de pacientes: **a dificuldade de ler e compreender laudos de exames laboratoriais**. 

Ao receber o PDF bruto de um exame de sangue, a plataforma extrai os dados estruturados de forma inteligente, analisa e classifica cada indicador e traduz os termos técnicos médicos em uma linguagem humana, leiga, empática e altamente personalizada de acordo com o perfil de saúde do usuário.

Tudo isso é exibido através de uma **interface Web moderna, elegante e responsiva**, com painéis visuais que indicam a situação de cada marcador (Normal, Atenção ou Indefinido).

---

## 🚀 Arquitetura Técnica do Projeto

O MedSync foi construído seguindo rigorosos padrões de engenharia de software e de dados, estruturando-se em três camadas principais conforme exigido no desafio final:

```mermaid
graph TD
    A[Laudo em PDF] --> B[Extrator PyPDF2]
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
Antes de processar qualquer dado cognitivo, o sistema converte os marcadores e valores estruturados para um **Pandas DataFrame**. O Pandas é usado ativamente para:
* **Tratamento de Nulos**: Remoção de registros inválidos que não possuem marcador (`dropna`).
* **Tratamento de Strings e Tipagem**: Correção de tipagem e remoção de espaços em branco adicionais (`astype(str).str.strip()`), além de preenchimento inteligente de valores nulos na leitura (`fillna`).
* **Remoção de Duplicatas**: Descarte automático de marcadores duplicados gerados erroneamente na extração (`drop_duplicates`).

### 2. 🧠 Camada Cognitiva (Arquitetura de RAG Híbrido)
A fim de mitigar totalmente as alucinações e erros de cálculo clássicos em LLMs, o motor de busca e classificação foi desenvolvido como uma **arquitetura híbrida avançada**:
* **Busca Determinística (Índice Local)**: O sistema tenta casar o nome do marcador diretamente com o índice em memória. Se a correspondência for direta ou altamente confiável (via Fuzzy Matching/Similaridade Textual com threshold de `0.78`), ele extrai a regra exata correspondente da base médica.
* **Busca Semântica (ChromaDB)**: Caso a correspondência determinística falhe (abreviações ou variações complexas de nomenclatura), o sistema consulta a base vetorial do **ChromaDB** para resgatar semanticamente as diretrizes médicas mais próximas.
* **Parser Matemático Nativo**: Em vez de deixar a IA deduzir se um número está fora da faixa, o próprio motor em Python interpreta limites matemáticos de referência (ex: `"70 a 99"`, `"< 100"`, `"> 5"`) por expressões regulares (Regex), classificando o status em tempo recorde e sem custo de tokens da API.
* **Classificação e Tradução Assistida**: O `gpt-4o-mini` resolve regras complexas com dependência de idade ou gênero do perfil de saúde e o `gpt-4o` gera a explicação humana e empática sem markdown para exibição nativa.

### 3. 🗄️ Camada de Persistência e Segurança
* **Neon PostgreSQL**: Banco de dados na nuvem que armazena os dados cadastrais criptografados dos usuários, seus perfis de saúde detalhados e o histórico de metadados dos exames processados.
* **Autenticação JWT**: Segurança de ponta para controle de acesso às rotas da API.
* **Variáveis de Ambiente**: Arquivo `.env` configurado rigorosamente no `.gitignore` para proteção das chaves privadas de API.

---

## 📂 Estrutura de Pastas do Projeto

```text
MedSync/
├── frontend/                  # Camada Visual (Interface SPA)
│   ├── index.html             # Estrutura HTML5 semântica e moderna
│   ├── style.css              # Estilização com Glassmorphism, Micro-animações e Dark Mode
│   └── script.js              # Lógica de integração assíncrona com a API (Fetch)
├── backend/                   # Camada de Serviços (Python + FastAPI)
│   ├── main.py                # Ponto de entrada do servidor Uvicorn
│   ├── api/                   # Roteamento e Dependências
│   │   ├── deps.py            # Injeção de dependências (Auth JWT & Conexão DB)
│   │   ├── router.py          # Centralizador de rotas da API
│   │   └── routes/            # Endpoints: auth, perfil e exames
│   ├── core/                  # Motores Inteligentes
│   │   ├── extractor.py       # Extração de PDF e estruturação via IA
│   │   └── rag_engine.py      # Camada de Dados (Pandas) + RAG Híbrido (ChromaDB / OpenAI)
│   ├── database/              # Conectores e Migrações de Banco de Dados
│   │   └── db.py              # Pool de conexões do Neon PostgreSQL
│   ├── models/                # Schemas de dados e Validação
│   │   └── schemas.py         # Modelos de validação de dados Pydantic
│   ├── services/              # Regras de Negócio e Serviços
│   │   ├── auth.py            # Criptografia de senhas (bcrypt) e geração de tokens JWT
│   │   └── perfil.py          # Lógica para criação e busca do perfil do paciente
│   ├── data/                  # Fontes de Dados
│   │   └── base_conhecimento_medica.txt   # Base médica de referências e faixas normativas
│   └── scripts/               # Scripts Utilitários
│       └── testar_conexao.py  # Script para testar a comunicação com o Neon PostgreSQL
└── README.md                  # Documentação do Projeto

```

---

## ⚙️ Pré-requisitos e Instalação

### Pré-requisitos
* **Python 3.9+** instalado.
* Conta na **OpenAI** (com saldo de API Key ativo).
* Instância do **PostgreSQL** ativa (Recomendado: Neon DB) contendo as tabelas do banco de dados (as migrations rodam nativamente ao iniciar a API).

### Instalação Passo a Passo

1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/DavidSanchezBD/MedSync.git
   cd MedSync
   ```

2. **Configurar o Ambiente Virtual (venv)**:
   ```bash
   python -m venv venv
   
   # Ativação no Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   
   # Ativação no Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar as Dependências do Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configurar as Variáveis de Ambiente**:
   Copie o arquivo de exemplo e insira suas credenciais:
   ```bash
   cp .env.example .env
   ```
   Abra o arquivo `.env` e preencha as variáveis:
   ```env
   OPENAI_API_KEY=sua-chave-da-openai-aqui
   DATABASE_URL=postgresql://usuario:senha@seu-host-neon.tech/neondb?sslmode=require
   JWT_SECRET=sua-chave-secreta-jwt-aqui
   JWT_EXPIRE_HOURS=72
   ```

---

## 🏃‍♂️ Como Executar a Aplicação

### 1. Iniciar o Servidor Backend (FastAPI)
Dentro da pasta `backend`, com o ambiente virtual ativado, execute:
```bash
uvicorn main:app --reload
```
A API estará de pé e escutando em `http://localhost:8000`.

### 2. Iniciar o Frontend Web
O frontend é construído puramente em Vanilla HTML, CSS e JS (SPA).
Você pode abrir o arquivo `frontend/index.html` diretamente no navegador ou, preferencialmente, executá-lo usando a extensão **Live Server** do VS Code em `http://127.0.0.1:5500`.

---

## 🔬 Testes e Validação

Você pode validar a conexão da aplicação com o banco de dados Neon a qualquer momento executando o utilitário na pasta `backend`:
```bash
python scripts/testar_conexao.py
```

---

## 🧑‍💻 Autores e Contribuição

Este projeto foi desenvolvido com dedicação como o **Desafio Final** da disciplina de **IA na Prática** do **Instituto Mauá de Tecnologia (IMT)**:

* **David Sanchez Bittencourt Daniel**
* **Mateus Yuji Ohira**

---
