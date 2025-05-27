import unittest
from unittest.mock import patch, Mock
import os
from io import StringIO
import requests
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from frostAPI.fetch_frostapi import (
    fetch_data_from_frostAPI,
    get_info_frostAPI,
    process_weather_data,
    save_data_as_json)

from frostAPI.main_frost import (
    get_elements_frostAPI,
    get_stations_frostAPI,
    data_frostAPI)

class TestFetchFunctions(unittest.TestCase):

    def test_fetch_data_from_frostAPI(self):
        #Tester at data hentes riktig fra API når responsen er vellykket
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"data": [{"mock": "value"}]}
        with patch("frostAPI.fetch_frostapi.requests.get", return_value=mock_response):
            result = fetch_data_from_frostAPI("test_endpoint", "test_id", ["air_temperature"])
            self.assertEqual(result, [{"mock": "value"}])

    def test_fetch_data_from_frostAPI_error(self):
        #Tester at funksjonen returnerer tom liste ved HTTP-feil (f.eks. 404)
        mock_response = Mock(status_code=404, text="Not Found")
        mock_response.json.return_value = {}
        with patch("frostAPI.fetch_frostapi.requests.get", return_value=mock_response):
            result = fetch_data_from_frostAPI("test_endpoint", {}, "test_id")
            self.assertEqual(result, [])

    @patch("frostAPI.fetch_frostapi.requests.get")
    def test_get_info_success(self, mock_get):
        #Tester at get_info_frostAPI returnerer elementer og skriver navn til konsoll
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = {
            "data": [{"id": "e1", "name": "Element1"}, {"id": "e2"}]
        }
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = get_info_frostAPI("url", None, "client")
            self.assertEqual(len(result), 2)
            self.assertIn("Element1", fake_out.getvalue())

    @patch("frostAPI.main_frost.get_info_frostAPI")
    def test_get_elements_wrapper(self, mock_info):
        #Tester at get_elements_frostAPI bare kaller get_info_frostAPI
        get_elements_frostAPI("test_client")
        mock_info.assert_called_once()

    @patch("frostAPI.main_frost.get_info_frostAPI")
    def test_get_stations_wrapper(self, mock_info):
        #Tester at get_stations_frostAPI bare kaller get_info_frostAPI
        get_stations_frostAPI("test_client")
        mock_info.assert_called_once()

    def test_process_weather_data_structure(self):
        #Tester at process_weather_data henter riktige kolonner og verdier fra raw-data
        raw = [{
            "referenceTime": "2023-01-01T00:00:00Z",
            "sourceId": "SN123",
            "observations": [
                {"elementId": "temp", "value": 4.5},
                {"elementId": "wind", "value": 2.1},
            ]
        }]
        mapping = {"temp": "Temperatur", "wind": "Vind"}
        processed = process_weather_data(raw, mapping)
        self.assertEqual(processed[0]["Dato"], "2023-01-01")
        self.assertEqual(processed[0]["Stasjon"], "SN123")
        self.assertEqual(processed[0]["Temperatur"], 4.5)
        self.assertEqual(processed[0]["Vind"], 2.1)
    
    def test_process_weather_data_empty_observations(self):
        #Tester at tom "observations"-liste ikke gir KeyError eller feilkolonner
        raw = [{
            "referenceTime": "2023-01-01T00:00:00Z",
            "sourceId": "SN123",
            "observations": []
        }]
        mapping = {"temp": "Temperatur"}
        result = process_weather_data(raw, mapping)
        self.assertEqual(result[0]["Dato"], "2023-01-01")
        self.assertEqual(result[0]["Stasjon"], "SN123")
        self.assertNotIn("Temperatur", result[0])

    @patch("frostAPI.main_frost.fetch_data_from_frostAPI")
    @patch("frostAPI.main_frost.save_data_as_json")
    def test_data_frostAPI(self, mock_save, mock_fetch):
        # Tester at data_frostAPI kaller både fetch og lagring når det får data
        mock_fetch.return_value = [{
            "referenceTime": "2023-01-01T00:00:00Z",
            "sourceId": "SN123",
            "observations": [
                {"elementId": "mean(air_temperature P1D)", "value": 5.0},
                {"elementId": "sum(precipitation_amount P1D)", "value": 3.0},
                {"elementId": "mean(wind_speed P1D)", "value": 1.2}
            ]
        }]
        data_frostAPI("test_client")
        self.assertTrue(mock_save.called)

    @patch("frostAPI.fetch_frostapi.requests.get")
    def test_get_info_error(self, mock_get):
        #Tester at funksjonen håndterer forespørselsfeil (f.eks. timeout) riktig
        mock_get.side_effect = requests.RequestException("Timeout")
        result = get_info_frostAPI("url", None, "client")
        self.assertIsNone(result)

    @patch("frostAPI.fetch_frostapi.pd.DataFrame.to_json")
    def test_save_data_as_json(self, mock_to_json):
        # Tester at save_data_as_json forsøker å skrive til JSON
        data = [{"Dato": "2023-01-01", "Stasjon": "S1", "Temperatur": 4.0}]
        save_data_as_json(data, "dummy.json", ["Dato", "Stasjon"], ["Temperatur"])
        mock_to_json.assert_called_once()


if __name__ == "__main__":
    unittest.main()

