from __future__ import annotations

import pandas as pd
import plotly.express as px


def grafik_ranking(hasil: pd.DataFrame):
    fig = px.bar(
        hasil.sort_values("Skor", ascending=True),
        x="Skor",
        y="Alternatif",
        orientation="h",
        text="Skor",
        title="Grafik Skor Preferensi SAW",
    )
    fig.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig.update_layout(
        xaxis_range=[0, 1.05],
        yaxis_title="Alternatif",
        xaxis_title="Skor Preferensi",
        height=430,
        margin=dict(l=20, r=30, t=60, b=20),
    )
    return fig


def grafik_bobot(kriteria: list[str], bobot_normal: list[float]):
    df_bobot = pd.DataFrame({"Kriteria": kriteria, "Bobot": bobot_normal})
    fig = px.pie(df_bobot, names="Kriteria", values="Bobot", title="Komposisi Bobot Kriteria")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=60, b=20))
    return fig
