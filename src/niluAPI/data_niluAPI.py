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


def analyse_and_fix_skewness(clean_data_file, analyzed_data_file):
    """
    Leser JSON-fil og analyserer skjevhet i dataene med Yeo-Johnson transformasjon.
    Lagre den transformerte dataen til en ny fil.
    Args:
        pivot_df (pd.DataFrame): DataFrame med værdata med fjernet outliers.
        clean_data_file (str): Filsti for lagring av renset data.
        from_date (str): Startdato for interpolering i formatet 'YYYY-MM-DD'.
        to_date (str): Sluttdato for interpolering i formatet 'YYYY-MM-DD'.

    """
   
    try:
        pivot_df = pd.read_json(clean_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av fil: {e}")
        return
    
    df_transformed = pivot_df.copy()
    
    print("Analyse av skjevhet i dataen:")

    pt = PowerTransformer(method='yeo-johnson')
    
    for col in pivot_df.select_dtypes(include=[np.number]).columns:
        if col.startswith('Verdi'):
            mean = pivot_df[col].mean()
            median = pivot_df[col].median()
            changes_count = 0
            
            # Hvis det er høyreskjevhet 
            if mean > median:
                skewness = 'Positivt skjev (høyreskjev)'
                transformasjon = 'yeo-johnson'
                original_values = df_transformed[col].copy()
                
                # Bruk Yeo-Johnson for transformasjonen
                df_transformed[[col]] = pt.fit_transform(df_transformed[[col]])
                changes_count += (original_values != df_transformed[col]).sum()
            
            # Hvis det er venstreskjevhet
            elif mean < median:
                skewness = 'Negativt skjev (venstreskjev)'
                transformasjon = 'yeo-johnson'
                original_values = df_transformed[col].copy()
                
                # Bruk Yeo-Johnson for transformasjonen
                df_transformed[[col]] = pt.fit_transform(df_transformed[[col]])
                changes_count += (original_values != df_transformed[col]).sum()
            
            else:
                skewness = 'Symmetrisk'
                transformasjon = 'ingen'

            print(f"→ {col}: {skewness} | Transformasjon: {transformasjon} | Endrede verdier: {changes_count}")

    df_transformed.to_json(analyzed_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nGruppert data er lagret under {analyzed_data_file}")