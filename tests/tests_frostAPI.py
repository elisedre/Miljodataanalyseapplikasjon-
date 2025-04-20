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
    fetch_weather_data_frostAPI,
    #process_weather_data - får ikke til 
    #remove_outliers_frost_data  - får ikke til 
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
            
            result = analyse_and_fix_skewness(input_file, output_file)
            # Lager en DataFrame med opprinnelige verider som skal sammenlignes med resultatet
            original_df = pd.DataFrame(test_data)

            # Tester om skjevheten er fikset
            self.assertFalse(result["Temperatur"].equals(original_df["Temperatur"]))

         finally:
            # Sletter filene etter testing
            os.remove(input_file)
            os.remove(output_file)
            

# Kjører testene 
if __name__ == "__main__":
    unittest.main()

