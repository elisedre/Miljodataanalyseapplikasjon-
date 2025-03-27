import requests
import json
import pandas as pd


def fetch_nilu_oslo(endpoint, output_file):
   
    # Hent data fra API
    response = requests.get(endpoint)
    
    if response.status_code == 200:  
        data = response.json()
        if data:
            # Prosesser data for gruppering
            målinger = []
            for stasjon in data:
                for måling in stasjon.get("values", []):
                    if "dateTime" in måling and "value" in måling:
                        målinger.append({
                            "Dato": måling["dateTime"][:10],  
                            "Stasjon": stasjon.get("station"),
                            "Komponent": stasjon.get("component"),
                            "Verdi": måling["value"],
                            "Dekningsgrad": måling.get("coverage", None)  
                        })
            
            # Konverter til DataFrame
            df = pd.DataFrame(målinger)
            
            # Lag pivot tabell for gruppering av verdier
            pivot_df = df.pivot_table(
                index=["Dato", "Stasjon"],  
                columns="Komponent",       
                values=["Verdi", "Dekningsgrad"],  
                aggfunc="mean"            
            ).reset_index()
            
            # Fjerne paranteser
            pivot_df.columns = [
                f"{col[0]}_{col[1]}" if col[1] else col[0] for col in pivot_df.columns
            ]
            
            # Lagre pivotert data som JSON
            pivot_df.to_json(output_file, orient="records", indent=4, force_ascii=False)
            print(f"Gruppert data er lagret under {output_file}")
            
            
        else:
            print("Ingen data tilgjengelig for den angitte perioden")
            return pd.DataFrame()
    else:         
        print("Feil ved henting av data: Status Code:", response.status_code)
        print("Response Text:", response.text)
        return pd.DataFrame()

