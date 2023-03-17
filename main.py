import loader as ld
import panel as pn
import datetime as dt
import folium
import pandas as pd
import os
import plotly.express as px
import holoviews as hv
import webbrowser
import matplotlib.pyplot as plt
import statistics as stats

####################
### PYTHON FILES ###
####################

import loader as ld

pd.options.plotting.backend = 'holoviews'

PATH = 'data/Global_Landslide_Catalog_Export.csv'


pn.config.js_files = {'leaflet': 'https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.js', 'jquery': 'https://code.jquery.com/jquery-1.12.4.min.js', 'bootstrap': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js', 'aw': 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js', 'd3': 'https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js',
                      'iso': 'https://cdn.jsdelivr.net/npm/iso8601-js-period@0.2.1/iso8601.min.js', 'time': 'https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.min.js', 'pa7': 'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/pa7_hm.min.js', 'pa': 'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/pa7_leaflet_hm.min.js'}
pn.config.css_files = ['https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.css', "https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.css", "https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css", "https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css", "https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css",
                       "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css", "https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css", "https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.control.css"]

pn.extension()
pn.extension(sizing_mode='stretch_width')
pn.extension(template='bootstrap')
pn.state.template.param.update(title="Super Title for Landslides uWu >.<")

pipeline = pn.pipeline.Pipeline()
data = pd.read_csv(PATH)
print(data['landslide_category'].unique().tolist())


#######################
# WIDGETS (LEFT PANEL)#
#######################

# SlIDER EXAMPLE (to adapt)
date_range_slider = pn.widgets.DateSlider(name='Date Slider', start=dt.date(2021, 9, 6), end=dt.date(
    2021, 9, 12), value=dt.date(2021, 9, 6), value_throttled=dt.date(2021, 9, 6))
hour_slider = pn.widgets.IntSlider(
    name='Hour Slider', start=0, end=24, value=10)

# CHECKBOX GROUP
category_checkbox = pn.widgets.CheckBoxGroup(
    name='Landslide Category', options=data['landslide_category'].unique().tolist(), inline=False)
category_checkbox_group = pn.Column(
    pn.pane.Str("Landslide Category"), category_checkbox)

trigger_checkbox = pn.widgets.CheckBoxGroup(
    name='Landslide Trigger', options=data['landslide_trigger'].unique().tolist(), inline=False)
trigger_checkbox_group = pn.Column(
    pn.pane.Str("Landslide Trigger"), trigger_checkbox)

size_checkbox = pn.widgets.CheckBoxGroup(
    name='Landslide Size', options=data['landslide_size'].unique().tolist(), inline=False)
size_checkbox_group = pn.Column(
    pn.pane.Str("Landslide Size"), trigger_checkbox)

# EXAMPLE OF LIST BOX (to adapt)
select_line = pn.widgets.Select(name='Lorem Ipsum', options=[])


# BUTTON (to adapt)
button = pn.widgets.Button(name='Fetch data', button_type='primary')

title = pn.pane.Str('Parameters', style={
                    'font-size': '18pt', "font-weigth": "bold"})
parameters = pn.Column(title, date_range_slider, category_checkbox_group, trigger_checkbox_group, size_checkbox_group, select_line,
                       button, sizing_mode='stretch_width')


# DATAFRAME EXAMPLE (to adapt)
df_widget = pn.widgets.DataFrame(data, name='DataFrame')
df_widget

parameters.servable(area='sidebar')
main = pn.Tabs()
main.servable(area='main')
