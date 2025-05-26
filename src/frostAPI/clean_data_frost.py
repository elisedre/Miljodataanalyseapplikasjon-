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


def calculate_outlier_limits(df, variable, threshold=3):
    """
    Beregner nedre og øvre grense for outliers basert på standardavvik.

    Args:
        df (pd.DataFrame): DataFrame med data.
        variable (str): Kolonnenavn som skal analyseres.
        threshold (float): Antall standardavvik som definerer outlier.

    Returns:
        tuple: (lower_limit, upper_limit)
    """
    mean = df[variable].mean()
    std = df[variable].std()
    lower_limit = mean - threshold * std
    upper_limit = mean + threshold * std
    return lower_limit, upper_limit


def plot_outlier_distribution(df, variable, lower_limit, upper_limit):
    """
    Plotter distribusjonen til en variabel med markerte outlier-grenser.

    Args:
        df (pd.DataFrame): DataFrame med data.
        variable (str): Kolonnenavn som skal plottes.
        lower_limit (float): Nedre grense for outlier.
        upper_limit (float): Øvre grense for outlier.
    """
    plot = sns.displot(data=df, x=variable, kde=True)
    plot.set(title=f"Distribusjon av {variable}", xlabel=variable)

    for ax in plot.axes.flat:
        ax.axvline(lower_limit, color='r', linestyle='--', label='Lower Limit')
        ax.axvline(upper_limit, color='r', linestyle='--', label='Upper Limit')
        ax.legend()

    plt.show()


def visualize_missing_data_missingno(df_or_path):
    """
    Visualiserer manglende verdier i værdata med missingno.

    Args:
        df_or_path (str eller pd.DataFrame): Filsti til JSON-data ELLER en DataFrame.
    """
    if isinstance(df_or_path, str):
        df = pd.read_json(df_or_path, orient="records", encoding="utf-8")
    elif isinstance(df_or_path, pd.DataFrame):
        df = df_or_path.copy()
    else:
        raise ValueError("Input må være en filsti (str) eller en pandas DataFrame.")


    msno.matrix(df)
    plt.title("Visualisering av manglende data (missingno.matrix)")
    plt.show()

    

def print_duplicate_rows(df, subset):
    """
    Skriver ut informasjon om dupliserte rader basert på angitte kolonner.

    Args:
        df (pd.DataFrame): DataFrame som skal sjekkes.
        subset_cols (list): Liste over kolonner som skal brukes for duplikatsjekk.
    
    Returns:
        None: Skriver ut antall duplikater og duplikatrader.
    """
    if not all(col in df.columns for col in subset):
        raise ValueError(f"Alle kolonner i {subset} må finnes i DataFrame.")

    duplicates = df[df.duplicated(subset=subset, keep=False)]
    
    if duplicates.empty:
        print(f"Ingen duplikater funnet basert på kolonner: {subset}")
    else:
        print(f"Totalt {len(duplicates)} duplikatrader basert på kolonner: {subset}")
        print(duplicates)

def remove_duplicate_dates(df, subset):
    """
    Fjerner duplikater basert på angitte kolonner (standard: kun 'Dato').

    Args:
        df (pd.DataFrame): DataFrame som må inneholde kolonnene i 'subset'.
        subset (list): Kolonner som brukes for å identifisere duplikater.

    Returns:
        pd.DataFrame: DataFrame uten duplikater i angitt subset.
    """
    for col in subset:
        if col not in df.columns:
            raise ValueError(f"DataFrame mangler nødvendig kolonne: {col}")

    return df.drop_duplicates(subset=subset, keep='first').copy()


def label_station(df):
    # Label encoding
    encoder = LabelEncoder()
    df["Stasjon"] = encoder.fit_transform(df["Stasjon"]).astype(int)
    return df


def analyze_and_plot_outliers(df, variables, threshold=3):
    """
    Analyserer outlier-grenser for gitte variabler og plotter resultatene.

    Args:
        df (pd.DataFrame): Datasettet.
        variables (list): Liste over kolonnenavn som skal analyseres.
        threshold (float): Antall standardavvik som definerer outlier.
    """
    for var in variables:
        lower_limit, upper_limit = calculate_outlier_limits(df, var, threshold)
        outliers = df[df[var].notna() & ~df[var].between(lower_limit, upper_limit)]
        print(f"\nOutliers for {var}: {outliers.shape[0]}")

        plot_outlier_distribution(df, var, lower_limit, upper_limit)


def interpolate_data(pivot_df, from_date, to_date, interpolate_columns):
    """
    Setter verdiene som mangler målinger til Nan, og interpolerer alle NaN-verdier med linær metode. 
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
    for col in interpolate_columns:
        if col in pivot_df.columns:
            interpolated_mask = pivot_df[col].isna()
            null_values = pivot_df[col].isna().sum()
            pivot_df[col] = pivot_df[col].interpolate(method='linear')

            interpolated_col_name = f"Interpolert_{col}"
            pivot_df[interpolated_col_name] = interpolated_mask.fillna(False)

            print(f"{col}: {null_values} verdier ble interpolert")
    return pivot_df

def save_data_json(pivot_df, data_file):
    """Lagrer data som en JSON-fil."""

    pivot_df.to_json(data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nGruppert data er lagret under {data_file}")

