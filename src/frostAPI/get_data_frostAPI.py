import requests
import pandas as pd

# Funksjon for å hente rådata fra Frost API
def fetch_data_from_api(endpoint, parameters, client_id):
    """
    Henter rådata fra Frost API.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict): Parametere for API-kallet.
        client_id (str): Client ID for autentisering.

    Returns:
        list: Liste med data fra API-et, eller en tom liste hvis noe går galt.
    """
    response = requests.get(endpoint, params=parameters, auth=(client_id, ""))
    
    # Sjekk om forespørselen var vellykket
    if response.status_code != 200:
        print("Feil ved henting av data: Status Code:", response.status_code)
        print("Response Text:", response.text)
        return []
    
    # Returner data fra API-responsen
    return response.json().get("data", [])


# Funksjon for å prosessere rådata
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


#Funksjon for å lagre data som JSON-fil
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


# Hovedfunksjon for å hente, prosessere og lagre værdata fra Frost API
def fetch_weather_data_frostAPI(endpoint, parameters, file, client_id, elements):
    """
    Hovedfunksjon for å hente, prosessere og lagre værdata fra Frost API.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict): Parametere for API-kallet.
        file (str): Filsti for lagring av data.
        client_id (str): Client ID for autentisering.
        elements (dict): Mapping av elementId til kolonnenavn.
    """
    
    raw_data = fetch_data_from_api(endpoint, parameters, client_id)
    if not raw_data:
        print("Ingen data hentet.")
        return
    
    processed_data = process_weather_data(raw_data, elements)

    save_data_as_json(
        data=processed_data,
        file=file,
        index_columns=["Dato"],  
        value_columns=list(elements.values()),  
        aggfunc="mean"  
    )


# Funksjon for å hente informasjon om tilgjengelige elementer fra Frost API
def get_info_frostAPI(endpoint, parameters, client_id):
    """
    Henter informasjon om tilgjengelige elementer fra Frost API.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict): Parametere for API-kallet.
        client_id (str): Client ID for autentisering.
    """
    response = requests.get(endpoint, params=parameters, auth=(client_id, ''))
    data = response.json()

    if response.status_code == 200:
        elements = data['data']
        for element in elements:
            print(f"ID: {element['id']}, Navn: {element.get('name', 'Ingen navn')}")
    else:
        print(f"Feil ved henting av stasjoner: {data}")
