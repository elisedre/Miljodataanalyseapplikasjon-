import unittest
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
# Importer funksjonene fra ditt modul
from data_frostAPI import (analyse_skewness, fix_skewness)

class TestSkewnessFunctions(unittest.TestCase):

    def setUp(self):
        # Eksempeldata med høy skjevhet
        self.df = pd.DataFrame({
            "Nedbør": [1, 2, 3, 4, 100],  # høy skjevhet
            "Temperatur": [10, 11, 12, 13, 14],  # lav skjevhet
        })
        self.temp_file = "temp_skew_data.json"
        self.df.to_json(self.temp_file, orient="records", indent=4)

    def tearDown(self):
        # Rydder opp midlertidig fil
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_analyse_skewness_with_specific_columns(self):
        # Tester at analyse_skewness returnerer DataFrame og riktige kolonnenavn
        df_loaded, cols = analyse_skewness(self.temp_file, cols=["Nedbør"])
        self.assertIsInstance(df_loaded, pd.DataFrame)
        self.assertEqual(cols, ["Nedbør"])
        self.assertAlmostEqual(df_loaded["Nedbør"].skew(), self.df["Nedbør"].skew(), places=2)

    def test_analyse_skewness_all_numeric(self):
        # Tester at alle numeriske kolonner blir returnert når cols=None
        df_loaded, cols = analyse_skewness(self.temp_file, cols=None)
        expected_cols = ["Nedbør", "Temperatur"]
        self.assertCountEqual(cols, expected_cols)

    def test_analyse_skewness_invalid_json(self):
        # Tester at funksjonen håndterer feil fil korrekt
        invalid_path = "nonexistent.json"
        df, cols = analyse_skewness(invalid_path)
        self.assertIsNone(df)
        self.assertIsNone(cols)

    def test_fix_skewness_behavior(self):
        # Tester at Yeo-Johnson brukes på sterkt skjev kolonne og StandardScaler på andre
        df_transformed = fix_skewness(self.df, threshold=1.0, cols=["Nedbør", "Temperatur"])

        # Skjekk at data er transformert og normalisert
        self.assertTrue(np.allclose(df_transformed["Nedbør"].mean(), 0, atol=1e-1))
        self.assertTrue(np.allclose(df_transformed["Temperatur"].mean(), 0, atol=1e-1))
        self.assertEqual(list(df_transformed.columns), ["Nedbør", "Temperatur"])

    def test_fix_skewness_handles_empty_dataframe(self):
        # Tester at tom DataFrame ikke kaster feil
        empty_df = pd.DataFrame(columns=["X", "Y"])
        transformed = fix_skewness(empty_df, threshold=1.0, cols=[])
        self.assertTrue(transformed.empty)

if __name__ == "__main__":
    unittest.main()