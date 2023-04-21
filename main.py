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

app = dash.Dash(
    __name__,
    title="Landslides",
    external_stylesheets=[dbc.themes.DARKLY, "assets/styles.css"],
)

print("###### RESTART #######")

df_landslide = pd.read_csv("./data/Global_Landslide_Catalog_Export.csv", parse_dates=["event_date"])

# Preprocess dataframes
df_landslide = preprocess.preprocess(df_landslide)

title = html.H1(children="⛰️ Landslides 🏞️", className="title")

# Get a list of unique landslide categories
categories = df_landslide["landslide_category"].unique()

# Create a tab for each category
tabs = [dcc.Tab(label=category, value=category) for category in categories]

# Create the tabs component
tablist = dcc.Tabs(
    id="category-tabs",
    value=categories[0],
    children=tabs,
)

# Twitter
twitter = html.Div(
    children=[
        dcc.Input(
            id="tweet-text",
            type="text",
            placeholder="Enter your tweet here",
            value="[message] #landslides #Info-Vis",
            style={"width": "100%", "zIndex": 10},
        ),
        dcc.Link(
            "Share on Twitter 🐦",
            id="twitter-share-button",
            href="https://youtu.be/dQw4w9WgXcQ",
            target="_blank",
            style={
                "color": "white",
                "text-decoration": "none",
                "font-size": "20px",
                "padding": "10px",
            },
        ),
    ]
)

# TikTok
tiktok = html.Div(
    children=[
        dcc.Link(
            "Share on TikTok 🎵",
            id="tiktok-share-button",
            href="https://www.tiktok.com/",
            target="_blank",
            style={
                "color": "white",
                "text-decoration": "none",
                "font-size": "20px",
                "padding": "10px",
            },
        ),
    ]
)

# # Date Picker Range
# date_picker_label = dbc.Label("Date Range", className="control-label")
# # doc: https://www.dash-mantine-components.com/components/datepicker
# date_picker = dmc.DateRangePicker(
#     id="datepickerrange",
#     minDate=df_landslide["event_date"].min().date(),
#     maxDate=df_landslide["event_date"].max().date(),
#     value=[
#         pd.to_datetime("2016-01-01").date(),
#         pd.to_datetime("2016-12-31").date(),
#     ],
#     style={"width": "100%", "zIndex": 10},
#     inputFormat="YYYY",
#     className="datepicker",
#     #allowLevelChange = False,
#     #initialLevel = 'year',
# )

# Extract years from the dataset
min_year = df_landslide["event_date"].min().year
max_year = df_landslide["event_date"].max().year
years = list(range(min_year, max_year + 1))

# Date Picker
date_picker_label = dbc.Label("Select Year", className="control-label")
date_picker = dcc.Dropdown(
    id="datepickerrange",
    options=[{"label": year, "value": year} for year in years],
    value=2017,
    multi=False,
    placeholder="Select a Year",
    className="dropdown",
    style={"color": "black", "width": "100%", "zIndex": 10},
)


date_store = dcc.Store(
    id="date-range-storage", data={"start_date": None, "end_date": None}
)

# Landslide Trigger
landslide_trigger_label = dbc.Label("Landslide Triggers", className="control-label")
landslide_trigger = dcc.Dropdown(
    id="trigger-dropdown",
    options=[
        {"label": i, "value": i}
        for i in df_landslide["landslide_trigger"].dropna().unique()
    ],
    value='downpour', #TODO change plus tard
    multi=True,
    placeholder="Select Landslide Triggers",
    className="dropdown",
    style={"color": "black", "width": "100%", "zIndex": 8},
)
# Landslide Size
landslide_size_label = dbc.Label("Landslide Sizes", className="control-label")
landslide_size = dcc.Dropdown(
    id="size-dropdown",
    options=[
        {"label": i, "value": i}
        for i in df_landslide["landslide_size"].dropna().unique()
    ],
    value=None,
    multi=True,
    placeholder="Select Landslide Sizes",
    className="dropdown",
    style={"color": "black", "width": "100%", "zIndex": 7},
)

debounce_interval = dcc.Interval(
    id="debounce-interval",
    interval=500,  # in milliseconds (500 ms = 0.5 seconds)
    n_intervals=0,
)

picker = dbc.Card(
    [
        dbc.CardHeader("Data Filters"),
        dbc.CardBody(
            [
                # Date Picker Range
                dbc.Row([date_picker_label]),
                dbc.Row([date_picker, date_store], class_name="mb-3"),
                # Landslide Trigger
                dbc.Row([landslide_trigger_label]),
                dbc.Row([landslide_trigger], class_name="mb-3"),
                # Landslide Size
                dbc.Row([landslide_size_label]),
                dbc.Row([landslide_size], class_name="mb-3"),
                debounce_interval,
            ]
        ),
    ],
    className="mb-4",
)

