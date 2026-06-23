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
    page_title="Aplikasi Sistem Pendukung Keputusan",
    page_icon="📊",
    layout="wide",
)

DEFAULT_CRITERIA = ["Harga", "Kualitas", "Ketepatan"]
DEFAULT_TYPES = ["cost", "benefit", "benefit"]
DEFAULT_WEIGHTS = [40, 35, 25]
METHOD_OPTIONS = {
    "SAW": "SAW (Simple Additive Weighting)",
    "TOPSIS": "TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)",
}


@st.cache_data
def load_example_data() -> pd.DataFrame:
    return pd.read_csv("data/contoh_data.csv")


def validate_dataset(df: pd.DataFrame, kriteria: list[str]) -> tuple[bool, str]:
    required_columns = ["Alternatif", *kriteria]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return False, f"Kolom wajib belum ada: {', '.join(missing)}"

    if df.empty:
        return False, "Dataset masih kosong."

    for col in kriteria:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"Kolom {col} harus berisi angka."
        if df[col].isna().any():
            return False, f"Kolom {col} tidak boleh ada nilai kosong."

    if df["Alternatif"].isna().any():
        return False, "Kolom Alternatif tidak boleh kosong."

    return True, "Dataset valid."


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
        5. Menghitung jarak setiap alternatif dari solusi ideal.
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

st.markdown('<div class="main-title">Aplikasi Sistem Pendukung Keputusan</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Aplikasi Pendukung Keputusan untuk menentukan alternatif terbaik berdasarkan bobot kriteria.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Pengaturan DSS")
    dataset_name = st.text_input("Nama kasus/dataset", value="Pemilihan Supplier Terbaik")

    st.subheader("Metode Perhitungan")
    selected_method_label = st.selectbox(
        "Pilih metode",
        options=list(METHOD_OPTIONS.values()),
        index=0,
    )
    selected_method = next(key for key, value in METHOD_OPTIONS.items() if value == selected_method_label)

    st.subheader("Bobot Kriteria")
    harga_weight = st.slider("Harga / Biaya", 0, 100, DEFAULT_WEIGHTS[0])
    kualitas_weight = st.slider("Kualitas", 0, 100, DEFAULT_WEIGHTS[1])
    ketepatan_weight = st.slider("Ketepatan", 0, 100, DEFAULT_WEIGHTS[2])

    raw_weights = [harga_weight, kualitas_weight, ketepatan_weight]
    normalized_weights = normalize_weight_percentages(raw_weights)
    st.caption(f"Total bobot input: {sum(raw_weights)}. Sistem otomatis menormalisasi bobot menjadi total 1.")

    st.subheader("Tipe Kriteria")
    st.caption("Harga = cost karena semakin rendah semakin baik. Kualitas dan ketepatan = benefit karena semakin tinggi semakin baik.")

    if is_connected():
        st.success("Supabase terkoneksi")
    else:
        st.warning("Supabase belum terkoneksi")

uploaded_file = st.file_uploader(
    "Upload data CSV alternatif",
    type=["csv"],
    help="Kolom wajib: Alternatif, Harga, Kualitas, Ketepatan",
)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    data = load_example_data()

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
            "Kriteria": DEFAULT_CRITERIA,
            "Tipe": DEFAULT_TYPES,
            "Bobot Normal": normalized_weights,
        }
    )
    st.dataframe(bobot_df, use_container_width=True, hide_index=True)

is_valid, message = validate_dataset(edited_data, DEFAULT_CRITERIA)
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
            hasil, normalisasi = hitung_topsis(edited_data, DEFAULT_CRITERIA, normalized_weights, DEFAULT_TYPES)
        else:
            hasil, normalisasi = hitung_saw(edited_data, DEFAULT_CRITERIA, normalized_weights, DEFAULT_TYPES)

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
            st.plotly_chart(grafik_bobot(DEFAULT_CRITERIA, normalized_weights), use_container_width=True)

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
            DEFAULT_CRITERIA,
            DEFAULT_TYPES,
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

st.caption("Dibuat oleh Rian Ferdiansyah | Aplikasi Sistem Pendukung Keputusan")
