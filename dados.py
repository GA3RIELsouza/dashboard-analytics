import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Carregamento e Preparação dos Dados
# O arquivo é UTF-8 com BOM (utf-8-sig trata o BOM no início e os acentos).
df = pd.read_csv('dados.csv', sep=';', encoding='utf-8-sig')
df['Data'] = pd.to_datetime(df['Data'])

COLUNAS_NUMERICAS = [
    'Faturamento', 'Perda_Financeira', 'Taxa_Defeitos_%',
    'Quantidade_Defeitos', 'Quantidade_Vendida',
    'Quantidade_Retrabalho', 'Quantidade_Segunda_Qualidade',
    'Quantidade_Produzida', 'Meta_Producao',
]
for col in COLUNAS_NUMERICAS:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

SEM_DEFEITO = 'Sem defeito relevante'

# Cores fixas para a classificação (consertável x perdido)
CORES_CLASSIFICACAO = {
    'Retrabalho': '#2C9F45',            # consertável (verde)
    'Segunda Qualidade': '#E74C3C',     # perdido / rebaixado (vermelho)
    'Sem ocorrência relevante': '#95A5A6',
}


# ---------------------------------------------------------------------------
# Opções de filtro
# ---------------------------------------------------------------------------
def get_setores():
    return sorted(df['Setor'].dropna().unique())


def get_tipos_defeito():
    tipos = df['Tipo_Defeito_Predominante'].dropna().unique()
    return sorted(t for t in tipos if t != SEM_DEFEITO)


def filtrar(setores=None, tipos_defeito=None):
    """Aplica os filtros globais (Setor e Tipo de Defeito) ao DataFrame."""
    dff = df
    if setores:
        dff = dff[dff['Setor'].isin(setores)]
    if tipos_defeito:
        dff = dff[dff['Tipo_Defeito_Predominante'].isin(tipos_defeito)]
    return dff


# ---------------------------------------------------------------------------
# Cartões de KPI (Visão Geral)
# ---------------------------------------------------------------------------
def calcular_kpis(dff):
    total_faturamento = dff['Faturamento'].sum()
    total_perda = dff['Perda_Financeira'].sum()
    media_taxa_defeitos = dff['Taxa_Defeitos_%'].mean() if len(dff) else 0
    alertas_estoque_total = dff[dff['Alerta_Estoque'] == 'Sim'].shape[0]
    return total_faturamento, total_perda, media_taxa_defeitos, alertas_estoque_total


# ---------------------------------------------------------------------------
# 2. Construtores de Gráficos (Plotly) — recebem o DataFrame já filtrado
# ---------------------------------------------------------------------------

# KPI: Faturamento vs. Meta Mensal
def fig_faturamento(dff):
    d = dff.groupby('AnoMes')['Faturamento'].sum().reset_index()
    fig = px.bar(d, x='AnoMes', y='Faturamento',
                 title='Faturamento Mensal', text_auto='.2s',
                 labels={'AnoMes': 'Mês/Ano', 'Faturamento': 'Faturamento'})
    fig.add_hline(y=350000, line_dash="dash", line_color="red",
                  annotation_text="Meta Mínima (R$ 350k)")
    fig.add_hline(y=450000, line_dash="dash", line_color="green",
                  annotation_text="Meta Máxima (R$ 450k)")
    return fig


# KPI: Perda Financeira por Má Qualidade (Pareto — prioriza onde está a maior perda)
def fig_perda_financeira(dff):
    d = dff.groupby('Tipo_Defeito_Predominante')['Perda_Financeira'].sum().reset_index()
    d = d[d['Perda_Financeira'] > 0].sort_values('Perda_Financeira', ascending=False)

    if d.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Perda Financeira por Tipo de Defeito (Pareto)',
            xaxis={'visible': False}, yaxis={'visible': False},
            annotations=[{'text': 'Sem perda financeira no período/filtro selecionado',
                          'xref': 'paper', 'yref': 'paper',
                          'x': 0.5, 'y': 0.5, 'showarrow': False,
                          'font': {'size': 14}}])
        return fig

    total = d['Perda_Financeira'].sum()
    d['Percentual_Acumulado'] = d['Perda_Financeira'].cumsum() / total * 100

    def _reais(v):
        return 'R$ ' + f'{v:,.2f}'.replace(',', '@').replace('.', ',').replace('@', '.')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d['Tipo_Defeito_Predominante'],
        y=d['Perda_Financeira'],
        name='Perda Financeira',
        marker_color='#E74C3C',
        text=[_reais(v) for v in d['Perda_Financeira']],
        textposition='outside',
        cliponaxis=False,
        hovertemplate='<b>%{x}</b><br>Perda: %{text}<extra></extra>',
        yaxis='y'))
    fig.add_trace(go.Scatter(
        x=d['Tipo_Defeito_Predominante'],
        y=d['Percentual_Acumulado'],
        name='% Acumulado',
        mode='lines+markers+text',
        marker_color='#2C3E50',
        line={'color': '#2C3E50'},
        text=[f'{v:.0f}%' for v in d['Percentual_Acumulado']],
        textposition='top center',
        hovertemplate='<b>%{x}</b><br>%% Acumulado: %{y:.1f}%<extra></extra>',
        yaxis='y2'))
    fig.add_hline(y=80, line_dash='dash', line_color='#7F8C8D',
                  annotation_text='80%', annotation_position='right',
                  yref='y2')
    fig.update_layout(
        title='Perda Financeira por Tipo de Defeito (Pareto - regra 80/20)',
        xaxis={'title': 'Tipo de Defeito Predominante'},
        yaxis={'title': 'Perda Financeira (R$)',
               'range': [0, d['Perda_Financeira'].max() * 1.18]},
        yaxis2={'title': '% Acumulado', 'overlaying': 'y', 'side': 'right',
                'range': [0, 105], 'ticksuffix': '%'},
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02,
                'xanchor': 'right', 'x': 1},
        bargap=0.3)
    return fig


