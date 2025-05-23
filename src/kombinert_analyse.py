import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_no2_with_temperature(df):
    """
    Lager en linjegraf for Verdi_NO2 med temperatur og NO₂ på to forskjellige y-akser.
    
    Forventede kolonner: 'Dato', 'Temperatur', 'Verdi_NO2'
    """

    df['Dato'] = pd.to_datetime(df['Dato'])
    df = df.sort_values('Dato')

    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Temperatur på venstre y-akse
    ax1.set_xlabel("Dato")
    ax1.set_ylabel("Temperatur (°C)", color='tab:blue')
    ax1.plot(df['Dato'], df['Temperatur'], color='tab:blue', label='Temperatur', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # NO₂ på høyre y-akse
    ax2 = ax1.twinx()
    ax2.set_ylabel("NO₂ (μg/m³)", color='tab:orange')
    ax2.plot(df['Dato'], df['Verdi_NO2'], color='tab:orange', label='NO₂ (μg/m³)', linewidth=2)
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    # tittel og rutenett
    ax1.set_title("Temperatur og NO₂ over tid")
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Datoformat på x-aksen
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)

    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(vmin=df['Temperatur'].min(), vmax=df['Temperatur'].max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax1, orientation='vertical', label='Temperatur (°C)')

    plt.tight_layout()
    plt.show()



def load_merge_and_plot_no2_temp():
    """
    Leser inn frost- og nilu-data fra JSON-filer, slår sammen på 'Dato',
    og plotter NO2 og temperatur over tid med to y-akser.

    """
    # Last inn JSON-data
    with open("../data/clean_data/frostAPI_clean_data.json", "r", encoding="utf-8") as file:
        data_frost = json.load(file)

    with open("../data/clean_data/niluAPI_clean_data.json", "r", encoding="utf-8") as file:
        data_nilu = json.load(file)

    # Konverter til DataFrames
    frost_df = pd.DataFrame(data_frost)
    nilu_df = pd.DataFrame(data_nilu)

    # Sørg for at 'Dato' er datetime
    frost_df['Dato'] = pd.to_datetime(frost_df['Dato'])
    nilu_df['Dato'] = pd.to_datetime(nilu_df['Dato'])

    # Slå sammen på 'Dato'
    merged_df = pd.merge(frost_df, nilu_df, on='Dato', how='inner')

    # Kall på plottefunksjonen
    plot_no2_with_temperature(merged_df)
