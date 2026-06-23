# Aplikasi Sistem Pendukung Keputusan - Streamlit + Supabase + Railway

Aplikasi ini dibuat untuk tugas UAS mata kuliah Aplikasi Pendukung Keputusan.
Fungsi utama aplikasi adalah menentukan alternatif terbaik berdasarkan bobot kriteria. Aplikasi menyediakan pilihan metode SAW dan TOPSIS.

## Fitur

- Input data alternatif melalui CSV.
- Edit data langsung dari tabel aplikasi.
- Pengaturan bobot kriteria dengan slider.
- Normalisasi otomatis bobot kriteria.
- Pilihan metode perhitungan SAW dan TOPSIS.
- Perhitungan ranking alternatif otomatis.
- Visualisasi grafik ranking dan komposisi bobot.
- Download hasil ranking dalam CSV.
- Simpan histori hasil perhitungan ke Supabase.
- Siap deploy ke Railway.

## Struktur Folder

```txt
dss_railway_supabase/
├─ app.py
├─ Procfile
├─ requirements.txt
├─ runtime.txt
├─ .env.example
├─ .streamlit/
│  └─ config.toml
├─ data/
│  └─ contoh_data.csv
├─ modules/
│  ├─ saw.py
│  ├─ topsis.py
│  ├─ visualizer.py
│  └─ supabase_handler.py
└─ supabase/
   └─ schema.sql
```

## Cara Run Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Environment Variable

Buat file `.env` untuk lokal atau isi Railway Variables saat deploy:

```env
SUPABASE_URL=https://PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Setup Supabase

1. Buka Supabase.
2. Buat project baru.
3. Buka SQL Editor.
4. Copy isi file `supabase/schema.sql`.
5. Klik Run.
6. Ambil Project URL dan anon key dari Project Settings > API.
7. Masukkan value tersebut ke Railway Variables.

## Deploy Railway

Railway akan menjalankan command dari `Procfile`:

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Pastikan `requirements.txt` ikut terupload agar Railway bisa install library Python.
