import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from niluAPI.clean_data_nilu import (
    remove_outliers, #må splitte opp i flere funskjoner for å teste
    interpolate_data,
    save_clean_data
)

class TestCleanNILUData(unittest.TestCase):

    def setUp(self):
        # Eksempeldata med en outlier (500)
        self.df = pd.DataFrame({
            "Dato": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Verdi_NO2": [10, 500, 12],
            "Dekningsgrad_NO2": [True, True, True]
        })
        self.test_file = "test_nilu_data.json"
        self.df.to_json(self.test_file, orient="records", indent=4)

    def tearDown(self):
        # Fjern midlertidig fil etter hver test
        if os.path.exists(self.test_file):
            os.remove(self.test_file)


    def test_interpolate_data_fills_gaps(self):
        # Fjerner midtdato og sjekker at den blir interpolert
        df_missing = self.df.drop(index=1).reset_index(drop=True)
        interpolated = interpolate_data(df_missing, "2023-01-01", "2023-01-03")
        self.assertEqual(len(interpolated), 3)
        self.assertAlmostEqual(interpolated.loc[1, "Verdi_NO2"], 11.0)

    def test_interpolate_marks_coverage_false(self):
        # Setter NaN i dekningsgrad og sjekker at den settes til False
        df_nan = self.df.copy()
        df_nan.loc[1, "Verdi_NO2"] = np.nan
        df_nan.loc[1, "Dekningsgrad_NO2"] = np.nan
        interpolated = interpolate_data(df_nan, "2023-01-01", "2023-01-03")
        self.assertFalse(interpolated.loc[1, "Dekningsgrad_NO2"])

    def test_save_clean_data_writes_file(self):
        # Tester at JSON-fil faktisk blir lagret
        output_file = "test_output.json"
        save_clean_data(self.df, output_file)
        self.assertTrue(os.path.exists(output_file))
        os.remove(output_file)

if __name__ == "__main__":
    unittest.main()
