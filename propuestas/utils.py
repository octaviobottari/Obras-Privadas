import requests

API_BASE_URL = "https://apis.datos.gob.ar/georef/api/"

def fetch_provincias():
    url = f"{API_BASE_URL}/provincias"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        provincias = data['provincias']
        return provincias
    else:
        return []

def fetch_municipios(provincia_id):
    url = f"{API_BASE_URL}/municipios"
    params = {
        'provincia': provincia_id
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        municipios = data['municipios']
        return municipios
    else:
        return []
