'''import requests
import pandas as pd

def fetch_data(endpoint, parameters, file):
    response = requests.get(endpoint, params=parameters)
    
    if response.status_code != 200:  
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("Kunne ikke hente data")
        return pd.DataFrame()
    
    print('Det funket!')

    data = response.json()["data"]
    målinger = []
    
    for måling in data:
        stasjon = måling.get("stasjon")
        komponent = måling.get("component")
        enhet = måling.get("unit")
        latitude = måling.get("latitude")
        longitude = måling.get("longitude")
        
        for verdi in målinger.get("values", []):
            tidspunkt = verdi.get("dateTime")
            målt_verdi = verdi.get("value")
            dekning = verdi.get("coverage")
            
            målinger.append({
                "Stasjon": stasjon,
                "Komponent": komponent,
                "Enhet": enhet,
                "Latitude": latitude,
                "Longitude": longitude,
                "Tidspunkt": tidspunkt,
                "Verdi": målt_verdi,
                "Dekning (%)": dekning
            })

    # Opprett DataFrame
    df = pd.DataFrame(målinger, columns=["Stasjon", "Komponent", "Enhet", "Latitude", "Longitude", "Tidspunkt", "Verdi", "Dekning (%)"])
    
    # Lagre som JSON
    df.to_json(file, orient="records", indent=4, force_ascii=False)'''

import requests
import pandas as pd

def fetch_data(endpoint, parameters, file):
    response = requests.get(endpoint, params=parameters)
    
    if response.status_code != 200:  
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("Kunne ikke hente data")
        return pd.DataFrame()
    
    print('Det funket!')

    # Responsen er sannsynligvis en liste
    data = response.json()
    målinger = []
    
    # Iterer over hver stasjon/målepunkt
    for måling in data:
        stasjon = måling.get("station")
        komponent = måling.get("component")
        enhet = måling.get("unit")
        latitude = måling.get("latitude")
        longitude = måling.get("longitude")
        
        # Gå gjennom verdiene
        for verdi in måling.get("values", []):
            tidspunkt = verdi.get("dateTime")
            målt_verdi = verdi.get("value")
            dekning = verdi.get("coverage")
            
            målinger.append({
                "Stasjon": stasjon,
                "Komponent": komponent,
                "Enhet": enhet,
                "Latitude": latitude,
                "Longitude": longitude,
                "Tidspunkt": tidspunkt,
                "Verdi": målt_verdi,
                "Dekning (%)": dekning
            })

    # Opprett DataFrame
    df = pd.DataFrame(målinger, columns=["Stasjon", "Komponent", "Enhet", "Latitude", "Longitude", "Tidspunkt", "Verdi", "Dekning (%)"])
    
    # Lagre som JSON
    df.to_json(file, orient="records", indent=4, force_ascii=False)

    return df