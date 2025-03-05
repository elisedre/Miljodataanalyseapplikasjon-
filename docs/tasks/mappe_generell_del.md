# Prosjekt: Miljødataanalyse – generell del

![PROJECT](../../resources/images/project.png) \
Designed by [Freepik](https://www.freepik.com/)

## Målsetning

I dette prosjektet skal dere utvikle en applikasjon som henter, analyserer og visualiserer miljødata fra åpne kilder, som værdata, luftkvalitetsdata, havnivådata etc. Prosjektet gir dere praktisk erfaring med programmeringskonsepter, dataanalyse og visualisering, samt innføring i versjonshåndtering og enhetstesting. Gjennom disse ferdighetene vil dere bli bedre rustet til å håndtere mer komplekse programmeringsoppgaver i fremtiden. Prosjektet bidrar ikke bare til å utvikle ferdigheter som er relevante for datavitenskap, men hever også den generelle kompetansen innen programvareutvikling.

## Innledning og bakgrunn

I dagens samfunn er det en økende bevissthet rundt miljøspørsmål, drevet av bekymringer om klimaendringer, forurensning og bærekraftig utvikling. For å kunne ta informerte beslutninger og utvikle effektive strategier for å håndtere disse utfordringene, er det avgjørende å ha tilgang til og forståelse av miljødata. Miljødata kan gi innsikt i en rekke faktorer, inkludert værmønstre, luftkvalitet, vannkvalitet og økosystemers helse. Ved å analysere disse dataene kan vi identifisere trender, forutsi fremtidige forhold og utvikle tiltak for å forbedre miljøet. For mer informasjon om dette kan en studere f.eks. [IPCC rapporter](https://www.ipcc.ch/reports/) som gir vurdering av klimaendringer og deres konsekvenser.

Prosjektet med utvikling av en miljødataanalyseapplikasjon gir dere en unik mulighet til å jobbe med virkelige datasett fra åpne kilder, som meteorologiske institutter (f.eks. developer.yr.no) og miljøovervåkingsorganisasjoner (f.eks. <https://www.eea.europa.eu/en/analysis>). Dette gir ikke bare praktisk erfaring, men også en dypere forståelse av hvordan data kan brukes til å belyse komplekse miljøspørsmål. Gjennom prosjektet vil dere lære å navigere i ulike datakilder, vurdere datakvalitet og pålitelighet, samt anvende programmeringsferdigheter for å hente, bearbeide og analysere data.

I tillegg til å utvikle tekniske ferdigheter, vil prosjektet også fremme kritisk tenkning og problemløsning. Dere vil bli utfordret til å identifisere relevante datakilder, håndtere manglende verdier og uregelmessigheter i dataene, samt bruke statistiske metoder for å trekke meningsfulle konklusjoner. Dette er essensielle ferdigheter, spesielt i en tid der datadrevne beslutninger blir stadig mer sentrale i både offentlig og privat sektor.
Videre vil prosjektet gi dere innsikt i viktigheten av versjonshåndtering og enhetstesting, som er kritiske komponenter i moderne programvareutvikling. Ved å bruke verktøy som Gitlab/GitHub for versjonering og unittest for testing, vil dere lære hvordan man sikrer kodekvalitet og samarbeider effektivt i team. Dette vil ikke bare heve deres tekniske kompetanse, men også forberede dere på kravene i arbeidsmarkedet, hvor samarbeid og kvalitetssikring er avgjørende.

## Generelle krav og betingelse

### Enhetstesting

Skrive enhetstester ved hjelp av unittest-rammeverket for å sikre at funksjonene i applikasjonen fungerer som forventet. Dere må utvikle enhetstester (både positive og negative) for den delen av koden som er kritisk, det vil si for den koden som er mest avgjørende for å oppfylle sentrale krav.

Sjekkpunkter:

- Har enhetstestene beskrivende navn som dokumenterer hva testene gjør?
- Tas det hensyn til både positive og negative tilfeller?
- Er testdekningen god nok?

### Versjonshåndtering

Bruke Git for å versjonere koden gjennom hele prosjektet, inkludert oppretting av grenene for forskjellige funksjoner og sammenslåing til hovedgrenen.

Sjekkpunkter:

- Er prosjektet underlagt versjonskontroll med sentral repro?
- Sjekkes det inn jevnlig?
- Beskriver commit-meldingene endringene på en kort og konsis måte?

### Dokumentasjon

Det er viktig at dere følger god praksis for dokumentasjon av kode og annen prosjektdokumentasjon, inkludert kildehenvisning. For å sikre at koden er lesbar og vedlikehold bar, anbefales det å følge standarder for kodestil, som f.eks. PEP 8 for Python eller Googles Python Style Guide, som gir retningslinjer for formatering, navngivning og strukturering av koden. Dette inkluderer bruk av beskrivende variabelnavn, riktig innrykk, og konsistent bruk av kommentarer for å forklare komplekse logiske trinn. Videre er det viktig å dokumentere kildene til dataene som benyttes i prosjektet, inkludert API-er og åpne datakilder, for å sikre transparens og etterprøvbarhet. Kildereferanser bør inkludere informasjon om kildeautoritet, datakvalitet og tilgjengelighet, og bør presenteres i en klar og konsistent form. Ved å følge disse retningslinjene vil dere ikke bare forbedre kvaliteten på prosjektet, men også utvikle ferdigheter som er essensielle for fremtidig arbeid.

Sjekkpunkter:

- Er all kode og annen prosjektdokumentasjon godt dokumentert, med tydelige forklaringer og kildereferanser?
- Følger anbefalte standarder, som PEP 8 for Python for kodestil?
- Dokumenterer hvor dataene kommer fra, inkludert API-er og åpne datakilder?

### Verktøy og Biblioteker

- Python
- Jupyter Notebook
- Pandas (for databehandling)
- NumPy (for numeriske beregninger)
- Matplotlib/Seaborn/Plotly (for visualisering)
- Pandas SQL

### Tidsplan

- Uke 6-7: Oppsett av utviklingsmiljø og datainnsamling.
- Uke 8-11: Databehandling og analyse (Innlevering av mappedel 1: 23.03.2025).
- Uke 12-14: Visualisering og prediktiv analyse (Innlevering av mappedel 2: 27.04.2025 ).
- Uke 15-21: Videreutvikling av prosjektet, testing, dokumentasjon.
- Uke 22: Prosjektinnlevering (27.05.2025 kl. 14:00).

### Resultater

Ved prosjektets slutt får studentene en fungerende applikasjon som de leverer i Inspera for vurdering. Dette prosjektet er designet for å styrke deres programmeringsferdigheter, forståelse av dataanalyse og samarbeidskompetanse gjennom praktisk anvendelse.

### Generelle vurderingskriterier

1. Kvaliteten på datainnsamlingen og forberedelsen
    Vurderingen av datainnsamlingen vil fokusere på hvor godt dere har identifisert relevante og pålitelige åpne datakilder. Det vil også bli vurdert hvordan dere har implementert funksjonalitet for å hente data ved hjelp av Python-moduler, samt deres evne til å håndtere ulike datatyper som tekstfiler, CSV og JSON. Kvaliteten på databehandlingen, inkludert rensing og formatering av dataene, samt håndtering av manglende verdier og uregelmessigheter, vil også være sentral i vurderingen.

    - Identifiserer relevante og pålitelige åpne datakilder.
    - Implementerer funksjonalitet for å hente data ved hjelp av Python-moduler.
    - Håndterer ulike datatyper som tekstfiler, CSV og JSON.
    - Sikre god kvalitet på databehandlingen, herunder:
        - Renser og formatere dataene korrekt
        - Håndterer manglende verdier og uregelmessigheter på en hensiktsmessig måte

2. Dyktighet i dataanalyse og bruk av statistiske metoder
    Dette kriteriet vurderer deres evne til å anvende NumPy og Pandas for å analysere dataene. Det vil bli sett på hvor godt dere kan beregne statistiske mål som gjennomsnitt, median og standardavvik. Anvender NumPy og Pandas for å analysere dataene.

3. Kvaliteten og klarheten i visualiseringene
    Vurderingen av visualiseringene vil fokusere på brukt av Matplotlib, Seaborn, Plotly eller Bokeh for å presentere dataene. Kvaliteten på visualiseringene vil bli vurdert ut fra hvor godt dere kommuniserer informasjon, inkludert bruk av passende diagramtyper, fargevalg, aksetitler og legender.

    - Bruker visualiseringsbiblioteker som Matplotlib, Seaborn, Plotly eller Bokeh for å presentere dataene.
    - Kvalitet på visualiseringene, herunder:
        - Bruk av passende diagramtyper
        - Fargevalg
        - Aksetitler
        - Legender
    - Klarhet i visualiseringene for å kommunisere informasjon på en informativ og lettfattelig måte for målgruppen.

4. Versjonskontroll
    - Lokalt/sentralt repo, commits og branching:
        - Prosjektet har sentralt repo (GitHub/GitLab).
        - Fornuftig jevnlig innsjekking (commit) av endringer.
        - Gode commit-meldinger som beskriver kort hvilke endringer som er gjort/hvilke problem som er løst.
        - Har benyttet greiner som del av arbeidsflyt (f.eks. develop/main), for features/utprøving og liknende.
        - Har gjennomført merge mellom greiner.
        - Har benyttet tags for å merke versjoner.

    - Filer lagt til versjonskontroll
        - Benytter .gitignore
        - Har filtrert bort de fleste filer og mapper
        - Sjekker ikke inn viruelt miljø i versjonskontrollsystemet.
        - Versjonshåndterer requirements-filen.
        - Har opprettet README.md-fil som gir en kort beskrivelse av prosjektet, og info om hvordan bygge og kjøre applikasjonen

5. Enhetstesting
    - Har gode beskrivende navn på testene
    - Har enhetstester for de viktigste funksjonene
    - Har helt greie negative tester (viser at kandidaten har forstått hovedpoenget med positive/negative tester)

6. Filhåndtering
    - Leser fra tekstfil
    - Begrenset eller ingen sjekk/kontroll av filformat/struktur
    - Enkel håndtering av unntak
    - Skriver til tekstfil
    - Lukker filressurser på en trygg måte

7. KI deklarasjon
KI-deklarasjonen som finnes under `docs\ki` i dette repoet skal fylles ut og undertegnes av *hver* student i gruppen. Den skal leveres sammen med den endelige prosjektleveransen i Inspera.
