# Mappe del 1

## Oppgaver: Oversikt

I dette prosjektet skal dere gjennomføre oppgaver som fokuserer på oppsett av utviklingsmiljø, innsamling, behandling, analyse, visualisering og prediktiv analyse av miljødata. Oppgave 1 handler om å sette opp et fungerende utviklingsmiljø. Oppgave 2 innebærer å identifisere relevante åpne datakilder og implementere funksjonalitet for å hente data fra disse kildene ved hjelp av Python. I oppgave 3 skal dere utvikle funksjoner for å rense og formatere de innsamlede dataene, med fokus på håndtering av manglende verdier.

### Oppgave 1: Sett opp utviklingsmiljø

Før dere begynner med datainnsamlingen, er det viktig å sette opp et utviklingsmiljø som vil støtte dere gjennom hele prosjektet. Denne oppgaven vil veilede dere i å opprette et prosjekt i GitHub, installere nødvendige verktøy og opprette en test Jupyter Notebook for å sikre at alt fungerer som det skal.

1. Opprett et nytt «repository» på GitHub med et beskrivende navn for prosjektet (f.eks. "Miljødataanalyseapplikasjon"). Det skal opprettes en sentral repo for prosjektgruppen.
2. Last ned og installer den nyeste versjonen av Python fra den offisielle nettsiden (https://www.python.org/downloads/). Sørg for at Python er lagt til i systemets PATH under installasjonen.
3. Last ned og installer Visual Studio Code fra den offisielle nettsiden (https://code.visualstudio.com/). Åpne VSCode og installer nødvendige utvidelser for Python og Jupyter. Dette kan gjøres ved å gå til Extensions (Ctrl+Shift+X) og søke etter "Python" og "Jupyter".
4. Klon [dette repoet](https://git.ntnu.no/TDT4114/proj_environment.git) til din lokale maskin ved hjelp av Git (eller utviklingsverktøyet ditt).
5. I VSCode, opprett en ny Jupyter Notebook-fil (med filendelsen «.ipynb») i prosjektmappen. Skriv og kjør følgende kode i den første cellen for å teste at miljøet fungerer som det skal:

```Python
print("Utviklingsmiljøet er klart!")
```

NB! Du kan også repoet som mal for ditt prosjekt.

### Oppgave 2: Datainnsamling

I prosjektet for utvikling av en miljødataanalyseapplikasjon skal dere først identifisere relevante åpne datakilder, som f.eks. API-er fra meteorologiske institutter og miljøovervåkingsorganisasjoner. Deretter skal dere implementere funksjonalitet for å hente data fra disse kildene ved hjelp av Python-moduler (som eks. requests). For å integrere dataene i applikasjonen, bruker dere teknikker som håndtering av tekstfiler, CSV-filer, JSON-data, samt fil- og katalogadministrasjon. I tillegg skal dere benytte dere av list comprehensions, iteratorer og Pandas SQL (sqldf) for å utforske og forstå dataenes struktur og innhold før de forberedes for videre analyse.

*Vurderingskriterier:*

1. Hvilke åpne datakilder er identifisert som relevante for miljødata, og hva er kriteriene (f.eks. kildeautoritet, datakvalitet, tilgjengelighet, brukervennlighet osv.) for å vurdere deres pålitelighet og kvalitet?
2. Hvilke teknikker (f.eks. håndtering av CSV-filer, JSON-data) er valgt å bruke for å lese inn dataene, og hvordan påvirker disse valgene datakvaliteten og prosessen videre?
3. Dersom det er brukt API-er, hvilke spesifikke API-er er valgt å bruke, og hva er de viktigste dataene som kan hentes fra disse kildene?

### Oppgave 3: Databehandling

Her skal dere fokusere på databehandling ved å utvikle funksjoner som renser og formaterer de innsamlede dataene, med særlig vekt på håndtering av manglende verdier og uregelmessigheter ved hjelp av Pandas. I tillegg skal dere benytte teknikker som list comprehensions, iteratorer, pandas og pandas sql (sqldf) for å manipulere dataene effektivt, noe som vil bidra til å forberede dataene for videre analyse.

*Vurderingskriterier:*

1. Hvilke metoder vil du bruke for å identifisere og håndtere manglende verdier i datasettet?
2. Kan du gi et eksempel på hvordan du vil bruke list comprehensions for å manipulere dataene?
3. Hvordan kan Pandas SQL (sqldf) forbedre datamanipuleringen sammenlignet med tradisjonelle Pandas-operasjoner?
4. Hvilke spesifikke uregelmessigheter i dataene forventer du å møte, og hvordan planlegger du å håndtere dem?
