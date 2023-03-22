import dash
import pandas as pd
import geopandas as gpd
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import preprocess as prep
import dash_leaflet as dl

from shapely.geometry import Point
from datetime import datetime

app = dash.Dash(__name__, title='Landslides',
                external_stylesheets=[dbc.themes.DARKLY])

print('###### RESTART #######')

# df_landslide = prep.get_df()  # TODO TODO TODO (cf. preprocess.py)
df_landslide = pd.read_csv('./data/Global_Landslide_Catalog_Export.csv')
# df_landslide["event_date"] = pd.to_datetime(df_landslide["event_date"])


"""
╔═════════════════════════╗
║         Dashboard       ║
╚═════════════════════════╝
"""

app.layout = html.Div([

    html.Div(children=[
        html.H1(
            children="⛰️ Landslides 🏞️",
            style={"fontSize": "48px", "color": "#CFCFCF",
                   "textAlign": "center"},
        ),
        html.P(
            children=[
                "Druids be like. ",
                html.A("source", href="https://www.youtube.com/watch?v=1S6QTHwYTLI"),
                "."
            ],
            style={"fontSize": "16px", "color": "white", "text-align": "center"},),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.DatePickerRange(
                        id='datepickerrange',
                        start_date=datetime.strptime(
                            df_landslide['event_date'].min(), '%m/%d/%Y %I:%M:%S %p').date(),
                        end_date=datetime.strptime(
                            df_landslide['event_date'].max(), '%m/%d/%Y %I:%M:%S %p').date(),
                        min_date_allowed=datetime.strptime(
                            df_landslide['event_date'].min(), '%m/%d/%Y %I:%M:%S %p').date(),
                        max_date_allowed=datetime.strptime(
                            df_landslide['event_date'].max(), '%m/%d/%Y %I:%M:%S %p').date(),
                        display_format='MM/DD/YYYY',
                        style={'width': '100%', 'zIndex': 10}
                    ),
                    html.P(id='output-container-date-picker-range'),
                ], width=5,
                ),
                dbc.Col([
                    dcc.Dropdown(id='dropdown', style={"color": "black", 'width': '100%'}, options=[
                                 {'label': i, 'value': i} for i in df_landslide['landslide_category'].dropna().unique()], value='landslide')
                ], width=3)
            ], style={'align': "center"})
        ]),
        dl.Map(
            [
                dl.TileLayer(),
                dl.MarkerClusterGroup(
                    id='map'
                )
            ],
            style={'width': '100%', 'height': '50vh',
                   'margin': "auto", "display": "block"},
            center=[51.5074, -0.1278],
            zoom=10,
        ),
        # dcc.Graph(id='map', style={'height': '90vh'}, figure=dict(layout=dict(
        #    autosize=True)), config=dict(responsive=True, displayModeBar=False))

    ], style={'padding': 10, 'flex': 1}),

    html.Div(children=[
        # html.Label('Checkboxes'),
        # dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
        #               ['Montréal', 'San Francisco']
        # ),

        # html.Br(),
        # html.Label('Text Input'),
        # dcc.Input(value='MTL', type='text'),

        # html.Br(),
        # html.Label('Slider'),
        # dcc.Slider(
        #     min=datetime.strptime(df_landslide['event_date'].min(),
        #     max=datetime.strptime(df_landslide['event_date'].max(),
        #     #marks={i: f'Label {i}' if i == 1 else str(i) for i in range(1, 6)},
        #     #value=5,
        # ),
        html.Img(
            src="https://blogs.agu.org/landslideblog/files/2014/06/14_06-kakapo-3.jpg")
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'}
)


"""
╔══════════════════════╗
║         Others       ║
╚══════════════════════╝
"""


@app.callback(Output('map', 'children'),
              Input('dropdown', 'value'),
              Input('datepickerrange', 'start_date'),
              Input('datepickerrange', 'end_date'))
def update_figure(selected_value, start_date, end_date):
    start_date = datetime.strptime(
        start_date, '%Y-%m-%d')  # first transform to date
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    # then transform it to string again
    start_date = start_date.strftime('%m/%d/%Y %I:%M:%S %p')
    end_date = end_date.strftime('%m/%d/%Y %I:%M:%S %p')
    data = df_landslide[df_landslide['event_date'].between(
        start_date, end_date)]
    filtered_df = data[data['landslide_category'] == selected_value]
    filtered_df['fatality_count'] = filtered_df['fatality_count'].fillna(0)
    markers = [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            children=dl.Tooltip(row['event_id'])
        )
        for i, row in filtered_df.iterrows()
    ]
    return markers


@app.callback(Output('output-container-date-picker-range', 'children'),
              Input('datepickerrange', 'start_date'),
              Input('datepickerrange', 'end_date'))
def update_output_datepicker(start_date, end_date):
    return str(start_date)


"""
╔════════════════════════╗
║         Execution      ║
╚════════════════════════╝
"""

if __name__ == "__main__":
    app.run_server(debug=True)
    None
