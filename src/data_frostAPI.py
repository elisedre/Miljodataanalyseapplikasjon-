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


def fetch_data_from_frostAPI(endpoint, parameters, client_id):
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
        "mean(wind_speed P1D)": "Vindhastighet"
    }

    raw_data = fetch_data_from_frostAPI(endpoint, parameters, client_id)
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

def visualize_missing_data_missingno():
    """
    Leser inn værdata fra JSON og visualiserer manglende verdier per kolonne.

    Viser:
    - Antall manglende verdier per kolonne
    - Visualisering med missingno
    - Valgfri fremheving i plott (kan utvides)
    """
    # Les inn data
    df_frost = pd.read_json("../../data/raw_data/frostAPI_data.json")

    # Antall manglende verdier
    print("Antall manglende verdier per kolonne:")
    print(df_frost.isna().sum())

    # Visualisering med missingno (varme og tetthet)
    msno.matrix(df_frost)
    plt.title("Visualisering av manglende data (missingno.matrix)")
    plt.show()
    
import pandas as pd

def print_duplicate_dates(df):
    """
    Skriver ut informasjon om dupliserte datoer i en DataFrame.

    Args:
        df (pd.DataFrame): DataFrame som må inneholde 'Dato'-kolonnen.
    """
    if 'Dato' not in df.columns:
        raise ValueError("DataFrame må inneholde en kolonne som heter 'Dato'.")

    duplicate_dates = df[df.duplicated(subset='Dato', keep=False)]
    grouped = duplicate_dates.groupby('Dato').size()

    if grouped.empty:
        print("Ingen dupliserte datoer funnet.")
    else:
        print(f"Antall unike duplikatdatoer: {grouped.shape[0]}")
        for dato, antall in grouped.items():
            print(f" - {dato.date()}: {antall} forekomster")

def remove_duplicate_dates(df):
    """
    Fjerner duplikater basert på 'Dato' og returnerer en renset DataFrame. Fjerner den andre duplikaten.

    Args:
        df (pd.DataFrame): DataFrame som må inneholde 'Dato'-kolonnen.

    Returns:
        pd.DataFrame: DataFrame uten duplikater på 'Dato'.
    """
    if 'Dato' not in df.columns:
        raise ValueError("DataFrame må inneholde en kolonne som heter 'Dato'.")

    df_cleaned = df.drop_duplicates(subset='Dato', keep='first').copy()
    return df_cleaned

def check_and_clean_frost_duplicates():
    filepath = "../../data/raw_data/frostAPI_data.json"
    """
    Leser data fra Frost API JSON-fil, viser duplikater, fjerner dem og returnerer en renset DataFrame.

    Args:
        filepath (str): Filsti til Frost-data i JSON-format.

    Returns:
        pd.DataFrame: Renset DataFrame uten duplikat-datoer.
    """
    df = pd.read_json(filepath)
    
    print("Før opprydding:")
    print_duplicate_dates(df)

    df_cleaned = remove_duplicate_dates(df)

    print("\nEtter fjerning av duplikater:")
    print(f"Rader igjen i datasettet: {len(df_cleaned)}")
    
    return df_cleaned



def check_duplicate_dates_frostAPI():    
    """
    Leser inn værdata fra Frost API og sjekker for dupliserte datoer.
    Bruker funksjonen "check_duplicate_dates" for å finne og vise dupliserte datoer.

    """    
    df_frost = pd.read_json("../../data/raw_data/frostAPI_data.json")
    check_duplicate_dates(df_frost)   

def analyze_and_plot_outliers(df, variables, threshold=3):
    """
    Analyserer og plott outliers for gitte variabler i en DataFrame.

    Args:
        df (pd.DataFrame): Datasettet.
        variables (list): Liste over kolonnenavn som skal analyseres.
        threshold (float): Antall standardavvik som definerer en outlier.
    """
    for var in variables:
        mean = df[var].mean()
        std = df[var].std()
        lower_limit = mean - threshold * std
        upper_limit = mean + threshold * std

        outliers = df[~df[var].between(lower_limit, upper_limit)]
        print(f"\nOutliers for {var}:")
        print(outliers[[var]].count())

        plot = sns.displot(data=df, x=var, kde=True)
        plot.set(title=f"Distribusjon av {var}", xlabel=var)

        for ax in plot.axes.flat:
            ax.axvline(lower_limit, color='r', linestyle='--', label='Lower Limit')
            ax.axvline(upper_limit, color='r', linestyle='--', label='Upper Limit')
            ax.legend()

        plt.show()

