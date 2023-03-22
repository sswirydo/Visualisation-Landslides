import dash
import pandas as pd
import geopandas as gpd
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output
import preprocess as prep

from shapely.geometry import Point
from datetime import datetime

app = dash.Dash(__name__, title='Landslides',
                external_stylesheets=[dbc.themes.DARKLY])

print('###### RESTART #######')

# df_landslide_temperature = prep.get_df()  # TODO TODO TODO (cf. preprocess.py)
df_landslide = pd.read_csv('./data/Global_Landslide_Catalog_Export.csv')


"""
╔═════════════════════════╗
║         Dashboard       ║
╚═════════════════════════╝
"""

app.layout = html.Div(
    children=[
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
                        style={'width': '100%'}
                    ),
                    html.P(id='output-container-date-picker-range'),
                    html.Audio(
                        src='./assets/ara_ara.mp3', controls=True, autoPlay=True, loop=True, style={'width': '100%'})

                ], width=3,
                ),
                dbc.Col([
                    dcc.Dropdown(id='dropdown', style={"color": "black", 'width': '100%'}, options=[
                                 {'label': i, 'value': i} for i in df_landslide['landslide_category'].dropna().unique()], value='landslide')
                ], width=3)
            ], style={'align': "center"})
        ]),
        dcc.Graph(id='map', style={'height': '90vh'}, figure=dict(layout=dict(
            autosize=True)), config=dict(responsive=True, displayModeBar=False)),
    ]
)
'''
temperature_graph = dcc.Graph(id="regions", figure=fig1)
popover = dbc.Card(
    [
        dbc.Button(
            "Click to see temperature over the years",
            id="popover-target",
            color="dark",
            className="mr-1",
            style={"height": "40px"},
        ),
        dbc.Popover(
            [dbc.PopoverBody(region_graph)],
            id="popover",
            is_open=False,
            target="popover-target",
            placement="auto",
            style={
                "width": "100%",
                "margin-right": "10%",
                "border-radius": "10px",
                "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)",
            },
        ),
    ]
)
'''

"""
╔══════════════════════╗
║         Others       ║
╚══════════════════════╝
"""


@app.callback(Output('map', 'figure'),
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
    fig = px.scatter_mapbox(filtered_df, color_discrete_sequence=["red"], lat='latitude', lon='longitude', hover_name='landslide_size', hover_data={
                            "fatality_count": True, "latitude": False, "longitude": False}, zoom=1, height=800, title=str(selected_value))
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    # fig.update_layout(
    # mapbox_style="white-bg",
    # mapbox_layers=[
    #     {
    #         "below": 'traces',
    #         "sourcetype": "raster",
    #         "sourceattribution": "United States Geological Survey",
    #         "source": [
    #             "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
    #         ]
    #     },
    #     {
    #         "sourcetype": "raster",
    #         "sourceattribution": "Government of Canada",
    #         "source": ["https://geo.weather.gc.ca/geomet/?"
    #                    "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
    #                    "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"],
    #     }
    #   ])
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


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
