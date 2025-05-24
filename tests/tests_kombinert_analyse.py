import unittest
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kombinert_analyse import (
    kombinere_df,
    tren_modell,
    prediker_fremtid,
    legg_til_sesongvariabler
)


class TestKombinereDF(unittest.TestCase):
    def test_kombinere_df_success(self):
        data1 = [{"Dato": "2023-01-01", "A": 1}]
        data2 = [{"Dato": "2023-01-01", "B": 10}]
        with open("f1.json", "w", encoding="utf-8") as f:
            json.dump(data1, f)
        with open("f2.json", "w", encoding="utf-8") as f:
            json.dump(data2, f)

        df = kombinere_df("f1.json", "f2.json", "Dato")
        self.assertIn("A", df.columns)
        self.assertIn("B", df.columns)
        self.assertEqual(len(df), 1)

        os.remove("f1.json")
        os.remove("f2.json")

    def test_kombinere_df_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            kombinere_df("missing1.json", "missing2.json", "Dato")

    def test_kombinere_df_invalid_key(self):
        data1 = [{"Dato": "2023-01-01", "A": 1}]
        data2 = [{"Dato": "2023-01-01", "B": 10}]
        with open("f1.json", "w", encoding="utf-8") as f:
            json.dump(data1, f)
        with open("f2.json", "w", encoding="utf-8") as f:
            json.dump(data2, f)

        with self.assertRaises(KeyError):
            kombinere_df("f1.json", "f2.json", "FeilKolonne")

        os.remove("f1.json")
        os.remove("f2.json")


class TestTrenModell(unittest.TestCase):
    def test_tren_modell_success(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
        model = tren_modell(df, "y", ["x"], LinearRegression())
        self.assertAlmostEqual(model.coef_[0], 2.0)

    def test_tren_modell_missing_column(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        with self.assertRaises(KeyError):
            tren_modell(df, "y", ["x"], LinearRegression())

    def test_tren_modell_empty_df(self):
        df = pd.DataFrame(columns=["x", "y"])
        with self.assertRaises(ValueError):
            tren_modell(df, "y", ["x"], LinearRegression())


class TestLeggTilSesongvariabler(unittest.TestCase):
    def test_legg_til_sesongvariabler(self):
        df = pd.DataFrame({"Dato": ["2023-01-01", "2023-06-01"]})
        result = legg_til_sesongvariabler(df)
        self.assertIn("måned", result.columns)
        self.assertIn("sin_dag", result.columns)
        self.assertEqual(result.loc[0, "måned"], 1)
        self.assertEqual(result.loc[1, "måned"], 6)


class TestPredikerFremtid(unittest.TestCase):
    def test_prediker_fremtid_success(self):
        df = pd.DataFrame({
            "Dato": pd.date_range("2023-01-01", periods=5),
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10]
        })
        df = legg_til_sesongvariabler(df)
        model = tren_modell(df, "y", ["x", "måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"], LinearRegression())
        future = prediker_fremtid(df, model, ["x", "måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"], "y", 2)
        self.assertEqual(len(future), 2)
        self.assertIn("predicted_y", future.columns)

    def test_prediker_fremtid_invalid_feature(self):
        df = pd.DataFrame({
            "Dato": pd.date_range("2023-01-01", periods=5),
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10]
        })
        df = legg_til_sesongvariabler(df)
        model = tren_modell(df, "y", ["x", "måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"], LinearRegression())

        with self.assertRaises(KeyError):
            prediker_fremtid(df, model, ["feil_feature"], "y", 2)


if __name__ == "__main__":
    unittest.main()
