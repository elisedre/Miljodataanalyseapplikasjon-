import requests
import json


def fetch_data(endpoint,  plassering):
    response = requests.get(endpoint)
    
    if response.status_code == 200:  
        data=response.json()
        if data:
            with open(plassering,'w') as json_file:
                json.dump(data, json_file, indent=4)
                print(f'data er lagret under {plassering}')   
        else:
            print('Ingen data tilgjengelig for den angitte perioden') 
    else:         
        print("Feil ved henting av data: Status Code:", response.status_code)
        print("Response Text:", response.text)
        
        
    
        

    # Responsen er sannsynligvis en liste
    '''data = response.json()
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

    
    df = pd.DataFrame(målinger, columns=["Stasjon", "Komponent", "Enhet", "Latitude", "Longitude", "Tidspunkt", "Verdi", "Dekning (%)"])
    
  
    df.to_json(file, orient="records", indent=4, force_ascii=False)'''

    