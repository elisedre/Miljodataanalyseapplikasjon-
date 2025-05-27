import unittest
from unittest.mock import patch, Mock
import pandas as pd
import os
import sys
from io import StringIO
from requests.exceptions import RequestException

# Legg til src-stien hvis nødvendig
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from niluAPI.fetch_niluAPI import fetch_raw_data_niluAPI, process_raw_data, save_to_json

class TestNILUFunctions(unittest.TestCase):

    @patch("data_niluAPI.requests.get")
    def test_fetch_raw_data_success(self, mock_get):
        # Tester at data returneres korrekt ved gyldig respons
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"values": [{"dateTime": "2023-01-01T00:00:00Z", "value": 42}]}]
        mock_get.return_value = mock_response

        result = fetch_raw_data_niluAPI("http://fake-endpoint")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    @patch("data_niluAPI.requests.get")
    def test_fetch_raw_data_http_error(self, mock_get):
        mock_get.side_effect = RequestException("Network error")
        result = fetch_raw_data_niluAPI("http://fake-endpoint")
        self.assertEqual(result, [])

    @patch("data_niluAPI.requests.get")
    def test_fetch_raw_data_invalid_json(self, mock_get):
        # Tester at funksjonen håndterer feil JSON-format
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = fetch_raw_data_niluAPI("http://fake-endpoint")
        self.assertEqual(result, [])

    def test_process_raw_data_structure(self):
        # Tester at data prosesseres korrekt til et pivotert DataFrame
        mock_data = [
            {
                "component": "NO2",
                "values": [
                    {"dateTime": "2023-01-01T00:00:00Z", "value": 20, "coverage": 0.9},
                    {"dateTime": "2023-01-01T01:00:00Z", "value": 22, "coverage": 0.95}
                ]
            }
        ]
        df = process_raw_data(mock_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("Verdi_NO2", df.columns)
        self.assertIn("Dekningsgrad_NO2", df.columns)
        self.assertIn("Dato", df.columns)

    def test_process_raw_data_empty(self):
        # Tester at tom input gir tom DataFrame
        result = process_raw_data([])
        self.assertTrue(result.empty)

    @patch("data_niluAPI.pd.DataFrame.to_json")
    def test_save_to_json_success(self, mock_to_json):
        # Tester at lagring kalles riktig
        df = pd.DataFrame({"Dato": ["2023-01-01"], "NO2": [20]})
        save_to_json(df, "dummy.json")
        mock_to_json.assert_called_once()

    @patch("data_niluAPI.pd.DataFrame.to_json", side_effect=Exception("Diskfeil"))
    def test_save_to_json_failure(self, mock_to_json):
        # Tester at feil i lagring håndteres
        df = pd.DataFrame({"Dato": ["2023-01-01"], "NO2": [20]})
        with patch("sys.stdout", new=StringIO()) as fake_out:
            save_to_json(df, "dummy.json")
            self.assertIn("Feil ved lagring", fake_out.getvalue())

if __name__ == "__main__":
    unittest.main()
