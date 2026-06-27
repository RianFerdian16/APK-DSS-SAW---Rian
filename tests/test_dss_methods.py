import numpy as np
import pandas as pd

from modules.saw import hitung_saw
from modules.topsis import hitung_topsis


def laptop_dataset():
    return pd.DataFrame(
        {
            "Alternatif": [
                "Asus Vivobook 14",
                "Lenovo IdeaPad Slim 3",
                "Acer Aspire 5",
                "HP Pavilion 14",
                "MSI Modern 14",
            ],
            "Harga": [7500000, 7200000, 8000000, 8500000, 9000000],
            "Performa": [82, 80, 86, 88, 90],
            "Baterai": [78, 82, 76, 80, 84],
            "Portabilitas": [85, 88, 80, 83, 78],
        }
    )


CRITERIA = ["Harga", "Performa", "Baterai", "Portabilitas"]
TYPES = ["cost", "benefit", "benefit", "benefit"]


def test_saw_bobot_tidak_total_100_tetap_berjalan():
    df = laptop_dataset()
    bobot = [3, 3, 2, 1]  # total bukan 100, harus tetap dinormalisasi internal

    hasil, normalisasi = hitung_saw(df, CRITERIA, bobot, TYPES)

    assert len(hasil) == 5
    assert "Skor" in hasil.columns
    assert hasil["Skor"].notna().all()
    assert normalisasi.shape == (5, 4)
    assert hasil.iloc[0]["Ranking"] == 1


def test_topsis_semua_nilai_alternatif_sama_tidak_nan():
    df = pd.DataFrame(
        {
            "Alternatif": ["Laptop A", "Laptop B", "Laptop C", "Laptop D", "Laptop E"],
            "Harga": [8000000, 8000000, 8000000, 8000000, 8000000],
            "Performa": [80, 80, 80, 80, 80],
            "Baterai": [80, 80, 80, 80, 80],
            "Portabilitas": [80, 80, 80, 80, 80],
        }
    )
    bobot = [30, 30, 25, 15]

    hasil, normalisasi = hitung_topsis(df, CRITERIA, bobot, TYPES)

    assert len(hasil) == 5
    assert hasil["Skor"].notna().all()
    assert np.isfinite(hasil["Skor"]).all()
    assert normalisasi.shape == (5, 4)


def test_dataset_memenuhi_minimal_5_alternatif_4_kriteria():
    df = laptop_dataset()

    assert len(df) >= 5
    assert len(CRITERIA) >= 4
    assert all(col in df.columns for col in ["Alternatif", *CRITERIA])
