2
import pandas as pd

import dash
from dash import dcc
from dash import html
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go
import plotly.express as px
import preprocess as prep

from datetime import datetime

import tweepy 

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
    # dcc.Interval( # remove auto refresh component
    #     id='interval-component',
    #     interval=0,
    #     n_intervals=0
    # ),

    html.Div(children=[
        html.H1(    # Title
            children="⛰️ Landslides 🏞️",
            style={"fontSize": "48px", "color": "#CFCFCF",
                   "textAlign": "center"},
        ),
        html.P(     # Subtitle
            children=[
                "Druids be like. ",
                html.A("source", href="https://www.youtube.com/watch?v=1S6QTHwYTLI"),
                "."
            ],
            style={"fontSize": "16px", "color": "white", "text-align": "center"},),
        html.Div([  # Date picker
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
                                 {'label': i, 'value': i} for i in df_landslide['landslide_category'].dropna().unique()], value='rock_fall')
                ], width=3)
            ], style={'align': "center"})
        ]),
        dl.Map(     # Map
            children=[
                dl.TileLayer(),
                dl.MarkerClusterGroup(
                    html.Div(id='placeholder', hidden=True),
                    id='markers'
                )
            ],
            style={'width': '100%', 'height': '50vh',
                   'margin': "auto", "display": "block"},
            center=[51.5074, -0.1278],

            # Permet de limiter la carte infinie à juste 1x le monde
            bounds=[[-90, -180], [90, 180]],
            maxBounds=[[-90, -180], [90, 180]],
            maxBoundsViscosity=1.0,

            zoom=10,
            id='map'
        ),
        # dcc.Graph(id='map', style={'height': '90vh'}, figure=dict(layout=dict(
        #    autosize=True)), config=dict(responsive=True, displayModeBar=False))

    ], style={'padding': 10, 'flex': 1}),

    html.Div(children=[ # Right side
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

        dcc.Input(
            id='tweet-text',
            type='text',
            placeholder='Enter your tweet here',
            value='[message] #landslides #druids #Info-Vis',
            style={'width': '100%', 'zIndex': 10}
        ),

        # Define the layout for the Twitter share button
        dcc.Link(
            'Share on Twitter 🐦',
            id='twitter-share-button',
            href='https://youtu.be/dQw4w9WgXcQ',
            target='_blank',
            style={'color': 'white', 'text-decoration': 'none', 'font-size': '20px', 'padding': '10px'},
        ),

        # html.Img( # Image
        #     src="https://blogs.agu.org/landslideblog/files/2014/06/14_06-kakapo-3.jpg")

    ], style={'padding': 10, 'flex': 1})
], style={'backgroundColor':'#66c572','display': 'flex', 'flex-direction': 'row'}
)


"""
╔══════════════════════╗
║         Others       ║
╚══════════════════════╝
"""


@app.callback(Output('markers', 'children'),
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
            id=f"marker-{i}",
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(
                    html.Div([
                        html.H3(row['event_title'], style={
                                "color": "darkblue", "overflow-wrap": "break-word"}),
                        html.P(row['event_description'],),
                        html.P(row['source_name']),
                        html.Img(src=row['photo_link'], style={
                            "width": "300px", "height": "auto"}),
                    ], style={'width': '300px', 'white-space': 'normal'})),

                dl.Popup(
                    html.Div([
                        html.H3(row['event_title'], style={
                                "color": "darkblue", "overflow-wrap": "break-word"}),
                        html.P(row['event_description'],),
                        html.P(row['source_name']),
                        html.Img(src=row['photo_link'], style={
                            "width": "300px", "height": "auto"}),
                    ], style={'width': '300px', 'white-space': 'normal'})),
            ]
        )
        for i, row in filtered_df.iterrows()
    ]
    print(markers[0])
    return markers


@ app.callback(Output('output-container-date-picker-range', 'children'),
               Input('datepickerrange', 'start_date'),
               Input('datepickerrange', 'end_date'))
def update_output_datepicker(start_date, end_date):
    return str(start_date)


@ app.callback(Output("placeholder", "children"),
               [Input({'type': 'marker', 'index': ALL}, 'n_clicks')])
def marker_click(args):
    if not any(args):
        print('no args')
        return []
    value = dash.callback_context.triggered[0]['value']
    marker_id = json.loads(
        dash.callback_context.triggered[0]['prop_id'].split(".")[0])["index"]
    print(marker_id)
    return []


"""
╔════════════════════════╗
║         Execution      ║
╚════════════════════════╝
"""

if __name__ == "__main__":
    app.run_server(debug=True)
    None
