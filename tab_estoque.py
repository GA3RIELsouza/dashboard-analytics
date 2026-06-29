from dash import dcc
import dash_bootstrap_components as dbc


def get_layout():
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(id="graph-estoque"), width=12)
        ], className="mt-4"),
    ]