plots = dbc.Col(
    [
        dbc.Col(
            [
                # Landslide triggers pie chart
                dcc.Loading(
                    id="loading-icon-pie",
                    type="circle",
                    children=[dcc.Graph(id="pie-chart", style={ 'border-top-left-radius':'15px', 'border-top-right-radius':'15px', 'background-color':'#3E3E3E'})],
                    style={"textAlign": "center"},
                )
            ],
        ),
        dbc.Col(
            [
                # Histogram of landslide triggers by year
                dcc.Loading(
                    id="loading-icon-histogram",
                    type="circle",
                    children=[dcc.Graph(id="histogram", style={'border-bottom-left-radius':'15px', 'border-bottom-right-radius':'15px', 'background-color':'#3E3E3E'})],
                    style={"textAlign": "center"},
                )
            ],
        ),

    ],
    style={"height": "100vh", "padding-top": "5%",  "border-radius": "15px"},
)


map = html.Div(
    children=[
        dl.Map(
            [
                dl.TileLayer(url = "https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=ecc291031e064ce28fe61975dd9c1631"),
                dl.MarkerClusterGroup(
                    html.Div(id="placeholder", hidden=True),
                    id="markers",
                    options={"chunkedLoading": True, "chunkInterval": 200},
                ),
                html.Div(id="clicked-marker-index", hidden=True),
                html.Div(
                    id="prev-marker-clicks",
                    hidden=True,
                    children=[0] * len(df_landslide),
                ),
            ],
            style={
                "width": "100%",
                "height": "500px",
                "margin": "auto",
                "display": "block",
                "zIndex": 0,
            },
            center=[51.5074, -0.1278],
            bounds=[[-45, -90], [45, 90]],
            maxBounds=[[-90, -180], [90, 180]],
            maxBoundsViscosity=1.0,
            zoom=10,
            id="map",
        ),
        dcc.Loading(
            id="loading",
            type="circle",
            children=[html.Div(id="loading-placeholder", hidden=True)]
        ),
    ],
    style={"position": "relative", "transform": "scale(1)"},
)


landslide_info = html.Div(
    children=[
        html.Div(
            [  # Returned in a callback below

            ],
            id="landslide-info",
            style={
                "background-color": "white",
                "padding": "10px",
                "border-radius": "5px",
                "margin": "10px",
            },
        )
    ]
)

tab_style = {
    "backgroundColor": "black",
    'margin-left': '4px',
    'margin-right': '4px',
    'padding-top': '4px',    
    'padding-bottom': '4px',    
    'fontWeight': 'bold',
    'font-size': '18px',
    'border': 'none'
}
tab_selected_style = {
    'margin-left': '4px',
    'margin-right': '4px',
    'padding-top': '4px',    
    'padding-bottom': '4px',    
    'fontWeight': 'bold',
    'font-size': '18px',
    'border': 'none !important'

}

map_tabs = dbc.Row(
    dbc.Col(
        [
            map,
            dcc.Tabs(
                id="category-tabs",
                value="rock_fall",
                parent_className="custom-tabs",
                vertical=True,
                className="custom-tabs-container",
                style={
                    'display': 'inline-block',
                    'border': 'none !important'

                },
                children=[
                    dcc.Tab(
                        label="Land Slide",
                        value="landslide",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style
                    ),
                    dcc.Tab(
                        label="Mud Slide",
                        value="mudslide",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style
                    ),
                    dcc.Tab(
                        label="River Bank Collapse",
                        value="riverbank_collapse",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Lahar",
                        value="lahar",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Debris Flow",
                        value="debris_flow",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Rock Fall",
                        value="rock_fall",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Complex",
                        value="complex",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Snow avalanche",
                        value="snow_avalanche",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Creep",
                        value="creep",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style
                    ),
                    dcc.Tab(
                        label="Earth flow",
                        value="earth_flow",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Translational Slide",
                        value="translational_slide",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                    dcc.Tab(
                        label="Topple",
                        value="topple",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style

                    ),
                ]
            ),
        ],
        width=12,
    ),
    justify="center",
    align="center",
    style={"height": "80vh"},
)



container = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([title, picker, landslide_info,  
                    html.Div(
                    [
                        twitter,
                        tiktok,
                    ]
                )], width=3),
                dbc.Col([map_tabs], width=6),
                dbc.Col([plots], width=3),
            ]
        )
    ],
    fluid=True,
    style={
        "background-image": "url(https://images.unsplash.com/photo-1502239608882-93b729c6af43?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80)",
        "background-repeat": "no-repeat",
        "background-position": "center",
        "background-size": "cover",
        "width": "100%",
        "max-height": "100vh",
    },
)






app.layout = container


# TODO MAKE THEM ALL USE THE global_filtered_df VARIABLE
global_filtered_df = None


