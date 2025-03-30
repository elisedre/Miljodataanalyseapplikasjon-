# Datasettvalg for miljøanalyse

*Beskriver valg av datasett.*

## Innhold

- Beskrivelse av valgte datasett
- Bakgrunn for valg av parametere 
- Bakgrunn for valg av API

## Beskrivelse av valgte datasett

Prosjektet benytter data fra to hovedkilder: **FrostAPI** og **NiluAPI**. Datasettene inneholder miljø- og værdata for Oslo over en lengre tidsperiode. 

### FrostAPI
- **Tidsperiode**: 2010-04-01 til 2022-04-03
- **Parametere**:
    1. Temperatur (°C)
    2. Nedbør (mm)
    3. Vindhastighet (m/s)
### NiluAPI
- **Tidsperiode**: 2010-01-01 til 2024-12-31
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
### NiluAPI
- Inneholder luftkvalitetsdata med ufullstendige registreringer.
- Krever omfattende datarensing og behandling, noe som gir erfaring med håndtering av manglende verdier.


