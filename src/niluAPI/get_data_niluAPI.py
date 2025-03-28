import requests
import pandas as pd

def fetch_air_quality_nilu(endpoint, output_file):
    # Definerer tidsperioden som skal dekkes
    start_date = "2010-01-01"
    end_date = "2018-12-31"
    all_dates = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d')
    
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
    
    # Setter opp alle datoer og fyller manglende verdier med NaN
    pivot_df.set_index("Dato", inplace=True)
    pivot_df = pivot_df.reindex(all_dates).reset_index()

    # Interpolerer verdier for manglende data
    for col in pivot_df.columns:
        if "Verdi" in col:
            pivot_df[col] = pivot_df[col].interpolate(method='linear')
    
    # Setter Dekningsgrad til False hvis verdien er interpolert
    for col in pivot_df.columns:
        if "Dekningsgrad" in col:
            value_col = "Verdi_" + col.split('_')[1]
            interpolated_mask = pivot_df[value_col].isna()
            pivot_df[col] = pivot_df[col].where(~interpolated_mask, False)
    
    # Erstatter NaN med False for Dekningsgrad kolonner
    dekningsgrad_cols = ["Dekningsgrad_NO2", "Dekningsgrad_O3", "Dekningsgrad_SO2"]
    pivot_df[dekningsgrad_cols] = pivot_df[dekningsgrad_cols].fillna(False)
    
    # Lagre pivotert data som JSON
    pivot_df.to_json(output_file, orient="records", indent=4, force_ascii=False)
    print(f"Gruppert data er lagret under {output_file}")
