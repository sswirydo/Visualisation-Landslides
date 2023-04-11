import datetime
import urllib.parse

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate


app = dash.Dash(__name__, title='Landslides',
                external_stylesheets=[dbc.themes.DARKLY])

print('###### RESTART #######')

df_landslide = pd.read_csv(
    './data/Global_Landslide_Catalog_Export.csv', parse_dates=['event_date'])

app.layout = dbc.Container([
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
    ]),
    dbc.Row([
        dbc.Col([  # Data selection (left)
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
                ], width=12,
                ),
                dbc.Col([
                    dcc.Dropdown(id='dropdown', style={"color": "black", 'width': '100%'}, options=[
                                 {'label': i, 'value': i} for i in df_landslide['landslide_category'].dropna().unique()], value='rock_fall')
                ], width=12)
            ]),
            # Landslide trigger selector
            dbc.Col([
                dcc.Dropdown(id='trigger-dropdown',
                             style={"color": "black", 'width': '100%'},
                    options=[{'label': i, 'value': i}
                                 for i in df_landslide['landslide_trigger'].dropna().unique()],
                             value=None,
                             multi=True,
                             placeholder="Select Landslide Triggers")
            ], width=12),

            # Landslide size selector
            dbc.Col([
                dcc.Dropdown(id='size-dropdown',
                             style={"color": "black", 'width': '100%'},
                    options=[{'label': i, 'value': i}
                                 for i in df_landslide['landslide_size'].dropna().unique()],
                             value=None,
                             multi=True,
                             placeholder="Select Landslide Sizes")
            ], width=12),

        ], width=3),
        dbc.Col([  # Plots (middle)
            dcc.Loading(     # Bar chart
                id="loading-icon",
                type="circle",
                children=[dcc.Graph(id='bar-chart')],
                style={'textAlign': 'center'}
            ),            dcc.Loading(     # Pie chart
                id="loading-icon-pie",
                type="circle",
                children=[dcc.Graph(id='pie-chart')],
                style={'textAlign': 'center'}
            ),
            dcc.Loading(     # Histogram
                id="loading-icon-histogram",
                type="circle",
                children=[dcc.Graph(id='histogram')],
                style={'textAlign': 'center'}
            ),
        ], width=6),
        dbc.Col([  # Map (right)
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
        ], width=3),
        dbc.Col([
            html.Div(children=[  # Tweet input and share button
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
            ]),
        ], width=4),
    ]),
], fluid=True, style={'backgroundColor': '#66c572'})


global_filtered_df = None


@ app.callback(Output('markers', 'children'),
               Input('dropdown', 'value'),
               Input('datepickerrange', 'start_date'),
               Input('datepickerrange', 'end_date'),
               Input('trigger-dropdown', 'value'),
               Input('size-dropdown', 'value'))
def update_figure(selected_value, start_date, end_date, selected_triggers, selected_sizes):
    global global_filtered_df
    data = df_landslide[df_landslide['event_date'].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date))]
    filtered_df = data[data['landslide_category'] == selected_value]

    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(
            selected_triggers)]

    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(
            selected_sizes)]

    global_filtered_df = filtered_df
    global_filtered_df['fatality_count'] = global_filtered_df['fatality_count'].fillna(
        0)
    markers = [
        dl.Marker(
            id={"type": "marker", "index": i},
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(row['event_title']),
                dl.Popup(
                    html.Div([
                        html.H3(row['event_title'], style={
                            "color": "darkblue", "overflow-wrap": "break-word"}),
                        html.P(
                            f"Date: {row['event_date'].strftime('%Y-%m-%d')}"),
                        html.P(f"Trigger: {row['landslide_trigger']}"),
                        html.P(f"Size: {row['landslide_size']}"),
                        html.P(f"Fatalities: {int(row['fatality_count'])}"),
                        html.P(f"Source: {row['source_name']}"),
                        html.A("Source URL",
                               href=row['source_link'], target="_blank"),
                    ], style={'width': '300px', 'white-space': 'normal'})),
            ]
        )
        for i, row in global_filtered_df.iterrows()
    ]

    print(markers[0])
    return markers


@ app.callback(Output('output-container-date-picker-range', 'children'),
               Input('datepickerrange', 'start_date'),
               Input('datepickerrange', 'end_date'))
def update_output_datepicker(start_date, end_date):
    return str(start_date)


@ app.callback([Output("clicked-marker-index", "children"),
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


@ app.callback(Output('tweet-text', 'value'),
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


@ app.callback(Output('twitter-share-button', 'href'),
               Input('tweet-text', 'value'))
def update_twitter_share_button(tweet_text):
    tweet_url = "https://twitter.com/intent/tweet?text=" + \
        urllib.parse.quote(tweet_text)
    return tweet_url

# Add a callback to update the bar chart


@ app.callback(Output('bar-chart', 'figure'),
               Input('dropdown', 'value'),
               Input('datepickerrange', 'start_date'),
               Input('datepickerrange', 'end_date'),
               Input('trigger-dropdown', 'value'),
               Input('size-dropdown', 'value'))
def update_bar_chart(selected_value, start_date, end_date, selected_triggers, selected_sizes):
    data = df_landslide[df_landslide['event_date'].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date))]
    filtered_df = data[data['landslide_category'] == selected_value]

    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(
            selected_triggers)]

    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(
            selected_sizes)]

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


# Pie chart callback
@ app.callback(Output('pie-chart', 'figure'),
               Input('dropdown', 'value'),
               Input('datepickerrange', 'start_date'),
               Input('datepickerrange', 'end_date'),
               Input('trigger-dropdown', 'value'),
               Input('size-dropdown', 'value'))
def update_pie_chart(selected_value, start_date, end_date, selected_triggers, selected_sizes):
    data = df_landslide[df_landslide['event_date'].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date))]
    filtered_df = data[data['landslide_category'] == selected_value]

    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(
            selected_triggers)]

    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(
            selected_sizes)]

    pie_data = filtered_df['landslide_trigger'].value_counts()
    fig = px.pie(pie_data, values=pie_data.values,
                 names=pie_data.index, title='Landslide Triggers')
    fig.update_layout(font=dict(color="#CFCFCF"),
                      plot_bgcolor="#3E3E3E", paper_bgcolor="#3E3E3E")
    return fig

# Histogram callback


@ app.callback(Output('histogram', 'figure'),
               Input('dropdown', 'value'),
               Input('datepickerrange', 'start_date'),
               Input('datepickerrange', 'end_date'),
               Input('trigger-dropdown', 'value'),
               Input('size-dropdown', 'value'))
def update_histogram(selected_value, start_date, end_date, selected_triggers, selected_sizes):
    data = df_landslide[df_landslide['event_date'].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date))]
    filtered_df = data[data['landslide_category'] == selected_value]

    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(
            selected_triggers)]

    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(
            selected_sizes)]

    fig = px.histogram(filtered_df, x='landslide_trigger', y='event_date', nbins=10,
                       title='Histogram of Landslide Triggers by Year')
    fig.update_layout(font=dict(color="#CFCFCF"),
                      plot_bgcolor="#3E3E3E", paper_bgcolor="#3E3E3E")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
