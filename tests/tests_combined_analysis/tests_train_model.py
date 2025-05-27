import unittest
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from combined.combined_analysis import (
    train_model,
    evaluate_and_train_model)

class TestTrainModel(unittest.TestCase):
    def test_train_model_success(self):
        # Tester at modellen lærer korrekt sammenheng (y = 2x)
        df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
        model = train_model(df, "y", ["x"], LinearRegression())
        self.assertAlmostEqual(model.coef_[0], 2.0)

    def test_tren_modell_missing_column(self):
        # Forventer KeyError når target-kolonnen mangler
        df = pd.DataFrame({"x": [1, 2, 3]})
        with self.assertRaises(KeyError):
            train_model(df, "y", ["x"], LinearRegression())

    def test_tren_modell_empty_df(self):
        # Forventer ValueError når datasettet er tomt
        df = pd.DataFrame(columns=["x", "y"])
        with self.assertRaises(ValueError):
            train_model(df, "y", ["x"], LinearRegression())

class TestEvaluateAndTrainModel(unittest.TestCase):
    def test_evaluate_and_train_model(self):
        df = pd.DataFrame({"x": range(10), "y": [i * 2 for i in range(10)]})
        y_train, y_test, y_pred = evaluate_and_train_model(df, "y", ["x"], LinearRegression(), test_size=0.3)
        self.assertEqual(len(y_test), len(y_pred))


if __name__ == "__main__":
    unittest.main()