# KPI: Taxa de Defeitos Diária
def fig_taxa_defeitos(dff):
    d = dff.groupby('Data')['Taxa_Defeitos_%'].mean().reset_index()
    fig = px.line(d, x='Data', y='Taxa_Defeitos_%',
                  title='Taxa Média de Defeitos Diária (%)',
                  markers=True, labels={'Taxa_Defeitos_%': 'Taxa de Defeitos (%)'})
    fig.add_hline(y=5, line_dash="dash", line_color="red",
                  annotation_text="Limite Superior (5%)")
    fig.add_hline(y=3, line_dash="dash", line_color="orange",
                  annotation_text="Margem Alerta (3%)")
    return fig


# KPI: Refugo vs. Retrabalho (Segunda Qualidade)
def fig_refugo_retrabalho(dff):
    d = (dff.groupby('Tipo_Defeito_Predominante')[['Quantidade_Retrabalho',
                                                   'Quantidade_Segunda_Qualidade']]
            .sum().reset_index())
    d = d[d['Tipo_Defeito_Predominante'] != SEM_DEFEITO]
    fig = px.bar(d, x='Tipo_Defeito_Predominante',
                 y=['Quantidade_Retrabalho', 'Quantidade_Segunda_Qualidade'],
                 title='Refugo (2ª Qualidade) vs Retrabalho por Tipo de Defeito',
                 barmode='group',
                 labels={'value': 'Quantidade', 'variable': 'Tipo de Ação',
                         'Tipo_Defeito_Predominante': 'Tipo de Defeito Predominante'})
    fig.for_each_trace(lambda t: t.update(
        name={'Quantidade_Retrabalho': 'Quantidade de Retrabalho',
              'Quantidade_Segunda_Qualidade': 'Quantidade de 2ª Qualidade'}.get(t.name, t.name)))
    return fig


