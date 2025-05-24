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
        list: Liste med data fra API-et, eller en tom liste hvis noe går galt.
    """
    
    # Henter data fra API
    response = requests.get(endpoint)
    if response.status_code != 200:
        print(f"Feil ved henting av data: Status Code: {response.status_code}")
        print("Response Text:", response.text)
        return pd.DataFrame()
    
    data = response.json()
    if not data:
        print("Ingen data tilgjengelig for den angitte perioden")
        return pd.DataFrame()
    return data

def process_and_save_raw_data(data, output_file):
    """
    Prosesserer rådata fra NILU API, setter det inn i en DataFrame og lagrer det som en JSON-fil.
    Args:
        data (list): Liste med rådata fra API-et.
        raw_data_file (str): Filsti for lagring av rådata.
    """
   
    # Prosesserer data for gruppering
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
    
    # Konverterer til DataFrame
    df = pd.DataFrame(målinger)
    
    # Lager pivot tabell for gruppering av verdier
    pivot_df = df.pivot_table(
        index="Dato",
        columns="Komponent",
        values=["Verdi", "Dekningsgrad"],
        aggfunc="mean"
    ).reset_index()
    
    pivot_df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in pivot_df.columns]

    pivot_df.to_json(output_file, orient="records", indent=4, force_ascii=False)
    print(f"Gruppert data er lagret under {output_file}")



def get_raw_data_niluAPI(): 
    """ 
    Spesiell funksjon for å hente ut rådata fra NILU API for Oslo og lagre
    det i en JSON-fil.
    Bruker de generelle funksjonene "fetch_raw_data_niluAPI" og "process_and_save_raw_data".

    returns:
        pd.DataFrame: DataFrame med rådata fra NILU API for Oslo.
    """

    base_url = "https://api.nilu.no/stats/day"
    from_date = "2010-04-02"
    to_date = "2016-12-31"
    latitude = 59.9139
    longitude = 10.7522
    radius = 20
    
    # Bygger API-endepunktet
    endpoint = f"{base_url}/{from_date}/{to_date}/{latitude}/{longitude}/{radius}"

    output_file =  "../../data/raw_data/raw_air_quality_nilu_oslo.json"
    raw_data= fetch_raw_data_niluAPI(endpoint)
    processed_data = process_and_save_raw_data(raw_data, output_file)
    return processed_data


def remove_outliers(raw_data_file, cols, threshold=3):
    """
    leser JSON-fil og finner outliers med mer enn 3 standardavvik fra gjennomsnittet.
    fjerner outliers og setter dem til NaN.

    Args:
        raw_data_file (str): Filsti for rådata.
        cols (list): Liste over kolonnenavn som skal sjekkes for outliers.

    Returns:
        pd.DataFrame: DataFrame med fjernet outliers, eller None hvis det oppstod en feil ved lesing.
    """
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

        mean = pivot_df[col].mean()
        std = pivot_df[col].std()
        
        # Finn outliers (mer enn 3 standardavvik unna gjennomsnittet)
        is_outlier = (pivot_df[col] > mean + x * std) | (pivot_df[col] < mean - x * std)

        outlier_count = is_outlier.sum()
        print(f"{col}:")
        print(f"Fjernet {outlier_count} outliers")
        print(f"Standaravvik: {round(std,2)}")
        print(f"Gjennomsnitt: {round(mean,2)}\n")
        
        # Sett outliers til NaN
        pivot_df.loc[is_outlier, col] = np.nan


    return pivot_df


def interpolate_and_save_clean_data(pivot_df, clean_data_file, from_date, to_date):
    """
    Setter verdiene som mangler målinger fra til NaN, og interpolerer alle NaN-verdier med linær metode.
    Markerer hvilke verdier som ble interpolert med true. 
    Lagre den rensede dataen som en JSON-fil.

    Args:
        pivot_df (pd.DataFrame): DataFrame med værdata med fjernet outliers.
        clean_data_file (str): Filsti for lagring av renset data.
        from_date (str): Startdato for interpolering i formatet 'YYYY-MM-DD'.
        to_date (str): Sluttdato for interpolering i formatet 'YYYY-MM-DD'.

    """

    all_dates = pd.date_range(start=from_date, end=to_date).strftime('%Y-%m-%d')

    # Setter opp alle datoer og fyller manglende verdier med NaN
    pivot_df.set_index("Dato", inplace=True)
    pivot_df = pivot_df.reindex(all_dates).reset_index()
    pivot_df = pivot_df.rename(columns={'index': 'Dato'})

    print("\nInterpolering av Nan-verdier:")
    # Interpolerer verdier for manglende data
    for col in pivot_df.columns:
        if "Verdi" in col:
            null_values = pivot_df[col].isna().sum()
            pivot_df[col] = pivot_df[col].interpolate(method='linear')
            
            print(f"{col}: {null_values} verdier ble interpolert")
            
    # Setter Dekningsgrad til False hvis verdien er interpolert
    for col in pivot_df.columns:
        if "Dekningsgrad" in col:
            pivot_df[col] = pivot_df[col].fillna(False)
        
        
    # Lagre pivotert data som JSON
    pivot_df.to_json(clean_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nGruppert data er lagret under {clean_data_file}")

def clean_raw_data():
    """
    Henter rådata fra NILU API, fjerner outliers og lagrer renset data i en JSON-fil.
    Bruker de generelle funksjonene "remove_outliers" og "interpolate_and_save_clean_data".

    """
    raw_data_file =  "../../data/raw_data/raw_air_quality_nilu_oslo.json"
    clean_data_file = "../../data/clean_data/niluAPI_clean_data.json"
    cols= ["Verdi_NO2", "Verdi_O3", "Verdi_SO2"]
    from_date = "2010-04-02"
    to_date = "2016-12-31"
 
    # Først fjern outliers fra rådataene
    pivot_df = remove_outliers(raw_data_file, cols, threshold=3)
    # Hvis dataen ble lest riktig, prosesser og lagre dataen
    if pivot_df is not None:
        interpolate_and_save_clean_data(pivot_df, clean_data_file, from_date, to_date)


def analyse_and_fix_skewness(clean_data_file, analyzed_data_file, threshold, cols=None):
    """
    Leser JSON-fil, analyserer og korrigerer skjevhet i dataene.
    Skjeve kolonner (>|threshold|) får Yeo-Johnson transformasjon og standardisering.
    Ikke-skjeve kolonner blir kun standardisert.
    Transformerte verdier lagres i nye kolonner med '_Trans'-suffix.

    Args:
        clean_data_file (str): Filsti til ren data.
        analyzed_data_file (str): Filsti for lagring av transformert data.
        threshold (float): Grense for skjevhet.
        cols (list): Kolonner som skal analyseres. Hvis None, velges alle numeriske.
    """
    try:
        df = pd.read_json(clean_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av fil: {e}")
        return

    df_transformed = df.copy()
    yeo = PowerTransformer(method='yeo-johnson')
    scaler = StandardScaler()

    if cols is None:
        cols = df.select_dtypes(include='number').columns

    print("Skjevhet før transformasjon:")
    for col in cols:
        print(f"→ {col}: {df[col].skew():.2f}")

    print(f"\nBehandler kolonner med skjevhet over ±{threshold}:\n")

    for col in cols:
        skew = df[col].skew()
        new_col = f"{col}_Trans"
        try:
            if abs(skew) > threshold:
                print(f" {col}: skjevhet {skew:.2f} → Yeo-Johnson + skalering")
                transformed = yeo.fit_transform(df[[col]])
                scaled = scaler.fit_transform(transformed)
                df_transformed[new_col] = scaled
            else:
                print(f"{col}: skjevhet {skew:.2f} → kun skalering")
                scaled = scaler.fit_transform(df[[col]])
                df_transformed[new_col] = scaled
        except Exception as e:
            print(f"Feil ved transformasjon av {col}: {e}")

    print("\nSkjevhet etter transformasjon:")
    for col in cols:
        new_col = f"{col}_Trans"
        if new_col in df_transformed.columns:
            print(f"→ {new_col}: {df_transformed[new_col].skew():.2f}")
    
    # Fjern de originale verdikolonene og behold kun de transformerte kolonnene
    transformed_columns = [col for col in df_transformed.columns if "_Trans" in col]

    # Velg kun de nødvendige kolonnene (dato, dekningsgrad, og de transformerte verdiene)
    final_columns = ['Dato', 'Dekningsgrad_NO2', 'Dekningsgrad_O3', 'Dekningsgrad_SO2'] + transformed_columns
    df_transformed = df_transformed[final_columns]

    df_transformed.to_json(analyzed_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nTransformert data lagret i: {analyzed_data_file}")
    return df_transformed

#Funskjon som skal nomalfordele skjevheten i dataene med yeo-johnson metoden
def fix_skewness_data_niluAPI():
    """
    Henter renset data fra NILU API, analyserer og fikser skjevhet i dataene.
    Bruker den generelle funksjonen "analyse_and_fix_skewness".
    """
    
    clean_data_file = "../../data/clean_data/niluAPI_clean_data.json"
    analyze_data_file= "../../data/analyzed_data/niluAPI_analyzed_data.json"
    threshold = 1.0
    cols= ["Verdi_NO2", "Verdi_O3", "Verdi_SO2"]
    
    analyse_and_fix_skewness(clean_data_file, analyze_data_file, threshold, cols)



def plot_air_quality(df, verdi_kolonner, dekningsgrad_kolonner, titler, tidskolonne="Dato"):
    """
    Lager separate figurer for hver verdi og fargekodede punkter for datakvalitet.

    Parametre:
        df: DataFrame med miljødata
        verdi_kolonner: Liste med kolonnene som skal plottes (f.eks. ['Verdi_NO2', 'Verdi_O3', 'Verdi_SO2'])
        dekningsgrad_kolonner: Liste med kolonner som skal brukes til å vurdere datakvalitet (f.eks. ['Dekningsgrad_NO2'])
        titler: Liste med titler for hver kolonne
        tidskolonne: Kolonnen som inneholder dato/tid (default 'Dato')
    """
    
    df[tidskolonne] = pd.to_datetime(df[tidskolonne])

    def get_color(row):
        if not row['Dekningsgrad_NO2'] or not row['Dekningsgrad_O3'] or not row['Dekningsgrad_SO2']:
            return 'red'  # Interpolerte verdier
        elif row['Dekningsgrad_NO2'] < 90 or row['Dekningsgrad_O3'] < 90 or row['Dekningsgrad_SO2'] < 90:
            return 'yellow'  # Dekningsgrad < 90
        else:
            return 'green'  # Dekningsgrad >= 90

    df['color'] = df.apply(get_color, axis=1)

    # Lager en figur per verdi-kolonne
    for i, verdi_kolonne in enumerate(verdi_kolonner):
        fig = go.Figure()

        
        fig.add_trace(go.Scatter(
            x=df[tidskolonne], y=df[verdi_kolonne], mode='markers',
            marker=dict(color=df['color'], size=6),
            name=f'Datapunkter for {titler[i]}'
        ))

        # Legg til trendlinje
        fig.add_trace(go.Scatter(
            x=df[tidskolonne], y=df[verdi_kolonne], mode='lines',
            line=dict(color='blue', width=1), name=f'Trend for {titler[i]}'
        ))

        # Oppdater layout for hver figur
        fig.update_layout(
            title=titler[i],  # Bruker tittel per graf
            xaxis_title="Dato",
            yaxis_title=f'Verdi ({verdi_kolonne})',
            width=1000,
            height=500
        )

        fig.show()


def load_and_plot_air_quality():
    """
    Leser luftkvalitetsdata fra JSON og kaller `plot_air_quality` med riktige kolonner og titler.
    Bruker generelle funksjonen `plot_air_quality`.

    """

    with open("../../data/clean_data/niluAPI_clean_data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)

    # Definer hvilke kolonner som skal plottes og vurderes
    verdi_kolonner = ['Verdi_NO2', 'Verdi_O3', 'Verdi_SO2']
    dekningsgrad_kolonner = ['Dekningsgrad_NO2', 'Dekningsgrad_O3', 'Dekningsgrad_SO2']
    titler = ['Verdi NO2 over tid', 'Verdi O3 over tid', 'Verdi SO2 over tid']

    # Kjør plot-funksjonen
    plot_air_quality(df, verdi_kolonner, dekningsgrad_kolonner, titler, tidskolonne="Dato")



