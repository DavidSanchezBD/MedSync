# 🩺 Decode.Med: O Tradutor de Exames Clínicos

> ⚠️ **Aviso Legal:** Este é um projeto acadêmico de prova de conceito desenvolvido para a disciplina de Inteligência Artificial. A inteligência artificial pode apresentar alucinações ou extrair dados de forma incorreta. **Nunca substitua a avaliação e o diagnóstico de um profissional de saúde pelos resultados gerados por este software.**

---

## 📌 O Problema
Pacientes frequentemente recebem exames laboratoriais em arquivos PDF complexos e difíceis de interpretar, repletos de números soltos e jargões técnicos. Além disso, cada laboratório possui um layout de laudo diferente, o que dificulta a extração padronizada de dados e o acompanhamento histórico dessas métricas essenciais de saúde.

## 💡 A Solução
O **Decode.Med** é um aplicativo web interativo que automatiza a leitura e a interpretação de exames de sangue e laudos clínicos. 

O sistema recebe um arquivo PDF, extrai os valores numéricos através de Inteligência Artificial, cruza esses resultados com uma base de referência médica utilizando engenharia de dados e exibe as métricas de forma limpa em um painel interativo. Marcadores classificados como "Alterados" são traduzidos pela IA para uma linguagem leiga, acessível e tranquilizadora.

---

## ⚙️ Arquitetura do Pipeline de Dados

Este projeto foi construído sobre uma arquitetura de 4 camadas:

1. **Camada de Extração (Python & IA):** Utilização da biblioteca `PyPDF2` para a leitura do documento e integração com a API da OpenAI (modelo `gpt-4o-mini`). O uso de *Structured Outputs* garante o retorno dos dados em um formato JSON rigoroso (`nome_exame` e `valor_encontrado`), mitigando alucinações.
2. **Camada de Dados (Pandas):** Cruzamento (`pd.merge`) dos dados extraídos com uma base estática de referências médicas (`referencias_medicas.csv`). O Pandas valida matematicamente se a métrica está dentro do limite aceitável, classificando o status como "Normal" ou "Alterado".
3. **Camada Cognitiva (Tradução LLM):** Os exames classificados como "Alterados" passam por uma nova inferência na IA, que gera uma explicação simples sobre a função daquele marcador biológico.
4. **Camada de Interface (Streamlit):** Front-end responsivo, com upload nativo de PDF, tratamento de estado (cache) e visualização de tabelas e métricas.

---

## 🚀 Como rodar o projeto localmente

### 1. Pré-requisitos
Certifique-se de ter o [Python](https://www.python.org/downloads/) (versão 3.9 ou superior) instalado em sua máquina.

### 2. Instalação e Configuração
Clone este repositório para o seu ambiente local:
```bash
git clone https://github.com/seu-usuario/decodemed.git
cd decodemed
```

Crie e ative um ambiente virtual para isolar as dependências:
```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows:
venv\Scripts\activate

# Ativar no Mac/Linux:
source venv/bin/activate
```

Instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie um arquivo chamado `.env` na raiz do projeto. (Nota: O repositório já conta com um `.gitignore` configurado para impedir o vazamento desta chave). Adicione sua chave da API da OpenAI neste arquivo:
```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

### 4. Execução
Com o ambiente configurado, inicie a aplicação Streamlit:
```bash
streamlit run app.py
```
O aplicativo será aberto automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).

---

## 👨‍💻 Autores e Desenvolvedores

Projeto de Inteligência Artificial desenvolvido no **Instituto Mauá de Tecnologia** por:

* **David Sanchez Bittencourt Daniel**
* **Mateus Yuji Ohira**