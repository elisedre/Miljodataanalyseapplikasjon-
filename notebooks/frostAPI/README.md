# Frost API Notebook

*Beskriver funksjonalitet for å hente og prosessere værdata fra Frost API.*

## Innhold

- Beskrivelse
- Funksjonalitet
- Viktige funksjoner
- Forutsetninger

## Beskrivelse

Denne notebooken er laget for å hente værdata fra **Frost API**, prosessere dataene og lagre dem som en JSON-fil. I tillegg gir den funksjonalitet for å hente informasjon om tilgjengelige elementer og stasjoner fra Frost API. Dette gjør det enklere å tilpasse hvilke data som skal hentes og fra hvilke stasjoner.

## Funksjonalitet

### Hente værdata fra Frost API

- **Endepunkt**: `https://frost.met.no/observations/v0.jsonld`
- **Stasjon**: `SN18700` (Oslo)
- **Parametere**:
    1. Temperatur (°C)
    2. Nedbør (mm)
    3. Vindhastighet (m/s)
- **Tidsperiode**: 2010-04-01 til 2022-04-03

### Prosessere værdata

- Dataene prosesseres til en strukturert form:
    - `mean(air_temperature P1D)` → **Temperatur**
    - `sum(precipitation_amount P1D)` → **Nedbør**
    - `mean(wind_speed P1D)` → **Vindhastighet**

### Lagre værdata

- **Mappe**: `../../data/raw_data/`
- **Filnavn**: `frostAPI_data.json`

### Hente tilgjengelige elementer fra Frost API

- **Endepunkt**: `https://frost.met.no/elements/v0.jsonld`
- **Beskrivelse**: Liste over tilgjengelige elementer (f.eks. temperatur, nedbør, vindhastighet).

### Hente tilgjengelige stasjoner fra Frost API

- **Endepunkt**: `https://frost.met.no/sources/v0.jsonld`
- **Beskrivelse**: Liste over tilgjengelige stasjoner (f.eks. målestasjoner i Oslo).

## Viktige funksjoner

### `data_frostAPI()`

- Definerer API-endepunkt, parametere og elementer som skal hentes.
- Importerer `fetch_weather_data_frostAPI` fra `get_data_frostAPI.py`.
- Kaller funksjonen for å hente, prosessere og lagre dataene.

### `fetch_weather_data_frostAPI()`

- Henter rådata fra Frost API.
- Prosesserer dataene til en strukturert form.
- Lagrer dataene som en JSON-fil.

### `get_info_frostAPI()`

- Tar inn et API-endepunkt (f.eks. `https://frost.met.no/elements/v0.jsonld` eller `https://frost.met.no/sources/v0.jsonld`).
- Viser en liste over tilgjengelige elementer eller stasjoner.

## Forutsetninger

- En **API-nøkkel** fra [Frost API](https://frost.met.no/)
- **Python** installert med nødvendige avhengigheter
- Tilgang til de relevante mappene for lagring av data