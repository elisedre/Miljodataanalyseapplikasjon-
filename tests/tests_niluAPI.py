# Importerer nødvendige biblioteker 
import unittest
import pandas as pd
import numpy as np
import json
import sys, os
from unittest.mock import patch, Mock

#importere moduler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.niluAPI.data_niluAPI import (
    fetch_raw_data_niluAPI,
    process_and_save_raw_data,
    remove_outliers,
    interpolate_and_save_clean_data,
    analyse_and_fix_skewness
)

class TestNiluAPI(unittest.TestCase):

    '''Tester for funksjonen som henter rådata fra NILU API (fetch_raw_data_niluAPI)'''
    def test_fetch_raw_data_niluAPI_success(self):

    # Mocket API-respons med statuskode 200 og gyldig JSON (bruker dette grunnet api nøkkel)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"component": "NO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 15.0}]}]

        with patch("src.niluAPI.data_niluAPI.requests.get", return_value=mock_response):
            result = fetch_raw_data_niluAPI("https://uekte_api.no")

            # Vi forventer at den returnerer en liste (ikke tomt)
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

    '''Tester for funksjonen som prosesserer og lagrer rådata (process_and_save_raw_data)'''
        
    def test_process_and_save_raw_data(self):
        # Simulerer rådata fra NILU API
        test_data = [
            {"component": "NO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 10.0}]},
            {"component": "SO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 5.0}]}
        ]
        # Simulerer prosessering og lagring av data
        output_file = "test_output.json"
        process_and_save_raw_data(test_data, output_file)

        try:
            # Leser den lagrede filen for å sjekke innholdet
            with open(output_file, "r", encoding="utf-8") as f:
                result = json.load(f)

            # Sjekker at dataene er lagret riktig
            self.assertIsInstance(result, list)
            self.assertIn("Verdi_NO2", result[0])
        
        finally:
            # Sletter testfilen etter testing
            if os.path.exists(output_file):
                os.remove(output_file)

    '''Tester for funksjonen som fjerner utstikkere (remove_outliers)'''

    def test_remove_outliers(self):
    # Lager testdata med én outlier
        test_data = [{"Dato": f"2024-01-{i:02d}", "Verdi_NO2": 10} for i in range(1, 21)]
        test_data.append({"Dato": "2024-01-21", "Verdi_NO2": 5000}) 
        
        input_file = "test_outliers.json"
        
        # Lagrer testdata til fil
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        try:
            # Kjører funksjonen
            df_cleaned = remove_outliers(input_file, cols=["Verdi_NO2"])

            # Sjekker at outlier er satt til NaN
            outlier_value = df_cleaned.loc[df_cleaned["Dato"] == "2024-01-21", "Verdi_NO2"].values[0]
            self.assertTrue(np.isnan(outlier_value))

            # Sjekker at ikke-outliers ikke er NaN
            normal_value = df_cleaned.loc[df_cleaned["Dato"] == "2024-01-01", "Verdi_NO2"].values[0]
            self.assertFalse(np.isnan(normal_value))

        finally:
            # Sletter testfil
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
            self.assertFalse(df_cleaned["Verdi_NO2"].isna().any(), "Ingen verdier skal være NaN")
        finally:
            if os.path.exists(input_file):
                os.remove(input_file)


    '''Tester for funksjonen som setter null verdier til Nan, interpolerer Nan og lagrer rene data (interpolate_and_save_clean_data)'''
    def test_interpolate_and_save_clean_data(self):
        # Lager testdata
        df = pd.DataFrame({
            "Dato": ["2024-01-01", "2024-01-03"],
            "Verdi_NO2": [1, 3],
            "Dekningsgrad_NO2": [True, True]
        })

        # Lagrer testdata til en midlertidig JSON-fil
        output_file = "interpolert_data.json"

        try:
            interpolate_and_save_clean_data(df, output_file, "2024-01-01", "2024-01-03")

            # Leser innholdet fra den lagrede filen
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            df_result = pd.DataFrame(data)

            # Henter interpolert verdi 
            interpolated_value = df_result.loc[df_result["Dato"] == "2024-01-02", "Verdi_NO2"].values[0]
            
            # Sjekker at interpoleringen er korrekt
            self.assertEqual(interpolated_value, 2.0)

        finally:
            # Sletter filen etter testing
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
            self.assertFalse(interpolert["Dekningsgrad_NO2"], "Interpolerte verdier skal ha Dekningsgrad = False")

        finally:
            if os.path.exists(output_file):
                os.remove(output_file)
        
    '''Tester for funksjonen som analyserer og fikser skjevhet i data (analyse_and_fix_skewness)'''

    def test_analyse_and_fix_skewness(self):
        # Lager testdata med skjevhet 
        df = pd.DataFrame({
            "Dato": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "Verdi_NO2": [1, 1, 10],
                "Dekningsgrad_NO2": [True, True, True],
                "Dekningsgrad_O3": [True, True, True],        
                "Dekningsgrad_SO2": [True, True, True]})
        
        input_file = "clean_data.json"
        output_file = "transformed_data.json"

        try:
            # Lagrer testdata som JSON
            df.to_json(input_file, orient="records")

            # Kjører transformasjonsfunksjonen
            analyse_and_fix_skewness(input_file, output_file, threshold=3)

            # Leser inn transformert fil
            with open(output_file, "r", encoding="utf-8") as f:
                transformed = json.load(f)

            # Sjekker at transformert kolonne finnes
            self.assertIn("Verdi_NO2_Trans", transformed[0])

            # Verifiser at verdien faktisk er transformert (ikke samme som original)
            original_value = df["Verdi_NO2"].iloc[0]
            transformed_value = transformed[0]["Verdi_NO2_Trans"]
            self.assertNotEqual(original_value, transformed_value)

        finally:
            # Sikker sletting av midlertidige filer
            if os.path.exists(input_file):
                os.remove(input_file)

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
            



# Kjører testene 
if __name__ == '__main__':
    unittest.main()


