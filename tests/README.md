# Enhetstester for vær- og luftkvalitetsdata

*Testmappen inneholder enhetstester for funksjoner i to Python-moduler som henter ut og behandler miljødata:*
- *tests_frostAPI.py*
- *tests_niluAPI.py*

Det er viktig å implementere enhetstester for å oppdage tidlig om datagrunnlaget svikter - jo tidligere man oppdager problemene, jo billigere og raskere er det å fikse dem. 

## Tester
**frostAPI:**
- test_fetch_data_from_frostAPI
- test_fetch_weather_data_frostAPI
- test_process_weather_data (jobbes med)
- test_remove_outliers_frost_data (jobbes med)
- test_interpolate_and_save_clean_data
- test_analyse_and_fix_skewness

**niluAPI:**
- test_fetch_raw_data_niluAPI (jobbes med)
- test_process_and_save_raw_data 
- test_remove_outliers (jobbes med)
- test_interpolate_and_save_clean_data
- test_analyse_and_fix_skewness

## Bakgrunn for valg av tester 
Pareto-prinsippet (80/20-regelen) er brukt for å konkludere med hvilke tester som skulle lages. Den viktigste komponenten i koden vår er å hente ut data (da dette er grunnpilaren for prosjektet) og disse enhetstestene ble derfor prioritert. Videre var det viktig å fokusere på å opprette tester for funksjonene som er nødvendige at skal funke for korrekte resultater i videre analyse. 

