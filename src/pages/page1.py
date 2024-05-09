import dash
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
import pathlib


dash.register_page(__name__, path='/', name="Übersicht")

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("../assets").resolve()
# print(BASE_PATH)
# print(DATA_PATH)

# Read data
df = pd.read_csv(DATA_PATH.joinpath("df.csv"))

# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# server = app.server

# Components

card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Information", className="card-title"),
            html.P(
                """Der öffentlich verfügbare 
                Datensatz "Belegung neu erstellter Wohnungen" enthält für die Jahre 2011-2019
                Informationen zur Belegung mit Erwachsenen und Kindern.
                Auf Basis dieser Daten liefert die Auswertung für eine "Top-Down-Sicht". Die "Heatmap"
                zeigt die Wohndichte [Definition: (Anzahl Erw. + 0.5 * Anz. Kinder) / Anzahl Zimmer)].
                Ein Wert von 0.00 impliziert, dass es keine Wohnung mit dieser Anzahl Zimmer für den Zeitraum gibt. 
                Bei der Einstellung des Zeitraums steht zB 2014 für den 1.1.2014 um 0.00 Uhr.  """,
                className="card-text"),
        ]
    ),
)

slider = dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Einstellung Zeitraum (für Grafik und Tabelle)", className="card-title"),
                    dcc.RangeSlider(
                    id="zeitraum",
                    marks={i: f"{i}" for i in range(2011, 2021, 1)},
                    min=2011,
                    max=2020,
                    step=1,
                    value=[2011, 2020],
                    included=False,
                    ),
                ]
            ),
        className="mt-4"   
)

info = dbc.Card([card, slider], className="mt-2")

options = [
        {'label': ' Anzahl Wohnungen (welche in die Analyse einfliessen)', 'value': 'Anzahl Wohnungen'},
        {'label': ' Wohnungswechsel (in %)', 'value': 'Wohnungswechsel'},
        {'label': ' Überbelegung (Anz. Personen > Anz. Zimmer + 2)', 'value': 'Überbelegung'},
        {'label': ' Kinder (Durchschnitt pro Wohnung)', 'value': 'Kinder'},
        {'label': ' Anzahl Kinder (absolut)', 'value': 'Anzahl Kinder'},
]

param = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                            html.H5("Auswahl Messgrösse für Tabelle", className="card-title"),
                            dcc.RadioItems(
                            id="auswahl",
                            options = options,
                            value='Anzahl Wohnungen'),
                            ],
                        )
                    ],
                className="mt-2"
)


layout = dbc.Container(
    [
        dbc.Row(
                [
                    dbc.Col(info, width=12, lg=3, className="mt-3 "),
                    dbc.Col(dcc.Graph(id="heatmap"), width=12, lg=9, className="mt-4 border"),               
                ],
                className="ms-1",
                ),
        dbc.Row(
                [
                    dbc.Col(param, width=12, lg=3, className="mt-3"),
                    dbc.Col(html.Div(id="tabelle"), width=12, lg=9, className="mt-4 border"),
                ],
                className="ms-1",
                ),
    ],
    fluid=True,
)

# functions
def filter_df(zeitraum):
    low = zeitraum[0]
    high = zeitraum[1]
    df_filtered = df.query('@low <= Belegungsjahr < @high')
    return df_filtered

@callback(
    Output("heatmap", "figure"),
    Input("zeitraum", "value"),
)
def fig_update(zeitraum):
    df_filtered = filter_df(zeitraum)

    fig = px.density_heatmap(df_filtered, x='Quartiersgruppe Name', y='WGM', z="Dichte",
                             category_orders = {"WGM": ["1", "2", "3", "4", "5", "6+"]},
                             color_continuous_midpoint = 0.9,
                             title = "Wohndichte nach Quartier und Anzahl Zimmer",
                             labels = {"WGM": "Anzahl Zimmer", "Quartiersgruppe Name": ""}, 
                             histfunc="avg", text_auto='.2f', color_continuous_scale='YlGnBu')

    # fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(
    coloraxis_showscale=False,
    yaxis_title=None,
    title=dict(font_size=18, x=0.05, y=0.92),
    margin=dict(l=40, r=10, t=70, b=40),
    )
    # fig.update_xaxes(tickangle=15)
    fig.update_yaxes(title_standoff = 0, ticks="outside", ticklen=0)
    fig.update_xaxes(categoryorder='category ascending')

    return fig

