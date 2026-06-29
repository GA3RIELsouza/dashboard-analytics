from dash import dcc
import dash_bootstrap_components as dbc

def get_layout(fig_taxa_defeitos, fig_refugo_retrabalho):
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_taxa_defeitos), width=12)
        ], className="mt-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_refugo_retrabalho), width=12)
        ], className="mt-4"),
    ]
