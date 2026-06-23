from __future__ import annotations

import numpy as np
import pandas as pd


def normalisasi_saw(df: pd.DataFrame, kriteria: list[str], tipe: list[str]) -> pd.DataFrame:
    """Melakukan normalisasi matriks keputusan untuk metode SAW.

    Benefit: nilai / nilai maksimum.
    Cost: nilai minimum / nilai.
    """
    if len(kriteria) != len(tipe):
        raise ValueError("Jumlah kriteria dan tipe kriteria harus sama.")

    matrix = df[kriteria].astype(float).to_numpy()
    normalized = np.zeros_like(matrix, dtype=float)

    for index, jenis in enumerate(tipe):
        column = matrix[:, index]
        if np.any(column < 0):
            raise ValueError("Nilai kriteria tidak boleh negatif.")

        if jenis == "benefit":
            max_value = column.max()
            normalized[:, index] = 0 if max_value == 0 else column / max_value
        elif jenis == "cost":
            if np.any(column == 0):
                raise ValueError("Kriteria bertipe cost tidak boleh memiliki nilai 0.")
            min_value = column.min()
            normalized[:, index] = min_value / column
        else:
            raise ValueError("Tipe kriteria hanya boleh 'benefit' atau 'cost'.")

    return pd.DataFrame(normalized, columns=kriteria)


def hitung_saw(
    df: pd.DataFrame,
    kriteria: list[str],
    bobot: list[float],
    tipe: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Menghitung skor preferensi dan ranking dengan metode SAW."""
    if len(kriteria) != len(bobot):
        raise ValueError("Jumlah kriteria dan bobot harus sama.")

    total_bobot = sum(bobot)
    if total_bobot <= 0:
        raise ValueError("Total bobot harus lebih dari 0.")

    bobot_normal = np.array(bobot, dtype=float) / total_bobot
    normalisasi = normalisasi_saw(df, kriteria, tipe)
    skor = normalisasi.to_numpy().dot(bobot_normal)

    hasil = df.copy()
    hasil["Skor"] = skor
    hasil["Ranking"] = hasil["Skor"].rank(ascending=False, method="dense").astype(int)
    hasil = hasil.sort_values(["Ranking", "Skor"], ascending=[True, False]).reset_index(drop=True)
    hasil["Skor"] = hasil["Skor"].round(4)

    return hasil, normalisasi.round(4)
