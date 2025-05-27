# 📁 Samleside for prosjektet - Miljødataanalyseapplikasjon 

## Dokumentasjon  
| Dokument | Beskrivelse |
| -------- | ----------- |
| [README - hoved](../Miljodataanalyseapplikasjon-/README.md) | Hovedoversikt over prosjektet |
|  [README - notebooks](../Miljodataanalyseapplikasjon-/notebooks/README.md) | Beskrivelse av notebook-strukturen |
|  [README - src](../Miljodataanalyseapplikasjon-/data/README.md) | Beskrivelse av kildekode og funksjoner  |
| [README - data](../Miljodataanalyseapplikasjon-/data/README.md)| Beskrivelse av datasettene
|  [README - tests](../Miljodataanalyseapplikasjon-/tests/README.md) | Informasjon om enhetstester  |

## Notebooks  
| Notebook | Beskrivelse |
| -------- | ----------- |
| [frostAPI.ipynb](../Miljodataanalyseapplikasjon-/notebooks/frostAPI/frostAPI.ipynb) | Datahenting og analyse fra Frost API (værdata)  |
| [niluAPI.ipynb](../Miljodataanalyseapplikasjon-/notebooks/niluAPI/niluAPI.ipynb) | Datahenting og analyse fra NILU API (luftkvalitet)  |
| [Kombinert_analyse.ipynb](../Miljodataanalyseapplikasjon-/notebooks/Kombinert_analyse.ipynb) | Kombinert analyse av miljødata fra begge kilder  |

## Data  
| Ressurs | Beskrivelse |
|--------|-------------|
| [data/](../Miljodataanalyseapplikasjon-/data/) | Lagring av rå og bearbeidede datasett (JSON) organisert i underkategorier |
| [raw_data/](../Miljodataanalyseapplikasjon-/data/raw_data/)| Rådata direkte fra APIene – ufiltrert og utransformert |
| [clean_data/](../Miljodataanalyseapplikasjon-/data/clean_data/)| Renset data med fjerning av mangler, outliers og inkonsistens |
| [analyzed_data/](../Miljodataanalyseapplikasjon-/data/analyzed_data/) | Ferdig analyserte og transformerte datasett klare for modellering og visualisering |


## Kildekode  
| Modul | Beskrivelse |
| ----- | ----------- |
| [data_frostAPI.py](../Miljodataanalyseapplikasjon-/src/frostAPI/data_frostAPI.py) | Funksjoner for datainnhenting, behandling og analyse fra Frost API |
| [data_niluAPI.py](../Miljodataanalyseapplikasjon-/src/niluAPI/data_niluAPI.py)| Funksjoner for datainnhenting, behandling og analyse fra NILU API |
| [kombinert_analyse.py](../Miljodataanalyseapplikasjon-/src/kombinert_analyse.py)| Funksjoner for analyse for Frost API og NILU API |
| [sql_analysis.py](../Miljodataanalyseapplikasjon-/src/sql_analysis.py) | Funksjoner som bruker SQL for analyse |

## Tester 
| Testmappe | Beskrivelse |
| --------- | ----------- |
| [tests_frostAPI.py](../Miljodataanalyseapplikasjon-/tests/tests_frostAPI.py)| Enhetstester for funksjonene knyttet til Frost API |
| [tests_niluAPI.py](../Miljodataanalyseapplikasjon-/tests/tests_niluAPI.py)| Enhetstester for funksjonene knyttet til NILU API |
| [tests_kombinert_analyse.py](../Miljodataanalyseapplikasjon-/tests/tests_kombinert_analyse.py)| Enhetstester for funksjonene knyttet til kombinert analyse |

##  Refleksjon  
| Dokument | Beskrivelse |
| -------- | ----------- |
| [Refleksjonsnotat](legg-inn-lenke-her) | Tanker og erfaringer fra prosjektet  |