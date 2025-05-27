import unittest
import json
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from combined.combined_analysis import (
    combine_df,
    prepare_dataframe)

class TestCombineDF(unittest.TestCase):

    def test_combine_df_success(self):
            # Tester at to JSON-filer kan kombineres korrekt på 'Dato'
            data1 = [{"Dato": "2023-01-01", "A": 1}]
            data2 = [{"Dato": "2023-01-01", "B": 10}]
            with open("f1.json", "w", encoding="utf-8") as f:
                json.dump(data1, f)
            with open("f2.json", "w", encoding="utf-8") as f:
                json.dump(data2, f)

            df = combine_df("f1.json", "f2.json", "Dato")
            self.assertIn("A", df.columns)
            self.assertIn("B", df.columns)
            self.assertEqual(len(df), 1)

            os.remove("f1.json")
            os.remove("f2.json")

    def test_combine_df_missing_file(self):
        # Forventer FileNotFoundError hvis filene mangler
        with self.assertRaises(FileNotFoundError):
            combine_df("missing1.json", "missing2.json", "Dato")

    def test_kombinere_df_invalid_key(self):
        # Forventer KeyError ved feil kolonnenavn for join
        data1 = [{"Dato": "2023-01-01", "A": 1}]
        data2 = [{"Dato": "2023-01-01", "B": 10}]
        with open("f1.json", "w", encoding="utf-8") as f:
            json.dump(data1, f)
        with open("f2.json", "w", encoding="utf-8") as f:
            json.dump(data2, f)

        with self.assertRaises(KeyError):
            combine_df("f1.json", "f2.json", "FeilKolonne")

        os.remove("f1.json")
        os.remove("f2.json")

class TestPrepareDataFrame(unittest.TestCase):

    def test_prepare_dataframe_success(self):
        # Tester at dato konverteres riktig og sorteres stigende
        df = pd.DataFrame({"Dato": ["2023-01-02", "2023-01-01"]})
        result = prepare_dataframe(df, "Dato")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result["Dato"]))
        self.assertTrue(result.iloc[0]["Dato"] < result.iloc[1]["Dato"])

    def test_prepare_dataframe_missing_column(self):
        # Tester at feil kastes når datokolonne mangler
        df = pd.DataFrame({"NotDate": ["2023-01-01"]})
        with self.assertRaises(ValueError):
            prepare_dataframe(df, "Dato")

    def test_prepare_dataframe_invalid_format(self):
        # Tester at feil kastes ved ugyldig datoverdi
        df = pd.DataFrame({"Dato": ["invalid-date"]})
        with self.assertRaises(ValueError):
            prepare_dataframe(df, "Dato")


if __name__ == "__main__":
    unittest.main()