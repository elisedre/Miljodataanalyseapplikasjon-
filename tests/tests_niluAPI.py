# Importerer nødvendige biblioteker for testing
import unittest
import pandas as pd
import numpy as np
import json
import sys, os
from unittest.mock import patch, Mock

# Sikrer at vi får importert moduler fra prosjektets rotmappe
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importerer funksjonene som skal testes
from data_niluAPI import (
    fetch_raw_data_niluAPI,
    process_and_save_raw_data,
    remove_outliers,
    interpolate_and_save_clean_data,
    analyse_and_fix_skewness
)

# Tester API-henting med simulert (mocked) respons
class TestFetchRawData(unittest.TestCase):

    def test_fetch_raw_data_niluAPI_success(self):
        # Simulerer vellykket API-respons med gyldige data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"component": "NO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 15.0}]}]

        with patch("src.niluAPI.data_niluAPI.requests.get", return_value=mock_response):
            result = fetch_raw_data_niluAPI("https://uekte_api.no")
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)

    def test_fetch_raw_data_niluAPI_error_status(self):
        # Simulerer feil fra API (404)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("src.niluAPI.data_niluAPI.requests.get", return_value=mock_response):
            result = fetch_raw_data_niluAPI("https://uekte_api.no")
            self.assertTrue(result.empty)

    def test_fetch_raw_data_niluAPI_empty_json(self):
        # Simulerer tom JSON-respons
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch("src.niluAPI.data_niluAPI.requests.get", return_value=mock_response):
            result = fetch_raw_data_niluAPI("https://uekte_api.no")
            self.assertTrue(result.empty)

