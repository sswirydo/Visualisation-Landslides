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
import urllib.parse
import plotly.graph_objects as go


app = dash.Dash(__name__, title='Landslides',
                external_stylesheets=[dbc.themes.DARKLY])

print('###### RESTART #######')

df_landslide = pd.read_csv(
    './data/Global_Landslide_Catalog_Export.csv', parse_dates=['event_date'])

app.layout = html.Div([
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
                html.Div(id='clicked-marker-index', hidden=True),
                html.Div(id='prev-marker-clicks', hidden=True,
                         children=[0]*len(df_landslide))
            ],
            style={'width': '100%', 'height': '50vh',
                   'margin': "auto", "display": "block"},
            center=[51.5074, -0.1278],
            bounds=[[-90, -180], [90, 180]],
            maxBounds=[[-90, -180], [90, 180]],
            maxBoundsViscosity=1.0,
            zoom=10,
            id='map'
        ),
    ], style={'padding': 10, 'flex': 1}),

    html.Div(children=[  # Right side
        dcc.Input(
            id='tweet-text',
            type='text',
            placeholder='Enter your tweet here',
            value='[message] #landslides #druids #Info-Vis',
            style={'width': '100%', 'zIndex': 10}

        ),

        dcc.Link(
            'Share on Twitter 🐦',
            id='twitter-share-button',
            href='https://youtu.be/dQw4w9WgXcQ',
            target='_blank',
            style={'color': 'white', 'text-decoration': 'none',
                   'font-size': '20px', 'padding': '10px'},
        ),

        dcc.Graph(id='bar-chart'),
    ], style={'padding': 10, 'flex': 1})
], style={'backgroundColor': '#66c572', 'display': 'flex', 'flex-direction': 'row'}
)

global_filtered_df = None


@app.callback(Output('markers', 'children'),
              Input('dropdown', 'value'),
              Input('datepickerrange', 'start_date'),
              Input('datepickerrange', 'end_date'))
def update_figure(selected_value, start_date, end_date):
    global global_filtered_df
    data = df_landslide[df_landslide['event_date'].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date))]
    global_filtered_df = data[data['landslide_category'] == selected_value]
    global_filtered_df['fatality_count'] = global_filtered_df['fatality_count'].fillna(
        0)
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
        for i, row in global_filtered_df.iterrows()
    ]
    print(markers[0])
    return markers


@app.callback(Output('output-container-date-picker-range', 'children'),
              Input('datepickerrange', 'start_date'),
              Input('datepickerrange', 'end_date'))
def update_output_datepicker(start_date, end_date):
    return str(start_date)


@app.callback([Output("clicked-marker-index", "children"),
               Output('prev-marker-clicks', 'children')],
              [Input({'type': 'marker', 'index': ALL}, 'n_clicks')],
              [State({'type': 'marker', 'index': ALL}, 'position'),
               State('prev-marker-clicks', 'children')])
def marker_click(n_clicks, positions, prev_clicks):
    clicked_marker_idx = None

    for i, (prev, curr) in enumerate(zip(prev_clicks, n_clicks)):
        if prev != curr:
            clicked_marker_idx = i
            break

    if clicked_marker_idx is not None:
        clicked_position = positions[clicked_marker_idx]
        print(
            f"Clicked marker: position={clicked_position}, index={clicked_marker_idx}")
        return clicked_marker_idx, n_clicks
    return dash.no_update, prev_clicks


@app.callback(Output('tweet-text', 'value'),
              Input('clicked-marker-index', 'children'))
def update_tweet_text(clicked_marker_idx):
    if clicked_marker_idx is None:
        raise PreventUpdate

    row = global_filtered_df.iloc[clicked_marker_idx]
    event_title = row['event_title']
    source_name = row['source_name']
    event_date = row['event_date'].strftime("%Y-%m-%d")

    tweet = f"{event_title} on {event_date} by {source_name}. #landslides #druids #Info-Vis"
    return tweet


@app.callback(Output('twitter-share-button', 'href'),
              Input('tweet-text', 'value'))
def update_twitter_share_button(tweet_text):
    tweet_url = "https://twitter.com/intent/tweet?text=" + \
        urllib.parse.quote(tweet_text)
    return tweet_url

# Add a callback to update the bar chart


@app.callback(Output('bar-chart', 'figure'),
              Input('dropdown', 'value'),
              Input('datepickerrange', 'start_date'),
              Input('datepickerrange', 'end_date'))
def update_bar_chart(selected_value, start_date, end_date):
    data = df_landslide[df_landslide['event_date'].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date))]
    filtered_df = data[data['landslide_category'] == selected_value]
    filtered_df['year'] = filtered_df['event_date'].dt.year
    yearly_counts = filtered_df.groupby(
        'year').size().reset_index(name='count')

    fig = go.Figure(data=[
        go.Bar(x=yearly_counts['year'], y=yearly_counts['count'])
    ])
    fig.update_layout(
        title=f"Landslides per Year for {selected_value}",
        xaxis_title="Year",
        yaxis_title="Number of Landslides",
        font=dict(color="#CFCFCF"),
        plot_bgcolor="#3E3E3E",
        paper_bgcolor="#3E3E3E",
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
