import unittest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
import json
import sys, os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.frostAPI.data_frostAPI import (
    fetch_data_from_frostAPI,
    process_weather_data,
    save_data_as_json,
    fetch_weather_data_frostAPI,
    remove_outliers,
    interpolate_and_save_clean_data,
    analyse_and_fix_skewness,
    get_season
)

# Henting av data
class TestFetchFunctions(unittest.TestCase):

    def test_fetch_data_from_frostAPI(self):
        # Tester at fetch_data_from_frostAPI returnerer korrekt data ved vellykket respons
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"data": [{"mock": "value"}]}
        with patch("src.frostAPI.data_frostAPI.requests.get", return_value=mock_response):
            result = fetch_data_from_frostAPI("test_endpoint", "test_id", ["air_temperature"])
            self.assertEqual(result, [{"mock": "value"}])

    def test_fetch_data_from_frostAPI_error(self):
        # Tester at funksjonen returnerer tom liste ved 404-feil
        mock_response = Mock(status_code=404, text="Not Found")
        mock_response.json.return_value = {}
        with patch("src.frostAPI.data_frostAPI.requests.get", return_value=mock_response):
            result = fetch_data_from_frostAPI("test_endpoint", {}, "test_id")
            self.assertEqual(result, [])

    def test_fetch_weather_data_frostAPI(self):
        # Tester at fetch_weather_data_frostAPI henter, prosesserer og returnerer riktig struktur
        with patch("src.frostAPI.data_frostAPI.fetch_data_from_frostAPI") as mock_fetch:
            mock_fetch.return_value = [{
                "referenceTime": "2023-02-01T00:00:00Z",
                "sourceId": "SN54321",
                "observations": [{"elementId": "air_temperature", "value": 2.0}]
            }]
            result = fetch_weather_data_frostAPI(
                file="test_file",
                client_id="test_id",
                elements={"air_temperature": "Temperatur"},
                endpoint="test_endpoint",
                parameters={"mock": "params"}
            )
            expected = [{"Dato": "2023-02-01", "Stasjon": "SN54321", "Temperatur": 2.0}]
            self.assertEqual(result, expected)
            os.remove("test_file")

# Prosessering av data
class TestProcessingFunctions(unittest.TestCase):

    def test_process_weather_data(self):
        # Tester at rådata blir riktig prosessert til strukturert format
        raw_data = [{
            "referenceTime": "2023-02-01T00:00:00Z",
            "sourceId": "SN12345",
            "observations": [
                {"elementId": "air_temperature", "value": 2.5},
                {"elementId": "wind_speed", "value": 5.0}
            ]
        }]
        elements = {"air_temperature": "Temperatur", "wind_speed": "Vind"}
        result = process_weather_data(raw_data, elements)
        self.assertEqual(result, [{"Dato": "2023-02-01", "Stasjon": "SN12345", "Temperatur": 2.5, "Vind": 5.0}])

    def test_save_data_as_json(self):
        # Tester at data lagres riktig som JSON med pivotering
        data = [{"Dato": "2023-02-01", "Temperatur": 2.0}]
        file = "saved_file.json"
        try:
            save_data_as_json(data, file, ["Dato"], ["Temperatur"])
            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)
            self.assertEqual(content[0]["Temperatur"], 2.0)
        finally:
            if os.path.exists(file):
                os.remove(file)
    def test_process_weather_data_empty_observations(self):
        raw_data = [{
            "referenceTime": "2023-02-01T00:00:00Z",
            "sourceId": "SN12345",
            "observations": []
        }]
        elements = {"air_temperature": "Temperatur"}
        result = process_weather_data(raw_data, elements)
        self.assertEqual(result, [{"Dato": "2023-02-01", "Stasjon": "SN12345"}])

# Rensing av data
class TestCleaningFunctions(unittest.TestCase):

    def test_remove_outliers(self):
        # Tester at ekstreme verdier (outliers) blir satt til NaN
        test_data = [{"Dato": f"2023-02-{i:02d}", "Temperatur": 10.0} for i in range(1, 21)]
        test_data.append({"Dato": "2023-02-21", "Temperatur": 999})  # outlier
        file = "outliers_test.json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        try:
            df = remove_outliers(file, ["Temperatur"])
            self.assertTrue(np.isnan(df.loc[df["Dato"] == "2023-02-21", "Temperatur"]).all())
        finally:
            os.remove(file)

