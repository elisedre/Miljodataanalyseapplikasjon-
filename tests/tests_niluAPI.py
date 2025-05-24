import unittest
import pandas as pd
import numpy as np
import json
import sys, os
from unittest.mock import patch, Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.niluAPI.data_niluAPI import (
    fetch_raw_data_niluAPI,
    process_and_save_raw_data,
    remove_outliers,
    interpolate_and_save_clean_data,
    analyse_and_fix_skewness
)

class TestFetchRawData(unittest.TestCase):
    def test_fetch_raw_data_niluAPI_success(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"component": "NO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 15.0}]}]

        with patch("src.niluAPI.data_niluAPI.requests.get", return_value=mock_response):
            result = fetch_raw_data_niluAPI("https://uekte_api.no")
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)

    def test_fetch_raw_data_niluAPI_error_status(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("src.niluAPI.data_niluAPI.requests.get", return_value=mock_response):
            result = fetch_raw_data_niluAPI("https://uekte_api.no")
            self.assertTrue(result.empty)

    def test_fetch_raw_data_niluAPI_empty_json(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch("src.niluAPI.data_niluAPI.requests.get", return_value=mock_response):
            result = fetch_raw_data_niluAPI("https://uekte_api.no")
            self.assertTrue(result.empty)

class TestProcessRawData(unittest.TestCase):
    def test_process_and_save_raw_data(self):
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
        output_file = "empty_output.json"
        process_and_save_raw_data([], output_file)
        with open(output_file) as f:
            result = json.load(f)
        self.assertEqual(result, [])

class TestRemoveOutliers(unittest.TestCase):
    def test_remove_outliers(self):
        test_data = [{"Dato": f"2024-01-{i:02d}", "Verdi_NO2": 10} for i in range(1, 21)]
        test_data.append({"Dato": "2024-01-21", "Verdi_NO2": 5000})
        input_file = "test_outliers.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        try:
            df_cleaned = remove_outliers(input_file, cols=["Verdi_NO2"])
            outlier_value = df_cleaned.loc[df_cleaned["Dato"] == "2024-01-21", "Verdi_NO2"].values[0]
            self.assertTrue(np.isnan(outlier_value))
            normal_value = df_cleaned.loc[df_cleaned["Dato"] == "2024-01-01", "Verdi_NO2"].values[0]
            self.assertFalse(np.isnan(normal_value))
        finally:
            if os.path.exists(input_file):
                os.remove(input_file)

    def test_remove_outliers_none_found(self):
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
        data = [{"Dato": "2024-01-01", "Verdi_X": 100}]
        input_file = "invalid_col.json"
        with open(input_file, "w") as f:
            json.dump(data, f)
        df = remove_outliers(input_file, cols=["Verdi_NO2"])
        self.assertIsNotNone(df)

class TestInterpolateCleanData(unittest.TestCase):
    def test_interpolate_and_save_clean_data(self):
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
            df_result = pd.DataFrame(data)
            interpolated_value = df_result.loc[df_result["Dato"] == "2024-01-02", "Verdi_NO2"].values[0]
            self.assertEqual(interpolated_value, 2.0)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_interpolation_sets_false_coverage(self):
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

class TestSkewnessAnalysis(unittest.TestCase):
    def test_analyse_and_fix_skewness(self):
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
            original_value = df["Verdi_NO2"].iloc[0]
            transformed_value = transformed[0]["Verdi_NO2_Trans"]
            self.assertNotEqual(original_value, transformed_value)
        finally:
            for f in [input_file, output_file]:  # ← Nå ryddes begge filer
                if os.path.exists(f):
                    os.remove(f)

    def test_analyse_and_fix_skewness_low_skew(self):
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

if __name__ == '__main__':
    unittest.main()