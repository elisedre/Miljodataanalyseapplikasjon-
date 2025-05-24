# README for `src`-mappen

## 1. Introduksjon
`src`-mappen inneholder all kildekode for prosjektets kjernelogikk i form av funksjoner. Funksjonene i denne mappen importeres og benyttes i Notebooks-mappen.  

## 2. Mappestruktur


## 3. Bruk av Args


## 4. Nøkkelhåndtering
- **Frost API** krever en klient-ID (API-nøkkel), som lastes inn fra en `.env`-fil.
- **NILU API** er offentlig og krever ingen autorisering.

## 5. Avhengigheter## 4. Avhengigheter
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







