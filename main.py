import urllib.parse
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import dash_leaflet as dl
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import preprocess
import wikipedia
import plotly.graph_objects as go


app = dash.Dash(
    __name__,
    title="Landslides",
    external_stylesheets=[dbc.themes.DARKLY, "assets/styles.css"],
)

df_landslide = pd.read_csv(
    "./data/Global_Landslide_Catalog_Export.csv", parse_dates=["event_date"]
)

# Preprocess dataframes
df_landslide = preprocess.preprocess(df_landslide)
landslide_categories = df_landslide["landslide_category"].unique()
dataframes_by_category_trigger_year = {}

for category in landslide_categories:
    dataframes_by_category_trigger_year[category] = {}
    category_df = df_landslide[df_landslide["landslide_category"] == category]
    triggers = category_df["landslide_trigger"].unique()

    for trigger in triggers:
        dataframes_by_category_trigger_year[category][trigger] = {}
        trigger_df = category_df[category_df["landslide_trigger"] == trigger]
        years = trigger_df["event_date"].dt.year.unique()

        for year in years:
            year_df = trigger_df[trigger_df["event_date"].dt.year == year]
            dataframes_by_category_trigger_year[category][trigger][year] = year_df


# Helper functions
# Rename columns to be more human-readable
def pretty_column_name(column_name):
    return column_name.replace("_", " ").title()


title = html.H1(
    children="⛰️ Landslides  Explorer🔎",
    className="title",
    style={"margin": "3%"},
)

# Get a list of unique landslide categories
categories = df_landslide["landslide_category"].unique()

# Create a tab for each category
tabs = [dcc.Tab(label=category, value=category) for category in categories]

details_tab_title = html.H4(
    id="details_tab_title",
    children="ℹ️ Did you know?",
    className="detailstab",
    style={"margin": "3%"},
)
details_tab = html.H6(
    id="details_tab", children="", className="detailstab", style={"margin": "3%"}
)
# Create the tabs component
tablist = dcc.Tabs(
    id="category-tabs",
    value=categories[0],
    children=tabs,
)

# Twitter
twitter_input = html.Div(
    children=[
        dcc.Input(
            id="tweet-text",
            type="text",
            placeholder="Enter your tweet here",
            value="[message] #landslides #Info-Vis",
            style={"width": "100%", "zIndex": 10},
        ),
    ]
)

twitter_btn = html.Div(
    children=[
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
                "float": "right",
                "margin": "auto",
            },
        ),
    ]
)

# Dataset source
dataset_btn = html.Div(
    children=[
        dcc.Link(
            "Dataset 🌐",
            id="dataset-source-button",
            href="https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog-Export/dd9e-wu2v",
            target="_blank",
            style={
                "color": "white",
                "text-decoration": "none",
                "font-size": "20px",
                "padding": "10px",
                "float": "left",
                "margin": "auto",
            },
        ),
    ]
)

# Extract years from the dataset
min_year = df_landslide["event_date"].min().year
max_year = df_landslide["event_date"].max().year
years = list(range(min_year, max_year + 1))

# Per Year range picker for dates
date_picker_label = dbc.Label("Select Year Range", className="control-label")
date_picker = dcc.RangeSlider(
    id="datepickerrange",
    min=min_year,
    max=max_year,
    step=1,
    value=[2016, 2017],
    marks={min_year: str(min_year), max_year: str(max_year)},
    className="slider",
    tooltip={"placement": "bottom", "always_visible": True},
)

# Date store, used to store the selected date range
date_store = dcc.Store(
    id="date-range-storage", data={"start_date": None, "end_date": None}
)

# Landslide Trigger Dropdown
landslide_trigger_label = dbc.Label("Landslide Triggers", className="control-label")
landslide_trigger = dcc.Dropdown(
    id="trigger-dropdown",
    options=[
        {"label": pretty_column_name(i), "value": i}
        for i in sorted(
            df_landslide["landslide_trigger"].dropna().unique(),
            key=lambda x: pretty_column_name(x),
        )
    ],
    value="downpour",
    multi=True,
    placeholder="Select Landslide Triggers",
    className="dropdown",
    style={"color": "black", "width": "100%", "zIndex": 8},
)

manual_order = ["unknown", "small", "medium", "large", "very_large", "catastrophic"]

# Sort the dropdown options based on the manual order
options = [
    {"label": pretty_column_name(i), "value": i}
    for i in sorted(
        df_landslide["landslide_size"].dropna().unique(),
        key=lambda x: manual_order.index(x) if x in manual_order else float("inf"),
    )
]
landslide_size_label = dbc.Label("Landslide Sizes", className="control-label")

