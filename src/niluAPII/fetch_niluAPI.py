import requests
import pandas as pd
import json

def fetch_raw_data_niluAPI(endpoint):
    """
    Henter rådata fra NILU API.

    Args:
        endpoint (str): API-endepunktet.

    Returns:
        list: Liste med data fra API-et, eller tom liste ved feil.
    """
    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # Sjekker statuskode
    except requests.RequestException as e:
        print(f"Feil ved henting av data: {e}")
        return []

    try:
        data = response.json()
    except ValueError:
        print("Feil ved parsing av JSON")
        return []

    if not data:
        print("Ingen data tilgjengelig for den angitte perioden")
        return []

    return data

def process_raw_data(data):
    """
    Prosesserer rådata til en pandas DataFrame.

    Args:
        data (list): Liste med rådata fra API-et.

    Returns:
        pd.DataFrame: Prosessert data i DataFrame-format.
    """
    målinger = [
        {
            "Dato": måling["dateTime"][:10],
            "Komponent": stasjon["component"],
            "Verdi": måling["value"],
            "Dekningsgrad": måling.get("coverage", None)
        }
        for stasjon in data for måling in stasjon.get("values", [])
        if "dateTime" in måling and "value" in måling
    ]
    df = pd.DataFrame(målinger)

    pivot_df = df.pivot_table(
        index="Dato",
        columns="Komponent",
        values=["Verdi", "Dekningsgrad"],
        aggfunc="mean"
    ).reset_index()

    pivot_df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in pivot_df.columns]
    return pivot_df

def save_to_json(df, output_file):
    """
    Lagrer DataFrame som JSON-fil.

    Args:
        df (pd.DataFrame): DataFrame som skal lagres.
        output_file (str): Filsti for JSON-filen.
    """
    try:
        df.to_json(output_file, orient="records", indent=4, force_ascii=False)
        print(f"Gruppert data er lagret under {output_file}")
    except Exception as e:
        print(f"Feil ved lagring av fil: {e}")
