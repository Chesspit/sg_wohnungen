import dash 
from dash import Dash, dcc, html, callback
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions=True, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


navbar = dbc.NavbarSimple(
    # children=[
    #     dbc.NavItem(dbc.NavLink("Übersicht   ", href="/", style={'font-weight': 'bold', 'color': 'black'})),
    #     dbc.NavItem(dbc.NavLink("Details   ", href="/page2", style={'font-weight': 'bold', 'color': 'black'})),
    # ],
    brand="Belegung neuer Wohnungen in St. Gallen",
    brand_style={'font-size': '20px', 'font-weight': 'bold', 'color': 'black'},
    brand_href="#",
    # color="info",
    color="#F8F8F8" ,
    dark=True,
)

app.layout = html.Div(
    [
        navbar,
        # html.Hr(),
        dash.page_container,
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
