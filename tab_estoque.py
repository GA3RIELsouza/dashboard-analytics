from dash import dcc
import dash_bootstrap_components as dbc

def get_layout(fig_estoque):
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_estoque), width=12)
        ], className="mt-4"),
    ]
