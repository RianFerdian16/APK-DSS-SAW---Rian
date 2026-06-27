# UAS APK Rian - DSS Pemilihan Laptop Terbaik

Aplikasi ini dibuat untuk tugas UAS mata kuliah Aplikasi Pendukung Keputusan. Aplikasi digunakan untuk membantu memilih laptop terbaik untuk mahasiswa berdasarkan beberapa kriteria menggunakan metode **SAW** atau **TOPSIS**.

## Studi Kasus

Studi kasus yang digunakan adalah **pemilihan laptop terbaik untuk mahasiswa**. Pemilihan dilakukan berdasarkan kebutuhan kuliah dan penggunaan harian.

Alternatif laptop:

1. Asus Vivobook 14
2. Lenovo IdeaPad Slim 3
3. Acer Aspire 5
4. HP Pavilion 14
5. MSI Modern 14

Kriteria:

| Kriteria | Tipe | Keterangan |
|---|---|---|
| Harga | Cost | Semakin murah semakin baik |
| Performa | Benefit | Semakin tinggi performa semakin baik |
| Baterai | Benefit | Semakin tahan lama semakin baik |
| Portabilitas | Benefit | Semakin mudah dibawa semakin baik |

## Fitur Utama

- Input data alternatif laptop melalui CSV.
- Minimal 5 alternatif dan minimal 4 kriteria sesuai spesifikasi UAS.
- Kriteria otomatis dibaca dari kolom numerik CSV selain `Alternatif`.
- Edit data langsung dari tabel aplikasi.
- Pengaturan bobot kriteria dengan slider.
- Pengaturan tipe kriteria `benefit` atau `cost` melalui dropdown.
- Normalisasi otomatis bobot kriteria.
- Pilihan metode perhitungan SAW dan TOPSIS.
- Perhitungan skor dan ranking laptop.
- Visualisasi grafik ranking dan komposisi bobot.
- Fitur what-if: ubah bobot, tipe kriteria, atau data alternatif, lalu hitung ulang.
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

Jika command `streamlit` tidak dikenali, gunakan:

```bash
python -m streamlit run app.py
```

## Format Dataset CSV

Dataset minimal berisi kolom `Alternatif` dan minimal 4 kriteria numerik.

Contoh dataset laptop:

```csv
Alternatif,Harga,Performa,Baterai,Portabilitas
Asus Vivobook 14,7500000,82,78,85
Lenovo IdeaPad Slim 3,7200000,80,82,88
Acer Aspire 5,8000000,86,76,80
HP Pavilion 14,8500000,88,80,83
MSI Modern 14,9000000,90,84,78
```

Keterangan tipe kriteria:

- `cost`: semakin kecil nilainya semakin baik, contoh Harga.
- `benefit`: semakin besar nilainya semakin baik, contoh Performa, Baterai, dan Portabilitas.

## Cara Penggunaan Aplikasi

1. Jalankan aplikasi dengan `streamlit run app.py`.
2. Gunakan dataset default atau upload CSV baru.
3. Cek dan edit data alternatif jika diperlukan.
4. Atur bobot setiap kriteria menggunakan slider.
5. Atur tipe kriteria: Harga = `cost`, Performa/Baterai/Portabilitas = `benefit`.
6. Pilih metode SAW atau TOPSIS.
7. Klik tombol hitung untuk melihat skor dan ranking.
8. Lihat hasil ranking dalam bentuk tabel dan grafik.
9. Download hasil ranking jika diperlukan.

## Cara Testing

Jalankan:

```bash
pytest
```

Test yang disediakan:

1. Edge case bobot tidak total 100%.
2. Edge case semua nilai alternatif sama.
3. Validasi dataset minimal 5 alternatif dan 4 kriteria.

Contoh hasil:

```txt
3 passed
```

## Environment Variable Supabase

Buat file `.env` untuk lokal atau isi Railway Variables saat deploy:

```env
SUPABASE_URL=https://PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

Supabase bersifat opsional. Jika belum terkoneksi, aplikasi tetap bisa digunakan untuk input data, perhitungan SAW/TOPSIS, ranking, grafik, dan download hasil.

## Tidak Perlu Setting Railway dan Supabase dari Awal

Jika project Railway dan Supabase sudah pernah dibuat sebelumnya, tidak perlu membuat ulang.

Yang perlu dilakukan hanya:

1. Replace/update file project ini di folder atau repository lama.
2. Commit dan push ke GitHub yang sudah tersambung ke Railway.
3. Railway akan redeploy otomatis.
4. Environment variable lama tetap dipakai:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
5. Tabel Supabase `dss_history` tetap bisa dipakai karena struktur data kriteria, bobot, dan hasil disimpan dalam format JSON.

File `supabase/schema.sql` hanya perlu dijalankan ulang jika tabel `dss_history` belum pernah dibuat.

## Deploy Railway

Railway menjalankan command dari `Procfile`:

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Pastikan `requirements.txt` ikut terupload agar Railway dapat menginstal semua library Python yang dibutuhkan.

## Catatan Nama Railway

Nama deployment di Railway mengikuti pesan commit terakhir dari GitHub. Gunakan commit message berikut agar deployment tampil sebagai `uas apk rian`:

```bash
git add .
git commit -m "uas apk rian"
git push
```

Untuk mengganti nama project/service Railway secara permanen, ubah dari dashboard Railway pada bagian Settings.
