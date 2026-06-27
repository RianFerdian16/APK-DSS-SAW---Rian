from __future__ import annotations

import pandas as pd
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from modules.saw import hitung_saw
from modules.topsis import hitung_topsis
from modules.supabase_handler import ambil_history, is_connected, simpan_history
from modules.visualizer import grafik_bobot, grafik_ranking

st.set_page_config(
    page_title="UAS APK Rian - DSS Laptop",
    page_icon="💻",
    layout="wide",
)

METHOD_OPTIONS = {
    "SAW": "SAW (Simple Additive Weighting)",
    "TOPSIS": "TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)",
}

DEFAULT_WEIGHT_BY_CRITERIA = {
    "Harga": 30,
    "Performa": 30,
    "Baterai": 25,
    "Portabilitas": 15,
}


def load_example_data() -> pd.DataFrame:
    return pd.read_csv("data/contoh_data.csv")


def infer_criteria(df: pd.DataFrame) -> list[str]:
    """Ambil semua kolom numerik selain kolom Alternatif sebagai kriteria."""
    return [
        col
        for col in df.columns
        if col != "Alternatif" and pd.api.types.is_numeric_dtype(df[col])
    ]


def default_type_for_criteria(criteria_name: str) -> str:
    lower_name = criteria_name.lower()
    cost_keywords = ["harga", "biaya", "cost", "tarif", "jarak", "waktu"]
    return "cost" if any(keyword in lower_name for keyword in cost_keywords) else "benefit"


def default_weight_for_criteria(criteria_name: str, criteria_count: int) -> int:
    if criteria_name in DEFAULT_WEIGHT_BY_CRITERIA:
        return DEFAULT_WEIGHT_BY_CRITERIA[criteria_name]
    return max(1, round(100 / max(criteria_count, 1)))


def validate_dataset(df: pd.DataFrame, kriteria: list[str]) -> tuple[bool, str]:
    if "Alternatif" not in df.columns:
        return False, "Kolom wajib 'Alternatif' belum ada."

    if df.empty:
        return False, "Dataset masih kosong."

    if len(df) < 5:
        return False, "Dataset minimal harus memiliki 5 alternatif."

    if len(kriteria) < 4:
        return False, "Dataset minimal harus memiliki 4 kriteria numerik."

    for col in kriteria:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"Kolom {col} harus berisi angka."
        if df[col].isna().any():
            return False, f"Kolom {col} tidak boleh ada nilai kosong."

    if df["Alternatif"].isna().any():
        return False, "Kolom Alternatif tidak boleh kosong."

    if df["Alternatif"].astype(str).str.strip().eq("").any():
        return False, "Nama alternatif tidak boleh kosong."

    return True, "Dataset valid dan memenuhi minimal 5 alternatif + 4 kriteria."


def normalize_weight_percentages(weights: list[int]) -> list[float]:
    total = sum(weights)
    if total == 0:
        return [0 for _ in weights]
    return [round(weight / total, 4) for weight in weights]


def get_method_explanation(method: str) -> str:
    if method == "TOPSIS":
        return """
        **TOPSIS** bekerja dengan cara:
        1. Menentukan alternatif dan kriteria.
        2. Melakukan normalisasi matriks keputusan.
        3. Mengalikan nilai normalisasi dengan bobot.
        4. Menentukan solusi ideal positif dan negatif.
        5. Menghitung jarak alternatif dari solusi ideal.
        6. Menentukan ranking berdasarkan nilai preferensi terbesar.
        """

    return """
    **SAW (Simple Additive Weighting)** bekerja dengan cara:
    1. Menentukan alternatif dan kriteria.
    2. Menentukan tipe kriteria: cost atau benefit.
    3. Melakukan normalisasi nilai.
    4. Mengalikan nilai normalisasi dengan bobot.
    5. Menentukan ranking berdasarkan skor terbesar.
    """


st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: .25rem;
    }
    .subtitle {
        color: #64748b;
        margin-bottom: 1.25rem;
    }
    .metric-card {
        border: 1px solid rgba(148, 163, 184, .25);
        border-radius: 18px;
        padding: 18px;
        background: rgba(255,255,255,.03);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">UAS APK Rian - DSS Pemilihan Laptop Terbaik</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Aplikasi pendukung keputusan untuk memilih laptop terbaik untuk mahasiswa menggunakan metode SAW/TOPSIS.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Pengaturan DSS")
    dataset_name = st.text_input("Nama kasus/dataset", value="Pemilihan Laptop Terbaik untuk Mahasiswa")

    st.subheader("Upload Dataset")
    uploaded_file = st.file_uploader(
        "Upload data CSV alternatif",
        type=["csv"],
        help="Kolom wajib: Alternatif + minimal 4 kriteria numerik. Contoh: Harga, Performa, Baterai, Portabilitas.",
    )

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    data = load_example_data()

