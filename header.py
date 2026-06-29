from dash import html
import dash_bootstrap_components as dbc

# Função auxiliar para criar Cartões KPI
def criar_cartao(titulo, valor, cor):
    return dbc.Card([
        dbc.CardBody([
            html.H5(titulo, className="card-title"),
            html.H3(valor, className=f"text-{cor}")
        ])
    ], className="shadow-sm mb-4")

def get_layout(total_faturamento, total_perda, media_taxa_defeitos, alertas_estoque_total):
    return [
        html.H1("Dashboard de Controle Industrial", className="mt-4 mb-4 text-center"),
        
        # Cartões Superiores
        dbc.Row([
            dbc.Col(criar_cartao("Faturamento Total", f"R$ {total_faturamento:,.2f}", "success"), width=3),
            dbc.Col(criar_cartao("Perda Financeira", f"R$ {total_perda:,.2f}", "danger"), width=3),
            dbc.Col(criar_cartao("Taxa Média Defeitos", f"{media_taxa_defeitos:.2f}%", "warning"), width=3),
            dbc.Col(criar_cartao("Alertas de Estoque", f"{alertas_estoque_total}", "info"), width=3),
        ])
    ]
