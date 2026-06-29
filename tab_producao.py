from dash import dcc
import dash_bootstrap_components as dbc


def get_layout():
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(id="graph-producao-meta"), width=12)
        ], className="mt-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="graph-atingiu-meta"), width=12)
        ], className="mt-4"),
    ]
