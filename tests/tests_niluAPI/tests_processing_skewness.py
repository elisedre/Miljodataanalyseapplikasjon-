import unittest
import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer, StandardScaler
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from niluAPI.analyze_data_nilu import analyse_skewness, fix_skewness

class TestSkewnessNILU(unittest.TestCase):

    def setUp(self):
        # Eksempeldata med kjent skjevhet
        self.df = pd.DataFrame({
            "Verdi_NO2": [1, 2, 3, 4, 100],     # Høy skjevhet
            "Verdi_O3": [10, 11, 12, 13, 14],   # Lav skjevhet
            "Verdi_SO2": [5, 5, 5, 5, 5]        # Null variasjon
        })
        self.cols = ["Verdi_NO2", "Verdi_O3", "Verdi_SO2"]

    def test_analyse_skewness_returns_dict(self):
        # Tester at analyse_skewness returnerer riktig type og nøkler
        result = analyse_skewness(self.df, self.cols)
        self.assertIsInstance(result, dict)
        self.assertCountEqual(result.keys(), self.cols)

    def test_analyse_skewness_detects_high_skew(self):
        # Verifiser at Verdi_NO2 gir høy skjevhet
        result = analyse_skewness(self.df, ["Verdi_NO2"])
        self.assertGreater(result["Verdi_NO2"], 1.0)

    def test_fix_skewness_creates_transformed_columns(self):
        skewness_dict = analyse_skewness(self.df, self.cols)
        transformed_df = fix_skewness(self.df, skewness_dict, threshold=1.0)
        for col in self.cols:
            self.assertIn(f"{col}_Trans", transformed_df.columns)

    def test_fix_skewness_handles_constant_column(self):
        # Kolonnen Verdi_SO2 har ingen variasjon — test at den ikke feiler
        skewness_dict = analyse_skewness(self.df, self.cols)
        transformed_df = fix_skewness(self.df, skewness_dict, threshold=1.0)
        self.assertIn("Verdi_SO2_Trans", transformed_df.columns)
        self.assertTrue(np.allclose(transformed_df["Verdi_SO2_Trans"], 0))

    def test_fix_skewness_output_has_zero_mean(self):
        # Test at transformerte kolonner har ~0 gjennomsnitt
        skewness_dict = analyse_skewness(self.df, ["Verdi_NO2"])
        transformed_df = fix_skewness(self.df, skewness_dict, threshold=1.0)
        mean_val = transformed_df["Verdi_NO2_Trans"].mean()
        self.assertAlmostEqual(mean_val, 0, places=1)

if __name__ == "__main__":
    unittest.main()