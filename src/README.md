# 🧠 README for `src`-mappen

## 1. Introduksjon
`src`-mappen inneholder all kildekode for prosjektets kjernelogikk i form av funksjoner. Funksjonene i denne mappen importeres og benyttes i Notebooks-mappen.  

## 2. 📁 Mappestruktur 
```
├── src/
│   ├── frostAPI/              
│   │   ├── _init_.py      
│   │   ├── analyze_data_frost.py      
│   │   └── clean_data_frost.py 
│   │   ├── fetch_frostapi.py     
│   │   ├── main_frost.py    
│   │   └── visualization_frost.py
│   │   
│   ├── niluAPI/              
│   │   ├── _init_.py      
│   │   ├── analyze_data_nilu.py      
│   │   └── clean_data_nilu.py 
│   │   ├── fetch_niluapi.py     
│   │   ├── main_nilu.py    
│   │   └── visualization_nilu.py   
│   │
│   ├── combined_analysis/      
│   │   └── combined_analysis.py
│   │
│   ├── README.md     
│   │
│   └── sql_analysis/           
│       └── sql_analysis.py
```
Begrunnelse for filstrukturen:

- Delte opp APIene i separate mapper for bedre oversikt
- At hver mappe er "oppgavefordelt" bidrar også til bedre orden - klare, beskrivende filnavn gjør det intuitivt å finne relevant kode for hvert steg i prosessen.
- Mappen `combined_analysis` gjør det tydelig at funksjonene gjelder flere datakilder.
- Alle moduler ligger under `src/` for å samle alt kodearbeid på ett sted - god kodepraksis 

## Filbeskrivelser 

### `src/frostAPI/`
- **`fetch_frostapi.py`**  
  Funksjoner for å hente værdata fra Frost API. Inneholder API-kall, autentisering og datainnhenting.

- **`clean_data_frost.py`**  
  Funksjoner for rensing og klargjøring av rådata fra Frost API. Håndterer uteliggere, manglende verdier og formatering.

- **`analyze_data_frost.py`**  
  Analysefunksjoner for Frost-data, inkludert statistikk, trender og korrelasjonsanalyser.

- **`visualization_frost.py`**  
  Kode for visualisering av Frost-data med grafer og diagrammer.

- **`main_frost.py`**  
  Hovedfil for å kjøre hele prosessen med Frost API-data: henting, rensing, analyse og visualisering.

- **`__init__.py`**  
  Gjør `frostAPI` til en Python-pakke.

---

### `src/niluAPI/`
- **`fetch_niluapi.py`**  
  Funksjoner for henting av luftkvalitetsdata fra NILU API.

- **`clean_data_nilu.py`**  
  Rensing og preprosessering av rå NILU-data, inkludert behandling av uteliggere og manglende verdier.

- **`analyze_data_nilu.py`**  
  Analysefunksjoner for NILU-data, for eksempel statistikk og mønstergjenkjenning.

- **`visualization_nilu.py`**  
  Visualisering av NILU-data gjennom plott og grafer.

- **`main_nilu.py`**  
  Hovedfil for å kjøre hele NILU API-dataflyten fra henting til analyse.

- **`__init__.py`**  
  Gjør `niluAPI` til en Python-pakke.

---

### `src/combined_analysis/`
- **`combined_analysis.py`**  
  Funksjoner for å kombinere og analysere data på tvers av Frost API og NILU API for helhetlig innsikt.

---

### `src/sql_analysis/`
- **`sql_analysis.py`**  
  Skript for SQL-basert analyse av data, inkludert spørringer og oppsett.

---

### `src/README.md`
- Prosjektdokumentasjon som forklarer struktur, formål og samspill mellom moduler.


## Konvensjoner i `src/` 

Denne seksjonen beskriver retningslinjer og strukturvalg som er fulgt i `src/`-mappen for å sikre **lesbarhet**, **gjenbrukbarhet** og **vedlikeholdbarhet** i koden.

#### Mapper og modulstruktur

- **Navnekonvensjoner**:  
  - Mapper, filnavn, funksjoner og variabler bruker `snake_case`  

#### Kodekonvensjoner

- **PEP8** følges som standard for Python-kode.
- Importer gruppert: standardbibliotek → eksternt → egne moduler.
- Ikke bruk av **from x import *.**

