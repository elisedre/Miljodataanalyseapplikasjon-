# 💾 Datasettvalg for miljøanalyse

I dette prosjektet har vi valgt datasett som gir innsikt i miljøforholdene over tid, med fokus på værdata og luftkvalitet. Datasettvalgene er gjort for å dekke ulike aspekter av miljøanalyse, som temperatur, nedbør, vindhastighet og luftforurensning. Disse datasettene er hentet fra pålitelige kilder som Frost API og NILU API.

## Struktur 

Datamappen er strukturert slik:

```
data/
├── analyzed_data/
│   ├── frostAPI_analyzed_data.json
│   └── niluAPI_analyzed_data.json
├── clean_data/
│   ├── frostAPI_clean_data.json
│   └── niluAPI_clean_data.json
├── raw_data/
│   ├── frostAPI_data.json
│   └── niluAPI_data.json
└── README.md
```
- **[raw_data/](../data/raw_data/)**: Inneholder rådata hentet direkte fra API-ene.
- **[clean_data/](../data/clean_data/)**: Inneholder rensede og ferdigbehandlede datasett klare for analyse.
- **[analyzed_data/](../data/analyzed_data/)**: Inneholder datasett som er analysert eller transformert videre, f.eks. med transformasjoner.

Å strukturere datamappen på denne måten har flere fordeler:

- **Orden:** Det er viktig å skille mellom rådata, rensede data og analyserte data for å lettere holde oversikt hvor i prosessen et datasett befinner seg.
- **Reproduserbarhet:**: Siden rådataene alltid bevares i `raw_data/` kan man alltid gå tilbake og reprodusere rensingen eller analysen om det er behov for dette. 
- **Datakvalitet:** Ved å ha en egen mappe for `clean_data/` sikrer du at videre analyse kun gjøres på data som er kvalitetssikret og fri for feil, manglende verdier og duplikater. 

## Beskrivelse av valgte datasett

Prosjektet benytter data fra to hovedkilder: **FrostAPI** og **NILU API**. Datasettene inneholder miljø- og værdata for Oslo over en lengre tidsperiode (en tidsperiode på seks år gir oss grunnlag for å vurdere om det er trender eller bare naturlig variasjon når vi analyserer data). 

### FrostAPI
- **Tidsperiode**: 2010-04-02 til 2016-12-30
- **Parametere**:
    1. Temperatur (°C)
    2. Nedbør (mm)
    3. Vindhastighet (m/s)
### NILU API
- **Tidsperiode**: 2010-04-02 til 2016-12-30
- **Parametere**: 
    1. NO₂ (Nitrogendioksid)
    2. O₃ (Ozon)
    3. SO₂ (Svoveldioksid)
    4. Dekningsgrad NO₂ (%)
    5. Dekningsgrad O₃ (%)
    6. Dekningsgrad SO₂ (%)

## Bakgrunn for valg av parametere 

Valget av parametere er basert på deres relevans for miljøanalyse:
- **Temperatur, nedbør og vindhastighet** er viktige faktorer for klimaanalyse og værmodeller.
- **Luftfoururensingsparametere (NO₂, O₃, SO₂)** brukes til å vurdere luftkvalitet og analysere dens påvirkning på klimaendringer.
- **Dekningsgrad for luftforurensningsparametere** brukes for å vudere datakvalitet og identifisere perioder med manglende målinger.


## Bakgrunn for valg av API 

### FrostAPI
- Gir et pålitelig datasett med god data.
- Velegnet for videre prediktiv analyse.
### NILU API
- Inneholder luftkvalitetsdata med ufullstendige registreringer.
- Krever omfattende datarensing og behandling, noe som gir erfaring med håndtering av manglende verdier.


