import unittest
import os
import sys
import pandas as pd

# Legg til src-mappen i path slik at modulen kan importeres
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from frostAPI.clean_data_frost import (
    calculate_outlier_limits,
    remove_duplicate_dates,
    label_station,
    interpolate_data
)

class TestCleanProcessData(unittest.TestCase):

    def test_calculate_outlier_limits(self):
        # Tester at grenseverdier for outliers beregnes korrekt
        df = pd.DataFrame({"val": [10, 10, 10, 100]})  # én outlier
        low, high = calculate_outlier_limits(df, "val", threshold=1)
        self.assertLess(low, 10)   # Nedre grense skal være mindre enn normalverdi
        self.assertGreater(high, 10)  # Øvre grense skal være høyere enn normalverdi

    def test_remove_duplicate_dates(self):
        # Tester at duplikater fjernes basert på "Dato" og "Stasjon"
        df = pd.DataFrame({
            "Dato": ["2023-01-01", "2023-01-01"],
            "Stasjon": ["S1", "S1"],
            "Temp": [1, 1]
        })
        cleaned = remove_duplicate_dates(df, ["Dato", "Stasjon"])
        self.assertEqual(len(cleaned), 1)  # Bare én rad skal være igjen

    def test_remove_duplicate_dates_no_dupes(self):
        # Tester at ikke-dupliserte rader beholdes
        df = pd.DataFrame({
            "Dato": ["2023-01-01", "2023-01-02"],
            "Stasjon": ["S1", "S2"]
        })
        cleaned = remove_duplicate_dates(df, ["Dato", "Stasjon"])
        self.assertEqual(len(cleaned), 2)  # Ingen rader fjernes

    def test_label_station_encoding(self):
        # Tester at stasjonsnavn konverteres til heltall (label encoded)
        df = pd.DataFrame({"Stasjon": ["A", "B", "A"]})
        encoded = label_station(df)
        self.assertTrue(pd.api.types.is_integer_dtype(encoded["Stasjon"]))  # Må være integer

    def test_label_station_consistency(self):
        # Tester at samme stasjonsnavn får samme tallverdi
        df = pd.DataFrame({"Stasjon": ["X", "Y", "X"]})
        labeled = label_station(df)
        self.assertEqual(labeled["Stasjon"].iloc[0], labeled["Stasjon"].iloc[2])  # "X" skal ha samme label

    def test_interpolate_data_gap(self):
        # Tester at interpolering mellom to datoer fungerer korrekt
        df = pd.DataFrame({
            "Dato": ["2023-01-01", "2023-01-03"],
            "Temperatur": [1.0, 3.0]
        })
        df["Dato"] = pd.to_datetime(df["Dato"])
        result = interpolate_data(df, "2023-01-01", "2023-01-03", ["Temperatur"])
        interpolated = result[result["Dato"] == "2023-01-02"]["Temperatur"].iloc[0]
        self.assertAlmostEqual(interpolated, 2.0)  # Interpolert verdi mellom 1.0 og 3.0 skal være 2.0

    def test_interpolation_flag_column(self):
        # Tester at interpolert verdi flagges med "Interpolert_<kolonnenavn>"
        df = pd.DataFrame({
            "Dato": ["2023-01-01", "2023-01-03"],
            "Temperatur": [1.0, 3.0]
        })
        df["Dato"] = pd.to_datetime(df["Dato"])
        result = interpolate_data(df, "2023-01-01", "2023-01-03", ["Temperatur"])
        self.assertIn("Interpolert_Temperatur", result.columns)  # Ny kolonne skal finnes
        self.assertTrue(result.loc[result["Dato"] == "2023-01-02", "Interpolert_Temperatur"].iloc[0])  # Skal være True for interpolert dag

if __name__ == "__main__":
    unittest.main()
