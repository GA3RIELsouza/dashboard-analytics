from dash import html, dcc
import dash_bootstrap_components as dbc


# Função auxiliar para criar Cartões KPI
def criar_cartao(titulo, valor, cor, valor_id):
    return dbc.Card([
        dbc.CardBody([
            html.H5(titulo, className="card-title"),
            html.H3(valor, id=valor_id, className=f"text-{cor}")
        ])
    ], className="shadow-sm mb-4")


def get_layout(total_faturamento, total_perda, media_taxa_defeitos,
               alertas_estoque_total, setores, tipos_defeito):
    return [
        html.H1("Dashboard de Controle Industrial", className="mt-4 mb-4 text-center"),

        # Cartões Superiores (KPIs reativos aos filtros)
        dbc.Row([
            dbc.Col(criar_cartao("Faturamento Total", f"R$ {total_faturamento:,.2f}",
                                 "success", "kpi-faturamento"), width=3),
            dbc.Col(criar_cartao("Perda Financeira", f"R$ {total_perda:,.2f}",
                                 "danger", "kpi-perda"), width=3),
            dbc.Col(criar_cartao("Taxa Média Defeitos", f"{media_taxa_defeitos:.2f}%",
                                 "warning", "kpi-taxa"), width=3),
            dbc.Col(criar_cartao("Alertas de Estoque", f"{alertas_estoque_total}",
                                 "info", "kpi-estoque"), width=3),
        ]),

        # Painel de Filtros Globais
        dbc.Card(dbc.CardBody(dbc.Row([
            dbc.Col([
                html.Label("Setor", className="fw-bold"),
                dcc.Dropdown(
                    id="filtro-setor",
                    options=[{"label": s, "value": s} for s in setores],
                    multi=True, placeholder="Todos os setores"),
            ], width=6),
            dbc.Col([
                html.Label("Tipo de Defeito Predominante", className="fw-bold"),
                dcc.Dropdown(
                    id="filtro-tipo-defeito",
                    options=[{"label": t, "value": t} for t in tipos_defeito],
                    multi=True, placeholder="Todos os tipos de defeito"),
            ], width=6),
        ])), className="shadow-sm mb-4"),
    ]