# Create the dropdown with the sorted options
landslide_size = dcc.Dropdown(
    id="size-dropdown",
    options=options,
    value=None,
    multi=True,
    placeholder="Select Landslide Sizes",
    className="dropdown",
    style={"color": "black", "width": "100%", "zIndex": 7},
)


# Debounce interval, used to prevent the callback from being fired too often
debounce_interval = dcc.Interval(
    id="debounce-interval",
    interval=500,  # in milliseconds (500 ms = 0.5 seconds)
    n_intervals=0,
)

# Data Filters Card, contains the date picker, landslide trigger and size dropdowns
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
    style={"margin-top": "5%"},
    className="mb-4",
)

# Plots, contains the pie charts and histogram
plots = dbc.Col(
    [
        dbc.Col(
            [
                # Landslide triggers pie chart
                dcc.Loading(
                    id="loading-icon-pie",
                    type="circle",
                    children=[
                        dcc.Graph(
                            id="pie-chart",
                            style={
                                "border-top-left-radius": "15px",
                                "border-top-right-radius": "15px",
                                "background-color": "#3E3E3E",
                            },
                        )
                    ],
                    style={"textAlign": "center"},
                )
            ],
        ),
        dbc.Col(
            [
                # Histogram of landslide triggers by year
                dcc.Loading(
                    id="loading-icon-histogram-1",
                    type="circle",
                    children=[
                        dcc.Graph(id="histogram", style={"background-color": "#3E3E3E"})
                    ],
                    style={"textAlign": "center"},
                )
            ],
        ),
        dbc.Col(
            [
                # New pie chart of landslide triggers by year
                dcc.Loading(
                    id="loading-icon-histogram-2",
                    type="circle",
                    children=[
                        dcc.Graph(
                            id="new_pie-chart",
                            style={
                                "border-bottom-left-radius": "15px",
                                "border-bottom-right-radius": "15px",
                                "background-color": "#3E3E3E",
                            },
                        )
                    ],
                    style={"textAlign": "center"},
                )
            ],
        ),
    ],
    style={"height": "100vh", "padding-top": "5%", "border-radius": "15px"},
)

# Map, contains the map and the marker cluster
map = html.Div(
    children=[
        dcc.Loading(
            id="loading",
            type="circle",
            children=[
                dl.Map(
                    [
                        dl.TileLayer(
                            url="https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=ecc291031e064ce28fe61975dd9c1631"
                        ),
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
            ],
        ),
    ],
    style={"position": "relative", "transform": "scale(1)"},
)

# Landslide Info, contains the information about the selected landslide
landslide_info = html.Div(
    children=[
        html.Div(
            [],  # Returned in a callback below
            id="landslide-info",
            style={
                "background-color": "#303030",
                "padding": "10px",
                "border-radius": "5px",
                "margin": "10px",
                "height": "45vh",
                "overflowY": "scroll",
                "scrollbarWidth": "thin",
                "scrollbarColor": "#000000 #F5F5F5",
                "scrollbarGutter": "1px solid black",
            },
        )
    ]
)
tab_style = {
    "backgroundColor": "black",
    "margin-left": "4px",
    "margin-right": "4px",
    "padding-top": "4px",
    "padding-bottom": "4px",
    "fontWeight": "bold",
    "font-size": "18px",
    "border": "none",
}
tab_selected_style = {
    "margin-left": "4px",
    "margin-right": "4px",
    "padding-top": "4px",
    "padding-bottom": "4px",
    "fontWeight": "bold",
    "font-size": "18px",
    "border": "none !important",
}

# Map Tabs, contains the map category tabs
map_tabs = dbc.Row(
    dbc.Col(
        [
            title,
            map,
            dcc.Tabs(
                id="category-tabs",
                value="rock_fall",
                parent_className="custom-tabs",
                vertical=True,
                className="custom-tabs-container",
                style={"display": "inline-block", "border": "none !important"},
                children=[
                    dcc.Tab(
                        label="Land Slide",
                        value="landslide",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Mud Slide",
                        value="mudslide",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="River Bank Collapse",
                        value="riverbank_collapse",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Lahar",
                        value="lahar",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Debris Flow",
                        value="debris_flow",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Rock Fall",
                        value="rock_fall",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Complex",
                        value="complex",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Snow avalanche",
                        value="snow_avalanche",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Creep",
                        value="creep",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Earth flow",
                        value="earth_flow",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Translational Slide",
                        value="translational_slide",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Topple",
                        value="topple",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                ],
            ),
            details_tab_title,
            details_tab,
        ],
        width=12,
    ),
    justify="center",
    align="center",
    # style={"height": "80%"},
)

# Global container, contains all the elements
container = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        picker,
                        landslide_info,
                        html.Div(
                            [
                                twitter_input,
                                dataset_btn,
                                twitter_btn,
                            ],
                        ),
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=3,
                    xl=3,
                ),
                dbc.Col([map_tabs], xs=12, sm=12, md=12, lg=6, xl=6),
                dbc.Col(
                    [plots],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=3,
                    xl=3,
                    style={
                        "height": "90vh",
                        "overflowY": "scroll",
                        "padding": "0",
                        "padding-right": "10px",
                        "scrollbarWidth": "thin",
                        "scrollbarColor": "#000000 #F5F5F5",
                        "scrollbarGutter": "1px solid black",
                        "border-bottom-left-radius": "15px",
                        "border-bottom-right-radius": "15px",
                    },
                ),
            ]
        ),
        # Add a hidden div for intermediate value storage
        dcc.Store(id="intermediate-value"),
    ],
    fluid=True,
    style={
        "background-image": "url(https://images.unsplash.com/photo-1502239608882-93b729c6af43?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80)",
        "background-repeat": "no-repeat",
        "background-position": "center",
        "background-size": "cover",
        "width": "100%",
        "height": "100vh",
        "max-height": "100vh",
    },
)

