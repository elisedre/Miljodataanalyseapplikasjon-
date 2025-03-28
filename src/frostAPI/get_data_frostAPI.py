import requests
import pandas as pd

def fetch_weather_data_frostAPI(endpoint, parameters, file, client_id,elements): # henter ut værdata fra frostAPI
    
    # Hent data fra API
    response = requests.get(endpoint, params=parameters, auth=(client_id, ""))
    
    # Sjekk om forespørselen var vellykket
    if response.status_code != 200:  
        print("Feil ved henting av data: Status Code:", response.status_code)
        print("Response Text:", response.text)
        return pd.DataFrame()
    

    #Henter ut verdier knyttet til data
    data = response.json().get("data", [])
    målinger = []
    
    #Iterer gjennom dataene og hent ut verdier
    målinger = []
    for måling in data:
        tidspunkt = måling["referenceTime"]
        stasjon = måling["sourceId"]
        måling_dict = {"Dato": tidspunkt[:10], "Stasjon": stasjon}
        for verdi in måling.get("observations", []):
            if verdi["elementId"] in elements:
                måling_dict[elements[verdi["elementId"]]] = verdi["value"]
        målinger.append(måling_dict)

    # Opprett DataFrame
    df = pd.DataFrame(målinger)
    
    # Lag pivot tabell for gruppering av verdier
    pivot_df = df.pivot_table(
        index=["Dato"],  
        values=["Temperatur", "Nedbør", "Vindhastighet"],  
        aggfunc="mean"            
    ).reset_index()
    
    # Lagre pivotert data som JSON
    pivot_df.to_json(file, orient="records", indent=4, force_ascii=False)
    print(f"Gruppert data er lagret under {file}")




def get_info_frostAPI(endpoint, parameters, client_id):
    response = requests.get(endpoint, params=parameters, auth=(client_id, ''))
    data = response.json()

    if response.status_code == 200:
        elements = data['data']
        for element in elements:
            print(f"ID: {element['id']}, Navn: {element.get('name', 'Ingen navn')}")
    else:
        print(f"Feil ved henting av stasjoner: {data}")
