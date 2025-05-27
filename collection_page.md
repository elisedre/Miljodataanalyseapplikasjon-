# 📁 Samleside for prosjektet - Miljødataanalyseapplikasjon 

## Dokumentasjon  
| Dokument | Beskrivelse |
| -------- | ----------- |
| [README - hoved](../Miljodataanalyseapplikasjon-/README.md) | Hovedoversikt over prosjektet |
|  [README - notebooks](../Miljodataanalyseapplikasjon-/notebooks/README.md) | Beskrivelse av notebook-strukturen |
|  [README - src](../Miljodataanalyseapplikasjon-/src/README.md) | Beskrivelse av kildekode og funksjoner  |
| [README - data](../Miljodataanalyseapplikasjon-/data/README.md)| Beskrivelse av datasettene
|  [README - tests](../Miljodataanalyseapplikasjon-/tests/README.md) | Informasjon om enhetstester  |

## Notebooks  
| Notebook | Beskrivelse |
| -------- | ----------- |
| [frostAPI.ipynb](../Miljodataanalyseapplikasjon-/notebooks/frostAPI/frostAPI.ipynb) | Datahenting og analyse fra Frost API (værdata)  |
| [niluAPI.ipynb](../Miljodataanalyseapplikasjon-/notebooks/niluAPI/niluAPI.ipynb) | Datahenting og analyse fra NILU API (luftkvalitet)  |
| [combined_analysis.ipynb](../Miljodataanalyseapplikasjon-/notebooks/combined/combined_analysis.ipynb) | Kombinert analyse av miljødata fra begge kilder  |

## Data  
| Ressurs | Beskrivelse |
|--------|-------------|
| [data/](../Miljodataanalyseapplikasjon-/data/) | Lagring av rå og bearbeidede datasett (JSON) organisert i underkategorier |
| [raw_data/](../Miljodataanalyseapplikasjon-/data/raw_data/)| Rådata direkte fra APIene – ufiltrert og utransformert |
| [clean_data/](../Miljodataanalyseapplikasjon-/data/clean_data/)| Renset data med fjerning av mangler, outliers og inkonsistens |
| [analyzed_data/](../Miljodataanalyseapplikasjon-/data/analyzed_data/) | Ferdig analyserte og transformerte datasett klare for modellering og visualisering |


## Kildekode  
| Modulmappe | Beskrivelse |
| ----- | ----------- |
| [frostAPI/](../Miljodataanalyseapplikasjon-/src/frostAPI/) | Funksjoner for datainnhenting, behandling og analyse fra Frost API |
| [niluAPI/](../Miljodataanalyseapplikasjon-/src/niluAPI/)| Funksjoner for datainnhenting, behandling og analyse fra NILU API |
| [combined/](../Miljodataanalyseapplikasjon-/src/combined/)| Funksjoner for analyse for Frost API og NILU API |
| [SQL/](../Miljodataanalyseapplikasjon-/src/SQL/) | Funksjoner som bruker SQL for analyse |

## Tester 
| Testmappe | Beskrivelse |
| --------- | ----------- |
| [tests_frostAPI.py](../Miljodataanalyseapplikasjon-/tests/tests_frostAPI/)| Enhetstester for funksjonene knyttet til Frost API |
| [tests_niluAPI.py](../Miljodataanalyseapplikasjon-/tests/tests_niluAPI/)| Enhetstester for funksjonene knyttet til NILU API |
| [tests_combined_analysis.py](../Miljodataanalyseapplikasjon-/tests/tests_combined_analysis/)| Enhetstester for funksjonene knyttet til kombinert analyse |

##  Ekstra  
| Dokument | Beskrivelse |
| -------- | ----------- |
| [Refleksjonsnotat](../Miljodataanalyseapplikasjon-/docs/refleksjonsnotat.md) | Tanker og erfaringer fra prosjektet  |
| [Releasenote](../Miljodataanalyseapplikasjon-/releasenote.md) | Versjonsbeskrivelse  |
