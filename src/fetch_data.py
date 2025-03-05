import requests
import pandas as pd

def fetch_data(url, client_id, parameters):
    response = requests.get(url, params=parameters, auth=(client_id, ""))
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
    if response.status_code != 200:  
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("Kunne ikke hente data")
        return pd.DataFrame()  # Returner en tom DataFrame i stedet for å stoppe koden

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
    df.to_json("../data/weather_data.json", orient="records", indent=4, force_ascii=False)

    #Funker ikke 

    

