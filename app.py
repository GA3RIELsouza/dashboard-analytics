import dash
from dash import Input, Output
import dash_bootstrap_components as dbc

import dados
import tab_executiva
import tab_qualidade
import tab_producao
import tab_estoque
import header

# 3. Estruturação do Dashboard Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# KPIs iniciais (sem filtro)
_fat, _perda, _taxa, _alertas = dados.calcular_kpis(dados.df)

# Layout Principal
app.layout = dbc.Container([
    *header.get_layout(
        _fat, _perda, _taxa, _alertas,
        dados.get_setores(), dados.get_tipos_defeito()
    ),

    # Abas
    dbc.Tabs([
        dbc.Tab(label="Visão Executiva", tab_id="tab-1",
                children=tab_executiva.get_layout()),
        dbc.Tab(label="Produção", tab_id="tab-2",
                children=tab_producao.get_layout()),
        dbc.Tab(label="Qualidade", tab_id="tab-3",
                children=tab_qualidade.get_layout()),
        dbc.Tab(label="Estoque", tab_id="tab-4",
                children=tab_estoque.get_layout()),
    ], active_tab="tab-1")
], fluid=True)


# Callback: filtros -> KPIs + todos os gráficos
@app.callback(
    Output("kpi-faturamento", "children"),
    Output("kpi-perda", "children"),
    Output("kpi-taxa", "children"),
    Output("kpi-estoque", "children"),
    Output("graph-faturamento", "figure"),
    Output("graph-perda-financeira", "figure"),
    Output("graph-taxa-defeitos", "figure"),
    Output("graph-refugo-retrabalho", "figure"),
    Output("graph-classificacao-qualidade", "figure"),
    Output("graph-producao-meta", "figure"),
    Output("graph-atingiu-meta", "figure"),
    Output("graph-estoque", "figure"),
    Input("filtro-setor", "value"),
    Input("filtro-tipo-defeito", "value"),
)
def atualizar_dashboard(setores, tipos_defeito):
    dff = dados.filtrar(setores, tipos_defeito)
    total_faturamento, total_perda, media_taxa, alertas = dados.calcular_kpis(dff)

    return (
        f"R$ {total_faturamento:,.2f}",
        f"R$ {total_perda:,.2f}",
        f"{media_taxa:.2f}%",
        f"{alertas}",
        dados.fig_faturamento(dff),
        dados.fig_perda_financeira(dff),
        dados.fig_taxa_defeitos(dff),
        dados.fig_refugo_retrabalho(dff),
        dados.fig_classificacao_qualidade(dff),
        dados.fig_producao_meta(dff),
        dados.fig_atingiu_meta(dff),
        dados.fig_estoque(dff),
    )


if __name__ == '__main__':
    app.run(debug=True)
