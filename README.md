# Aplikasi Sistem Pendukung Keputusan - Streamlit + SAW/TOPSIS

Aplikasi ini dibuat untuk tugas UAS mata kuliah Aplikasi Pendukung Keputusan. Aplikasi menentukan alternatif terbaik berdasarkan beberapa kriteria menggunakan metode **SAW** atau **TOPSIS**.

## Fitur Utama

- Input data alternatif melalui CSV.
- Minimal 5 alternatif dan minimal 4 kriteria, sesuai spesifikasi UAS.
- Kriteria otomatis dibaca dari kolom numerik CSV selain `Alternatif`.
- Edit data langsung dari tabel aplikasi.
- Pengaturan bobot kriteria dengan slider.
- Pengaturan tipe kriteria `benefit` atau `cost`.
- Normalisasi otomatis bobot kriteria.
- Pilihan metode perhitungan SAW dan TOPSIS.
- Perhitungan skor dan ranking alternatif.
- Visualisasi grafik ranking dan komposisi bobot.
- Fitur what-if: ubah bobot, ubah tipe kriteria, ubah data alternatif, lalu hitung ulang.
- Download hasil ranking dalam CSV.
- Histori hasil perhitungan ke Supabase bersifat opsional. Jika Supabase belum terkoneksi, aplikasi tetap bisa dipakai lokal.

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
├─ assets/
│  └─ grafik_saw.png
├─ data/
│  └─ contoh_data.csv
├─ laporan/
│  └─ Laporan_UAS_DSS.pdf
├─ modules/
│  ├─ saw.py
│  ├─ topsis.py
│  ├─ visualizer.py
│  └─ supabase_handler.py
├─ tests/
│  └─ test_dss_methods.py
└─ supabase/
   └─ schema.sql
```

## Cara Run Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aplikasi bisa langsung jalan tanpa Supabase. Jika variabel Supabase belum diisi, bagian histori hanya menampilkan info bahwa Supabase belum terkoneksi.

## Format Dataset CSV

Dataset minimal berisi kolom `Alternatif` dan minimal 4 kriteria numerik.

Contoh:

```csv
Alternatif,Harga,Kualitas,Ketepatan,Kapasitas
Supplier A,5000000,80,90,75
Supplier B,4500000,75,85,80
Supplier C,6000000,90,95,85
Supplier D,3500000,70,80,70
Supplier E,5500000,85,88,90
```

Keterangan tipe kriteria:

- `cost`: semakin kecil semakin baik, contoh Harga/Biaya.
- `benefit`: semakin besar semakin baik, contoh Kualitas/Ketepatan/Kapasitas.

## Cara Testing

Jalankan:

```bash
pytest
```

Test yang disediakan:

1. Perhitungan SAW pada dataset default.
2. Edge case TOPSIS ketika semua alternatif bernilai sama.
3. Edge case SAW ketika kriteria cost memiliki nilai 0.

## Environment Variable Supabase

Buat file `.env` untuk lokal atau isi Railway Variables saat deploy:

```env
SUPABASE_URL=https://PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Tidak Perlu Setting Railway dan Supabase dari Awal

Jika kamu sudah pernah membuat project Railway dan Supabase sebelumnya, tidak perlu membuat ulang.

Yang perlu dilakukan hanya:

1. Replace/update file project ini di folder/repository lama.
2. Commit dan push ke GitHub yang sudah tersambung ke Railway.
3. Railway akan redeploy otomatis.
4. Environment variable lama tetap dipakai:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
5. Tabel Supabase `dss_history` tetap bisa dipakai karena struktur data kriteria, bobot, dan hasil disimpan dalam format JSON.

File `supabase/schema.sql` hanya perlu dijalankan ulang kalau tabel `dss_history` belum pernah dibuat.

## Deploy Railway

Railway menjalankan command dari `Procfile`:

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Pastikan `requirements.txt` ikut terupload agar Railway bisa install library Python.
