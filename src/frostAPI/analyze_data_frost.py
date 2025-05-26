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


def analyse_skewness(clean_data_file, cols=None):
    """
    Leser data fra JSON og skriver ut skjevhet for kolonner.

    Args:
        clean_data_file (str): Filsti for input-data (renset).
        cols (list): Kolonner som skal analyseres. Hvis None, analyseres alle numeriske.
    
    Returns:
        pd.DataFrame: DataFrame med innlest data.
        list: Liste over kolonner som analyseres.
    """
    try:
        df = pd.read_json(clean_data_file, orient="records", encoding="utf-8")
    except (ValueError, FileNotFoundError) as e:
        print(f"Feil ved lesing av fil: {e}")
        return None, None
    
    if cols is None:
        cols = df.select_dtypes(include='number').columns.tolist()

    print("Skjevhet før transformasjon:")
    for col in cols:
        skew_val = df[col].skew()
        print(f"→ {col}: {skew_val:.2f}")

    return df, cols


def fix_skewness(df, threshold, cols):
    """
    Transformerer data i kolonner med skjevhet over terskel med Yeo-Johnson + skalering.
    Andre kolonner skaleres kun.

    Args:
        df (pd.DataFrame): DataFrame med input-data.
        threshold (float): Grense for skjevhet.
        cols (list): Kolonner som skal transformeres.

    Returns:
        pd.DataFrame: Transformert DataFrame.
    """
    yeo_transformer = PowerTransformer(method='yeo-johnson')
    scaler = StandardScaler()

    df_transformed = df.copy()

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

    return df_transformed


