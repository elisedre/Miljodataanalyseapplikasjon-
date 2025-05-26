import requests
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import PowerTransformer, StandardScaler
import plotly.graph_objects as go

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
    output_file = "../../data/raw_data/raw_air_quality_nilu_oslo.json"

    raw_data = fetch_raw_data_niluAPI(endpoint)
    if not raw_data:
        return pd.DataFrame()

    processed_data = process_raw_data(raw_data)
    save_to_json(processed_data, output_file)


def check_and_clean_nilu_duplicates():
    """
    Leser data fra Frost API JSON-fil, viser duplikater, fjerner dem og returnerer en renset DataFrame.

    Returns:
        pd.DataFrame: Renset DataFrame uten duplikat-datoer.
    """
    from data_frostAPI import print_duplicate_dates, remove_duplicate_dates
    filepath = "../../data/raw_data/frostAPI_data.json"
    df = pd.read_json(filepath)

    print("Før opprydding:")
    print_duplicate_dates(df)

    original_len = len(df)
    df_cleaned = remove_duplicate_dates(df)
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
    from data_frostAPI import analyze_and_plot_outliers
    df_frost = pd.read_json("../../data/raw_data/raw_air_quality_nilu_oslo.json")
    variables = ['Verdi_NO2', 'Verdi_SO2', 'Verdi_O3']
    threshold = 3

    analyze_and_plot_outliers(df_frost, variables, threshold)    

