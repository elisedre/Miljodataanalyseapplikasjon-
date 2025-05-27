# 🚀 Releasenote - Miljødataanalyseapplikasjon

**Dato:** 27.05.2025

**Versjon:** 1.0

### Introduksjon

Releasenotatet beskriver den første versjonen laget i miljøaanalyseprosjektet. Applikasjonen er utviklet som en del av emnet TDT4114 ved NTNU.

Applikasjonen henter vær- og luftkvalitetsdata fra **Frost API** og **NILU API** fra Oslo (SN18700) i tidsperioden 02.04.2010-30.12.2016.

### 🔧 Høydepunker ved versjon 1.0:

#### Henting av data
- Applikasjonen henter daglige vær og luftkvalitetsdata og bearbeider disse fra et JSON-format til en strukturert pandas-DataFrame. Resultatet lagres som `.json` i en prosjektstrukturert mappe for videre bruk. 

#### Rensing og klargjøring av data
- Applikasjon renser rådataene ved å identifisere og fjerne uteliggere basert på statistiske grenser.
- Duplikater fjernes. 
- Manglende og fjernede verdier interpoleres for å sikre kontinuitet i datasettet. 
- Renset datasett lagres separat for transparens og sporbarhet. 
- Visualisering brukes til å støtte beslutninger om datakvalitet og dokumentere rensing. 

#### Analyse og visualisering
- Dataene analyseres for å identifisere trender og mønstre i Oslo over tid. 
- Bruker blant annet `pandas`, `pandasql`, `matplotlib`, `plotly` og `seaborn` til både analyse og visualisering.
- Markdown-forklaringer dokumenterer observasjoner og gir fyldige tolkninger. 

#### Prediktiv analyse

- Applikasjonen inneholder en modul for **lineær regresjon og LGBM_modellering** for å forutsi fremtidige værverdier basert på historiske data.
- Standardiserte og transformerte data (Yeo-Johnson) brukes for bedre modellpresisjon. 
- Evalueres med R² og RMSE for å vurdere modellkvalitet.

#### Enhetstesting
- Det er utviklet omfattende enhetstesting for samtlige funksjoner i prosjektet. Dette sikrer både pålitelige resultater og trygg videreutvikling. 

#### ✅ Forslag til videreutvikling
- Større spenn av data:
    - Større tidspenn 
    - Flere datatyper
    - Data fra andre geografiske områder 
- Ytterligere prediktiv analyse


#### Ansvarlige utviklere 
Kaja Aamlid, Elise Dreiem, Josefine Huffman