# Set the app layout
app.layout = container

# Global filtered dataframe, used to only have to filter the dataframe once
global_filtered_df = None


# Update the global_filtered_df
def update_global_filtered_df(selected_tab, dates, selected_triggers, selected_sizes):
    global global_filtered_df

    # Get all triggers for the selected category if no triggers are selected
    if not selected_triggers:
        selected_triggers = list(
            dataframes_by_category_trigger_year[selected_tab].keys()
        )

    # If selected_triggers is a string, convert it to a list
    if isinstance(selected_triggers, str):
        selected_triggers = [selected_triggers]

    data = pd.DataFrame()
    start_date = dates[0]
    end_date = dates[1]
    for trigger in selected_triggers:
        for year, temp_df in dataframes_by_category_trigger_year[selected_tab][
            trigger
        ].items():
            try:
                if start_date <= year <= end_date:
                    data = pd.concat([data, temp_df])
            except Exception as e:
                print(f"Error while processing trigger '{trigger}': {e}")

    if selected_sizes:
        if isinstance(selected_sizes, str):
            selected_sizes = [selected_sizes]
        data = data[data["landslide_size"].isin(selected_sizes)]

    global_filtered_df = data
    if global_filtered_df is not None and not global_filtered_df.empty:
        global_filtered_df["fatality_count"] = global_filtered_df[
            "fatality_count"
        ].fillna(0)
        global_filtered_df["injury_count"] = global_filtered_df["injury_count"].fillna(
            0
        )


# Update the dataframe when the datepicker or dropdowns are changed, store the result in the hidden div
@app.callback(
    Output("intermediate-value", "data"),
    Input("datepickerrange", "value"),
    Input("trigger-dropdown", "value"),
    Input("size-dropdown", "value"),
    Input("category-tabs", "value"),
)
def update_figure(dates, selected_triggers, selected_sizes, selected_tab):
    update_global_filtered_df(selected_tab, dates, selected_triggers, selected_sizes)
    return global_filtered_df.to_json(date_format="iso", orient="split")


# Update the map markers
@app.callback(
    Output("markers", "children"),
    Input("intermediate-value", "data"),
)
def update_markers(jsonified_global_filtered_df):
    global_filtered_df = pd.read_json(jsonified_global_filtered_df, orient="split")
    markers = [
        dl.Marker(
            # icon = emoji_icon,
            id={"type": "marker", "index": i},
            position=[row["latitude"], row["longitude"]],
            children=[
                dl.Tooltip(row["event_title"]),
            ],
        )
        for i, row in global_filtered_df.iterrows()
    ]
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
        # clicked_position = positions[clicked_marker_idx]
        return clicked_marker_idx, n_clicks
    return dash.no_update, prev_clicks


