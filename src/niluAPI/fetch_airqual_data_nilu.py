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
        