# Interpolering
class TestInterpolationFunctions(unittest.TestCase):

    def test_interpolate_and_save_clean_data(self):
        # Tester at funksjonen interpolerer manglende dato (NaN) korrekt
        df = pd.DataFrame({
            "Dato": ["2023-02-01", "2023-02-03"],
            "Temperatur": [1.0, 3.0]
        })
        df["Dato"] = pd.to_datetime(df["Dato"])
        output_file = "interpolated_data.json"
        try:
            interpolate_and_save_clean_data(df, output_file, "2023-02-01", "2023-02-03")
            result = pd.read_json(output_file)
            interpolated_value = result.loc[result["Dato"] == "2023-02-02", "Temperatur"].iloc[0]
            self.assertAlmostEqual(interpolated_value, 2.0)
        finally:
            os.remove(output_file)

    def test_interpolation_when_no_missing_values(self):
        # Tester at funksjonen ikke endrer verdier når ingen mangler
        df = pd.DataFrame({
            "Dato": pd.date_range("2023-02-01", periods=3),
            "Temperatur": [1.0, 2.0, 3.0]
        })
        file = "no_missing.json"
        try:
            interpolate_and_save_clean_data(df, file, "2023-02-01", "2023-02-03")
            result = pd.read_json(file)
            self.assertFalse(result["Temperatur"].isna().any())
        finally:
            os.remove(file)

    def test_interpolation_flags_added(self):
        # Tester at interpolerte verdier blir flagget i ny kolonne
        df = pd.DataFrame({
            "Dato": ["2023-02-01", "2023-02-03"],
            "Temperatur": [1.0, 3.0]
        })
        df["Dato"] = pd.to_datetime(df["Dato"])
        file = "flagged.json"
        try:
            interpolate_and_save_clean_data(df, file, "2023-02-01", "2023-02-03")
            result = pd.read_json(file)
            self.assertIn("Interpolert_Temperatur", result.columns)
            self.assertTrue(result.loc[result["Dato"] == "2023-02-02", "Interpolert_Temperatur"].iloc[0])
        finally:
            os.remove(file)

# Skjevhetsanalyse
class TestSkewnessFunctions(unittest.TestCase):

    def test_analyse_and_fix_skewness(self):
        # Tester at skjev data blir transformert og standardisert
        test_data = [
            {"Dato": "2023-02-01", "Temperatur": 5.0},
            {"Dato": "2023-02-02", "Temperatur": 150.0},
            {"Dato": "2023-02-03", "Temperatur": 7.0}
        ]
        input_file = "clean_data.json"
        output_file = "transformed_data.json"
        try:
            with open(input_file, "w", encoding="utf-8") as f:
                json.dump(test_data, f)
            result = analyse_and_fix_skewness(input_file, output_file, threshold=3)
            original = pd.DataFrame(test_data)
            self.assertFalse(result["Temperatur"].equals(original["Temperatur"]))
        finally:
            for f in [input_file, output_file]:
                os.remove(f)

    def test_analyse_and_fix_skewness_empty_file(self):
        # Tester at tom input returnerer tomt resultat
        input_file = "empty.json"
        output_file = "transformed_empty.json"
        try:
            with open(input_file, "w", encoding="utf-8") as f:
                json.dump([], f)
            result = analyse_and_fix_skewness(input_file, output_file, threshold=3)
            self.assertTrue(result.empty)
        finally:
            for f in [input_file, output_file]:
                os.remove(f)

# Sesongberegning
class TestSeasonUtility(unittest.TestCase):

    def test_get_season(self):
        # Tester at riktig sesong returneres basert på måned
        self.assertEqual(get_season(datetime(2023, 3, 15)), "Vår")
        self.assertEqual(get_season(datetime(2023, 7, 1)), "Sommer")
        self.assertEqual(get_season(datetime(2023, 10, 5)), "Høst")
        self.assertEqual(get_season(datetime(2023, 12, 25)), "Vinter")

# Kjører testene
if __name__ == "__main__":
    unittest.main()