@callback(
    Output("tabelle", "children"),
    Input("zeitraum", "value"),
    Input("auswahl", "value"),
)
def table_update(zeitraum, auswahl):
    # print("huhu3")
    df_filtered = filter_df(zeitraum)
    if auswahl == 'Anzahl Wohnungen':
        print("huhu44")
        df_grouped = df_filtered.groupby(['Quartiersgruppe Name', 'WGM'])['ID'].nunique().reset_index()
        df_table = df_grouped.pivot(index='WGM', columns='Quartiersgruppe Name', values='ID')
        df_table = df_table.reset_index()
        columnDefs=[{"field": i, "maxWidth": 92} for i in df_table.columns[1:]]
        columnDefs = [{"field": "Anzahl Zimmer", "maxWidth": 84}] + columnDefs
        df_table.rename(columns={"WGM": "Anzahl Zimmer"}, inplace=True)        
        tabelle = dag.AgGrid(
            id="table",
            rowData=df_table.to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions = {"suppressFieldDotNotation": True},
            defaultColDef ={"wrapHeaderText": True, "autoHeaderHeight": True},
            columnSize="autoSize"
        )
        return tabelle
    elif auswahl == 'Wohnungswechsel':
        print("huhu11")
        df_grouped = df_filtered.groupby(['Quartiersgruppe Name', 'WGM'])['Wechsel'].mean().reset_index()
        df_table = df_grouped.pivot(index='WGM', columns='Quartiersgruppe Name', values='Wechsel')
        df_table = df_table.reset_index()
        columnDefs=[{"field": i, "valueFormatter": {"function": "params.value == null ? '' :  d3.format(',.1%')(params.value)"}, "maxWidth": 92} for i in df_table.columns[1:]] 
        columnDefs = [{"field": "Anzahl Zimmer", "maxWidth": 84}] + columnDefs
        df_table.rename(columns={"WGM": "Anzahl Zimmer"}, inplace=True)        
        tabelle = dag.AgGrid(
            id="table",
            rowData=df_table.to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions = {"suppressFieldDotNotation": True},
            defaultColDef ={"wrapHeaderText": True, "autoHeaderHeight": True},
            columnSize="autoSize"
        )
        return tabelle
    elif auswahl == 'Überbelegung':
        print("huhu22")
        df_grouped = df_filtered.groupby(['Quartiersgruppe Name', 'WGM'])['Ueberbelegung'].sum().reset_index()
        df_table = df_grouped.pivot(index='WGM', columns='Quartiersgruppe Name', values='Ueberbelegung')
        df_table = df_table.reset_index()
        columnDefs=[{"field": i, "maxWidth": 92} for i in df_table.columns[1:]]
        columnDefs = [{"field": "Anzahl Zimmer", "maxWidth": 84}] + columnDefs
        df_table.rename(columns={"WGM": "Anzahl Zimmer"}, inplace=True)        
        tabelle = dag.AgGrid(
            id="table",
            rowData=df_table.to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions = {"suppressFieldDotNotation": True},
            defaultColDef ={"wrapHeaderText": True, "autoHeaderHeight": True},
            columnSize="autoSize"
        )
        return tabelle
    elif auswahl == 'Kinder':
        print("huhu33")
        df_grouped = df_filtered.groupby(['Quartiersgruppe Name', 'WGM'])['Anz_Kinder'].mean().reset_index()
        df_table = df_grouped.pivot(index='WGM', columns='Quartiersgruppe Name', values='Anz_Kinder')
        df_table = df_table.reset_index()
        columnDefs=[{"field": i, "valueFormatter": {"function": "params.value == null ? '' :  d3.format(',.2')(params.value)"}, "maxWidth": 92} for i in df_table.columns[1:]] 
        columnDefs = [{"field": "Anzahl Zimmer", "maxWidth": 84}] + columnDefs
        df_table.rename(columns={"WGM": "Anzahl Zimmer"}, inplace=True)        
        tabelle = dag.AgGrid(
            id="table",
            rowData=df_table.to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions = {"suppressFieldDotNotation": True},
            defaultColDef ={"wrapHeaderText": True, "autoHeaderHeight": True},
            columnSize="autoSize"
        )        
        return tabelle        
    elif auswahl == 'Anzahl Kinder':
        print("huhu55")
        df_grouped = df_filtered.groupby(['Quartiersgruppe Name', 'WGM'])['Anz_Kinder'].sum().reset_index()
        df_table = df_grouped.pivot(index='WGM', columns='Quartiersgruppe Name', values='Anz_Kinder')
        df_table = df_table.reset_index()
        columnDefs=[{"field": i, "maxWidth": 92} for i in df_table.columns[1:]]
        columnDefs = [{"field": "Anzahl Zimmer", "maxWidth": 84}] + columnDefs
        df_table.rename(columns={"WGM": "Anzahl Zimmer"}, inplace=True)        
        tabelle = dag.AgGrid(
            id="table",
            rowData=df_table.to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions = {"suppressFieldDotNotation": True},
            defaultColDef ={"wrapHeaderText": True, "autoHeaderHeight": True},
            columnSize="autoSize"
        )        
        return tabelle   

