# Håndtering av Skjevhet i Data for Maskinlæring

*Dataen i denne mappen er behandlet for å normalfordele daten. dette skal brukes i maskinlæringsprosesseringen.Her beskrives hvordan skjevhet i dataene håndteres for bedre maskinlæring.*

## Innhold

- Beskrivelse av metoden for skjevhetshåndtering
- Bakgrunn for transformasjonen
- Hvordan dette hjelper i maskinlæringsmodellen

## Beskrivelse av metoden for skjevhetshåndtering

For å forbedre datakvaliteten før bruk i maskinlæringsmodeller, benytter prosjektet **Yeo-Johnson transformasjon** for å redusere skjevhet i numeriske data. Dette metoden er valgt da tempratur kan inneholde negative verdier som ikke andre  metoder kan håndtere.

### Hva gjør funksjonen `analyse_and_fix_skewness()`?

Funksjonen utfører følgende trinn:
1. Leser inn data fra en JSON-fil.
2. Analyserer skjevheten i numeriske kolonner.
3. Påfører **Yeo-Johnson transformasjon** på kolonner med høy skjevhet (over en angitt grense).
4. Lagrer de transformerte dataene i en ny JSON-fil for videre bruk.

### Yeo-Johnson transformasjon
- Brukes til å gjøre skjeve data mer symmetriske.
- Egner seg for både positive og negative verdier, og hjelper med å tilpasse dataene til antakelsene om normalfordeling i mange maskinlæringsmodeller.

## Bakgrunn for transformasjonen

Skjevhet i dataene kan forstyrre treningen av maskinlæringsmodeller. Skjevhet kan føre til dårligere prediksjon og unøyaktigheter i modellens resultater. Ved å bruke Yeo-Johnson transformasjonen, kan vi forbedre modellens ytelse ved å redusere skjevhet og gjøre dataene mer symmetriske.

## Hvordan dette hjelper i maskinlæringsmodellen

Når dataene er mer symmetriske:
- Maskinlæringsmodellen kan lære mer effektivt og oppnå bedre resultater.
- Forbedrer modellens evne til å generalisere på ukjent data.
- Reduserer risikoen for at modellen blir overtilpasset til skjeve data.

---