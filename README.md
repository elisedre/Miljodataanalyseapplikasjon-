# 📖 Prosjekt: Miljødataanalyse 

Prosjektet er en besvarelse på årets eksamensoppgave i **TDT4114 Anvendt programmering (2025 VÅR)**. Målet er å utvikle en applikasjon som henter, analyserer og visualiserer miljødata - hvorav vi har valgt å analysere værdata (Frost API) og luftkvalitetsdata (NILU API).

## 📌 Mål for prosjektet
- Hente og strukturere data fra åpne API-er (NILU og Frost).
- Rense og klargjøre datasett for analyse.
- Gjennomføre analyse gjennom utforskning av trender og undersøkelser av sammenhenger. 
- Visualisere data for bedre innsikt

## ▶️ Gjennomkjøring av prosjektet
Prosjektet er strukturert slik at hovedarbeidet utføres i Jupyter Notebooks:
- [Prosjekt Frost API](../notebooks/frostAPI/frostAPI.ipynb)
- [Prosjekt NILU API](../notebooks/niluAPI/niluAPI.ipynb)
- [Kombinert analyse](../notebooks/Kombinert_analyse.ipynb)

I notebookene går vi steg for steg gjennom datainnhenting, rensing, analyse og visualisering. Denne strukturen er valgt for å gi en logisk og modulær gjennomgang av prosjektet - vi oppnår en tydelig progresjon fra enkeltdatakilder til sammensatt analyse.

For å holde fremvisningen ryddig og oversiktlig er alle funksjoner som håndterer API-kall, databehandling og analyser samlet i Python-moduler plassert i `src`-mappen:
- [frostAPI.py](../src/frostAPI/data_frostAPI.py)
- [niluAPI.py](../src/niluAPI/data_niluAPI.py)
- [kombinert_analyse.py](../src/kombinert_analyse.py)
- [sql_analysis.py](../src/sql_analysis.py)

### Anbefalt gjennomkjøring:

Start med [Prosjekt Frost API](../notebooks/frostAPI/frostAPI.ipynb) og følg deretter notebookene videre for å få en full oversikt over hele arbeidsflyten og analysene. 

## ✅ Forutsetninger for gjennomkjøring
- Python (?) eller nyere 
- Installerte pakker eller venv??
- Tilgang til internett for API-kall??
- Mer?

## 💾 Installasjon av prosjektet

1. Klon prosjektet fra GitHub:

```bash
git clone https://github.com/elisedre/Miljodataanalyseapplikasjon.git
cd Miljodataanalyseapplikasjon 
```

2. Installer avhengigheter:

```bash
pip install -r requirements.txt
```

## 🔍 Kjøring av enhetstester 

Testene ligger i `tests/`-mappen ([tests](../tests/)).

For å kjøre alle:

```bash
python -m unittest discover tests
```





