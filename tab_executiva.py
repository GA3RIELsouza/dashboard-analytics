from dash import dcc
import dash_bootstrap_components as dbc

def get_layout(fig_faturamento, fig_perda_financeira):
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_faturamento), width=12)
        ], className="mt-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_perda_financeira), width=12)
        ], className="mt-4"),
    ]
