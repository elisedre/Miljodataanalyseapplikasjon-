import requests

def get_elements(endpoint, client_id):

    response = requests.get(endpoint, auth=(client_id, ''))
    data = response.json()

    if response.status_code == 200:
        elements = data['data']
        for element in elements:
            print(f"ID: {element['id']}, Navn: {element.get('name', 'Ingen navn')}")
    else:
        print(f"Feil ved henting av måleelementer: {data}")