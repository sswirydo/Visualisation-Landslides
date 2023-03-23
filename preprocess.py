
import pandas as pd
#from shapely.geometry import Point
from datetime import datetime
#from shapely.geometry import Point
#from sklearn.neighbors import BallTree

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
    df_temperature = pd.read_csv(
        "./data/GlobalLandTemperatures/GlobalLandTemperaturesByMajorCity.csv")

    # Pre-process temperature
    df_landslide["event_date"] = pd.to_datetime(df_landslide["event_date"])
    min_date = df_landslide["event_date"].min()
    df_temperature["dt"] = pd.to_datetime(df_temperature["dt"])
    # Keep only rows with date >= min_date
    df_temperature = df_temperature.loc[df_temperature["dt"] >= min_date]
    df_temperature["Latitude"] = df_temperature.Latitude.apply(fix_latitude)
    df_temperature["Longitude"] = df_temperature.Longitude.apply(fix_longitude)
    df_temperature = df_temperature.rename(
        columns={"Latitude": "latitude", "Longitude": "longitude", "dt": "event_date"})

    # For each landslide, merge with the nearest temperature row, note: both by minimum distance AND time
    df_landslide = df_landslide.sort_values(
        ["latitude", "longitude", "event_date"])
    df_temperature = df_temperature.sort_values(
        ["latitude", "longitude", "event_date"])

    print(df_temperature['latitude'])
    print(df_landslide['latitude'])
    # FIXME FIXME FIXME → pandas.errors.MergeError: can only asof on a key for left
    df_merged_landslide_temperature = pd.merge_asof(df_landslide, df_temperature, on=[
                                                    'latitude', 'longitude', 'event_date'], direction='nearest')

    return df_merged_landslide_temperature
    # # Pre-process transform to geopandas
    # # Create a BallTree
    # tree = BallTree(
    #     df_temperature[['latitude', 'longitude']].values, leaf_size=2)
    # # Query the BallTree on each feature from 'df_landslids' to find the distance
    # # to the nearest 'df_temperature'
    # dist, ind = tree.query(
    #     # The input array for the query
    #     df_landslide[['latitude', 'longitude']].values,
    #     k=1,  # The number of nearest neighbors
    # )
    # print(df_landslide.size)
    # ind = ind.flatten()
    # # TODO on a des valeurs en trop, il faut les enlever (sinon algo ok)
    # # ind = ind.reshape(ind.shape[0]) # Flatten the array
    # df_landslide["temperature"] = df_temperature.iloc[ind].AverageTemperature.values
    # print(df_landslide['temperature'].max())
    # print(df_landslide.size)
    return df_landslide
