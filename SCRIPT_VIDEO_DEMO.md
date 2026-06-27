# Script Video Demo 3-5 Menit

Gunakan file ini sebagai panduan rekaman layar untuk deliverable UAS.

## 0:00 - 0:30 Pembukaan

Perkenalkan aplikasi:

> Aplikasi ini adalah Sistem Pendukung Keputusan untuk memilih supplier terbaik menggunakan metode SAW dan TOPSIS.

Sebutkan domain masalah:

> Alternatifnya adalah 5 supplier. Kriterianya adalah Harga, Kualitas, Ketepatan, dan Kapasitas.

## 0:30 - 1:15 Tunjukkan Dataset dan Input

Tunjukkan tabel data alternatif di aplikasi.

Jelaskan:

- Harga bertipe cost karena semakin murah semakin baik.
- Kualitas, Ketepatan, dan Kapasitas bertipe benefit karena semakin tinggi semakin baik.

## 1:15 - 2:00 Tunjukkan Bobot dan What-if

Ubah slider bobot, misalnya:

- Harga dari 30 ke 40.
- Kapasitas dari 15 ke 10.

Jelaskan:

> Ini adalah fitur what-if. Ketika bobot diubah, hasil ranking bisa dihitung ulang tanpa mengubah kode program.

## 2:00 - 3:00 Hitung Ranking SAW

Pilih metode SAW, klik tombol Hitung Ranking SAW.

Tunjukkan:

- Alternatif terbaik.
- Skor tertinggi.
- Tabel ranking.
- Grafik ranking.
- Grafik komposisi bobot.
- Matriks normalisasi.

## 3:00 - 4:00 Hitung Ranking TOPSIS

Pilih metode TOPSIS, klik Hitung Ranking TOPSIS.

Tunjukkan:

- Tabel ranking TOPSIS.
- Jarak ideal positif dan negatif.
- Skor preferensi.

## 4:00 - 4:30 Testing dan Penutup

Tunjukkan folder `tests` atau jalankan `pytest`.

Tutup dengan:

> Kesimpulannya, aplikasi sudah memenuhi fitur DSS: input data, normalisasi, perhitungan skor, ranking, visualisasi, what-if bobot, dan testing edge case.