# Add tabs details
@app.callback(Output("details_tab", "children"), Input("category-tabs", "value"))
def update_tab_details(selected_tab):
    if selected_tab == "riverbank_collapse":
        return "River bank failure can be caused when the gravitational forces acting on a bank exceed the forces which hold the sediment together. Failure depends on sediment type, layering, and moisture content. All river banks experience erosion, but failure is dependent on the location and the rate at which erosion is occurring.[2] River bank failure may be caused by house placement, water saturation, weight on the river bank, vegetation, and/or tectonic activity. When structures are built too close to the bank of the river, their weight may exceed the weight which the bank can hold and cause slumping, or accelerate slumping that may already be active."
    elif selected_tab == "lahar":
        return "A lahar (Javanese: ꦮ꧀ꦭꦲꦂ) is a violent type of mudflow or debris flow composed of a slurry of pyroclastic material, rocky debris and water. The material flows down from a volcano, typically along a river valley."
    elif selected_tab == "complex":
        return "These are complex landslides which could not be categorized"
    elif selected_tab == "creep":
        return "Creep is the slow downslope movement of material under gravity. It generally occurs over large areas. Three types of creep occur: seasonal movement or creep within the soil – due to seasonal changes in soil moisture and temperature, e.g. frost heave processes."
    elif selected_tab == "translational_slide":
        return "A translational or planar landslide is a downslope movement of material that occurs along a distinctive planar surface of weakness such as a fault, joint or bedding plane. Some of the largest and most damaging landslides on Earth are translational. These landslides occur at all scales and are not self-stabilising."
    elif selected_tab == "topple":
        return "Topple. This is characterized by the tilting of rock without collapse, or by the forward rotation of rocks about a pivot point. Topples have a rapid rate of movement and failure is generally influenced by the fracture pattern in rock. Material descends by abrupt falling, sliding, bouncing and rolling."
    elif selected_tab == "landslide":
        return "A landslide is defined as the movement of a mass of rock, debris, or earth down a slope. Landslides are a type of mass wasting, which denotes any down-slope movement of soil and rock under the direct influence of gravity."
    elif selected_tab == "mudslide":
        return "A mudflow, also known as mudslide or mud flow, is a form of mass wasting involving fast-moving flow of debris and dirt that has become liquified by the addition of water. Such flows can move at speeds ranging from 3 meters/minute to 5 meters/second. Mudflows contain a significant proportion of clay, which makes them more fluid than debris flows, allowing them to travel farther and across lower slope angles. Both types of flow are generally mixtures of particles with a wide range of sizes, which typically become sorted by size upon deposition"
    elif selected_tab == "debris_flow":
        return "Debris flows are fast-moving landslides that are particularly dangerous to life and property because they move quickly, destroy objects in their paths, and often strike without warning. They occur in a wide variety of environments throughout the world, including all 50 states and U.S. Territories. Debris flows generally occur during periods of intense rainfall or rapid snowmelt and usually start on hillsides or mountains. "
    elif selected_tab == "snow_avalanche":
        return "A snow avalanche begins when an unstable mass of snow breaks away from a slope. The snow picks up speed as it moves downhill, producing a river of snow and a cloud of icy particles that rises high into the air. The moving mass picks up even more snow as it rushes downhill."
    else:
        return wikipedia.summary(selected_tab)


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
    tweet = f"{event_title} on {event_date} by {source_name}. #landslides #InfoVis"
    return tweet


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
    # show_more = False
    event_description = html.P(
        row["event_description"], style={"font-size": 12, "color": "white"}
    )

    return [
        html.H1(row["event_title"], style={"font-size": 28, "color": "white"}),
        html.H2(
            [
                html.H2(
                    pretty_column_name(row["landslide_trigger"])
                    + " ("
                    + pretty_column_name(row["landslide_size"])
                    + ")",
                    style={"font-size": 16, "color": "white"},
                ),
                html.A(
                    "Source Link",
                    href=row["source_link"],
                    target="_blank",
                    style={"font-size": 16, "color": "cyan", "margin-bottom": "10px"},
                ),
            ],
            style={"center": "center", "font-size": 16, "color": "white"},
        ),
        html.H3(
            row["event_date"].strftime("%d %B %Y - %H:%M")
            + " ("
            + str(int(row["fatality_count"]))
            + " fatalities, "
            + str(int(row["injury_count"]))
            + " injuries)",
            style={"font-size": 12, "color": "white"},
        ),
        event_description,
        # show_more,
        html.Img(src=img_link, style={"width": "100%"}),
    ]


# Callback updates the twitter share button
@app.callback(Output("twitter-share-button", "href"), Input("tweet-text", "value"))
def update_twitter_share_button(tweet_text):
    tweet_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(
        tweet_text
    )
    return tweet_url



