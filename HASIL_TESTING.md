# Hasil Testing Edge Case

Testing dijalankan dengan perintah:

```bash
pytest
```

Hasil yang diharapkan:

```txt
3 passed
```

## Test Case 1 - Bobot tidak total 100%

Tujuan: memastikan sistem tetap dapat menghitung ranking meskipun total bobot input tidak berjumlah 100%.

Hasil: sistem berhasil melakukan normalisasi bobot dan menghasilkan ranking tanpa error.

Status: Berhasil.

## Test Case 2 - Semua nilai alternatif sama

Tujuan: memastikan sistem tidak error ketika semua laptop memiliki nilai kriteria yang sama.

Hasil: sistem tetap menghasilkan skor dan ranking tanpa nilai NaN/infinite.

Status: Berhasil.

## Test Case 3 - Dataset minimal 5 alternatif dan 4 kriteria

Tujuan: memastikan dataset memenuhi syarat UAS.

Hasil: dataset memiliki lima alternatif laptop dan empat kriteria, yaitu Harga, Performa, Baterai, dan Portabilitas.

Status: Berhasil.
