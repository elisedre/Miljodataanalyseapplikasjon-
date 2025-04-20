import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer
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


def remove_outliers(raw_data_file, cols):
    """
    leser JSON-fil og finner outliers med mer enn 3 standardavvik fra gjennomsnittet.
    fjerner outliers og setter dem til NaN.
    Args:
        raw_data_file (str): Filsti for rådata.
        cols (list): Liste over kolonnenavn som skal sjekkes for outliers.
    """
    try:
        pivot_df = pd.read_json(raw_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av rådata-fil: {e}")
        return
    x=3
    
    print("Fjerning av outliers:")
    print(f"Outliers er mer enn {x} standardavvik unna gjennomsnittet\n")
    for col in cols:
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


def analyse_and_fix_skewness(clean_data_file, analyzed_data_file, threshold, cols):
   
    """
    Leser JSON-fil og analyserer skjevhet i dataene med Yeo-Johnson transformasjon.
    Lagre den transformerte dataen til en ny fil.
    Args:
        clean_data_file (str): Filsti for lagring av renset data.
        analyzed_data_file (str): Filsti for lagring av analyserte og transformerte data.
        threshold (float): Grense for skjevhet, kolonner med høyere skjevhet vil bli transformert.
        cols (list): Liste med kolonner som skal analyseres og transformeres. Hvis None, analyseres alle numeriske kolonner.
    """
    try:
        pivot_df = pd.read_json(clean_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av fil: {e}")
        return
    
    df_transformed = pivot_df.copy()
    transformer = PowerTransformer(method='yeo-johnson')

    if cols is None:
        cols = df_transformed.select_dtypes(include='number').columns

    print("Skjevhet før transformasjon:")
    for col in cols:
        skew_before = df_transformed[col].skew()
        print(f"→ {col}: {skew_before:.2f}")

    print(f"\nPåfører Yeo-Johnson på kolonner med skjevhet > ±{threshold}")
    for col in cols:
        skew = df_transformed[col].skew()
        if abs(skew) > threshold:
            try:
                
                df_transformed[col] = transformer.fit_transform(df_transformed[[col]])
            except Exception as e:
                print(f"Feil ved transformasjon av {col}: {e}")

    print("\nSkjevhet etter transformasjon:")
    for col in cols:
        skew_after = df_transformed[col].skew()
        print(f"→ {col}: {skew_after:.2f}")

    # Lagre den transformerte dataen til en ny JSON-fil
    df_transformed.to_json(analyzed_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nGruppert data er lagret under {analyzed_data_file}")


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


