import numpy as np
import pandas as pd

def compute_kpi(df: pd.DataFrame) -> dict:
    """Возвращает словарь ключевых метрик для Overview"""
    return {
        "avg_score":  round(df["total_cup_points"].mean(), 2),
        "top_countries": (
            df.groupby("country_of_origin")["total_cup_points"]
              .mean()
              .sort_values(ascending=False)
              .head(5)
              .round(2)
              .to_dict()
        ),
        "process_share": (
            df["processing_method"]
              .fillna("Unknown")
              .value_counts(normalize=True)
              .round(3)
              .to_dict()
        ),
        "sample_count": len(df),
    }

def predict_score(row: pd.Series, aroma: float, acidity: float) -> float:
    """
    Линейная what-if модель:
    итоговая оценка изменяется пропорционально двум параметрам.
    """
    base = row["total_cup_points"]
    delta = 0.4 * (aroma - row["aroma"]) + 0.3 * (acidity - row["acidity"])
    return round(base + delta, 2)
