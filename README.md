# 📖 Prosjekt: Miljødataanalyse 

Prosjektet er en besvarelse på årets eksamensoppgave i **TDT4114 Anvendt programmering (2025 VÅR)**. Målet er å utvikle en applikasjon som henter, analyserer og visualiserer miljødata - hvorav vi har valgt å analysere værdata (Frost API) og luftkvalitetsdata (NILU API).

## 📌 Mål for prosjektet
- Hente og strukturere data fra åpne API-er (NILU og Frost).
- Rense og klargjøre datasett for analyse.
- Gjennomføre analyse gjennom utforskning av trender og undersøkelser av sammenhenger. 
- Visualisere data for bedre innsikt

## 🗂️ Mappestruktur

**Legger til mappestrukturen her når prosjektet er ferdigstilt**

## ▶️ Gjennomkjøring av prosjektet
Prosjektet er strukturert slik at hovedarbeidet utføres i Jupyter Notebooks:
- [Prosjekt Frost API](../notebooks/frostAPI/frostAPI.ipynb)
- [Prosjekt NILU API](../notebooks/niluAPI/niluAPI.ipynb)
- [Kombinert analyse](../notebooks/combined/combined_analysis.ipynb)

I notebookene går vi steg for steg gjennom datainnhenting, rensing, analyse og visualisering. Denne strukturen er valgt for å gi en logisk og modulær gjennomgang av prosjektet - vi oppnår en tydelig progresjon fra enkeltdatakilder til sammensatt analyse.

For å holde fremvisningen ryddig og oversiktlig er alle funksjoner som håndterer API-kall, databehandling og analyser samlet i Python-moduler plassert i `src`-mappen:
- [frostAPI/frostAPI.py](../src/frostAPI/data_frostAPI.py)
- [niluAPI/niluAPI.py](../src/niluAPI/data_niluAPI.py)
- [combined/combined_analysis.py](../src/combined/combined_analysis.py)
- [sql_analysis.py](../src/SQL/sql_analysis.py)

### Anbefalt gjennomkjøring:

Start med [Prosjekt Frost API](../notebooks/frostAPI/frostAPI.ipynb) og følg deretter notebookene videre for å få en full oversikt over hele arbeidsflyten og analysene. 

## ✅ Forutsetninger for gjennomkjøring

For å kunne kjøre prosjektet og reprodusere resultatene, må følgende forutsetninger være oppfylt:

1. **Python-versjon**:
   - Python 3.8 eller nyere er nødvendig for å sikre kompatibilitet med alle avhengigheter.

2. **Virtuelt miljø (anbefalt)**:
   - Opprett et virtuelt miljø for å isolere prosjektets avhengigheter:
	 ```bash
	 python -m venv venv
	 source venv/bin/activate  # For Mac/Linux
	 venv\Scripts\activate     # For Windows
	 ```

3. **Installerte pakker**:
   - Alle nødvendige Python-pakker må være installert. Dette kan gjøres ved å kjøre:
	 ```bash
	 pip install -r requirements.txt
	 ```

4. **Tilgang til internett**:
   - Internettforbindelse er nødvendig for å hente data fra Frost API og NILU API.

5. **API-nøkler**:
   - Gyldige API-nøkler og klient-ID-er for Frost API og NILU API må være konfigurert i en `.env`-fil:
	 ```
	 FROST_API_CLIENT_ID=din_frost_api_client_id
	 NILU_API_KEY=din_nilu_api_key
	 ```

6. **Datasett**:
   - Hvis du ikke ønsker å hente data fra API-ene, må rådataene være tilgjengelige i følgende filstier:
	 - [`data/raw_data/frostAPI_data.json`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fjosefinehuffman%2FDocuments%2FMiljodataanalyseapplikasjon--1%2Fdata%2Fraw_data%2FfrostAPI_data.json%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D]("/Users/josefinehuffman/Documents/Miljodataanalyseapplikasjon--1/data/raw_data/frostAPI_data.json")
	 - [`data/raw_data/niluAPI_data.json`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%22%2C%22path%22%3A%22%2FUsers%2Fjosefinehuffman%2FDocuments%2FMiljodataanalyseapplikasjon--1%2Fdata%2Fraw_data%2FniluAPI_data.json%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D]("/Users/josefinehuffman/Documents/Miljodataanalyseapplikasjon--1/data/raw_data/niluAPI_data.json")

7. **Operativsystem**:
   - Prosjektet er testet på MacOS, Linux og Windows. Sørg for at du har en kompatibel plattform.

8. **Tilleggsverktøy (valgfritt)**:
   - Jupyter Notebook eller JupyterLab for å kjøre og utforske notebooks i [`notebooks`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fjosefinehuffman%2FDocuments%2FMiljodataanalyseapplikasjon--1%2Fnotebooks%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D]("/Users/josefinehuffman/Documents/Miljodataanalyseapplikasjon--1/notebooks")-mappen.

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





