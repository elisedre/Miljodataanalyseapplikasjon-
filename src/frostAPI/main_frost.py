import requests
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import pearsonr
from sklearn.preprocessing import PowerTransformer
import seaborn as sns
from sklearn.preprocessing import PowerTransformer, StandardScaler
import missingno as msno
from sklearn.preprocessing import LabelEncoder
from .fetch_frostapi import get_info_frostAPI, fetch_data_from_frostAPI, process_weather_data, save_data_as_json
from .clean_data_frost import print_duplicate_rows, remove_duplicate_dates, interpolate_data, save_data_json, analyze_and_plot_outliers
from .analyze_data_frost import analyse_skewness, fix_skewness
from .visualization_frost import calculate_seasonal_stats, plot_seasonal_bars


def get_elements_frostAPI(client_id):
    """
    Bruker get_info_frostAPI til å hente elementer fra Frost API.

    Args:
        client_id (str): Client ID for autentisering.
    """
    parameters = None
    endpoint = 'https://frost.met.no/elements/v0.jsonld'
    get_info_frostAPI(endpoint, parameters, client_id)


def get_stations_frostAPI(client_id):
    """
    Bruker get_info_frostAPI til å hente stasjoner fra Frost API.

    Args:
        client_id (str): Client ID for autentisering.
    """
    
    parameters = {
        'types': 'SensorSystem',  
        'country': 'NO',      
    }

    endpoint = 'https://frost.met.no/sources/v0.jsonld'
    get_info_frostAPI(endpoint, parameters, client_id)

def data_frostAPI(client_id):
    """
    Henter, prosesserer og lagrer værdata fra Frost API.

    Argumenter:
        client_id (str): En streng som representerer klient-ID-en som brukes for autentisering mot Frost API.

    Returnerer:
        list: Liste med prosesserte værdata, eller None hvis ingen data ble hentet.
    """

    endpoint = "https://frost.met.no/observations/v0.jsonld"
    parameters = {
        "sources": "SN18700",
        "elements": "mean(air_temperature P1D),sum(precipitation_amount P1D),mean(wind_speed P1D)",
        "referencetime": "2010-04-02/2016-12-31",
    }

    file = "../../data/raw_data/frostAPI_data.json"
    elements = {
        "mean(air_temperature P1D)": "Temperatur",
        "sum(precipitation_amount P1D)": "Nedbør",
        "mean(wind_speed P1D)": "Vindhastighet",
        "sourceId": "Stasjon"
    }

    raw_data = fetch_data_from_frostAPI(endpoint, parameters, client_id)
    if not raw_data:
        print("Ingen data hentet.")
        return

    processed_data = process_weather_data(raw_data, elements)

    save_data_as_json(
        data=processed_data,
        file=file,
        index_columns=["Dato", "Stasjon"],
        value_columns=[v for v in elements.values() if v != "Stasjon"],
        aggfunc="mean"
    )

def visualize_missing_data_missingno(df_or_path):
    """
    Visualiserer manglende verdier i værdata med missingno.

    Args:
        df_or_path (str eller pd.DataFrame): Filsti til JSON-data ELLER en DataFrame.
    """
    if isinstance(df_or_path, str):
        df = pd.read_json(df_or_path, orient="records", encoding="utf-8")
    elif isinstance(df_or_path, pd.DataFrame):
        df = df_or_path.copy()
    else:
        raise ValueError("Input må være en filsti (str) eller en pandas DataFrame.")


    msno.matrix(df)
    plt.title("Visualisering av manglende data (missingno.matrix)")
    plt.show()


def check_and_clean_frost_duplicates():
    """
    Leser data fra Frost API JSON-fil, viser duplikater, fjerner dem og returnerer en renset DataFrame.

    Returns:
        pd.DataFrame: Renset DataFrame uten duplikat-datoer.
    """
    filepath = "../../data/raw_data/frostAPI_data.json"
    df = pd.read_json(filepath)
    subset = ["Dato", "Stasjon"]

    print("Før opprydding:")
    print_duplicate_rows(df=df, subset=subset)

    original_len = len(df)
    df_cleaned = remove_duplicate_dates(df=df, subset=["Dato", "Stasjon"])
    cleaned_len = len(df_cleaned)

    print("\nEtter fjerning av duplikater:")
    if original_len == cleaned_len:
        print("Ingen duplikater ble funnet. Ingen rader fjernet.")
    else:
        print(f"Rader igjen i datasettet: {cleaned_len} (fjernet {original_len - cleaned_len} duplikat(er))")

def label_station(df):
    # Label encoding
    encoder = LabelEncoder()
    df["Stasjon"] = encoder.fit_transform(df["Stasjon"]).astype(int)
    return df

def analyze_frost_data():
    """
    Leser Frost API-data fra en JSON-fil, analyserer og visualiserer outliers.
    """
    df_frost = pd.read_json("../../data/raw_data/frostAPI_data.json")
    variables = ['Nedbør', 'Temperatur', 'Vindhastighet']
    threshold = 3

    analyze_and_plot_outliers(df_frost, variables, threshold)

def clean_data_frostAPI(threshold=3):
    """
        Leser rådata fra Frost API, fjerner outliers og lagrer renset data i en JSON-fil.
        Bruker funksjonene "remove_outliers" og "interpolate_and_save_clean_data".

        Args:
        threshold (float, optional): Antall standardavvik for å definere outliers. Default er 3.
    """
    
    raw_data_file = "../../data/raw_data/frostAPI_data.json"
    clean_data_file = "../../data/clean_data/frostAPI_clean_data.json"
    cols = ["Nedbør", "Temperatur", "Vindhastighet"]
    from_date = "2010-04-02"
    to_date = "2016-12-31"
    

    # Fjern outliers fra rådataene
    from niluAPI.clean_data_nilu import remove_outliers
    pivot_df = remove_outliers(raw_data_file, cols, threshold=threshold)

    #Sjekker og fjerner duplikater
    pivot_df= remove_duplicate_dates(pivot_df, subset=["Dato", "Stasjon"])
    
    # Sjekk om dataen ble lastet inn riktig og ikke er tom
    if pivot_df is not None and not pivot_df.empty:
        
        pivot_df=interpolate_data(pivot_df, from_date, to_date, cols)
    else:
        print("Data kunne ikke leses eller er tom. Avbryter prosesseringen.")

    # Label encoding av stasjoner
    pivot_df=label_station(pivot_df)

    # Lagre den rensede dataen som en JSON-fil
    save_data_json(pivot_df, clean_data_file)


def fix_skewness_data_frostAPI():
    """
    Henter renset data fra Frost API, analyserer og fikser skjevhet.
    Lagrer transformert data til fil.
    """
    clean_data_file = "../../data/clean_data/frostAPI_clean_data.json"
    analyzed_data_file = "../../data/analyzed_data/frostAPI_analyzed_data.json"
    threshold = 1.0
    cols = ["Nedbør", "Temperatur", "Vindhastighet"]

    df, cols = analyse_skewness(clean_data_file, cols)
    if df is None:
        print("Avslutter pga. feil i innlasting.")
        return

    df_transformed = fix_skewness(df, threshold, cols)
    df_transformed.to_json(analyzed_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nTransformert data lagret i {analyzed_data_file}")



def load_and_plot_frost_seasonal_data():
    """
    Leser inn meteorologiske data fra en JSON-fil og visualiserer gjennomsnittlig
    temperatur og nedbør per sesong per år.
    """
    with open("../../data/clean_data/frostAPI_clean_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)
    stats = calculate_seasonal_stats(df)
    plot_seasonal_bars(stats)
