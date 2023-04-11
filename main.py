import tweepy
import datetime
import preprocess as prep
import plotly.express as px
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from dash import html
from dash import dcc
import dash
import pandas as pd

2


app = dash.Dash(__name__, title='Landslides',
                external_stylesheets=[dbc.themes.DARKLY])

print('###### RESTART #######')

# df_landslide = prep.get_df()  # TODO TODO TODO (cf. preprocess.py)
df_landslide = pd.read_csv(
    './data/Global_Landslide_Catalog_Export.csv', parse_dates=['event_date'])
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
                        start_date=df_landslide['event_date'].min().date(),
                        end_date=df_landslide['event_date'].max().date(),
                        min_date_allowed=df_landslide['event_date'].min(
                        ).date(),
                        max_date_allowed=df_landslide['event_date'].max(
                        ).date(),
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
                ),
                html.Div(id='clicked-marker-index', hidden=True)
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

    html.Div(children=[  # Right side
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
            style={'color': 'white', 'text-decoration': 'none',
                   'font-size': '20px', 'padding': '10px'},
        ),

        # html.Img( # Image
        #     src="https://blogs.agu.org/landslideblog/files/2014/06/14_06-kakapo-3.jpg")

    ], style={'padding': 10, 'flex': 1})
], style={'backgroundColor': '#66c572', 'display': 'flex', 'flex-direction': 'row'}
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
    data = df_landslide[df_landslide['event_date'].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date))]

    filtered_df = data[data['landslide_category'] == selected_value]
    filtered_df['fatality_count'] = filtered_df['fatality_count'].fillna(0)
    markers = [
        dl.Marker(
            id={"type": "marker", "index": i},
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


@app.callback(Output("clicked-marker-index", "children"),
              [Input({'type': 'marker', 'index': ALL}, 'n_clicks')],
              [State({'type': 'marker', 'index': ALL}, 'position')])
def marker_click(*args_position_n_clicks):
    args = args_position_n_clicks[0]  # n_clicks arguments
    positions = args_position_n_clicks[1]  # position arguments
    clicked_marker_idx = next((i for i, n in enumerate(args) if n), None)
    if clicked_marker_idx is not None:
        clicked_position = positions[clicked_marker_idx]
        print(f"Clicked marker: position={clicked_position}")
        return clicked_marker_idx

    return dash.no_update


@app.callback(Output('tweet-text', 'value'),
              Input('clicked-marker-index', 'children'))
def update_tweet_text(clicked_marker_idx):
    if clicked_marker_idx is not None:
        clicked_row = df_landslide.iloc[clicked_marker_idx]
        tweet_text = f"{clicked_row['event_title']} at {clicked_row['latitude']}, {clicked_row['longitude']} #landslides #druids #Info-Vis"
        return tweet_text
    else:
        return "[message] #landslides #druids #Info-Vis"


"""
╔════════════════════════╗
║         Execution      ║
╚════════════════════════╝
"""

if __name__ == "__main__":
    app.run_server(debug=True)
    None
