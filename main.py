import datetime
import urllib.parse

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

import preprocess


app = dash.Dash(__name__, title='Landslides',
                external_stylesheets=[dbc.themes.DARKLY, './assets/styles.css'])


print('###### RESTART #######')

df_landslide = pd.read_csv(
    './data/Global_Landslide_Catalog_Export.csv', parse_dates=['event_date'])

# df_landslide = preprocess.get_df()

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div(children=[
                html.H1(    # Title
                    children="⛰️ Landslides 🏞️",
                    className="title"
                ),
            ]),
            
            dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
            dcc.Tab(label='Map', value='tab-1-example-graph'),
            dcc.Tab(label='Dashboard', value='tab-2-example-graph'),
            ]),
            
            html.Div(id='tabs-content-example-graph'),

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
            
        ]),
    ]),
], fluid=True, style={
    'background-image': 'url(https://images.unsplash.com/photo-1501785888041-af3ef285b470?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80)',
    'background-repeat': 'no-repeat',
    'background-position': 'center',
    'background-size': 'cover',
    'height': '100%',
    'width': '100%'
})


# TODO MAKE THEM ALL USE THE global_filtered_df VARIABLE

global_filtered_df = None

@app.callback(Output('tabs-content-example-graph', 'children'),
            Input('tabs-example-graph', 'value'))

def render_content(tab):
    if tab == 'tab-1-example-graph':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Data Filters"),
                        dbc.CardBody([
                            # Date Picker
                            dbc.Row([
                                dbc.Label("Date Range", className="control-label"),
                            ]),
                            dbc.Row([
                                dcc.DatePickerRange(
                                    id='datepickerrange',
                                    start_date=df_landslide['event_date'].min().date(),
                                    end_date=df_landslide['event_date'].max().date(),
                                    min_date_allowed=df_landslide['event_date'].min(
                                    ).date(),
                                    max_date_allowed=df_landslide['event_date'].max(
                                    ).date(),
                                    display_format='MM/DD/YYYY',
                                    style={'width': '100%', 'zIndex': 10},
                                    className='datepicker'
                                ),
                                dcc.Store(id="date-range-storage", data={"start_date": None, "end_date": None}),
                            ], className="mb-3"),
                            # Landslide Category Dropdown
                            dbc.Row([
                                dbc.Label("Landslide Category",
                                        className="control-label"),
                            ]),
                            dbc.Row([
                                dcc.Dropdown(id='dropdown', 
                                            style={"color": "black", 'width': '100%'}, 
                                            options=[{'label': i, 'value': i} for i in df_landslide['landslide_category'].dropna().unique()], 
                                            value='rock_fall')
                            ], className="mb-3"),
                            # Landslide Trigger Dropdown
                            dbc.Row([
                                dbc.Label("Landslide Triggers",
                                        className="control-label"),
                            ]),
                            dbc.Row([
                                dcc.Dropdown(
                                    id='trigger-dropdown',
                                    options=[{'label': i, 'value': i}
                                            for i in df_landslide['landslide_trigger'].dropna().unique()],
                                    value=None,
                                    multi=True,
                                    placeholder="Select Landslide Triggers",
                                    className="dropdown",
                                    style={"color": "black", 'width': '100%'},
                                ),
                            ], className="mb-3"),
                            # Landslide Size Dropdown
                            dbc.Row([
                                dbc.Label("Landslide Sizes",
                                        className="control-label"),
                            ]),
                            dbc.Row([
                                dcc.Dropdown(
                                    id='size-dropdown',
                                    options=[{'label': i, 'value': i}
                                            for i in df_landslide['landslide_size'].dropna().unique()],
                                    value=None,
                                    multi=True,
                                    placeholder="Select Landslide Sizes",
                                    className="dropdown",
                                    style={"color": "black", 'width': '100%'},
                                ),
                            ], className="mb-3"),
                        ]),
                    ], className="mb-4"),

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
                        bounds=[[-45, -90], [45, 90]],
                        maxBounds=[[-90, -180], [90, 180]],
                        maxBoundsViscosity=1.0,
                        zoom=10,
                        id='map'
                    )
                ], width = 5),

                
                dbc.Col([
                    html.P("Sale pute"),
                    html.Img(src="https://images.unsplash.com/photo-1583665354191-634609954d54?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=764&q=80"),
                ], width=5)
            ])
        ])
    
    elif tab == 'tab-2-example-graph':
        return html.Div([
            dbc.Col([  # Plots (middle)
                dbc.Col([  # Bar chart
                    dcc.Loading(
                        id="loading-icon",
                        type="circle",
                        children=[dcc.Graph(id='bar-chart')],
                        style={'textAlign': 'center'}
                    ),
                ]),

                dbc.Col([  # Pie chart
                    dcc.Loading(
                        id="loading-icon-pie",
                        type="circle",
                        children=[dcc.Graph(id='pie-chart')],
                        style={'textAlign': 'center'}
                    ),
                ]),

                dbc.Col([  # Histogram
                    dcc.Loading(
                        id="loading-icon-histogram",
                        type="circle",
                        children=[dcc.Graph(id='histogram')],
                        style={'textAlign': 'center'},
                    ),
                ])
            ])
        ])
    
@app.callback(
    dash.dependencies.Output("date-range-storage", "data"),
    dash.dependencies.Input("datepickerrange", "start_date"),
    dash.dependencies.Input("datepickerrange", "end_date"),
)
def update_date_range_storage(start_date, end_date):
    return {"start_date": start_date, "end_date": end_date}

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
    return markers


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
