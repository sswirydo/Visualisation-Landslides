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
import functools
import dash_mantine_components as dmc
import preprocess

app = dash.Dash(__name__, title='Landslides',
                external_stylesheets=[dbc.themes.DARKLY, './assets/styles.css'])

print('###### RESTART #######')

df_landslide = pd.read_csv('./data/Global_Landslide_Catalog_Export.csv', parse_dates=['event_date'])

title = html.H1(children="⛰️ Landslides 🏞️", className="title")

# Twitter
twitter= html.Div(children=[
    dcc.Input(
        id='tweet-text',
        type='text',
        placeholder='Enter your tweet here',
        value='[message] #landslides #druids #Info-Vis',
        style={'width': '100%', 'zIndex': 10}
    ),
    dcc.Link('Share on Twitter 🐦',
        id='twitter-share-button',
        href='https://youtu.be/dQw4w9WgXcQ',
        target='_blank',
        style={'color': 'white', 'text-decoration': 'none', 'font-size': '20px', 'padding': '10px'},
    ),
])

# Date Picker Range
date_picker_label = dbc.Label("Date Range", className="control-label")
date_picker = dmc.DateRangePicker(
    id='datepickerrange',
    minDate=df_landslide['event_date'].min().date(),
    maxDate=df_landslide['event_date'].max().date(),
    value=[df_landslide['event_date'].min().date(), df_landslide['event_date'].max().date()],
    style={'width': '100%', 'zIndex': 10},
    className='datepicker'
)

date_store = dcc.Store(id="date-range-storage", data={"start_date": None, "end_date": None})
# Landslide Category
landslide_cat_label = dbc.Label("Landslide Category", className="control-label")
landslide_cat = dcc.Dropdown(
    id='category-dropdown',
    options=[{'label': i, 'value': i}
             for i in df_landslide['landslide_category'].dropna().unique()],
    value='rock_fall',
    multi=True,
    placeholder="Select Landslide Categories",
    className="dropdown",
    style={"color": "black", 'width': '100%', 'zIndex': 9},
)

# Landslide Trigger
landslide_trigger_label = dbc.Label("Landslide Triggers", className="control-label")
landslide_trigger = dcc.Dropdown(
    id='trigger-dropdown',
    options=[{'label': i, 'value': i}
             for i in df_landslide['landslide_trigger'].dropna().unique()],
    value='downpour',
    multi=True,
    placeholder="Select Landslide Triggers",
    className="dropdown",
    style={"color": "black", 'width': '100%', 'zIndex': 8},
)
# Landslide Size
landslide_size_label = dbc.Label("Landslide Sizes", className="control-label")
landslide_size = dcc.Dropdown(
    id='size-dropdown',
    options=[{'label': i, 'value': i}
             for i in df_landslide['landslide_size'].dropna().unique()],
    value=None,
    multi=True,
    placeholder="Select Landslide Sizes",
    className="dropdown",
    style={"color": "black", 'width': '100%', 'zIndex': 7},
)


picker = dbc.Card([
    dbc.CardHeader("Data Filters"),
    dbc.CardBody([
        # Date Picker Range
        dbc.Row([date_picker_label]),
        dbc.Row([date_picker, date_store], class_name="mb-3"),
        # Landslide Category
        dbc.Row([landslide_cat_label]),
        dbc.Row([landslide_cat], class_name="mb-3"),
        # Landslide Trigger
        dbc.Row([landslide_trigger_label]),
        dbc.Row([landslide_trigger], class_name="mb-3"),
        # Landslide Size
        dbc.Row([landslide_size_label]),
        dbc.Row([landslide_size], class_name="mb-3"),
    ])
], className="mb-4")

plots = dbc.Col([
    dbc.Row([
        dbc.Col([    
            # Pie chart
            dcc.Loading(     
                id="loading-icon-pie",
                type="circle",
                children=[dcc.Graph(id='pie-chart')],
                style={'textAlign': 'center'}
            )], width={"size": 6}),
        dbc.Col([    
            # Pie chart
            dcc.Loading(
                id="loading-icon-histogram",
                type="circle",
                children=[dcc.Graph(id='histogram')],
                style={'textAlign': 'center'}
            )], width={"size": 6})
    ]),
    
    dbc.Row([
        dbc.Col([    
            # Pie chart
            dcc.Loading(     
                id="loading-icon",
                type="circle",
                children=[dcc.Graph(id='bar-chart')],
                style={'textAlign': 'center'}
                )], width={"size": 6}),
        dbc.Col([    
            # Pie chart
            dcc.Loading(
                id="loading-icon-histogram",
                type="circle",
                children=[dcc.Graph(id='histogram')],
                style={'textAlign': 'center'}
            )], width={"size": 6})
    ])
], width=6, style={'height': '100vh'})