def remove_outliers(raw_data_file, cols, threshold=3):
    """
    Leser JSON-fil og finner outliers som ligger mer enn `threshold` standardavvik fra gjennomsnittet.
    Fjerner outliers ved å sette dem til NaN.

    Args:
        raw_data_file (str): Filsti for rådata.
        cols (list): Liste over kolonnenavn som skal sjekkes for outliers.
        threshold (int, optional): Antall standardavvik som definerer outlier (default 3).

    Returns:
        pd.DataFrame: DataFrame med fjernet outliers (NaN), eller tom DataFrame ved feil.
    """
    from data_frostAPI import visualize_missing_data_missingno
    try:
        pivot_df = pd.read_json(raw_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av rådata-fil: {e}")
        return pd.DataFrame()
    
    x = threshold
    
    print("Fjerning av outliers:")
    print(f"Outliers er mer enn {x} standardavvik unna gjennomsnittet\n")
    
    for col in cols:
        if col not in pivot_df.columns:
            print(f"Kolonnen '{col}' finnes ikke i dataene.")
            continue

        # Beregn gjennomsnitt og standardavvik for kolonnen
        mean = pivot_df[col].mean()
        std = pivot_df[col].std()
        
        # Finn rader som er outliers
        is_outlier = (pivot_df[col] > mean + x * std) | (pivot_df[col] < mean - x * std)

        outlier_count = is_outlier.sum()
        print(f"{col}:")
        print(f"Fjernet {outlier_count} outliers")
        print(f"Standardavvik: {round(std,2)}")
        print(f"Gjennomsnitt: {round(mean,2)}\n")
        
        # Sett outliers til NaN
        pivot_df.loc[is_outlier, col] = np.nan

        visualize_missing_data_missingno(pivot_df)

    return pivot_df


def interpolate_data(pivot_df, from_date, to_date):
    """
    Interpolerer manglende verdier i en DataFrame for et gitt datointervall.
    Marker interpolerte verdier ved å sette tilhørende dekningsgrad til False.

    Args:
        pivot_df (pd.DataFrame): DataFrame med rådata med outliers fjernet.
        from_date (str): Startdato for interpolering i format 'YYYY-MM-DD'.
        to_date (str): Sluttdato for interpolering i format 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: DataFrame med interpolerte verdier.
    """
    all_dates = pd.date_range(start=from_date, end=to_date).strftime('%Y-%m-%d')

    # Setter dato som indeks og fyller inn manglende datoer med NaN
    pivot_df.set_index("Dato", inplace=True)
    pivot_df = pivot_df.reindex(all_dates).reset_index()
    pivot_df = pivot_df.rename(columns={'index': 'Dato'})

    print("\nInterpolering av NaN-verdier:")
    for col in pivot_df.columns:
        if "Verdi" in col:
            null_values = pivot_df[col].isna().sum()
            pivot_df[col] = pivot_df[col].interpolate(method='linear')
            print(f"{col}: {null_values} verdier ble interpolert")

    # Setter Dekningsgrad til False hvis verdien er interpolert
    for col in pivot_df.columns:
        if "Dekningsgrad" in col:
            pivot_df[col] = pivot_df[col].fillna(False)

    return pivot_df


def save_clean_data(df, clean_data_file):
    """
    Lagrer en DataFrame som en JSON-fil.

    Args:
        df (pd.DataFrame): DataFrame som skal lagres.
        clean_data_file (str): Filsti for lagring av data.

    Returns:
        None
    """
    try:
        df.to_json(clean_data_file, orient="records", indent=4, force_ascii=False)
        print(f"\nRenset data er lagret under {clean_data_file}")
    except Exception as e:
        print(f"Feil ved lagring av fil: {e}")


def clean_raw_data():
    """
    Henter rådata fra NILU API, fjerner outliers og interpolerer manglende verdier.
    Lagrer deretter renset data i en JSON-fil.
    """
    raw_data_file = "../../data/raw_data/raw_air_quality_nilu_oslo.json"
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


def analyse_skewness(df, cols):
    """
    Analyserer og skriver ut skjevhet for valgte kolonner.

    Args:
        df (pd.DataFrame): DataFrame med data.
        cols (list): Liste over kolonner som skal analyseres.

    Returns:
        dict: Ordbok med kolonnenavn som nøkkel og skjevhetsverdi som verdi.
    """
    skewness_dict = {}
    print("Skjevhet før transformasjon:")
    for col in cols:
        skew_val = df[col].skew()
        skewness_dict[col] = skew_val
        print(f"→ {col}: {skew_val:.2f}")
    return skewness_dict


def fix_skewness(df, skewness_dict, threshold):
    """
    Transformerer/skalerer kolonner basert på skjevhetsverdier.
    Legger til nye kolonner med '_Trans'-suffix.

    Args:
        df (pd.DataFrame): DataFrame med data.
        skewness_dict (dict): Ordbok med skjevhetsverdier for kolonner.
        threshold (float): Grenseverdi for skjevhet.

    Returns:
        pd.DataFrame: DataFrame med transformerte kolonner lagt til.
    """
    yeo = PowerTransformer(method='yeo-johnson')
    scaler = StandardScaler()
    df_transformed = df.copy()

    print(f"\nBehandler kolonner med skjevhet over ±{threshold}:\n")
    for col, skew in skewness_dict.items():
        new_col = f"{col}_Trans"
        try:
            if abs(skew) > threshold:
                print(f"{col}: skjevhet {skew:.2f} → Yeo-Johnson + skalering")
                transformed = yeo.fit_transform(df[[col]])
                scaled = scaler.fit_transform(transformed)
                df_transformed[new_col] = scaled.flatten()
            else:
                print(f"{col}: skjevhet {skew:.2f} → kun skalering")
                scaled = scaler.fit_transform(df[[col]])
                df_transformed[new_col] = scaled.flatten()
        except Exception as e:
            print(f"Feil ved transformasjon av {col}: {e}")

    print("\nSkjevhet etter transformasjon:")
    for col in skewness_dict:
        new_col = f"{col}_Trans"
        if new_col in df_transformed.columns:
            print(f"→ {new_col}: {df_transformed[new_col].skew():.2f}")

    return df_transformed


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


def plot_air_quality(df, verdi_kolonner, titler, fargekolonne, tidskolonne="Dato"):
    """
    Lager separate figurer for hver verdi og fargekodede punkter.

    Parametre:
        df: DataFrame med miljødata.
        verdi_kolonner: Liste med kolonner som skal plottes.
        titler: Liste med titler for hver graf.
        fargekolonne: Navn på kolonne med fargekoder.
        tidskolonne: Tid/dato-kolonne (default 'Dato').
    """
    df[tidskolonne] = pd.to_datetime(df[tidskolonne])

    for i, verdi_kolonne in enumerate(verdi_kolonner):
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df[tidskolonne], y=df[verdi_kolonne], mode='markers',
            marker=dict(color=df[fargekolonne], size=6),
            name=f'Datapunkter for {titler[i]}'
        ))

        fig.add_trace(go.Scatter(
            x=df[tidskolonne], y=df[verdi_kolonne], mode='lines',
            line=dict(color='blue', width=1), name=f'Trend for {titler[i]}'
        ))

        fig.update_layout(
            title=titler[i],
            xaxis_title="Dato",
            yaxis_title=f'Verdi ({verdi_kolonne})',
            width=1000,
            height=500
        )

        fig.show()


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
