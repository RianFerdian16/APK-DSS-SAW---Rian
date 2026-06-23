from __future__ import annotations

import numpy as np
import pandas as pd


def hitung_topsis(
    df: pd.DataFrame,
    kriteria: list[str],
    bobot: list[float],
    tipe: list[str],
) -> pd.DataFrame:
    """Alternatif metode TOPSIS. Disiapkan sebagai pengembangan aplikasi."""
    matrix = df[kriteria].astype(float).to_numpy()
    pembagi = np.sqrt((matrix**2).sum(axis=0))
    pembagi[pembagi == 0] = 1

    bobot_normal = np.array(bobot, dtype=float) / sum(bobot)
    normalized = matrix / pembagi
    weighted = normalized * bobot_normal

    ideal_positif = np.array([
        weighted[:, i].max() if tipe[i] == "benefit" else weighted[:, i].min()
        for i in range(len(kriteria))
    ])
    ideal_negatif = np.array([
        weighted[:, i].min() if tipe[i] == "benefit" else weighted[:, i].max()
        for i in range(len(kriteria))
    ])

    jarak_positif = np.sqrt(((weighted - ideal_positif) ** 2).sum(axis=1))
    jarak_negatif = np.sqrt(((weighted - ideal_negatif) ** 2).sum(axis=1))
    preferensi = jarak_negatif / (jarak_positif + jarak_negatif)

    hasil = df.copy()
    hasil["Skor"] = preferensi
    hasil["Ranking"] = hasil["Skor"].rank(ascending=False, method="dense").astype(int)
    return hasil.sort_values(["Ranking", "Skor"], ascending=[True, False]).reset_index(drop=True)
