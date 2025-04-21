#importerte bibloteker
import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer

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


from sklearn.preprocessing import PowerTransformer, StandardScaler
import pandas as pd

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
