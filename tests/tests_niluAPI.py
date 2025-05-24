# Importerer nødvendige biblioteker 
import unittest
import pandas as pd
import numpy as np
import json
import sys, os

# Legger til riktig sti for å importere moduler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.niluAPI.data_niluAPI import (
    #fetch_raw_data_niluAPI -får ikke til
    process_and_save_raw_data,
    #remove_outliers - får ikke til
    interpolate_and_save_clean_data,
    analyse_and_fix_skewness
)

class TestNiluAPI(unittest.TestCase):
    
    def test_process_and_save_raw_data(self):
        # Simulerer rådata fra NILU API
        test_data = [
            {"component": "NO2", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 10.0}]},
            {"component": "PM10", "values": [{"dateTime": "2024-01-01T00:00:00Z", "value": 5.0}]}
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
            os.remove(output_file)

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
            os.remove(output_file)

    def test_analyse_and_fix_skewness(self):
        # Lager testdata med skjevhet 
        df = pd.DataFrame({
            "Dato": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "Verdi_NO2": [1, 1, 10],
                "Dekningsgrad_NO2": [True, True, True],
                "Dekningsgrad_O3": [True, True, True],          # <– Legg til disse
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
            if os.path.exists(output_file):
                os.remove(output_file)



# Kjører testene 
if __name__ == '__main__':
    unittest.main()


