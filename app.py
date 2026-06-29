import dash
import dash_bootstrap_components as dbc

import dados
import tab_executiva
import tab_qualidade
import tab_estoque
import header

# 3. Estruturação do Dashboard Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Layout Principal
app.layout = dbc.Container([
    *header.get_layout(
        dados.total_faturamento, 
        dados.total_perda, 
        dados.media_taxa_defeitos, 
        dados.alertas_estoque_total
    ),
    
    # Abas
    dbc.Tabs([
        # Aba 1: Visão Executiva e Financeira
        dbc.Tab(
            label="Visão Executiva", 
            tab_id="tab-1", 
            children=tab_executiva.get_layout(dados.fig_faturamento, dados.fig_perda_financeira)
        ),
        
        # Aba 2: Qualidade e Desperdício
        dbc.Tab(
            label="Qualidade", 
            tab_id="tab-2", 
            children=tab_qualidade.get_layout(dados.fig_taxa_defeitos, dados.fig_refugo_retrabalho)
        ),
        
        # Aba 3: Controle de Estoque
        dbc.Tab(
            label="Estoque e Produção", 
            tab_id="tab-3", 
            children=tab_estoque.get_layout(dados.fig_estoque)
        )
    ], active_tab="tab-1")
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)