#### Funksjonsdesign

- Alle funksjoner har docstrings.
- Funksjonene gjør **én ting hver** (Single Responsibility Principle).

---

### Bruk av docstring
I prosjekter hvor man kombinerer Jupyter Notebooks med modulære .py-filer, er det spesielt viktig med tydelig og konsistent dokumentasjon av funksjoner. Her spiller docstrings en sentral rolle. En docstring er en streng skrevet rett etter en funksjonsdefinisjon, som forklarer hva den gjør, hvilke argumenter den tar, og hva den returnerer. Dette gir umiddelbar dokumentasjon, både for utvikleren selv og for andre som bruker eller gjenbruker koden.

#### Grunner til at docstrings var nyttige for oss:
Når man utvikler kode i `.py`-filer og bruker den videre i notebooks via `import`, blir dokumentasjonen ofte mindre synlig sammenlignet med kommentarer inne i en notebook. Docstrings løser dette ved å:

- **Styrke gjenbruk og modularisering:**

  Ved å skrive `.py`-filer som moduler med gode docstrings, kan man lett gjenbruke funksjoner i ulike notebooks eller prosjekter uten å måtte åpne kildekoden for å forstå hvordan de brukes.

- **Forbedre samarbeidsflyt:**

  Når flere jobber på samme prosjekt, sørger docstrings for at alle forstår hva en funksjon gjør, hva slags input den forventer, og hva som returneres – uten at man trenger egne møter eller lang forklaring.

- **Effektiv utvikling med editorer:**

  De fleste moderne utviklingsverktøy, i dette tilfeller VS Code, viser docstrings når du holder musen over et funksjonsnavn eller bruker autocomplete. Dette gir en stor utviklerfordel.

  ### 📘 Docstring-mal

Vi dokumenterer hver funksjon med en docstring rett etter `def`-linjen. Formatet vårt følger dette mønsteret:

```python
def funksjonsnavn(param1, param2, ...):
    """
    Kort og presis beskrivelse av hva funksjonen gjør, på norsk.

    Args:
        param1 (type): Beskrivelse av første parameter.
        param2 (type): Beskrivelse av neste parameter.
        ... flere parametre ved behov.

    Returns:
        returtype: Forklaring på hva som returneres, evt. rekkefølge i en tuple.
    """
```

--- 

## 4.  🔑 Nøkkelhåndtering
- **Frost API** krever en klient-ID (API-nøkkel), som lastes inn fra en `.env`-fil.
- **NILU API** er offentlig og krever ingen autorisering.

---

## 5. 🔗 Avhengigheter

For å kjøre koden i `src`-mappen, trenger du følgende Python-moduler:

- **`requests`**: For å sende HTTP-forespørsler til API-ene (NILU og Frost).
- **`pandas`**: For å behandle og analysere data.
- **`numpy`**: For numeriske beregninger, som gjennomsnitt og standardavvik.
- **`matplotlib`**: For å lage statiske grafer og visualisere tidsseriedata.
- **`seaborn`**: For avanserte visualiseringer og distribusjonsgrafer.
- **`scipy`**: For statistiske beregninger, som korrelasjonsanalyse (`pearsonr`).
- **`scikit-learn`**: For datatransformasjoner, maskinlæring, `PowerTransformer`, `StandardScaler`, `LinearRegression`, m.m.
- **`plotly`**: For å lage interaktive grafer i Jupyter Notebooks.
- **`pandasql`**: For å utføre SQL-spørringer på Pandas DataFrames.
- **`json`**: For å lese og skrive JSON-data (innebygd i Python).
- **`os`**: For filhåndtering og miljøvariabler (innebygd i Python).
- **`sys`**: For å endre søkestier og systemspesifikke funksjoner (innebygd i Python).
- **`dotenv`**: For å laste inn miljøvariabler fra `.env`-filer.
- **`missingno`**: For å visualisere manglende data.
- **`lightgbm`**: For maskinlæringsmodellen `LGBMRegressor`.
- **`datetime`**: For håndtering av datoer og tid (innebygd i Python).


> Alle nødvendige pakker kan installeres med `pip install -r requirements.txt`.
