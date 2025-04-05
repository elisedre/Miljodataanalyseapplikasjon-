# Miljødataanalyseapplikasjon

Denne mappen samler inn miljødata fra åpne API-er, som NILU og Frost, og forbereder dem for analyse. All relevant kildekode ligger i src-mappen, som inneholder moduler for datainnhenting, transformasjon og strukturering av datasett for videre behandling og visualisering.

## Mappestruktur 

src/
├── frostAPI/
│   └── get_data_frostAPI.py       
├── niluAPI/
│   └── get_data_niluAPI.py        
├── README.md                     


## Beskrivelse av mapper og filer

### `frostAPI/`
Denne mappen inneholder kode relatert til Frost API (Meteorologisk institutt). Dette inkluderer funksjoner for å hente værdata som temperatur, nedbør og vind.

- **`get_data_frostAPI.py`**: Skript for å hente meteorologiske data fra Frost API.

### `niluAPI/`
Denne mappen inneholder kode relatert til NILU API (Norsk institutt for luftforskning). Dette inkluderer funksjoner for å koble til API-et, sende forespørsler og behandle svarene.

- **`get_data_niluAPI.py`**: Skript for å hente luftkvalitetsdata fra NILU API.


## Avhengigheter

Koden i `src`-mappen bruker følgende Python-moduler:
- **`requests`**: For å sende HTTP-forespørsler til API-ene (NILU og Frost).
- **`pandas`**: For å behandle og analysere data.





