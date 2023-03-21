
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

# https://stackoverflow.com/questions/61491965/changing-north-south-latitude-values-in-python
def fix_latitude(x):
    if x.endswith('S'):
        x = -float(x.strip('S'))
    else:
        x = x.strip('N')
    return x
def fix_longitude(x):
    if x.endswith('E'):
      x = -float(x.strip('E'))
    else:
        x = x.strip('W')
    return x


def get_df():

    df_landslide = pd.read_csv('./data/Global_Landslide_Catalog_Export.csv')
    df_temperature = pd.read_csv("./data/GlobalLandTemperatures/GlobalLandTemperaturesByMajorCity.csv")

    # Pre-process temperature 
    df_landslide["event_date"] = pd.to_datetime(df_landslide["event_date"])
    min_date = df_landslide["event_date"].min()
    df_temperature["dt"] = pd.to_datetime(df_temperature["dt"])
    df_temperature = df_temperature.loc[df_temperature["dt"] >= min_date]
    df_temperature["Latitude"] = df_temperature.Latitude.apply(fix_latitude)
    df_temperature["Longitude"] = df_temperature.Longitude.apply(fix_longitude)
    df_temperature = df_temperature.rename(columns={"Latitude":"latitude", "Longitude":"longitude", "dt":"event_date"})

    # For each landslide, merge with the nearest temperature row, note: both by minimum distance AND time
    df_landslide = df_landslide.sort_values(["latitude", "longitude", "event_date"])
    df_temperature = df_temperature.sort_values(["latitude", "longitude", "event_date"])
    # FIXME FIXME FIXME → pandas.errors.MergeError: can only asof on a key for left
    df_merged_landslide_temperature = pd.merge_asof(df_landslide, df_temperature, on=['latitude', 'longitude', 'event_date'], direction='nearest')
    
    return df_merged_landslide_temperature


