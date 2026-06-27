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

DEFAULT_CRITERIA = ["Harga", "Kualitas", "Ketepatan", "Kapasitas"]
DEFAULT_TYPES = ["cost", "benefit", "benefit", "benefit"]
DEFAULT_WEIGHTS = [30, 30, 25, 15]
METHOD_OPTIONS = {
    "SAW": "SAW (Simple Additive Weighting)",
    "TOPSIS": "TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)",
}
COST_KEYWORDS = ["harga", "biaya", "cost", "jarak", "waktu", "risiko", "risk"]


@st.cache_data
def load_example_data() -> pd.DataFrame:
    return pd.read_csv("data/contoh_data.csv")


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Mengubah kolom selain Alternatif menjadi angka jika memungkinkan."""
    prepared = df.copy()
    for col in prepared.columns:
        if col != "Alternatif":
            converted = pd.to_numeric(prepared[col], errors="coerce")
            if converted.notna().any():
                prepared[col] = converted
    return prepared


def infer_criteria(df: pd.DataFrame) -> list[str]:
    """Mengambil semua kolom numerik selain Alternatif sebagai kriteria DSS."""
    return [
        col
        for col in df.columns
        if col != "Alternatif" and pd.api.types.is_numeric_dtype(df[col])
    ]


def infer_default_type(criteria_name: str) -> str:
    lowered = criteria_name.lower()
    return "cost" if any(keyword in lowered for keyword in COST_KEYWORDS) else "benefit"


def get_default_weight(criteria_name: str, total_criteria: int) -> int:
    if criteria_name in DEFAULT_CRITERIA:
        return DEFAULT_WEIGHTS[DEFAULT_CRITERIA.index(criteria_name)]
    return max(1, round(100 / max(total_criteria, 1)))


def validate_dataset(df: pd.DataFrame, kriteria: list[str]) -> tuple[bool, str]:
    required_columns = ["Alternatif", *kriteria]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return False, f"Kolom wajib belum ada: {', '.join(missing)}"

    if df.empty:
        return False, "Dataset masih kosong."

    if len(df) < 5:
        return False, "Minimal harus ada 5 alternatif sesuai spesifikasi UAS."

    if len(kriteria) < 4:
        return False, "Minimal harus ada 4 kriteria sesuai spesifikasi UAS."

    for col in kriteria:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"Kolom {col} harus berisi angka."
        if df[col].isna().any():
            return False, f"Kolom {col} tidak boleh ada nilai kosong."
        if (df[col] < 0).any():
            return False, f"Kolom {col} tidak boleh berisi nilai negatif."

    if df["Alternatif"].isna().any() or (df["Alternatif"].astype(str).str.strip() == "").any():
        return False, "Kolom Alternatif tidak boleh kosong."

    return True, "Dataset valid: memenuhi minimal 5 alternatif dan 4 kriteria."


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
    '<div class="subtitle">Aplikasi DSS/SPK untuk menentukan alternatif terbaik menggunakan SAW atau TOPSIS.</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload data CSV alternatif",
    type=["csv"],
    help="Minimal kolom: Alternatif + 4 kriteria numerik. Contoh: Alternatif, Harga, Kualitas, Ketepatan, Kapasitas.",
)

if uploaded_file is not None:
    data = prepare_dataset(pd.read_csv(uploaded_file))
else:
    data = prepare_dataset(load_example_data())

available_criteria = infer_criteria(data)

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

    st.subheader("Bobot dan Tipe Kriteria")
    st.caption("Kriteria otomatis diambil dari kolom numerik CSV selain kolom Alternatif.")

    raw_weights: list[int] = []
    criteria_types: list[str] = []
    for criterion in available_criteria:
        default_weight = get_default_weight(criterion, len(available_criteria))
        raw_weights.append(
            st.slider(
                f"Bobot {criterion}",
                min_value=0,
                max_value=100,
                value=default_weight,
                key=f"weight_{criterion}",
            )
        )
        default_type = infer_default_type(criterion)
        criteria_types.append(
            st.selectbox(
                f"Tipe {criterion}",
                options=["benefit", "cost"],
                index=0 if default_type == "benefit" else 1,
                key=f"type_{criterion}",
            )
        )

    normalized_weights = normalize_weight_percentages(raw_weights)
    st.caption(f"Total bobot input: {sum(raw_weights)}. Sistem otomatis menormalisasi bobot menjadi total 1.")

    if is_connected():
        st.success("Supabase terkoneksi")
    else:
        st.warning("Supabase belum terkoneksi. Aplikasi tetap bisa dihitung, hanya histori online yang tidak tersimpan.")

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("Data Alternatif")
    st.caption("Kamu bisa edit nilai/alternatif langsung di tabel sebelum dihitung.")
    edited_data = st.data_editor(
        data,
        use_container_width=True,
        num_rows="dynamic",
        key="data_editor",
    )
    edited_data = prepare_dataset(edited_data)

with right:
    st.subheader("Ringkasan Metode")
    st.markdown(get_method_explanation(selected_method))
    if available_criteria:
        bobot_df = pd.DataFrame(
            {
                "Kriteria": available_criteria,
                "Tipe": criteria_types,
                "Bobot Normal": normalized_weights,
            }
        )
        st.dataframe(bobot_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Belum ada kolom kriteria numerik yang terdeteksi.")

is_valid, message = validate_dataset(edited_data, available_criteria)
if is_valid:
    st.success(message)
else:
    st.error(message)

if sum(raw_weights) <= 0:
    st.error("Total bobot harus lebih dari 0.")

calculate = st.button(
    f"Hitung Ranking {selected_method}",
    type="primary",
    use_container_width=True,
    disabled=not is_valid or sum(raw_weights) <= 0,
)

if calculate:
    try:
        if selected_method == "TOPSIS":
            hasil, normalisasi = hitung_topsis(edited_data, available_criteria, normalized_weights, criteria_types)
        else:
            hasil, normalisasi = hitung_saw(edited_data, available_criteria, normalized_weights, criteria_types)

        best = hasil.iloc[0]

        st.divider()
        st.subheader(f"Hasil Rekomendasi Metode {selected_method}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Alternatif Terbaik", best["Alternatif"])
        c2.metric("Skor Tertinggi", f"{best['Skor']:.4f}")
        c3.metric("Jumlah Alternatif", len(hasil))
        c4.metric("Jumlah Kriteria", len(available_criteria))

        st.dataframe(hasil, use_container_width=True, hide_index=True)

        chart_col, weight_col = st.columns([1.3, 0.7], gap="large")
        with chart_col:
            st.plotly_chart(grafik_ranking(hasil, selected_method), use_container_width=True)
        with weight_col:
            st.plotly_chart(grafik_bobot(available_criteria, normalized_weights), use_container_width=True)

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
            available_criteria,
            criteria_types,
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