# KPI: Classificação da Qualidade por Setor (consertável x perdido)
def fig_classificacao_qualidade(dff):
    # Barras empilhadas 100% (proporção) por Setor usando QUANTIDADE DE PEÇAS reais:
    # Quantidade_Retrabalho (consertável) vs Quantidade_Segunda_Qualidade (perdido).
    # A proporção responde "consertável x perdido"; para não esconder o VOLUME
    # (limitação clássica do 100% empilhado) o total de peças vai no rótulo do eixo Y.
    cols = ['Quantidade_Retrabalho', 'Quantidade_Segunda_Qualidade']
    titulo = ('Destino das Peças com Defeito por Setor — '
              'Consertável (Retrabalho) x Perdido (2ª Qualidade)')

    if dff is None or dff.empty:
        fig = px.bar(title=titulo + ' — sem dados')
        fig.add_annotation(text='Sem dados para o filtro selecionado',
                           showarrow=False, font=dict(size=14))
        return fig

    d = dff.groupby('Setor')[cols].sum().reset_index()
    d['Total'] = d['Quantidade_Retrabalho'] + d['Quantidade_Segunda_Qualidade']
    d = d[d['Total'] > 0].copy()
    if d.empty:
        fig = px.bar(title=titulo + ' — sem dados')
        fig.add_annotation(text='Sem peças de retrabalho ou 2ª qualidade no período',
                           showarrow=False, font=dict(size=14))
        return fig

    # Ordena para deixar EXPLÍCITO quem mais PERDE definitivamente (topo do gráfico).
    d['pct_perdido'] = d['Quantidade_Segunda_Qualidade'] / d['Total'] * 100
    d = d.sort_values('pct_perdido', ascending=True)

    # Rótulo do eixo Y com o volume total -> recupera a magnitude que o 100% achata.
    d['SetorLabel'] = (d['Setor'] + '  ('
                       + d['Total'].astype(int).map('{:,}'.format).str.replace(',', '.')
                       + ' pç)')
    ordem_setor = d['SetorLabel'].tolist()

    long = d.melt(id_vars=['SetorLabel', 'Total'], value_vars=cols,
                  var_name='Destino', value_name='Pecas')
    long['Destino'] = long['Destino'].map(
        {'Quantidade_Retrabalho': 'Retrabalho',
         'Quantidade_Segunda_Qualidade': 'Segunda Qualidade'})
    long['Pct'] = long['Pecas'] / long['Total'] * 100
    long['rotulo'] = (long['Pct'].round(1).astype(str) + '%<br>'
                      + long['Pecas'].astype(int).astype(str) + ' pç')

    fig = px.bar(
        long, x='Pct', y='SetorLabel', color='Destino', orientation='h',
        barmode='stack',
        color_discrete_map={'Retrabalho': CORES_CLASSIFICACAO['Retrabalho'],
                            'Segunda Qualidade': CORES_CLASSIFICACAO['Segunda Qualidade']},
        category_orders={'Destino': ['Retrabalho', 'Segunda Qualidade'],
                         'SetorLabel': ordem_setor},
        custom_data=['Destino', 'Pecas'],
        text='rotulo',
        title=titulo,
        labels={'Pct': 'Proporção de peças (%)', 'SetorLabel': 'Setor',
                'Destino': 'Destino da peça'})

    fig.update_traces(
        texttemplate='%{text}', textposition='inside', insidetextanchor='middle',
        hovertemplate='<b>%{y}</b><br>%{customdata[0]}: %{customdata[1]:,} peças'
                      ' (%{x:.1f}%)<extra></extra>')
    fig.update_layout(
        xaxis=dict(ticksuffix='%', range=[0, 100]),
        legend_title_text='Destino da peça',
        bargap=0.35)
    return fig


# Produção: Quantidade Produzida vs Meta por Setor
def fig_producao_meta(dff):
    d = (dff.groupby('Setor')
            .agg(Produzido=('Quantidade_Produzida', 'sum'),
                 Meta=('Meta_Producao', 'sum'))
            .reset_index())
    fig = px.bar(d, x='Setor', y=['Produzido', 'Meta'], barmode='group',
                 title='Produção Realizada vs Meta por Setor', text_auto='.2s',
                 labels={'value': 'Quantidade', 'variable': 'Indicador'})
    fig.for_each_trace(lambda t: t.update(
        name={'Produzido': 'Quantidade Produzida',
              'Meta': 'Meta de Produção'}.get(t.name, t.name)))
    return fig


# Produção: Atingimento de Meta por Setor (% das vezes — empilhado 100%)
def fig_atingiu_meta(dff):
    ordem_cat = ['Sim', 'Não']
    cores = {'Sim': '#2C9F45', 'Não': '#E74C3C'}
    if dff is None or dff.empty or 'Atingiu_Meta' not in dff.columns:
        fig = px.bar(title='Atingimento de Meta de Produção por Setor (% das vezes)')
        fig.add_annotation(text='Sem dados para o filtro selecionado',
                           showarrow=False, font=dict(size=14))
        return fig

    cont = (dff.groupby(['Setor', 'Atingiu_Meta']).size()
            .reset_index(name='Quantidade'))
    total = cont.groupby('Setor')['Quantidade'].transform('sum')
    cont['Percentual'] = cont['Quantidade'] / total * 100

    pct_sim = (cont[cont['Atingiu_Meta'] == 'Sim']
               .set_index('Setor')['Percentual'])
    ordem_setores = (pct_sim.reindex(cont['Setor'].unique(), fill_value=0)
                     .sort_values(ascending=False).index.tolist())

    fig = px.bar(
        cont, x='Setor', y='Percentual', color='Atingiu_Meta',
        barmode='stack',
        category_orders={'Setor': ordem_setores, 'Atingiu_Meta': ordem_cat},
        color_discrete_map=cores,
        title='Atingimento de Meta de Produção por Setor (% das vezes)',
        labels={'Percentual': '% dos Registros',
                'Atingiu_Meta': 'Atingiu a Meta?',
                'Setor': 'Setor'},
        custom_data=['Quantidade'],
        text='Percentual',
    )
    fig.update_traces(
        texttemplate='%{text:.0f}%', textposition='inside',
        insidetextanchor='middle',
        hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%'
                      '<br>Registros: %{customdata[0]}<extra></extra>')
    fig.update_yaxes(range=[0, 100], ticksuffix='%')
    fig.update_layout(yaxis_title='% dos Registros',
                      legend_title_text='Atingiu a Meta?',
                      uniformtext_minsize=10, uniformtext_mode='hide')
    return fig


