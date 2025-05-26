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


def get_info_frostAPI(endpoint, parameters, client_id):
    """
    Henter informasjon fra Frost API og printer ID og navn for hvert element.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict or None): Parametere for API-kallet.
        client_id (str): Client ID for autentisering.

    Returns:
        list or None: Liste med hentet data, eller None ved feil.
    """
    try:
        response = requests.get(endpoint, params=parameters or {}, auth=(client_id, ''))
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Feil ved forespørsel til Frost API: {e}")
        return None
    except ValueError as e:
        print(f"Feil ved parsing av JSON: {e}")
        return None

    elements = data.get("data", [])
    for element in elements:
        print(f"ID: {element['id']}, Navn: {element.get('name', 'Ingen navn')}")
    
    return elements


def fetch_data_from_frostAPI(endpoint, parameters, client_id):
    """
    Henter rådata fra Frost API med robust feilbehandling.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict): Parametere for API-kallet.
        client_id (str): Client ID for autentisering.

    Returns:
        list: Liste med data fra API-et, eller en tom liste hvis noe går galt.
    """
    try:
        response = requests.get(endpoint, params=parameters, auth=(client_id, ""))
        response.raise_for_status()  # Kaster exception hvis status != 200
        return response.json().get("data", [])
    
    except requests.exceptions.RequestException as e:
        print(f"Feil ved henting av data fra Frost API:\n→ {e}")
        return []

    except ValueError as e:
        print(f"Feil ved parsing av JSON-respons:\n→ {e}")
        return []
    

def process_weather_data(data, elements):
    """
    Prosesserer rådata fra Frost API til en liste med dictionaries.

    Args:
        data (list): Liste med rådata fra API-et.
        elements (dict): Mapping av elementId til kolonnenavn.

    Returns:
        list: Liste med prosesserte data.
    """
    målinger = []  
    for måling in data:
        tidspunkt = måling["referenceTime"]
        stasjon = måling["sourceId"]

        måling_dict = {"Dato": tidspunkt[:10], "Stasjon": stasjon}
        
        for verdi in måling.get("observations", []):
            if verdi["elementId"] in elements:
                måling_dict[elements[verdi["elementId"]]] = verdi["value"]
        
        
        målinger.append(måling_dict)
    return målinger


def save_data_as_json(data, file, index_columns, value_columns, aggfunc="mean"):
    """
    Lagrer data som JSON-fil med fleksible kolonner og aggregeringsfunksjon.

    Args:
        data (list): Liste med prosesserte data.
        file (str): Filsti for lagring av data.
        index_columns (list): Kolonner som skal brukes som indeks i pivot-tabellen.
        value_columns (list): Kolonner som skal aggregeres.
        aggfunc (str or function): Aggregeringsfunksjon (f.eks. "mean", "sum").
    """

    df = pd.DataFrame(data)
    
    pivot_df = df.pivot_table(
        index=index_columns,  
        values=value_columns,  
        aggfunc=aggfunc       
    ).reset_index()
    
    # Lagre pivot-tabellen som en JSON-fil
    pivot_df.to_json(file, orient="records", indent=4, force_ascii=False)
    print(f"Gruppert data er lagret under {file}")