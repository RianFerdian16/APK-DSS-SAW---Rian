import numpy as np
import pandas as pd
import pytest

from modules.saw import hitung_saw
from modules.topsis import hitung_topsis


def dataset_supplier():
    return pd.DataFrame(
        {
            "Alternatif": ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"],
            "Harga": [5000000, 4500000, 6000000, 3500000, 5500000],
            "Kualitas": [80, 75, 90, 70, 85],
            "Ketepatan": [90, 85, 95, 80, 88],
            "Kapasitas": [75, 80, 85, 70, 90],
        }
    )


def test_saw_default_dataset_ranking_valid():
    df = dataset_supplier()
    criteria = ["Harga", "Kualitas", "Ketepatan", "Kapasitas"]
    weights = [0.30, 0.30, 0.25, 0.15]
    types = ["cost", "benefit", "benefit", "benefit"]

    result, normalized = hitung_saw(df, criteria, weights, types)

    assert len(result) == 5
    assert list(normalized.columns) == criteria
    assert result.iloc[0]["Alternatif"] == "Supplier C"
    assert result["Ranking"].min() == 1
    assert result["Skor"].between(0, 1).all()


def test_topsis_equal_alternatives_no_nan_and_equal_rank():
    df = pd.DataFrame(
        {
            "Alternatif": ["A", "B", "C", "D", "E"],
            "Harga": [100, 100, 100, 100, 100],
            "Kualitas": [80, 80, 80, 80, 80],
            "Ketepatan": [90, 90, 90, 90, 90],
            "Kapasitas": [70, 70, 70, 70, 70],
        }
    )
    criteria = ["Harga", "Kualitas", "Ketepatan", "Kapasitas"]
    weights = [0.25, 0.25, 0.25, 0.25]
    types = ["cost", "benefit", "benefit", "benefit"]

    result, _ = hitung_topsis(df, criteria, weights, types)

    assert not result["Skor"].isna().any()
    assert np.isfinite(result["Skor"]).all()
    assert set(result["Ranking"]) == {1}


def test_saw_cost_zero_raises_error():
    df = dataset_supplier()
    df.loc[0, "Harga"] = 0
    criteria = ["Harga", "Kualitas", "Ketepatan", "Kapasitas"]
    weights = [0.30, 0.30, 0.25, 0.15]
    types = ["cost", "benefit", "benefit", "benefit"]

    with pytest.raises(ValueError, match="cost"):
        hitung_saw(df, criteria, weights, types)