# Callback updates the histogram
@app.callback(Output("histogram", "figure"), Input("intermediate-value", "data"))
def update_bar_chart(jsonified_global_filtered_df):
    global_filtered_df = pd.read_json(jsonified_global_filtered_df, orient="split")
    filtered_df = global_filtered_df
    if filtered_df.empty:
        return go.Figure().update_layout(
            title=f"No data for selected filters",
            font=dict(color="#CFCFCF"),
            plot_bgcolor="#3E3E3E",
            paper_bgcolor="rgba(0,0,0,0)",
        )
    filtered_df["event_date"] = pd.to_datetime(filtered_df["event_date"])
    filtered_df["year"] = filtered_df["event_date"].dt.to_period("Y")
    yearly_counts = (
        filtered_df.groupby("year")
        .agg({"injury_count": "sum", "fatality_count": "sum"})
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=yearly_counts["year"].astype(str),
            y=yearly_counts["injury_count"],
            name="Injury count",
        )
    )
    fig.add_trace(
        go.Bar(
            x=yearly_counts["year"].astype(str),
            y=yearly_counts["fatality_count"],
            name="Fatality count",
        )
    )

    pretty = filtered_df["landslide_category"].apply(pretty_column_name).unique()

    fig.update_layout(
        title=f"Injuries and Fatalities per Year for {pretty[0]}",
        xaxis_title="Year",
        yaxis_title="Number of Injuries and Fatalities",
        font=dict(color="#CFCFCF"),
        plot_bgcolor="#3E3E3E",
        paper_bgcolor="rgba(0,0,0,0)",
        barmode="group",
    )
    return fig


# Pie chart callback
@app.callback(
    Output("pie-chart", "figure"),
    Input("intermediate-value", "data"),
)
def update_pie_chart(jsonified_global_filtered_df):
    global_filtered_df = pd.read_json(jsonified_global_filtered_df, orient="split")
    filtered_df = global_filtered_df

    if filtered_df.empty:
        return go.Figure().update_layout(
            title=f"No data for selected filters",
            font=dict(color="#CFCFCF"),
            plot_bgcolor="#3E3E3E",
            paper_bgcolor="rgba(0,0,0,0)",
        )

    trigger_counts = filtered_df["landslide_trigger"].value_counts().reset_index()
    trigger_counts.columns = ["landslide_trigger", "count"]

    # Limit to top 5 triggers
    top_triggers = trigger_counts.head(5)
    other_count = trigger_counts.iloc[5:]["count"].sum()

    # Add "Other" to the top_triggers DataFrame
    other_row = pd.DataFrame({"landslide_trigger": ["Other"], "count": [other_count]})
    top_triggers = pd.concat([top_triggers, other_row], ignore_index=True)

    top_triggers["landslide_trigger"] = top_triggers["landslide_trigger"].apply(
        pretty_column_name
    )

    fig = go.Figure(
        go.Pie(
            labels=top_triggers["landslide_trigger"],
            values=top_triggers["count"],
            textinfo="label+percent",
            insidetextorientation="radial",
        )
    )

    fig.update_layout(
        title="Landslide Triggers",
        font=dict(color="#CFCFCF"),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# Second pie chart callback
@app.callback(Output("new_pie-chart", "figure"), Input("intermediate-value", "data"))
def update_new_pie_chart(jsonified_global_filtered_df):
    global_filtered_df = pd.read_json(jsonified_global_filtered_df, orient="split")
    filtered_df = global_filtered_df
    if filtered_df.empty:
        return go.Figure().update_layout(
            title=f"No data for selected filters",
            font=dict(color="#CFCFCF"),
            plot_bgcolor="#3E3E3E",
            paper_bgcolor="rgba(0,0,0,0)",
        )

    country_counts = filtered_df["country_name"].value_counts().reset_index()
    country_counts.columns = ["country_name", "count"]

    # Limit to top 5 countries
    top_countries = country_counts.head(5)
    other_count = country_counts.iloc[5:]["count"].sum()

    # Add "Other" to the top_countries DataFrame
    other_row = pd.DataFrame({"country_name": ["Other"], "count": [other_count]})
    top_countries = pd.concat([top_countries, other_row], ignore_index=True)

    top_countries["country_name"] = top_countries["country_name"].apply(
        pretty_column_name
    )

    fig = go.Figure(
        go.Pie(
            labels=top_countries["country_name"],
            values=top_countries["count"],
            textinfo="label+percent",
            insidetextorientation="radial",
        )
    )

    fig.update_layout(
        title=f"Landslide Distribution by Country",
        font=dict(color="#CFCFCF"),
        plot_bgcolor="#3E3E3E",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# Main function, runs the dashboard server
if __name__ == "__main__":
    app.run_server(debug=False)
