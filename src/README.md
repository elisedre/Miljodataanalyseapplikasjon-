# README for `src`-mappen

## 1. Introduksjon
`src`-mappen inneholder all kildekode for prosjektets kjernelogikk i form av funksjoner. Funksjonene i denne mappen importeres og benyttes i Notebooks-mappen for videre analyse og visualisering av data. Denne mappen er delt opp i moduler for hvert API (NILU og Frost), som henter og behandler miljødata.

## 2. Mappestruktur
src/
├── frostAPI/
│   └── get_data_frostAPI.py
├── niluAPI/
│   └── get_data_niluAPI.py
├── README.md

- **`frostAPI/`**: Inneholder koden for å hente og behandle data fra Frost API.
- **`niluAPI/`**: Inneholder koden for å hente og behandle data fra NILU API.

Hver mappe inneholder en Python-fil som utfører følgende trinn:
1. **Data innhenting**: Henter miljødata fra åpen API ved hjelp av Python og lagrer det som rådata i `.json`-filer.
2. **Data rensking**: Etter at rådata er hentet, behandles og struktureres dataene før de lagres som rensede `.json`-filer.
3. **Data visualisering**: Lager visualiseringer basert på de analyserte dataene.

## 3. Nøkkelhåndtering
- **Frost API** krever en klient-ID (API-nøkkel), som lastes inn fra en `.env`-fil.
- **NILU API** er offentlig og krever ingen autorisering.

## 4. Avhengigheter
For å kjøre koden i `src`-mappen, trenger du følgende Python-moduler:
- **`requests`**: For å sende HTTP-forespørsler til API-ene (NILU og Frost).
- **`pandas`**: For å behandle og analysere data.
- **`matplotlib`**: For å lage statiske grafer.
- **`plotly`**: For å lage interaktive grafer i Jupyter Notebooks.
....

### Installering av avhengigheter
Du kan installere alle nødvendige avhengigheter ved å kjøre følgende kommando:

```bash
pip install -r requirements.txt



