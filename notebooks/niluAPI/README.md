# NILU API Notebook

*Beskriver funksjonalitet for å hente og prosessere luftkvalitetsdata fra NILU API.*

## Innhold

- Beskrivelse
- Funksjonalitet
- Viktige funksjoner
- Forutsetninger

## Beskrivelse

Denne notebooken er laget for å hente luftkvalitetsdata fra **NILU API** for Oslo-området. Dataene lagres som en JSON-fil for videre analyse.

## Funksjonalitet

### Hente luftkvalitetsdata fra NILU API

- **Koordinater for Oslo**:
    - **Breddegrad**: `59.9139`
    - **Lengdegrad**: `10.7522`
- **Tidsperiode**: 2010-01-01 til 2024-12-31
- **Radius**: `20 km`
- **API-endepunkt**:
    ```
    https://api.nilu.no/stats/day/{from_date}/{to_date}/{latitude}/{longitude}/{radius}
    ```

### Prosessering og lagring av data

- **Mappe**: `../../data/raw_data/`
- **Filnavn**: `air_quality_nilu_oslo.json`
- **Dataformat**: JSON

## Viktige funksjoner

### `get_air_quality_nilu_oslo()`

- Definerer **koordinater** og **tidsperiode** for Oslo.
- Setter opp API-endepunktet med riktige parametere.
- Importerer `fetch_air_quality_nilu` fra `niluAPI.get_data_niluAPI`.
- Henter og lagrer dataene som en JSON-fil.

### `fetch_air_quality_nilu()`

- Importert fra `niluAPI.get_data_niluAPI`.
- Utfører API-kallet og prosesserer rådataene til en strukturert JSON-fil.

## Forutsetninger

- **Python** installert med nødvendige avhengigheter.
- **Gyldig API-tilgang** til [NILU API](https://api.nilu.no/).
- **Tilgang til lagringsmappen** for å lagre JSON-filen.
