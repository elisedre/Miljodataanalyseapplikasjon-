# 📚 Innhold og struktur: Notebooks

*Beskriver innholdet i den enkelte notebook, forklarer strukturen og hvorfor vi har valgt å gjøre det slik.*

## Innhold

- Beskrivelse
- Struktur
- Innhold i notebooks

## Beskrivelse

Prosjektet bruker **Jupyter Notebooks** for å håndtere miljødata fra eksterne API-er. Notebookene har to hovedroller:

1. **Datainnhenting og rensning**: Notebookene inneholder spesifikke funksjoner som kaller generelle funksjoner fra `py`-filer for å hente, lagre og rense data.
2. **Analyse og visualisering**: Analysere og visualisere de innsamlede dataene ved hjelp av matematiske funksjoner og diagrammer.

Ved gjennomgang av hver notebook vil man oppnå en oversikt over prosjektet. De gir til sammen en helhetlig forståelse av hele arbeidsflyten, og gjør det enkelt å følge prosessen steg for steg. 

## Struktur

Prosjektet er strukturert slik at alt arbeid relatert til Frost API er samlet i én notebook ([frostAPI.ipynb](../notebooks/frostAPI/frostAPI.ipynb)), alt arbeid relatert til NILU API er samlet i én notebook ([niluAPI.ipynb](../notebooks/niluAPI/niluAPI.ipynb)), mens analyser og sammenligninger som involverer begge datasett er samlet i en felles notebook ([combined_analysis.ipynb](../notebooks/combined/combined_analysis.ipynb)). Dette gir en ryddig og logisk arbeidsflyt, der hver notebook har et tydelig fokusområde. 

```
notebooks/
├── frostAPI.ipynb     
├── niluAPI.ipynb         
├── combined_analysis.ipynb           
└── README.md  
```

## Innhold i notebooks

Her følger en beskrivelse av innholdet og hovedfokuset i hver notebook:

---

### `frostAPI.ipynb`
Denne notebooken tar for seg hele arbeidsflyten for værdata hentet fra Frost API.

**Innhold:**
- Henting av rådata fra Frost API.
- Rensing og kvalitetssikring av data (fjerning av manglende verdier, uteliggere og duplikater).
- Transformasjon og aggregering av data.
- Analyse av temperatur, nedbør og vindhastighet.
- Visualisering av trender og sesongvariasjoner.
- Tolkning og diskusjon av funn.

---

### `niluAPI.ipynb`
Denne notebooken håndterer luftkvalitetsdata fra NILU API.  

**Innhold:**
- Henting av rådata fra NILU API.
- Rensing og transformasjon av luftkvalitetsdata (NO₂, O₃, SO₂).
- Analyse av nivåer og variasjoner for de ulike komponentene.
- Visualisering av luftkvalitet over tid med interaktive grafer.

---

### `combined_analysis.ipynb`
Denne notebooken samler analyser og visualiseringer som involverer både værdata og luftkvalitetsdata.  

**Innhold:**
- Sammenstilling av datasett fra Frost og NILU.
- Analyse av sammenhenger mellom værforhold og luftkvalitet.
- Visualisering av korrelasjoner og felles trender.
- Tverrfaglig tolkning og diskusjon av resultater.
- Prediktiv analyse.
- Oppsummering av hovedfunn på tvers av datakilder.

---

*For mer detaljer og forklaringer, se de utfyllende markdown-beskrivelsene inne i hver notebook.*

> **Tips:**  
> Det anbefales å starte gjennomgangen i [frostAPI.ipynb](../notebooks/frostAPI/frostAPI.ipynb), da denne notebooken anses som "starten" av prosjektstien. 