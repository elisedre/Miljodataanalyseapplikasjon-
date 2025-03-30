# Datahåndtering og Analyse Notebooks

*Dette prosjektet inneholder notebooks for datainnhenting, prosessering og analyse av miljødata.*

## Innhold

- Beskrivelse
- Strukturen i prosjektet


## Beskrivelse

Prosjektet bruker **Jupyter Notebooks** for å håndtere miljødata fra eksterne API-er. Notebookene har to hovedroller:

1. **Datainnhenting**: Notebookene inneholder spesifikke funksjoner som kaller generelle funksjoner fra `py`-filer for å hente og lagre data i JSON-format.
2. **Analyse og visualisering**: Noen notebooks er dedikert til å analysere og visualisere de innsamlede dataene ved hjelp av matematiske funksjoner og diagrammer.

## Strukturen i prosjektet

- **Datainnhenting (Notebooks for API-kall)**  
  - Notebookene inneholder **spesifikke funksjoner** for å hente data fra eksterne API-er.
  - Bruker **generelle funksjoner** fra Python-moduler (`.py`-filer) for å utføre API-kall.
  - Lagrede data blir formatert og lagret som **JSON-filer**.

- **Analyse og visualisering (Notebooks for databehandling)**  
  - Leser inn JSON-data fra datainnhentingsnotebookene.
  - Utfører analyser ved hjelp av statistiske og matematiske funksjoner.
  - Visualiserer data med grafer og diagrammer.
