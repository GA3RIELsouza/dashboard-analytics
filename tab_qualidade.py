from dash import dcc
import dash_bootstrap_components as dbc


def get_layout():
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(id="graph-taxa-defeitos"), width=12)
        ], className="mt-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="graph-refugo-retrabalho"), width=12)
        ], className="mt-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="graph-classificacao-qualidade"), width=12)
        ], className="mt-4"),
    ]
