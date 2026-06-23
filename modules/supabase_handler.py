from __future__ import annotations

import json
import os
from typing import Any

import pandas as pd

try:
    from supabase import Client, create_client
except Exception:  # pragma: no cover - supaya aplikasi tetap bisa jalan lokal tanpa library supabase
    Client = None
    create_client = None


TABLE_NAME = "dss_history"


def get_supabase_client() -> Client | None:
    """Membuat koneksi Supabase dari environment variable."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not url or not key or create_client is None:
        return None

    return create_client(url, key)


def is_connected() -> bool:
    return get_supabase_client() is not None


def simpan_history(
    dataset_name: str,
    kriteria: list[str],
    tipe: list[str],
    bobot: list[float],
    hasil: pd.DataFrame,
    metode: str = "SAW",
) -> tuple[bool, str]:
    """Menyimpan hasil perhitungan ke tabel Supabase."""
    client = get_supabase_client()
    if client is None:
        return False, "Supabase belum terkoneksi. Isi SUPABASE_URL dan SUPABASE_ANON_KEY di Railway Variables."

    best_row = hasil.iloc[0].to_dict()
    payload: dict[str, Any] = {
        "metode": metode,
        "dataset_name": dataset_name,
        "criteria": {"kriteria": kriteria, "tipe": tipe},
        "weights": {kriteria[i]: float(bobot[i]) for i in range(len(kriteria))},
        "result": json.loads(hasil.to_json(orient="records")),
        "best_alternative": str(best_row.get("Alternatif", "-")),
        "best_score": float(best_row.get("Skor", 0)),
    }

    try:
        client.table(TABLE_NAME).insert(payload).execute()
        return True, "Hasil perhitungan berhasil disimpan ke Supabase."
    except Exception as exc:
        return False, f"Gagal menyimpan ke Supabase: {exc}"


def ambil_history(limit: int = 10) -> tuple[pd.DataFrame, str | None]:
    """Mengambil histori perhitungan terbaru dari Supabase."""
    client = get_supabase_client()
    if client is None:
        return pd.DataFrame(), "Supabase belum terkoneksi."

    try:
        response = (
            client.table(TABLE_NAME)
            .select("id, created_at, metode, dataset_name, best_alternative, best_score")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return pd.DataFrame(response.data), None
    except Exception as exc:
        return pd.DataFrame(), f"Gagal mengambil histori: {exc}"
