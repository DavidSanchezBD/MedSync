import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
cliente_ia = OpenAI()

dados_cx = {
    'ID_Ticket': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 
                  1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022],
    'Status': ['Concluído', 'Pendente', 'Concluído', 'Concluído', 'Cancelado', 
               'Concluído', 'Concluído', 'Concluído', 'Concluído', 'Concluído',
               'Pendente', 'Concluído', 'Concluído', 'Concluído', 'Concluído',
               'Concluído', 'Cancelado', 'Concluído', 'Concluído', 'Concluído', 'Concluído', 'Concluído'],
    'Avaliacao': ['Negativa', 'Positiva', 'Negativa', 'Negativa', 'Negativa', 
                  'Positiva', 'Negativa', 'Negativa', 'Negativa', 'Negativa',
                  'Negativa', 'Positiva', 'Negativa', 'Negativa', 'Negativa',
                  'Negativa', 'Positiva', 'Negativa', 'Negativa', 'Negativa', 'Positiva', 'Negativa'],
    'Comentario': [
        'A transportadora demorou 15 dias além do prazo. Péssimo!',
        'Ainda não chegou, mas o código de rastreio atualiza rápido.',
        'A tela do celular veio com um trincado na ponta direita.',
        'Liguei para reclamar e a atendente foi super grossa comigo.',
        'Desisti da compra porque ninguém respondia meus e-mails.',
        'Produto excelente, chegou antes do prazo e muito bem embalado.',
        'A caixa estava toda amassada e o manual rasgado por causa da chuva.',
        'O lado esquerdo do fone de ouvido parou de funcionar em dois dias.',
        'O robô do chat de vocês não entende nada, impossível falar com humano.',
        'O entregador jogou o pacote pelo portão e quebrou o produto.',
        'Comprei faz um mês e até agora não emitiram a nota fiscal.',
        'O suporte técnico me ajudou a configurar o sistema em 5 minutos, nota 10!',
        'A qualidade do material é horrível, na primeira lavagem encolheu tudo.',
        'Fiquei 40 minutos na música de espera e a ligação simplesmente caiu.',
        'O código de rastreio que me passaram dá como inexistente nos Correios.',
        'O botão de ligar afundou e não volta mais, acabamento muito frágil.',
        'Cancelei por erro meu na cor, mas o estorno no cartão foi rápido.',
        'Mandaram o tamanho errado. Pedi GG e enviaram M.',
        'O atendente prometeu um desconto que não veio na fatura deste mês.',
        'A bateria não dura nem 2 horas, propaganda enganosa.',
        'Tudo perfeito, recomendo muito a loja.',
        'O entregador mentiu no sistema dizendo que não tinha ninguém em casa.'
    ]
}

df_setup = pd.DataFrame(dados_cx)
df_setup.to_csv('feedbacks_clientes.csv', index=False)
print("✅ Ficheiro 'feedbacks_clientes.csv' gerado com sucesso!\n")

print("--- INICIANDO AUDITORIA DE CX COM IA ---\n")

# ----------------------------------------------------------------
# TODO 1: LEITURA E FILTRAGEM (Pandas)
# ----------------------------------------------------------------

# 1. Carregue o 'feedbacks_clientes.csv'.
# 2. Crie um novo DataFrame (ex: df_problemas) que contenha APENAS:
#    Status == 'Concluído' E Avaliacao == 'Negativa'
# 3. Printar o DataFrame filtrado

df_filtro = df_setup[(df_setup['Avaliacao']=='Negativa') & (df_setup['Status']=='Concluído')]
# for index, row in df_filtro.iterrows():
#     print(f"ID_Ticket: {row['ID_Ticket']} - Comentário: {row['Comentario']}")

# ----------------------------------------------------------------
# TODO 2: ANÁLISE COM IA (A Mágica)
# ----------------------------------------------------------------

# Crie uma lista vazia chamada 'categorias_ia'.
categorias_ia = []

# Faça um loop (for) para passar por cada texto da coluna 'Comentario'.
for comentario in df_filtro['Comentario']:
    
    # Para cada comentário, chame a API da OpenAI para classificar o texto.
    # Peça à IA para classificar o texto numa destas categorias: [Logistica, Suporte, Produto].
    # Guarde a resposta da IA na lista 'categorias_ia'.
    resposta = cliente_ia.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um assistente de classificação de feedbacks de clientes."},
            {"role": "user", "content": f"Classifique o seguinte comentário em uma das categorias: [Logistica, Suporte, Produto]. Comentário: '{comentario}'. Responda apenas com a categoria sem explicações."}
        ],
        temperature=0.2
    )
    categoria = resposta.choices[0].message.content.strip()
    categorias_ia.append(categoria)

# ----------------------------------------------------------------
# TODO 3: ENRIQUECIMENTO E RELATÓRIO FINAL (Pandas)
# ----------------------------------------------------------------
# 1. Crie uma nova coluna no seu DataFrame filtrado chamada 'Categoria_Erro'
#    e atribua a ela a lista 'categorias_ia' que acabou de gerar.

df_filtro['Categoria_Erro'] = categorias_ia

# 2. Faça um groupby pela 'Categoria_Erro' e conte quantos problemas cada uma tem.
df_relatorio = df_filtro.groupby('Categoria_Erro').size()
print("\n📊 Relatório de Problemas por Departamento:")
print(df_relatorio)
# 3. Faça um relatório executivo usando IA
resposta = cliente_ia.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Você é um assistente de resumo de relatórios de feedbacks de clientes."},
        {"role": "user", "content": f"Resuma os problemas encontrados no seguinte relatório: {df_relatorio.to_string()}"}
    ],
    temperature=0.2
)

print("\n📋 Resumo Executivo:")
print(resposta.choices[0].message.content.strip())
