import unittest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
import json
import sys, os
from datetime import datetime
from lightgbm import LGBMRegressor
from sklearn.linear_model import LinearRegression

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kombinert_analyse import (
    kombinere_df,
    tren_modell,
    prediker_fremtid,
    legg_til_sesongvariabler
)


class TestFetchFunctions(unittest.TestCase):
    def test_kombinere_df(self):
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
    
    def test_tren_modell(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
        model = tren_modell(df, "y", ["x"], LinearRegression())
        self.assertAlmostEqual(model.coef_[0], 2.0)
    
    def test_prediker_fremtid(self):
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

if __name__ == "__main__":
    unittest.main()