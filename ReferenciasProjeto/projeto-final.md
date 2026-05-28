# 🏆 Desafio Final: IA na Prática

## O Cenário: Carta Branca
Ao longo do curso, vimos como a Inteligência Artificial e a Engenharia de Dados podem resolver o caos do mundo corporativo. Agora, a bola está com vocês e **vocês têm total liberdade para escolher o tema do projeto.**

O seu desafio é identificar um problema real e construir um *produto de dados* para resolvê-lo. Pode ser um gargalo do atual estágio/trabalho, uma dificuldade da vida universitária, ou até mesmo algo focado em hobbies (finanças pessoais, análise de jogos, esporte, viagens). A única regra é: **o sistema tem de ser útil e resolver um problema de forma automatizada.**

## Objetivo do Projeto
Construir um pipeline de dados inteligente, de ponta a ponta, que receba dados brutos/desestruturados, utilize a inteligência de um LLM para tratá-los ou consultá-los, e exiba os resultados numa interface visual funcional.

---

## Requisitos Técnicos Obrigatórios (MVP)

Apesar de o tema ser livre, o projeto de vocês **deve** conter obrigatoriamente as 3 camadas abaixo:

### Grupos de até 3 pessoas

### 1. Camada de Dados (Pandas)
* O sistema deve ler pelo menos uma base de dados externa (um `.csv` sujo, um `.xlsx` ou múltiplos arquivos `.txt`/`.pdf`).
* O código deve realizar pelo menos uma operação de **limpeza** (tratar nulos, remover duplicatas ou corrigir tipagem).

### 2. Camada Cognitiva (Inteligência Artificial)
* O sistema deve realizar chamadas para a API (OpenAI ou Gemini).
* **Opção A (Extração/Classificação):** Usar *Structured Outputs* (JSON) para ler textos livres da base de dados e criar uma nova coluna padronizada (ex: Análise de Sentimento de comentários, extração de dados específicos).
* **Opção B (RAG):** Usar o `ChromaDB` para vetorizar documentos complexos e permitir buscas semânticas (ex: um assistente que lê manuais e responde a dúvidas baseadas neles).

### 3. Camada de Engenharia e Versionamento (GitHub)
* O projeto deve estar num repositório público no GitHub.
* O repositório **NÃO** pode conter a chave da API (`.env` deve estar no `.gitignore`).
* O repositório deve ter um arquivo `requirements.txt`.
* O repositório deve ter um `README.md` muito bem escrito, explicando o que é o projeto, qual problema resolve e como rodar o código localmente.

## Entregáveis e Prazos

* **Data de Entrega (GitHub):** 31/05 até as 23h59. Apenas o link do repositório deve ser enviado.
* **Demo Day:** o projeto precisa ser apresentado para mim, na data melhor para o grupo.

### O formato do Demo Day:
Cada grupo terá **5 a 7 minutos** para apresentar. Não quero slides cheio de textos. A estrutura da apresentação deve ser:
1. **O Problema (1 min):** "Qual é a dor ou desafio que escolhemos resolver?"
2. **A Solução (1 min):** "Como usamos IA para criar este produto?"
3. **Ao Vivo (Live Demo) (3 min):** Executar a aplicação e mostrar que funciona.
4. **Desafios Técnicos (1 min):** "Qual foi a parte mais difícil do código e como a superamos?"

---

## Critérios de Avaliação

1. **Funcionalidade (40%):** O código roda sem quebrar? A aplicação resolve o problema proposto? A integração com a API funciona?
2. **Arquitetura e Clean Code (20%):** O código está organizado? As variáveis têm nomes lógicos? O System Prompt foi bem construído para evitar alucinações da IA?
3. **Complexidade e Domínio (20%):** O grupo demonstrou dominar o Pandas e o fluxo de dados, ou apenas copiou tutoriais básicos?
4. **Apresentação e Produto (20%):** A interface é amigável? O `README.md` está profissional? A apresentação foi clara e focado no valor entregue?
