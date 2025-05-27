import pandas as pd
import numpy as np

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
    from frostAPI.clean_data_frost import visualize_missing_data_missingno
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
