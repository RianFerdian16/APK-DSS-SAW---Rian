from __future__ import annotations

import numpy as np
import pandas as pd


def hitung_topsis(
    df: pd.DataFrame,
    kriteria: list[str],
    bobot: list[float],
    tipe: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Menghitung ranking dengan metode TOPSIS.

    TOPSIS memilih alternatif terbaik berdasarkan jarak terdekat dari solusi ideal positif
    dan jarak terjauh dari solusi ideal negatif.
    """
    if len(kriteria) != len(bobot) or len(kriteria) != len(tipe):
        raise ValueError("Jumlah kriteria, bobot, dan tipe kriteria harus sama.")

    total_bobot = sum(bobot)
    if total_bobot <= 0:
        raise ValueError("Total bobot harus lebih dari 0.")

    matrix = df[kriteria].astype(float).to_numpy()
    if np.any(matrix < 0):
        raise ValueError("Nilai kriteria tidak boleh negatif.")

    pembagi = np.sqrt((matrix**2).sum(axis=0))
    pembagi[pembagi == 0] = 1

    bobot_normal = np.array(bobot, dtype=float) / total_bobot
    normalisasi = matrix / pembagi
    terbobot = normalisasi * bobot_normal

    ideal_positif = np.array([
        terbobot[:, i].max() if tipe[i] == "benefit" else terbobot[:, i].min()
        for i in range(len(kriteria))
    ])
    ideal_negatif = np.array([
        terbobot[:, i].min() if tipe[i] == "benefit" else terbobot[:, i].max()
        for i in range(len(kriteria))
    ])

    jarak_positif = np.sqrt(((terbobot - ideal_positif) ** 2).sum(axis=1))
    jarak_negatif = np.sqrt(((terbobot - ideal_negatif) ** 2).sum(axis=1))
    preferensi = jarak_negatif / (jarak_positif + jarak_negatif)

    hasil = df.copy()
    hasil["Jarak Ideal +"] = jarak_positif.round(4)
    hasil["Jarak Ideal -"] = jarak_negatif.round(4)
    hasil["Skor"] = preferensi
    hasil["Ranking"] = hasil["Skor"].rank(ascending=False, method="dense").astype(int)
    hasil = hasil.sort_values(["Ranking", "Skor"], ascending=[True, False]).reset_index(drop=True)
    hasil["Skor"] = hasil["Skor"].round(4)

    normalisasi_df = pd.DataFrame(normalisasi, columns=kriteria).round(4)
    return hasil, normalisasi_df
