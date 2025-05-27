# 🧪 Enhetstester for Miljødataanalyseapplikasjon

Denne testpakken dekker kjernen av funksjonaliteten i applikasjonen som behandler vær- og luftkvalitetsdata. Vi har valgt å teste kritiske deler som påvirker datakvalitet og modellresultater, basert på prosjektets overordnede mål: å hente inn, prosessere og analysere miljødata pålitelig.

---

# Hvorfor teste?

Vi følger *Pareto-prinsippet (80/20-regelen)*: Vi fokuserer på å teste de *20 % av funksjonene* som er mest kritiske for korrekt funksjon – nemlig datainnhenting, prosessering og prediktiv analyse. Disse funksjonene utgjør grunnmuren for all videre databehandling og innsikt i prosjektet.

Eksempler:
- Hvis rådata feiler ved henting eller prosessering, blir alle videre analyser ugyldige.
- Hvis interpolering eller skjevhetskorrigering gir feil, kan modellene trenes på feil grunnlag.
- Derfor er slike funksjoner prioritert.
- Vi har valgt å ikke teste visualiserinsgfunskjoner og "wrapper" funskjoner.

---

# Testoversikt

## tests_frostAPI/

Tester relatert til værdata fra MET (Frost API):

| Filnavn | Tester | Hva den tester |
|---------|--------|----------------|
| tests_api.py | fetch_data_from_frostAPI, get_info_frostAPI, process_weather_data | Håndtering av API-respons, parsing og strukturering |
| tests_clean_process_data.py | remove_duplicate_dates, interpolate_data, label_station | Duplikatfjerning, interpolering og stasjonskoding |
| tests_processing_skewness.py | analyse_skewness, fix_skewness | Analyse og korreksjon av skjevfordelte værdata |
| tests_seasons.py | get_season, calculate_seasonal_stats | Sesongklassifisering og beregning av statistikk per sesong |

---

## tests_niluAPI/

Tester relatert til luftkvalitetsdata fra NILU:

| Filnavn | Tester | Hva den tester |
|---------|--------|----------------|
| tests_api.py | fetch_raw_data_niluAPI, process_raw_data, save_to_json | Robusthet mot nettverksfeil og korrekt filskriving |
| tests_clean_process_data.py | interpolate_data, save_clean_data | Interpolering av manglende verdier og JSON-lagring |
| tests_processing_skewness.py | analyse_skewness, fix_skewness | Deteksjon og transformasjon av skjevhet i luftmålinger |

---

## tests_combined_analysis/

Tester for sammenslåing, sesonganalyse, prediksjon og modelltrening:

| Filnavn | Tester | Hva den tester |
|---------|--------|----------------|
| tests_combine_df.py | combine_df, prepare_dataframe | Sammenslåing av datasett, datokonvertering og feilkontroll |
| tests_prediction_analysis.py | add_seasonal_features, predict_feature_values | Ekstraksjon av sesongbaserte features og fremtidsprediksjon |
| tests_train_model.py | train_model, evaluate_and_train_model | Modelltrening, evaluering og robusthet mot feil input |

---

# Begrunnede testvalg

*Vi tester det viktigste først*. Vi har valgt ut følgende som spesielt kritisk for funksjonell kvalitet:

- *Datainnhenting* – feiltoleranse ved API-kall er viktig for å unngå krasj.
- *Dataprosessering* – feil i interpolasjon eller outlier-fjerning gir feil modell.
- *Prediksjon og modellering* – sluttbrukerens innsikt avhenger av riktige modeller.
- *Skjevhetsanalyse* – normalisering sikrer bedre modellprestasjon.

Testene er designet for å:
- Oppdage feil tidlig
- Verifisere datastruktur og innhold
- Sjekke at feil håndteres riktig (f.eks. nettverksfeil, tomme datasett)
- Sørge for at modellene trener på gyldig og fornuftig data

---

# Kvalitetskriterier

- Vi bruker unittest`-rammeverket med mock` for å isolere eksterne avhengigheter
- Alle tester har rene setUp/tearDown-metoder ved behov
- Testene dekker både normaltilfeller og feiltilfeller
- Det er tydelig struktur med én modul = én testfilgruppe

---


