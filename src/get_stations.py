import requests

def get_stations(endpoint, parameters, client_id):
    response = requests.get(endpoint, params=parameters, auth=(client_id, ''))
    data = response.json()

    if response.status_code == 200:
        sources = data['data']
        for source in sources:
            print(f"ID: {source['id']}, Navn: {source.get('name', 'Ingen navn')}")
    else:
        print(f"Feil ved henting av stasjoner: {data}")