# Importerer nødvendige biblioteker 
import unittest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
import json
import sys, os

# Legger til riktig sti for å importere moduler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.frostAPI.data_frostAPI import (
    fetch_data_from_frostAPI,
    process_weather_data,
    save_data_as_json,
    fetch_weather_data_frostAPI,
    remove_outliers,
    interpolate_and_save_clean_data,
    analyse_and_fix_skewness,
)

class TestFrostAPIFunctions(unittest.TestCase):

    def test_fetch_data_from_frostAPI(self):
         # Mocker en respons fra API-et
         mock_response = Mock()
         mock_response.status_code = 200
         mock_response.json.return_value = {"data": [{"mock": "value"}]}

         # Bruker patch for å erstatte requests.get med egen mock-respons
         with patch("src.frostAPI.data_frostAPI.requests.get", return_value=mock_response):
            result = fetch_data_from_frostAPI("test_endpoint", "test_id", ["air_temperature"])

            # Sjekker at funksjonen returnerer riktig data
            self.assertEqual(result, [{"mock": "value"}])

    def test_fetch_data_from_frostAPI_error(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.json.return_value = {}

        with patch("src.frostAPI.data_frostAPI.requests.get", return_value=mock_response):
            result = fetch_data_from_frostAPI("test_endpoint", {}, "test_id")
            self.assertEqual(result, []) 
        

    def test_fetch_weather_data_frostAPI(self):
        # Bruker patch for å mocke fetch_data_from_frostAPI
        with patch("src.frostAPI.data_frostAPI.fetch_data_from_frostAPI") as mock_fetch:
            mock_fetch.return_value = [
                {
                    "referenceTime": "2023-02-01T00:00:00Z",
                    "sourceId": "SN54321",
                    "observations": [{"elementId": "air_temperature", "value": 2.0}]
                }
            ]
            # Kaller funksjonen med mock-data
            result = fetch_weather_data_frostAPI(
                file="test_file", 
                client_id="test_id", 
                elements={"air_temperature": "Temperatur"}, 
                endpoint="test_endpoint",
                parameters={"mock": "params"}
             )
            # Lager forventet resultat
            expected_result = [
                {
                    "Dato": "2023-02-01",
                    "Stasjon": "SN54321",
                    "Temperatur": 2.0
                }
            ]
            # Sjekker at resultatet er som forventet
            self.assertEqual(result, expected_result)

            # Sletter testfilen etter testing
            os.remove("test_file")  
    def test_process_weather_data(self):
        

        raw_data = [{
            "referenceTime": "2023-02-01T00:00:00Z",
            "sourceId": "SN12345",
            "observations": [
                {"elementId": "air_temperature", "value": 2.5},
                {"elementId": "wind_speed", "value": 5.0}
            ]
        }]
        elements = {
            "air_temperature": "Temperatur",
            "wind_speed": "Vind"
        }

        result = process_weather_data(raw_data, elements)
        self.assertEqual(result, [{"Dato": "2023-02-01", "Stasjon": "SN12345", "Temperatur": 2.5, "Vind": 5.0}])

    def test_save_data_as_json(self):

        data = [{"Dato": "2023-02-01", "Temperatur": 2.0}]
        output_file = "saved_file.json"

        try:
            save_data_as_json(data, output_file, index_columns=["Dato"], value_columns=["Temperatur"])
            with open(output_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            self.assertEqual(content[0]["Temperatur"], 2.0)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_remove_outliers(self):

        test_data = [{"Dato": f"2023-02-{i:02d}", "Temperatur": 10.0} for i in range(1, 6)]
        test_data.append({"Dato": "2023-02-06", "Temperatur": 999})  # outlier

        input_file = "outliers_test.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        try:
            df = remove_outliers(input_file, ["Temperatur"])
            self.assertTrue(np.isnan(df.loc[df["Dato"] == "2023-02-06", "Temperatur"]).all())
        finally:
            os.remove(input_file)

    def test_interpolate_and_save_clean_data(self):
        # Lager testdata
        df = pd.DataFrame({
            "Dato": ["2023-02-01", "2023-02-03"],
            "Temperatur": [1.0, 3.0]
        })

        # Omformer Dato-kolonnen til datetime-format
        df["Dato"] = pd.to_datetime(df["Dato"])
        # Lagrer testdata i en midlertidig json-fil
        output_file = "interpolated_data.json"

        try:
            interpolate_and_save_clean_data(df, output_file, "2023-02-01", "2023-02-03")
            # Leser den interpolerte dataen fra filen
            result = pd.read_json(output_file)

            # Henter interpolert verdi for 2023-02-02
            interpolated_value = result.loc[result["Dato"] == "2023-02-02", "Temperatur"].iloc[0]

            # Sjekker at interpoleringen er korrekt
            self.assertAlmostEqual(interpolated_value, 2.0)

        finally:   
            # Sletter filen etter testing
            os.remove(output_file)
    def test_interpolation_when_no_missing_values(self):
        df = pd.DataFrame({
            "Dato": pd.date_range("2023-02-01", periods=3),
            "Temperatur": [1.0, 2.0, 3.0]
        })
        output_file = "no_missing.json"

        try:
            interpolate_and_save_clean_data(df, output_file, "2023-02-01", "2023-02-03")
            result = pd.read_json(output_file)

            # Bekreft at ingen verdier var NaN
            self.assertFalse(result["Temperatur"].isna().any())
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_interpolation_flags_added(self):
        df = pd.DataFrame({
            "Dato": ["2023-02-01", "2023-02-03"],
            "Temperatur": [1.0, 3.0]
        })
        df["Dato"] = pd.to_datetime(df["Dato"])
        output_file = "flagged.json"

        try:
            interpolate_and_save_clean_data(df, output_file, "2023-02-01", "2023-02-03")
            result = pd.read_json(output_file)

            # Sjekk at interpolert kolonne finnes og flagges riktig
            self.assertIn("Interpolert_Temperatur", result.columns)
            is_interpolated = result.loc[result["Dato"] == "2023-02-02", "Interpolert_Temperatur"].iloc[0]
            self.assertTrue(is_interpolated)

        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_analyse_and_fix_skewness(self):
         # Lager testdata med skjevhet 
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
            # Lager en DataFrame med opprinnelige verider som skal sammenlignes med resultatet
            original_df = pd.DataFrame(test_data)

            # Tester om skjevheten er fikset
            self.assertFalse(result["Temperatur"].equals(original_df["Temperatur"]))

         finally:
            # Sletter filene etter testing
            os.remove(input_file)
            os.remove(output_file)

    def test_analyse_and_fix_skewness_empty_file(self):
        input_file = "empty.json"
        output_file = "transformed_empty.json"

        try:
            with open(input_file, "w", encoding="utf-8") as f:
                json.dump([], f)  # Tom liste

            result = analyse_and_fix_skewness(input_file, output_file, threshold=3)
            self.assertTrue(result.empty)  

        finally:
            for f in [input_file, output_file]:
                if os.path.exists(f):
                    os.remove(f)      

# Kjører testene 
if __name__ == "__main__":
    unittest.main()

