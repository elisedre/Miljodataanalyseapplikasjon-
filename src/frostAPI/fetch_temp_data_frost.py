import requests
import pandas as pd

def fetch_data(endpoint, parameters, file, client_id):
    response = requests.get(endpoint, params=parameters, auth=(client_id, ""))
    
    if response.status_code != 200:  
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("Kunne ikke hente data")
        return pd.DataFrame()
    
    print('Det funket!')

    data = response.json()["data"]
    målinger = []
    
    for måling in data:
        tidspunkt = måling["referenceTime"]
        stasjon = måling["sourceId"]
        
        for verdi in måling["observations"]:
            målinger.append({"Stasjon": stasjon, "Tidspunkt": tidspunkt, "Temperatur": verdi["value"]})

    # Opprett DataFrame
    df = pd.DataFrame(målinger, columns=["Stasjon", "Tidspunkt", "Temperatur"])
    
    # Lagre som JSON
    df.to_json(file, orient="records", indent=4, force_ascii=False)
