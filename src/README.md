# README for `src`-mappen

## 1. Introduksjon
`src`-mappen inneholder all kildekode for prosjektets kjernelogikk i form av funksjoner. Funksjonene i denne mappen importeres og benyttes i Notebooks-mappen.  

## 2. Mappestruktur (ikke ferdig)

## Filbeskrivelser (ikke ferdig)


### `data_frostAPI.py`

- **API-integrasjon**: Uthenting av elementer, stasjoner og observasjonsdata fra Frost API.
- **Dataprosessering**: Strukturering, aggregering og lagring av JSON-data.
- **Datakvalitet**: Håndtering av duplikater, outliers og manglende verdier.
- **Analyse**: Statistikk, skjevhet, transformasjoner og sesongtrender.
- **Visualisering**: Histogrammer, outliers og tidsserieanalyse.

### `data_niluAPI.py`

- **API-integrasjon**: Uthenting av observasjonsdata fra Nilu API.
- **Dataprosessering**: Strukturering, aggregering og lagring av JSON-data.
- **Datakvalitet**: Håndtering av duplikater, outliers og manglende verdier.
- **Analyse**: Statistikk, skjevhet og transformasjoner.
- **Visualisering**: Histogrammer, outliers og tidsserieanalyse.

### `kombinert_analyse.py`

- Kombinerer og sammenligner Frost- og NILU-data for felles analyse.

### `analysis_sql.py`

- Benytter SQL (via `pandasql`) til analyse direkte på Pandas-dataframes.

---

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

## 4. Nøkkelhåndtering
- **Frost API** krever en klient-ID (API-nøkkel), som lastes inn fra en `.env`-fil.
- **NILU API** er offentlig og krever ingen autorisering.

---

## 5. Avhengigheter (ikke ferdig)
For å kjøre koden i `src`-mappen, trenger du følgende Python-moduler:

- **`requests`**: For å sende HTTP-forespørsler til API-ene (NILU og Frost).
- **`pandas`**: For å behandle og analysere data.
- **`numpy`**: For numeriske beregninger, som gjennomsnitt og standardavvik.
- **`matplotlib`**: For å lage statiske grafer og visualisere tidsseriedata.
- **`seaborn`**: For avanserte visualiseringer og distribusjonsgrafer.
- **`scipy`**: For statistiske beregninger, som korrelasjonsanalyse (`pearsonr`).
- **`scikit-learn`**: For datatransformasjoner, som `PowerTransformer` og skalering med `StandardScaler`.
- **`plotly`**: For å lage interaktive grafer i Jupyter Notebooks.
- **`pandasql`**: For å utføre SQL-spørringer på Pandas DataFrames.
- **`json`**: For å lese og skrive JSON-data (innebygd i Python).

