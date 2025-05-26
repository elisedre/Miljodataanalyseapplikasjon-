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


def get_season(date):
    """
    Bestemmer hvilken sesong en gitt dato tilhører.

    Args:
    - date (datetime): En dato i datetime-format.

    Returns:
    - str: Navnet på sesongen ('Vår', 'Sommer', 'Høst', 'Vinter').
    """
    if date.month in [3, 4, 5]:
        return 'Vår'
    elif date.month in [6, 7, 8]:
        return 'Sommer'
    elif date.month in [9, 10, 11]:
        return 'Høst'
    else:
        return 'Vinter'


def calculate_seasonal_stats(data):
    """
    Legger til sesong og år, og beregner gjennomsnitt og standardavvik for temperatur og nedbør per sesong per år.

    Args:
    - data (DataFrame): Data med kolonnene 'Dato', 'Temperatur', og 'Nedbør'.

    Returns:
    - DataFrame: Aggregert statistikk per sesong og år.
    """
    data['Dato'] = pd.to_datetime(data['Dato'])
    data['Sesong'] = data['Dato'].apply(get_season)
    data['År'] = data['Dato'].dt.year

    stats = data.groupby(['År', 'Sesong']).agg({
        'Temperatur': ['mean', 'std'],
        'Nedbør': ['mean', 'std']
    }).reset_index()

    stats.columns = [
        'År', 'Sesong',
        'Temperatur_Gjennomsnitt', 'Temperatur_Std',
        'Nedbør_Gjennomsnitt', 'Nedbør_Std'
    ]
    return stats


def plot_seasonal_bars(stats_df):
    """
    Visualiserer gjennomsnittlig temperatur og nedbør per sesong per år.

    Args:
    - stats_df (DataFrame): Dataframe med kolonner som inneholder aggregerte verdier per sesong og år.
    """
    sesonger = ['Vår', 'Sommer', 'Høst', 'Vinter']

    for sesong in sesonger:
        data_sesong = stats_df[stats_df['Sesong'] == sesong]

        if data_sesong.empty:
            print(f"Ingen data for sesongen: {sesong}")
            continue

        # Temperatur søylediagram
        plt.figure(figsize=(10, 5))
        plt.bar(data_sesong['År'], data_sesong['Temperatur_Gjennomsnitt'],
                yerr=data_sesong['Temperatur_Std'], capsize=5,
                color='salmon', label='Temperatur')
        plt.title(f"Gjennomsnittstemperatur per år – {sesong}")
        plt.xlabel("År")
        plt.ylabel("Temperatur (°C)")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

        # Nedbør søylediagram
        plt.figure(figsize=(10, 5))
        plt.bar(data_sesong['År'], data_sesong['Nedbør_Gjennomsnitt'],
                yerr=data_sesong['Nedbør_Std'], capsize=5,
                color='skyblue', label='Nedbør')
        plt.title(f"Gjennomsnittsnedbør per år – {sesong}")
        plt.xlabel("År")
        plt.ylabel("Nedbør (mm)")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()