# Tester konvertering og lagring av rådata
class TestProcessRawData(unittest.TestCase):
    def test_process_and_save_raw_data(self):
        # Lager syntetisk data og tester at prosesseringen lykkes
        test_data = [
            {"component": "NO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 10.0}]},
            {"component": "SO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 5.0}]}
        ]
        output_file = "test_output.json"
        process_and_save_raw_data(test_data, output_file)

        try:
            with open(output_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            self.assertIsInstance(result, list)
            self.assertIn("Verdi_NO2", result[0])
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_process_raw_data_empty_input(self):
        # Tester at funksjonen ikke feiler med tom input
        output_file = "empty_output.json"
        process_and_save_raw_data([], output_file)
        with open(output_file) as f:
            result = json.load(f)
        self.assertEqual(result, [])

# Tester fjerning av ekstreme verdier (outliers)
class TestRemoveOutliers(unittest.TestCase):
    def test_remove_outliers(self):
        # Lager én outlier (5000) blant normale verdier
        test_data = [{"Dato": f"2024-01-{i:02d}", "Verdi_NO2": 10} for i in range(1, 21)]
        test_data.append({"Dato": "2024-01-21", "Verdi_NO2": 5000})
        input_file = "test_outliers.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        try:
            df_cleaned = remove_outliers(input_file, cols=["Verdi_NO2"])
            # Sjekker at outlier er satt til NaN
            self.assertTrue(np.isnan(df_cleaned.loc[df_cleaned["Dato"] == "2024-01-21", "Verdi_NO2"].values[0]))
            # Sjekker at vanlige verdier ikke påvirkes
            self.assertFalse(np.isnan(df_cleaned.loc[df_cleaned["Dato"] == "2024-01-01", "Verdi_NO2"].values[0]))
        finally:
            if os.path.exists(input_file):
                os.remove(input_file)

    def test_remove_outliers_none_found(self):
        # Ingen verdier burde være outliers
        test_data = [
            {"Dato": "2024-01-01", "Verdi_NO2": 10},
            {"Dato": "2024-01-02", "Verdi_NO2": 11},
            {"Dato": "2024-01-03", "Verdi_NO2": 9},
            {"Dato": "2024-01-04", "Verdi_NO2": 12}
        ]
        input_file = "test_no_outliers.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        try:
            df_cleaned = remove_outliers(input_file, cols=["Verdi_NO2"])
            self.assertFalse(df_cleaned["Verdi_NO2"].isna().any())
        finally:
            if os.path.exists(input_file):
                os.remove(input_file)

    def test_remove_outliers_invalid_column(self):
        # Tester at funksjonen håndterer manglende kolonne uten å krasje
        data = [{"Dato": "2024-01-01", "Verdi_X": 100}]
        input_file = "invalid_col.json"
        with open(input_file, "w") as f:
            json.dump(data, f)
        df = remove_outliers(input_file, cols=["Verdi_NO2"])
        self.assertIsNotNone(df)

# Tester interpolasjon og kvalitetssikring
class TestInterpolateCleanData(unittest.TestCase):
    def test_interpolate_and_save_clean_data(self):
        # Lager hull i data og forventer interpolert verdi
        df = pd.DataFrame({
            "Dato": ["2024-01-01", "2024-01-03"],
            "Verdi_NO2": [1, 3],
            "Dekningsgrad_NO2": [True, True]
        })
        output_file = "interpolert_data.json"

        try:
            interpolate_and_save_clean_data(df, output_file, "2024-01-01", "2024-01-03")
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            interpolated_value = pd.DataFrame(data).loc[1, "Verdi_NO2"]
            self.assertEqual(interpolated_value, 2.0)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_interpolation_sets_false_coverage(self):
        # Tester at interpolerte data får 'Dekningsgrad' = False
        df = pd.DataFrame({
            "Dato": ["2024-01-01", "2024-01-03"],
            "Verdi_NO2": [1, 3],
            "Dekningsgrad_NO2": [True, True]
        })
        output_file = "test_interpolation_flags.json"

        try:
            interpolate_and_save_clean_data(df, output_file, "2024-01-01", "2024-01-03")
            with open(output_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            interpolert = next(r for r in result if r["Dato"] == "2024-01-02")
            self.assertFalse(interpolert["Dekningsgrad_NO2"])
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

# Tester transformasjon av skjevhet i data
class TestSkewnessAnalysis(unittest.TestCase):
    def test_analyse_and_fix_skewness(self):
        # Lager skjevt datasett og forventer transformasjon
        df = pd.DataFrame({
            "Dato": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Verdi_NO2": [1, 1, 10],
            "Dekningsgrad_NO2": [True, True, True],
            "Dekningsgrad_O3": [True, True, True],
            "Dekningsgrad_SO2": [True, True, True]
        })
        input_file = "clean_data.json"
        output_file = "transformed_data.json"

        try:
            df.to_json(input_file, orient="records")
            analyse_and_fix_skewness(input_file, output_file, threshold=3)
            with open(output_file, "r", encoding="utf-8") as f:
                transformed = json.load(f)
            self.assertIn("Verdi_NO2_Trans", transformed[0])
            self.assertNotEqual(transformed[0]["Verdi_NO2_Trans"], df["Verdi_NO2"].iloc[0])
        finally:
            for f in [input_file, output_file]:
                if os.path.exists(f):
                    os.remove(f)

    def test_analyse_and_fix_skewness_low_skew(self):
        # Tester at selv lav skjevhet gir skalert utdata
        df = pd.DataFrame({
            "Dato": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Verdi_NO2": [10, 11, 12],
            "Dekningsgrad_NO2": [True, True, True],
            "Dekningsgrad_O3": [True, True, True],
            "Dekningsgrad_SO2": [True, True, True]
        })
        input_file = "low_skew_data.json"
        output_file = "low_skew_transformed.json"

        try:
            df.to_json(input_file, orient="records")
            analyse_and_fix_skewness(input_file, output_file, threshold=3)
            with open(output_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            self.assertIn("Verdi_NO2_Trans", result[0])
            self.assertNotEqual(result[0]["Verdi_NO2_Trans"], df["Verdi_NO2"].iloc[0])
        finally:
            for f in [input_file, output_file]:
                if os.path.exists(f):
                    os.remove(f)

# Kjører testene hvis filen kjøres direkte
if __name__ == '__main__':
    unittest.main()