map = html.Div(children=[
    dl.Map([
        dl.TileLayer(),
        dl.MarkerClusterGroup(html.Div(id='placeholder', hidden=True), id='markers'),
        html.Div(id='clicked-marker-index', hidden=True),
        html.Div(id='prev-marker-clicks', hidden=True, children=[0]*len(df_landslide))
    ],
        style={'width': '100%', 'height': '350px', 'margin': "auto", "display": "block", "zIndex": 0},
        center=[51.5074, -0.1278],
        bounds=[[-45, -90], [45, 90]],
        maxBounds=[[-90, -180], [90, 180]],
        maxBoundsViscosity=1.0,
        zoom=10,
        id='map'
    )
])

landslide_info = html.Div(children=[
    html.Div([ # Not necessary as populated in callback, but makes it easier to visualize
        html.H1(id='landslide-title'),
        html.P(id='landslide-description'),
        html.Img(id='landslide-image')
    ], id='landslide-info', style={'background-color': 'white', 'padding': '10px', 'border-radius': '5px', 'margin': '10px'})
])

container = dbc.Container([
    dbc.Row([
        dbc.Col([title, picker, map, twitter], width=3),
        dbc.Col([landslide_info], width=3),
        plots,
    ])
],  fluid=True, style={
    'background-image': 'url(https://images.unsplash.com/photo-1501785888041-af3ef285b470?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80)',
    'background-repeat': 'no-repeat',
    'background-position': 'center',
    'background-size': 'cover',
    'width': '100%',
    'max-height' : '100vh'
})


app.layout = container
        
            
# TODO MAKE THEM ALL USE THE global_filtered_df VARIABLE
global_filtered_df = None

# Date range storage callback
@app.callback(
    dash.dependencies.Output("date-range-storage", "data"),
    dash.dependencies.Input("datepickerrange", "value"),
)
def update_date_range_storage(date_value):
    return {"start_date": date_value[0], "end_date": date_value[1]}

# Map marker callback
@functools.lru_cache(maxsize=32)  # Adjust maxsize according to your needs
@app.callback(Output('markers', 'children'),
              Input('category-dropdown', 'value'),
              Input('datepickerrange', 'value'),
              Input('trigger-dropdown', 'value'),
              Input('size-dropdown', 'value'))
def update_figure(selected_value, date_value, selected_triggers, selected_sizes):    
    global global_filtered_df
    
    data = df_landslide[df_landslide['event_date'].between(pd.Timestamp(date_value[0]), pd.Timestamp(date_value[1]))]
    
    if selected_value:  # Only filter by category if selected_value is not None
        if isinstance(selected_value, str):
            selected_value = [selected_value]
        filtered_df = data[data['landslide_category'].isin(selected_value)]
    else:
        filtered_df = data

    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(selected_triggers)]
    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(selected_sizes)]
    global_filtered_df = filtered_df
    global_filtered_df['fatality_count'] = global_filtered_df['fatality_count'].fillna(0)

    markers = [
        dl.Marker(
            id={"type": "marker", "index": i},
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(row['event_title']),
                dl.Popup(
                    html.Div([
                        html.H3(row['event_title'], style={"color": "darkblue", "overflow-wrap": "break-word"}),
                        html.P(f"Date: {row['event_date'].strftime('%Y-%m-%d')}"),
                        html.P(f"Trigger: {row['landslide_trigger']}"),
                        html.P(f"Size: {row['landslide_size']}"),
                        html.P(f"Fatalities: {int(row['fatality_count'])}"),
                        html.P(f"Source: {row['source_name']}"),
                        html.A("Source URL", href=row['source_link'], target="_blank"),
                    ], style={'width': '300px', 'white-space': 'normal'})),
            ]
        )
        for i, row in global_filtered_df.iterrows()
    ]
    return markers

# Marker click callback
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
        print(f"Clicked marker: position={clicked_position}, index={clicked_marker_idx}")
        return clicked_marker_idx, n_clicks
    return dash.no_update, prev_clicks

# Add a callback to update the tweet text
@app.callback(Output('tweet-text', 'value'),
              Input('clicked-marker-index', 'children'))
def update_tweet_text(clicked_marker_idx):
    if clicked_marker_idx is None or global_filtered_df is None or global_filtered_df.empty:
        raise PreventUpdate
    row = global_filtered_df.iloc[clicked_marker_idx]
    event_title = row['event_title']
    source_name = row['source_name']
    event_date = row['event_date'].strftime("%Y-%m-%d")
    tweet = f"{event_title} on {event_date} by {source_name}. #landslides #druids #Info-Vis"
    return tweet


