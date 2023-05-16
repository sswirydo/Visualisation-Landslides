import pandas as pd
import numpy as np


def preprocess(df_landslide):
    df_landslide = df_landslide[
        [
            "source_name",
            "source_link",
            "event_id",
            "event_date",
            "event_description",
            "event_title",
            "landslide_category",
            "landslide_trigger",
            "landslide_size",
            "fatality_count",
            "injury_count",
            "photo_link",
            "latitude",
            "longitude",
            "country_name",
        ]
    ]
    return df_landslide


###########################
# OLD ARCHIVE STUFF BELOW #
###########################


def fix_latitude(lat):
    lat = str(lat).strip()
    multiplier = 1 if lat[-1] == "N" else -1
    lat = lat[:-1]
    try:
        lat = float(lat)
    except ValueError:
        lat = np.nan
    return lat * multiplier


def fix_longitude(lon: str) -> float:
    lon = str(lon).strip()
    multiplier = 1 if lon[-1] == "E" else -1
    lon = lon[:-1]
    try:
        lon = float(lon)
    except ValueError:
        lon = np.nan
    return lon * multiplier


def calculate_distance(row, latitude, longitude):
    return np.sqrt(
        (row["latitude"] - latitude) ** 2 + (row["longitude"] - longitude) ** 2
    )


def find_nearest_temperature(df_temperature, longitude, latitude, event_date):
    df_temp_filtered = df_temperature[
        (df_temperature["event_date"] - event_date).abs() <= pd.Timedelta(days=30)
    ]

    temp_df = df_temp_filtered.copy()
    temp_df["latitude"] = temp_df["latitude"].astype(str)
    temp_df["longitude"] = temp_df["longitude"].astype(str)
    temp_df["latitude"] = temp_df["latitude"].apply(fix_latitude)
    temp_df["longitude"] = temp_df["longitude"].apply(fix_longitude)

    # Drop rows with missing latitude or longitude values
    temp_df = temp_df.dropna(subset=["latitude", "longitude"])

    # Check if the DataFrame is empty, return None if it is
    if temp_df.empty:
        return None

    # Calculate distances using a custom function and find the index with the minimum distance
    idxmin = temp_df.apply(
        calculate_distance, args=(latitude, longitude), axis=1
    ).idxmin()

    return idxmin


def get_df():
    # Load data
    df_landslide = pd.read_csv("./data/Global_Landslide_Catalog_Export.csv")
    df_temperature = pd.read_csv(
        "./data/GlobalLandTemperatures/GlobalLandTemperaturesByMajorCity.csv"
    )

    # Pre-process data
    df_landslide["event_date"] = pd.to_datetime(df_landslide["event_date"])
    df_temperature["dt"] = pd.to_datetime(df_temperature["dt"])
    df_temperature["latitude"] = df_temperature.Latitude.apply(fix_latitude)
    df_temperature["longitude"] = df_temperature.Longitude.apply(fix_longitude)
    df_temperature = df_temperature.rename(
        columns={"Latitude": "latitude", "Longitude": "longitude", "dt": "event_date"}
    )

    # Find the nearest temperature data for each landslide event
    df_landslide["nearest_temperature_idx"] = df_landslide.apply(
        lambda row: find_nearest_temperature(
            df_temperature, row["longitude"], row["latitude"], row["event_date"]
        ),
        axis=1,
    )

    # Merge dataframes
    df_merged = pd.merge(
        df_landslide,
        df_temperature,
        left_on="nearest_temperature_idx",
        right_index=True,
        suffixes=("", "_temperature"),
    )

    # Drop unnecessary columns
    df_merged = df_merged.drop(["nearest_temperature_idx"], axis=1)

    print(df_merged.head())
    return df_merged
