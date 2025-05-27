import pandas as pd
import json
from datetime import datetime
from .fetch_niluAPI import fetch_raw_data_niluAPI, process_raw_data, save_to_json
from .clean_data_nilu import remove_outliers, interpolate_data, save_clean_data
from .analyze_data_nilu import analyse_skewness, fix_skewness
from .visualization_nilu import plot_air_quality

def get_raw_data_niluAPI():
    """
    Henter og prosesserer rådata fra NILU API for Oslo og lagrer det i JSON-fil.

    """
    base_url = "https://api.nilu.no/stats/day"
    from_date = "2010-04-02"
    to_date = "2016-12-31"
    latitude = 59.9139
    longitude = 10.7522
    radius = 20

    endpoint = f"{base_url}/{from_date}/{to_date}/{latitude}/{longitude}/{radius}"
    output_file = "../../data/raw_data/niluAPI_data.json"

    raw_data = fetch_raw_data_niluAPI(endpoint)
    if not raw_data:
        return pd.DataFrame()

    processed_data = process_raw_data(raw_data)
    save_to_json(processed_data, output_file=output_file)

def check_and_clean_nilu_duplicates():
    """
    Leser data fra NILU API JSON-fil, viser duplikater, fjerner dem og returnerer en renset DataFrame.

    Returns:
        pd.DataFrame: Renset DataFrame uten duplikat-datoer.
    """
    from frostAPI.clean_data_frost import print_duplicate_rows, remove_duplicate_dates
    filepath = "../../data/raw_data/niluAPI_data.json"
    df = pd.read_json(filepath)
    subset = ["Dato"]

    print("Før opprydding:")
    print_duplicate_rows(df, subset=subset)

    original_len = len(df)
    df_cleaned = remove_duplicate_dates(df, subset=subset)
    cleaned_len = len(df_cleaned)

    print("\nEtter fjerning av duplikater:")
    if original_len == cleaned_len:
        print("Ingen duplikater ble funnet. Ingen rader fjernet.")
    else:
        print(f"Rader igjen i datasettet: {cleaned_len} (fjernet {original_len - cleaned_len} duplikat(er))")

def analyze_outliers_nilu():
    """
    Leser Frost API-data fra en JSON-fil, analyserer og visualiserer outliers.
    """
    from frostAPI.clean_data_frost import analyze_and_plot_outliers
    df_frost = pd.read_json("../../data/raw_data/niluAPI_data.json")
    variables = ['Verdi_NO2', 'Verdi_SO2', 'Verdi_O3']
    threshold = 3

    analyze_and_plot_outliers(df_frost, variables, threshold)  

def clean_raw_data():
    """
    Henter rådata fra NILU API, fjerner outliers og interpolerer manglende verdier.
    Lagrer deretter renset data i en JSON-fil.
    """
    raw_data_file = "../../data/raw_data/niluAPI_data.json"
    clean_data_file = "../../data/clean_data/niluAPI_clean_data.json"
    cols = ["Verdi_NO2", "Verdi_O3", "Verdi_SO2"]
    from_date = "2010-04-02"
    to_date = "2016-12-31"

    try:
        # Fjerner outliers
        pivot_df = remove_outliers(raw_data_file, cols, threshold=3)
        if pivot_df.empty:
            print("Ingen data tilgjengelig etter outlier-fjerning.")
            return

        # Interpolerer og lagrer renset data
        interpolated_df = interpolate_data(pivot_df, from_date, to_date)
        save_clean_data(interpolated_df, clean_data_file)

    except Exception as e:
        print(f"Feil i renseprosessen: {e}")

def fix_skewness_data_niluAPI():
    """
    Henter renset data fra NILU API, analyserer og fikser skjevhet i måleverdiene.
    Lagrer kun relevante kolonner (transformerte verdier, dato og dekningsgrad).
    """
    clean_data_file = "../../data/clean_data/niluAPI_clean_data.json"
    analyzed_data_file = "../../data/analyzed_data/niluAPI_analyzed_data.json"
    threshold = 1.0
    cols = ["Verdi_NO2", "Verdi_O3", "Verdi_SO2"]

    try:
        df = pd.read_json(clean_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av fil: {e}")
        return

    skewness_dict = analyse_skewness(df, cols)
    df_transformed = fix_skewness(df, skewness_dict, threshold)

    if df_transformed.empty:
        print("Ingen data å lagre.")
        return

    transformed_columns = [f"{col}_Trans" for col in cols]
    final_columns = ['Dato', 'Dekningsgrad_NO2', 'Dekningsgrad_O3', 'Dekningsgrad_SO2'] + transformed_columns
    df_final = df_transformed[final_columns]

    try:
        df_final.to_json(analyzed_data_file, orient="records", indent=4, force_ascii=False)
        print(f"\nTransformert data lagret i: {analyzed_data_file}")
    except Exception as e:
        print(f"Feil ved lagring av transformert data: {e}")

def load_and_plot_air_quality():
    """
    Leser luftkvalitetsdata og kaller `plot_air_quality` med riktige parametere.
    Ansvarlig for å bestemme fargekoding basert på datakvalitet.
    """
    with open("../../data/clean_data/niluAPI_clean_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)

    verdi_kolonner = ['Verdi_NO2', 'Verdi_O3', 'Verdi_SO2']
    dekningsgrad_kolonner = ['Dekningsgrad_NO2', 'Dekningsgrad_O3', 'Dekningsgrad_SO2']
    titler = ['Verdi NO2 over tid', 'Verdi O3 over tid', 'Verdi SO2 over tid']

    # Lager ny kolonne for fargekoding
    def get_color(row):
        for col in dekningsgrad_kolonner:
            if pd.isna(row[col]) or not row[col]:
                return 'red'
            if row[col] < 90:
                return 'yellow'
        return 'green'

    df['farge'] = df.apply(get_color, axis=1)

    plot_air_quality(df, verdi_kolonner, titler, fargekolonne='farge', tidskolonne="Dato")