# FIXME: Puts a default value before the user clicks on a marker
# Callback updates the landslide description
@ app.callback(Output('landslide-info', 'children'),
               Input('clicked-marker-index', 'children'))
def update_landslide_details(clicked_marker_idx):
    if clicked_marker_idx is None:
        raise PreventUpdate
    row = global_filtered_df.iloc[clicked_marker_idx]
    return [
        html.H1(row['event_title'], style={"color": "darkblue"}),
        html.P(row["event_description"], style={"color": "blueviolet"}),
        html.Img(src=row['photo_link'], style={'width': '100%'})
    ]

# Callback updates the twitter share button
@ app.callback(Output('twitter-share-button', 'href'), Input('tweet-text', 'value'))
def update_twitter_share_button(tweet_text):
    tweet_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(tweet_text)
    return tweet_url

# Callback updates the bar chart
@functools.lru_cache(maxsize=32)  # Adjust maxsize according to your needs
@ app.callback(Output('bar-chart', 'figure'),
               Input('category-dropdown', 'value'),
               Input('datepickerrange', 'value'),
               Input('trigger-dropdown', 'value'),
               Input('size-dropdown', 'value'))
def update_bar_chart(selected_value, date_value, selected_triggers, selected_sizes):
    data = df_landslide[df_landslide['event_date'].between(pd.Timestamp(date_value[0]), pd.Timestamp(date_value[1]))]
    
    if selected_value:
        if isinstance(selected_value, str):
            selected_value = [selected_value]
        filtered_df = data[data['landslide_category'].isin(selected_value)]
    else:
        filtered_df = data
    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(selected_triggers)]
    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(selected_sizes)]
    if filtered_df.empty:
        return go.Figure().update_layout(
            title=f"No data for selected filters",
            font=dict(color="#CFCFCF"),
            plot_bgcolor="#3E3E3E",
            paper_bgcolor="#3E3E3E",
        )
    filtered_df['year'] = filtered_df['event_date'].dt.year
    yearly_counts = filtered_df.groupby('year').size().reset_index(name='count')
    fig = go.Figure(data=[go.Bar(x=yearly_counts['year'], y=yearly_counts['count'])])
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
@functools.lru_cache(maxsize=32)  # Adjust maxsize according to your needs
@ app.callback(Output('pie-chart', 'figure'),
               Input('category-dropdown', 'value'),
               Input('datepickerrange', 'value'),
               Input('trigger-dropdown', 'value'),
               Input('size-dropdown', 'value'))
def update_pie_chart(selected_value, date_value, selected_triggers, selected_sizes):
    data = df_landslide[df_landslide['event_date'].between(pd.Timestamp(date_value[0]), pd.Timestamp(date_value[1]))]
    
    if selected_value:
        if isinstance(selected_value, str):
            selected_value = [selected_value]
        filtered_df = data[data['landslide_category'].isin(selected_value)]
    else:
        filtered_df = data

    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(selected_triggers)]
    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(selected_sizes)]
    pie_data = filtered_df['landslide_trigger'].value_counts()
    fig = px.pie(pie_data, values=pie_data.values,names=pie_data.index, title='Landslide Triggers')
    fig.update_layout(font=dict(color="#CFCFCF"),plot_bgcolor="#3E3E3E", paper_bgcolor="#3E3E3E")
    return fig

# Histogram callback
@functools.lru_cache(maxsize=32)  # Adjust maxsize according to your needs
@ app.callback(Output('histogram', 'figure'),
               Input('category-dropdown', 'value'),
               Input('datepickerrange', 'value'),
               Input('trigger-dropdown', 'value'),
               Input('size-dropdown', 'value'))
def update_histogram(selected_value, date_value, selected_triggers, selected_sizes):
    data = df_landslide[df_landslide['event_date'].between(pd.Timestamp(date_value[0]), pd.Timestamp(date_value[1]))]
    if isinstance(selected_value, str):
        selected_value = [selected_value]
    filtered_df = data[data['landslide_category'].isin(selected_value)]

    # Filter by selected triggers
    if selected_triggers:
        filtered_df = filtered_df[filtered_df['landslide_trigger'].isin(selected_triggers)]
    # Filter by selected sizes
    if selected_sizes:
        filtered_df = filtered_df[filtered_df['landslide_size'].isin(selected_sizes)]
    fig = px.histogram(filtered_df, x='landslide_trigger', y='event_date', nbins=10, title='Histogram of Landslide Triggers by Year')
    fig.update_layout(font=dict(color="#CFCFCF"), plot_bgcolor="#3E3E3E", paper_bgcolor="#3E3E3E")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)