# KPI: Risco de Ruptura de Estoque (Estoque Atual vs Mínimo por matéria-prima)
def fig_estoque(dff):
    cols = ['Materia_Prima_Critica', 'Data', 'Estoque_Atual', 'Estoque_Minimo']

    def _vazio():
        fig = go.Figure()
        fig.update_layout(
            title='Risco de Ruptura: Estoque Atual vs. Mínimo (sem dados)',
            xaxis={'visible': False}, yaxis={'visible': False},
            annotations=[{'text': 'Sem dados para o filtro selecionado',
                          'xref': 'paper', 'yref': 'paper',
                          'showarrow': False, 'font': {'size': 14}}])
        return fig

    if dff is None or dff.empty or any(c not in dff.columns for c in cols):
        return _vazio()

    d = dff[cols].copy()
    d['Estoque_Atual'] = pd.to_numeric(d['Estoque_Atual'], errors='coerce')
    d['Estoque_Minimo'] = pd.to_numeric(d['Estoque_Minimo'], errors='coerce')
    d['Data'] = pd.to_datetime(d['Data'], errors='coerce')
    d = d.dropna(subset=['Estoque_Atual', 'Estoque_Minimo', 'Data'])
    if d.empty:
        return _vazio()

    # O Estoque_Minimo é fixo por material. O Estoque_Atual NÃO é um nível único
    # de inventário: há 8-9 leituras por dia (uma por registro/setor) com grande
    # dispersão intra-dia. Para o RISCO ATUAL de ruptura, usamos a fotografia do
    # dia mais recente de cada material e tomamos a PIOR leitura (mínimo) desse
    # dia — abordagem conservadora que NÃO esconde uma quebra do mínimo (a média
    # poderia mascarar leituras abaixo do mínimo). Mínimo é fixo, então 'max' o
    # recupera sem distorção.
    ult_data = d.groupby('Materia_Prima_Critica')['Data'].transform('max')
    recente = d[d['Data'] == ult_data]
    g = (recente.groupby('Materia_Prima_Critica')
         .agg(Estoque_Atual=('Estoque_Atual', 'min'),
              Estoque_Minimo=('Estoque_Minimo', 'max'),
              Data=('Data', 'max'))
         .reset_index())
    g['Estoque_Atual'] = g['Estoque_Atual'].round(0)
    g['Em_Risco'] = g['Estoque_Atual'] <= g['Estoque_Minimo']
    # Folga relativa ao mínimo: ordena os mais críticos primeiro. Guard p/ min=0.
    minimo_seguro = g['Estoque_Minimo'].replace(0, pd.NA)
    g['Folga_%'] = ((g['Estoque_Atual'] - g['Estoque_Minimo']) / minimo_seguro * 100)
    g['Folga_%'] = g['Folga_%'].fillna(0)
    g = g.sort_values('Folga_%').reset_index(drop=True)

    COR_RISCO = '#E74C3C'    # vermelho: pior leitura recente <= mínimo
    COR_OK = '#2C9F45'       # verde: acima do mínimo
    COR_MINIMO = '#34495E'   # cinza-azulado: referência do mínimo

    cores_atual = [COR_RISCO if r else COR_OK for r in g['Em_Risco']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=g['Materia_Prima_Critica'], y=g['Estoque_Atual'],
        name='Estoque Atual (pior leitura recente)', marker_color=cores_atual,
        text=g['Estoque_Atual'], texttemplate='%{text:.0f}', textposition='outside',
        customdata=g[['Estoque_Minimo', 'Folga_%']].values,
        hovertemplate=('<b>%{x}</b><br>Estoque Atual (pior leitura): %{y:.0f}<br>'
                       'Estoque Mínimo: %{customdata[0]:.0f}<br>'
                       'Folga sobre o mínimo: %{customdata[1]:.0f}%<extra></extra>')))
    fig.add_trace(go.Bar(
        x=g['Materia_Prima_Critica'], y=g['Estoque_Minimo'],
        name='Estoque Mínimo', marker_color=COR_MINIMO, opacity=0.55,
        text=g['Estoque_Minimo'], texttemplate='%{text:.0f}', textposition='outside',
        hovertemplate='<b>%{x}</b><br>Estoque Mínimo: %{y:.0f}<extra></extra>'))

    n_risco = int(g['Em_Risco'].sum())
    fig.update_layout(
        barmode='group',
        title=('Risco de Ruptura: Estoque Atual vs. Mínimo por Matéria-Prima '
               f'(pior leitura do dia mais recente · {n_risco} em risco)'),
        xaxis_title='Matéria-Prima Crítica',
        yaxis_title='Quantidade em Estoque',
        legend_title='Indicador')
    return fig
