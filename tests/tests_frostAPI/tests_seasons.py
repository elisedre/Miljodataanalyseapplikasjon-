import unittest
from datetime import datetime
import pandas as pd
import sys
import os

# Legg til sti til src-mappen for å kunne importere funksjoner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from frostAPI.visualization_frost import (get_season, calculate_seasonal_stats)


class TestSeasonalAnalysis(unittest.TestCase):

    def test_get_season(self):
        # Tester at funksjonen returnerer korrekt sesong for gitte datoer
        self.assertEqual(get_season(datetime(2023, 3, 15)), "Vår")
        self.assertEqual(get_season(datetime(2023, 6, 1)), "Sommer")
        self.assertEqual(get_season(datetime(2023, 10, 10)), "Høst")
        self.assertEqual(get_season(datetime(2023, 12, 31)), "Vinter")

    def test_calculate_seasonal_stats_structure(self):
        # Tester at funksjonen returnerer en DataFrame med forventede kolonner
        # og riktig antall rader basert på sesong og år
        df = pd.DataFrame({
            "Dato": ["2023-03-15", "2023-03-16", "2023-06-10"],
            "Temperatur": [10, 12, 20],
            "Nedbør": [5, 7, 10]
        })
        result = calculate_seasonal_stats(df)
        self.assertIn("Temperatur_Gjennomsnitt", result.columns)
        self.assertIn("Sesong", result.columns)
        self.assertEqual(len(result), 2)  # Skal være én rad for Vår og én for Sommer

    def test_seasonal_stats_empty_dataframe(self):
        # Tester at funksjonen håndterer tom DataFrame uten å kaste feil
        df = pd.DataFrame(columns=["Dato", "Temperatur", "Nedbør"])
        result = calculate_seasonal_stats(df)
        self.assertTrue(result.empty)

    def test_seasonal_stats_missing_columns(self):
        # Tester at funksjonen kaster KeyError hvis en nødvendig kolonne mangler
        df = pd.DataFrame({"Dato": ["2023-03-01"], "Temperatur": [10]})  # Mangler 'Nedbør'
        with self.assertRaises(KeyError):
            calculate_seasonal_stats(df)

    def test_seasonal_stats_multiple_years(self):
        # Tester at funksjonen grupperer korrekt per år og sesong
        df = pd.DataFrame({
            "Dato": ["2022-03-15", "2023-03-15"],
            "Temperatur": [10, 20],
            "Nedbør": [5, 15]
        })
        result = calculate_seasonal_stats(df)
        self.assertEqual(len(result), 2)  # Skal være én rad per år
        self.assertIn("Temperatur_Gjennomsnitt", result.columns)

if __name__ == "__main__":
    unittest.main()
