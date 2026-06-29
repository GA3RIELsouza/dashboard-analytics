import pandas as pd
import plotly.express as px

# 1. Carregamento e Preparação dos Dados
df = pd.read_csv('dados.csv', sep=';')
df['Data'] = pd.to_datetime(df['Data'])
df['Faturamento'] = pd.to_numeric(df['Faturamento'], errors='coerce').fillna(0)
df['Perda_Financeira'] = pd.to_numeric(df['Perda_Financeira'], errors='coerce').fillna(0)
df['Taxa_Defeitos_%'] = pd.to_numeric(df['Taxa_Defeitos_%'], errors='coerce').fillna(0)

# Cálculos para os Cartões de KPI (Visão Geral)
total_faturamento = df['Faturamento'].sum()
total_perda = df['Perda_Financeira'].sum()
media_taxa_defeitos = df['Taxa_Defeitos_%'].mean()
alertas_estoque_total = df[df['Alerta_Estoque'] == 'Sim'].shape[0]

# 2. Criação dos Gráficos (Plotly)

# KPI: Taxa de Defeitos Diária
df_diario = df.groupby('Data')['Taxa_Defeitos_%'].mean().reset_index()
fig_taxa_defeitos = px.line(df_diario, x='Data', y='Taxa_Defeitos_%', 
                            title='Taxa Média de Defeitos Diária (%)',
                            markers=True, labels={'Taxa_Defeitos_%': 'Taxa de Defeitos (%)'})
fig_taxa_defeitos.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Limite Superior (5%)")
fig_taxa_defeitos.add_hline(y=3, line_dash="dash", line_color="orange", annotation_text="Margem Alerta (3%)")

# KPI: Refugo vs Retrabalho
df_qualidade = df.groupby('Tipo_Defeito_Predominante')[['Quantidade_Retrabalho', 'Quantidade_Segunda_Qualidade']].sum().reset_index()
# Filtrando 'Sem defeito relevante' para focar nos problemas
df_qualidade = df_qualidade[df_qualidade['Tipo_Defeito_Predominante'] != 'Sem defeito relevante']
fig_refugo_retrabalho = px.bar(df_qualidade, x='Tipo_Defeito_Predominante', 
                               y=['Quantidade_Retrabalho', 'Quantidade_Segunda_Qualidade'],
                               title='Refugo (2ª Qualidade) vs Retrabalho por Tipo de Defeito',
                               barmode='group', 
                               labels={'value': 'Quantidade', 'variable': 'Tipo de Ação',
                                       'Tipo_Defeito_Predominante': 'Tipo de Defeito Predominante',
                                       'Quantidade_Retrabalho': 'Quantidade de Retrabalho',
                                       'Quantidade_Segunda_Qualidade': 'Quantidade de 2ª Qualidade'})

# KPI: Perda Financeira por Má Qualidade
df_perda = df.groupby('Tipo_Defeito_Predominante')['Perda_Financeira'].sum().reset_index()
df_perda = df_perda[df_perda['Perda_Financeira'] > 0]
fig_perda_financeira = px.pie(df_perda, names='Tipo_Defeito_Predominante', values='Perda_Financeira',
                              title='Perda Financeira por Tipo de Defeito', hole=0.3,
                              labels={'Tipo_Defeito_Predominante': 'Tipo de Defeito Predominante',
                                      'Perda_Financeira': 'Perda Financeira'})

# KPI: Faturamento vs Meta Mensal
df_faturamento = df.groupby('AnoMes')['Faturamento'].sum().reset_index()
fig_faturamento = px.bar(df_faturamento, x='AnoMes', y='Faturamento', 
                         title='Faturamento Mensal', text_auto='.2s',
                         labels={'AnoMes': 'Mês/Ano', 'Faturamento': 'Faturamento'})
fig_faturamento.add_hline(y=350000, line_dash="dash", line_color="red", annotation_text="Meta Mínima (R$ 350k)")
fig_faturamento.add_hline(y=450000, line_dash="dash", line_color="green", annotation_text="Meta Máxima (R$ 450k)")

# KPI: Risco de Ruptura de Estoque
df_estoque = df[df['Alerta_Estoque'] == 'Sim'].groupby('Materia_Prima_Critica').size().reset_index(name='Contagem_Alertas')
fig_estoque = px.bar(df_estoque, x='Materia_Prima_Critica', y='Contagem_Alertas',
                     title='Número de Alertas de Ruptura por Matéria-Prima',
                     color='Contagem_Alertas', color_continuous_scale='Reds',
                     labels={'Materia_Prima_Critica': 'Matéria-Prima Crítica',
                             'Contagem_Alertas': 'Contagem de Alertas'})