def analyze_frost_data():
    """
    Leser Frost API-data fra en JSON-fil, analyserer og visualiserer outliers.
    Bruker funksjonen "analyze_and_plot_outliers" for å finne og plotte outliers.

    """
    df_frost = pd.read_json("../../data/raw_data/frostAPI_data.json")
    variables = ['Nedbør', 'Temperatur', 'Vindhastighet']
    threshold = 3

    analyze_and_plot_outliers(df_frost, variables, threshold)

#
def interpolate_and_save_clean_data(pivot_df, clean_data_file, from_date, to_date):
    """
    Setter verdiene som mangler målinger fra til Nan, og interpolerer alle NaN-verdier med linær metode. 
    Lagre den rensede dataen som en JSON-fil.

    Args:
        pivot_df (pd.DataFrame): DataFrame med værdata med fjernet outliers.
        clean_data_file (str): Filsti for lagring av renset data.
        from_date (str): Startdato for interpolering i formatet 'YYYY-MM-DD'.
        to_date (str): Sluttdato for interpolering i formatet 'YYYY-MM-DD'.

    """
    # Konverterer datoer
    all_dates = pd.date_range(start=from_date, end=to_date).strftime('%Y-%m-%d')
    pivot_df["Dato"] = pd.to_datetime(pivot_df["Dato"])

    pivot_df.set_index("Dato", inplace=True)
    pivot_df = pivot_df.reindex(all_dates)
    pivot_df.reset_index(inplace=True)
    pivot_df.rename(columns={"index": "Dato"}, inplace=True)

    print("\nInterpolering av NaN-verdier:")
    for col in pivot_df.columns:
        if col != "Dato":

            
            interpolated_mask = pivot_df[col].isna()
            null_values = pivot_df[col].isna().sum()
            pivot_df[col] = pivot_df[col].interpolate(method='linear')
            
            interpolated_col_name = f"Interpolert_{col}"
            pivot_df[interpolated_col_name] = interpolated_mask.fillna(False)

            print(f"{col}: {null_values} verdier ble interpolert")

    # Lagre til JSON
    pivot_df.to_json(clean_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nGruppert data er lagret under {clean_data_file}")


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
    from data_niluAPI import remove_outliers
    pivot_df = remove_outliers(raw_data_file, cols, threshold=threshold)
    
    # Sjekk om dataen ble lastet inn riktig og ikke er tom
    if pivot_df is not None and not pivot_df.empty:
        interpolate_and_save_clean_data(pivot_df, clean_data_file, from_date, to_date)
    else:
        print("Data kunne ikke leses eller er tom. Avbryter prosesseringen.")

def analyse_and_fix_skewness(clean_data_file, analyzed_data_file, threshold, cols=None):

    """
    Leser JSON-fil og analyserer skjevhet i dataene med Yeo-Johnson transformasjon og/eller skalering.
    - Kolonner med skjevhet over ±threshold transformeres med Yeo-Johnson og deretter standardiseres.
    - Kolonner med lavere skjevhet standardiseres direkte.

    Args:
        clean_data_file (str): Filsti for input-data (renset).
        analyzed_data_file (str): Filsti for output-data (transformert).
        threshold (float): Grense for skjevhet. Kolonner med høyere skjevhet transformeres.
        cols (list): Valgfrie kolonnenavn for analyse. Hvis None, brukes alle numeriske kolonner.

    """
    try:
        df = pd.read_json(clean_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av fil: {e}")
        return
    
    df_transformed = df.copy()
    yeo_transformer = PowerTransformer(method='yeo-johnson')
    scaler = StandardScaler()

    if cols is None:
        cols = df_transformed.select_dtypes(include='number').columns

    print("Skjevhet før transformasjon:")
    for col in cols:
        skew_before = df_transformed[col].skew()
        print(f"→ {col}: {skew_before:.2f}")

    print(f"\nPåfører Yeo-Johnson eller standardisering basert på skjevhet (±{threshold}):")
    for col in cols:
        skew = df_transformed[col].skew()
        try:
            if abs(skew) > threshold:
                print(f" {col}: Skjevhet {skew:.2f} → bruker Yeo-Johnson + skalering")
                transformed = yeo_transformer.fit_transform(df_transformed[[col]])
                df_transformed[col] = scaler.fit_transform(transformed)
            else:
                print(f" {col}: Skjevhet {skew:.2f} → bruker kun standardisering")
                df_transformed[col] = scaler.fit_transform(df_transformed[[col]])
        except Exception as e:
            print(f"Feil ved transformasjon av {col}: {e}")

    print("\nSkjevhet etter transformasjon:")
    for col in cols:
        print(f"→ {col}: {df_transformed[col].skew():.2f}")
    df_transformed.to_json(analyzed_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nTransformert data lagret i {analyzed_data_file}")

    return df_transformed

def fix_skewness_data_frostAPI():
    """
    Henter renset data fra Frost API, analyserer og fikser skjevhet i dataene.
    Bruker den generelle funksjonen "analyse_and_fix_skewness".

    """
    clean_data_file = "../../data/clean_data/frostAPI_clean_data.json"
    analyze_data_file = "../../data/analyzed_data/frostAPI_analyzed_data.json"
    threshold = 1.0
    cols = ["Nedbør", "Temperatur", "Vindhastighet"]

    analyse_and_fix_skewness(clean_data_file, analyze_data_file, threshold, cols=None)


def get_season(date):
    """
    Bestemmer hvilken sesong en gitt dato tilhører.

    Args:
    - date (datetime): En dato i datetime-format.

    Returns:
    - str: Navnet på sesongen ('Vår', 'Sommer', 'Høst', 'Vinter') som datoen tilhører.

    """
    if date.month in [3, 4, 5]:
        return 'Vår'
    elif date.month in [6, 7, 8]:
        return 'Sommer'
    elif date.month in [9, 10, 11]:
        return 'Høst'
    else:
        return 'Vinter'


def calculate_and_plot_seasonal_bars(data):
    """
    Beregner og visualiserer gjennomsnittlig temperatur og nedbør per sesong per år
    i form av søylediagrammer.

    Args:
    - data: DataFrame med minst kolonnene 'Dato', 'Temperatur', og 'Nedbør'.
    - sesonger: Liste med sesonger å vise (f.eks. ['Vår', 'Sommer']), eller None for å vise alle.

    """

    # Konverter og legg til sesong og år
    data['Dato'] = pd.to_datetime(data['Dato'])

    data['Sesong'] = data['Dato'].apply(get_season)
    data['År'] = data['Dato'].dt.year

    # Grupperer data etter år og sesong
    season_stats = data.groupby(['År', 'Sesong']).agg({
        'Temperatur': ['mean', 'std'],
        'Nedbør': ['mean', 'std']
    }).reset_index()

    season_stats.columns = [
        'År', 'Sesong',
        'Temperatur_Gjennomsnitt', 'Temperatur_Std',
        'Nedbør_Gjennomsnitt', 'Nedbør_Std'
    ]

    sesonger = ['Vår', 'Sommer', 'Høst', 'Vinter']

    for sesong in sesonger:
        data_sesong = season_stats[season_stats['Sesong'] == sesong]

        if data_sesong.empty:
            print(f"Ingen data for sesongen: {sesong}")
            continue

        # Temperatur søylediagram
        plt.figure(figsize=(10, 5))
        plt.bar(data_sesong['År'], data_sesong['Temperatur_Gjennomsnitt'], yerr=data_sesong['Temperatur_Std'],
                capsize=5, color='salmon', label='Temperatur')
        plt.title(f"Gjennomsnittstemperatur per år – {sesong}")
        plt.xlabel("År")
        plt.ylabel("Temperatur (°C)")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

        # Nedbør søylediagram
        plt.figure(figsize=(10, 5))
        plt.bar(data_sesong['År'], data_sesong['Nedbør_Gjennomsnitt'], yerr=data_sesong['Nedbør_Std'],
                capsize=5, color='skyblue', label='Nedbør')
        plt.title(f"Gjennomsnittsnedbør per år – {sesong}")
        plt.xlabel("År")
        plt.ylabel("Nedbør (mm)")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()


def load_and_plot_frost_seasonal_data():
    """
    Leser inn meteorologiske data fra en JSON-fil og visualiserer gjennomsnittlig
    temperatur og nedbør per sesong per år med `calculate_and_plot_seasonal_bars`.

    Args:
    - filepath (str): Sti til JSON-filen som inneholder dataen.

    """
    # Lese JSON-filen
    with open("../../data/clean_data/frostAPI_clean_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Konverter til DataFrame
    df = pd.DataFrame(data)

    # Kall på eksisterende funksjon for beregning og visualisering
    calculate_and_plot_seasonal_bars(df)