# Update the global_filtered_df
def update_global_filtered_df(
    selected_tab, date_value, selected_triggers, selected_sizes
):
    global global_filtered_df
    selected_year = int(date_value)  # Convert the selected year to integer
    data = df_landslide[df_landslide["event_date"].dt.year == selected_year]

    if selected_tab != "all":
        data = data[data["landslide_category"] == selected_tab]
    if selected_triggers:
        if isinstance(selected_triggers, str):
            selected_triggers = [selected_triggers]
        data = data[data["landslide_trigger"].isin(selected_triggers)]
    if selected_sizes:
        if isinstance(selected_sizes, str):
            selected_sizes = [selected_sizes]
        data = data[data["landslide_size"].isin(selected_sizes)]
    global_filtered_df = data
    global_filtered_df["fatality_count"] = global_filtered_df["fatality_count"].fillna(
        0
    )
    global_filtered_df["injury_count"] = global_filtered_df["injury_count"].fillna(
        0
    )

# Map marker callback

ZOOM_THRESHOLD = 10  # Adjust this value #TODO

@functools.lru_cache(maxsize=32)  # Adjust maxsize according to your needs
@app.callback(
    Output("markers", "children"),
    Input("datepickerrange", "value"),
    Input("trigger-dropdown", "value"),
    Input("size-dropdown", "value"),
    Input("category-tabs", "value"),
    Input("map", "zoom"),  # Add the zoom level as an input
)
def update_figure(
    date_value, selected_triggers, selected_sizes, selected_tab, current_zoom
):
    update_global_filtered_df(
        selected_tab, date_value, selected_triggers, selected_sizes
    )
    print(global_filtered_df.shape[0])
    if current_zoom <= ZOOM_THRESHOLD:
        markers = [
            dl.Marker(
                id={"type": "marker", "index": i},
                position=[row["latitude"], row["longitude"]],
                children=[
                    dl.Tooltip(row["event_title"]),
                    # dl.Popup(
                    #     html.Div(
                    #         [
                    #             html.H3(
                    #                 row["event_title"],
                    #                 style={
                    #                     "color": "darkblue",
                    #                     "overflow-wrap": "break-word",
                    #                 },
                    #             ),
                    #             html.P(
                    #                 f"Date: {row['event_date'].strftime('%Y-%m-%d')}"
                    #             ),
                    #             html.P(f"Trigger: {row['landslide_trigger']}"),
                    #             html.P(f"Size: {row['landslide_size']}"),
                    #             html.P(f"Fatalities: {int(row['fatality_count'])}"),
                    #             html.P(f"Source: {row['source_name']}"),
                    #             html.A(
                    #                 "Source URL",
                    #                 href=row["source_link"],
                    #                 target="_blank",
                    #             ),
                    #         ],
                    #         style={"width": "300px", "white-space": "normal"},
                    #     )
                    # ),
                ],
            )
            for i, row in global_filtered_df.iterrows()
        ]
    else:
        return []
    return markers


# Marker click callback


@app.callback(
    [
        Output("clicked-marker-index", "children"),
        Output("prev-marker-clicks", "children"),
    ],
    [Input({"type": "marker", "index": ALL}, "n_clicks")],
    [
        State({"type": "marker", "index": ALL}, "position"),
        State("prev-marker-clicks", "children"),
    ],
)
def marker_click(n_clicks, positions, prev_clicks):
    clicked_marker_idx = None
    for i, (prev, curr) in enumerate(zip(prev_clicks, n_clicks)):
        if prev != curr:
            clicked_marker_idx = i
            break
    if clicked_marker_idx is not None:
        clicked_position = positions[clicked_marker_idx]
        print(
            f"Clicked marker: position={clicked_position}, index={clicked_marker_idx}"
        )
        return clicked_marker_idx, n_clicks
    return dash.no_update, prev_clicks


# Add a callback to update the tweet text


@app.callback(Output("tweet-text", "value"), Input("clicked-marker-index", "children"))
def update_tweet_text(clicked_marker_idx):
    if (
        clicked_marker_idx is None
        or global_filtered_df is None
        or global_filtered_df.empty
    ):
        raise PreventUpdate
    row = global_filtered_df.iloc[clicked_marker_idx]
    event_title = row["event_title"]
    source_name = row["source_name"]
    event_date = row["event_date"].strftime("%Y-%m-%d")
    tweet = (
        f"{event_title} on {event_date} by {source_name}. #landslides #Info-Vis"
    )
    return tweet


