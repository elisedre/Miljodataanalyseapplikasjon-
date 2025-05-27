import unittest
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from combined.combined_analysis import (
    add_seasonal_features,
    predict_feature_values,
    train_model)

class TestAddSeasonalFeatures(unittest.TestCase):
    def test_add_seasonal_features(self):
        # Tester at sesongbaserte variabler blir lagt til korrekt
        df = pd.DataFrame({"Dato": ["2023-01-01", "2023-06-01"]})
        result = add_seasonal_features(df)
        self.assertIn("måned", result.columns)
        self.assertIn("sin_dag", result.columns)
        self.assertEqual(result.loc[0, "måned"], 1)
        self.assertEqual(result.loc[1, "måned"], 6)


class TestPredictFeatureValues(unittest.TestCase):
    def test_predict_feature_values(self):
        # Tester at funksjonen genererer fremtidige prediksjoner korrekt
        df = pd.DataFrame({
            "Dato": pd.date_range("2023-01-01", periods=5),
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10]
        })
        df = add_seasonal_features(df)
        model = train_model(df, "y", ["x", "måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"], LinearRegression())
        future = predict_feature_values(df, model, ["x", "måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"], "y", 2)
        self.assertEqual(len(future), 2)
        self.assertIn("predicted_y", future.columns)

    def test_predict_invalid_feature(self):
        # Forventer KeyError ved bruk av ikke-eksisterende feature
        df = pd.DataFrame({
            "Dato": pd.date_range("2023-01-01", periods=5),
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10]
        })
        df = add_seasonal_features(df)
        model = train_model(df, "y", ["x", "måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"], LinearRegression())

        with self.assertRaises(KeyError):
            predict_feature_values(df, model, ["feil_feature"], "y", 2)

    def test_predict_feature_values_output(self):
        # Tester at prediksjon gir 3 rader og inneholder kolonnen "predicted_y"
        df = pd.DataFrame({
            "Dato": pd.date_range("2023-01-01", periods=5),
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10]
        })
        df = add_seasonal_features(df)
        features = ["x", "måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"]
        model = train_model(df, "y", features, LinearRegression())
        future = predict_feature_values(df, model, features, "y", num_days=3)
        self.assertEqual(len(future), 3)
        self.assertIn("predicted_y", future.columns)
        
if __name__ == "__main__":
    unittest.main()