criteria = infer_criteria(data)
criteria_count = len(criteria)

with st.sidebar:
    st.subheader("Metode Perhitungan")
    selected_method_label = st.selectbox(
        "Pilih metode",
        options=list(METHOD_OPTIONS.values()),
        index=0,
    )
    selected_method = next(key for key, value in METHOD_OPTIONS.items() if value == selected_method_label)

    st.subheader("Bobot Kriteria")
    raw_weights: list[int] = []
    for criterion in criteria:
        default_value = default_weight_for_criteria(criterion, criteria_count)
        raw_weights.append(st.slider(criterion, 0, 100, default_value, key=f"weight_{criterion}"))

    normalized_weights = normalize_weight_percentages(raw_weights)
    st.caption(f"Total bobot input: {sum(raw_weights)}. Sistem otomatis menormalisasi bobot menjadi total 1.")

    st.subheader("Tipe Kriteria")
    selected_types: list[str] = []
    for criterion in criteria:
        default_type = default_type_for_criteria(criterion)
        selected_types.append(
            st.selectbox(
                criterion,
                options=["benefit", "cost"],
                index=0 if default_type == "benefit" else 1,
                key=f"type_{criterion}",
                help="benefit = semakin besar semakin baik, cost = semakin kecil semakin baik.",
            )
        )

    st.caption("Untuk kasus laptop: Harga = cost, Performa/Baterai/Portabilitas = benefit.")

    if is_connected():
        st.success("Supabase terkoneksi")
    else:
        st.warning("Supabase belum terkoneksi")

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("Data Alternatif")
    st.caption("Kamu bisa edit langsung tabel di bawah sebelum dihitung.")
    edited_data = st.data_editor(
        data,
        use_container_width=True,
        num_rows="dynamic",
        key="data_editor",
    )

with right:
    st.subheader("Ringkasan Metode")
    st.markdown(get_method_explanation(selected_method))
    bobot_df = pd.DataFrame(
        {
            "Kriteria": criteria,
            "Tipe": selected_types,
            "Bobot Normal": normalized_weights,
        }
    )
    st.dataframe(bobot_df, use_container_width=True, hide_index=True)

is_valid, message = validate_dataset(edited_data, criteria)
if is_valid:
    st.success(message)
else:
    st.error(message)

calculate = st.button(
    f"Hitung Ranking {selected_method}",
    type="primary",
    use_container_width=True,
    disabled=not is_valid,
)

if calculate:
    try:
        if selected_method == "TOPSIS":
            hasil, normalisasi = hitung_topsis(edited_data, criteria, normalized_weights, selected_types)
        else:
            hasil, normalisasi = hitung_saw(edited_data, criteria, normalized_weights, selected_types)

        best = hasil.iloc[0]

        st.divider()
        st.subheader(f"Hasil Rekomendasi Metode {selected_method}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Alternatif Terbaik", best["Alternatif"])
        c2.metric("Skor Tertinggi", f"{best['Skor']:.4f}")
        c3.metric("Jumlah Alternatif", len(hasil))

        st.dataframe(hasil, use_container_width=True, hide_index=True)

        chart_col, weight_col = st.columns([1.3, 0.7], gap="large")
        with chart_col:
            st.plotly_chart(grafik_ranking(hasil), use_container_width=True)
        with weight_col:
            st.plotly_chart(grafik_bobot(criteria, normalized_weights), use_container_width=True)

        with st.expander(f"Lihat matriks normalisasi {selected_method}"):
            normalisasi_display = pd.concat([edited_data[["Alternatif"]].reset_index(drop=True), normalisasi], axis=1)
            st.dataframe(normalisasi_display, use_container_width=True, hide_index=True)

        csv_result = hasil.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download hasil ranking CSV",
            data=csv_result,
            file_name=f"hasil_ranking_{selected_method.lower()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        saved, save_message = simpan_history(
            dataset_name,
            criteria,
            selected_types,
            normalized_weights,
            hasil,
            selected_method,
        )
        if saved:
            st.success(save_message)
        else:
            st.info(save_message)

    except Exception as exc:
        st.error(f"Perhitungan gagal: {exc}")

st.divider()
st.subheader("Histori Perhitungan dari Supabase")
history, error = ambil_history(limit=10)
if error:
    st.info(error)
elif history.empty:
    st.caption("Belum ada histori perhitungan.")
else:
    if "created_at" in history.columns:
        history["created_at"] = pd.to_datetime(history["created_at"]).dt.strftime("%d %b %Y %H:%M")
    st.dataframe(history, use_container_width=True, hide_index=True)

st.caption("Dibuat oleh Rian Ferdiansyah | UAS Aplikasi Pendukung Keputusan")