# FIXME: Puts a default value before the user clicks on a marker
# Callback updates the landslide description
@app.callback(
    Output("landslide-info", "children"), Input("clicked-marker-index", "children")
)
def update_landslide_details(clicked_marker_idx):
    if clicked_marker_idx is None:
        raise PreventUpdate
    row = global_filtered_df.iloc[clicked_marker_idx]
    img_link = row["photo_link"]
    if img_link != img_link:  # if img_link is NaN
        img_link = "/assets/no_image.gif"
    print(row["photo_link"])
    return [
        html.H1(row["event_title"], style={"font-size": 28, "color": "black"}),
        html.H2(row['event_date'].strftime("%d %B %Y - %H:%M") + " (" + str(int(row['fatality_count'])) + " fatalities, " + str(int(row['injury_count'])) + " injuries)", style={"font-size": 12, "color": "#645a56"}),
        html.P(row["event_description"], style={"font-size": 12, "color": "#645a56"}),
        html.P(row["source_link"], style={"font-size": 12, "color": "#645a56"}),
        html.Img(src=img_link, style={"width": "100%"}),
    ]


# Callback updates the twitter share button


@app.callback(Output("twitter-share-button", "href"), Input("tweet-text", "value"))
def update_twitter_share_button(tweet_text):
    tweet_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(
        tweet_text
    )
    return tweet_url

@app.callback(Output("tiktok-share-button", "href"), Input("tweet-text", "value"))
def update_tiktok_share_button(tiktok_text):
    tiktok_url = f"https://www.tiktok.com/share?url={urllib.parse.quote(tiktok_text)}"
    return tiktok_url


@app.callback(
    Output("histogram", "figure"),
    Input("category-tabs", "value"),
    Input("datepickerrange", "value"),
    Input("trigger-dropdown", "value"),
    Input("size-dropdown", "value"),
)
def update_bar_chart(selected_value, date_value, selected_triggers, selected_sizes):
    update_global_filtered_df(
        selected_value, date_value, selected_triggers, selected_sizes
    )
    global global_filtered_df
    filtered_df = global_filtered_df
    if filtered_df.empty:
        return go.Figure().update_layout(
            title=f"No data for selected filters",
            font=dict(color="#CFCFCF"),
            plot_bgcolor="#3E3E3E",
            paper_bgcolor='rgba(0,0,0,0)',
        )

    filtered_df['month'] = filtered_df['event_date'].dt.to_period('M')
    monthly_counts = filtered_df.groupby("month").agg({"injury_count": "sum", "fatality_count": "sum"}).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_counts["month"].astype(str), y=monthly_counts["injury_count"], name="injury_count"))
    fig.add_trace(go.Bar(x=monthly_counts["month"].astype(str), y=monthly_counts["fatality_count"], name="fatality_count"))
    
    fig.update_layout(
        title=f"Injuries and Fatalities per Month for {selected_value}",
        xaxis_title="Month",
        yaxis_title="Number of Injuries and Fatalities",
        font=dict(color="#CFCFCF"),
        plot_bgcolor="#3E3E3E",
        paper_bgcolor='rgba(0,0,0,0)',
        barmode="group",
    )
    return fig

# Pie chart callback
@functools.lru_cache(maxsize=32)  # Adjust maxsize according to your needs
@app.callback(
    Output("pie-chart", "figure"),
    Input("category-tabs", "value"),
    Input("datepickerrange", "value"),
    Input("trigger-dropdown", "value"),
    Input("size-dropdown", "value"),
)
def update_pie_chart(selected_value, date_value, selected_triggers, selected_sizes):
    update_global_filtered_df(
        selected_value, date_value, selected_triggers, selected_sizes
    )
    global global_filtered_df
    filtered_df = global_filtered_df

    pie_data = filtered_df["landslide_trigger"].value_counts()
    fig = px.pie(
        pie_data,
        values=pie_data.values,
        names=pie_data.index,
        title="Landslide Triggers",
    )
    fig.update_layout(
        font=dict(color="#CFCFCF"),  paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig


# Histogram callback


# @functools.lru_cache(maxsize=32)  # Adjust maxsize according to your needs
# @app.callback(
#     Output("histogram", "figure"),
#     Input("category-tabs", "value"),
#     Input("datepickerrange", "value"),
#     Input("trigger-dropdown", "value"),
#     Input("size-dropdown", "value"),
# )
# def update_histogram(selected_value, date_value, selected_triggers, selected_sizes):
#     update_global_filtered_df(
#         selected_value, date_value, selected_triggers, selected_sizes
#     )
#     global global_filtered_df
#     filtered_df = global_filtered_df

#     fig = px.histogram(
#         filtered_df,
#         x="landslide_trigger",
#         y="event_date",
#         nbins=10,
#         title="Histogram of Landslide Triggers by Year",
#     )
#     fig.update_layout(
#         font=dict(color="#CFCFCF"), plot_bgcolor="#3E3E3E", paper_bgcolor="#3E3E3E"
#     )
#     return fig


if __name__ == "__main__":
    # TODO add back debug=True
    app.run_server(debug=False)
