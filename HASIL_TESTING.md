# Hasil Testing

Perintah yang dijalankan:

```bash
pytest
```

Hasil:

```txt
3 passed
```

Test yang tersedia:

1. `test_saw_default_dataset_ranking_valid` - memastikan perhitungan SAW pada dataset default menghasilkan ranking valid.
2. `test_topsis_equal_alternatives_no_nan_and_equal_rank` - edge case ketika semua alternatif memiliki nilai sama, skor tidak boleh NaN dan ranking harus sama.
3. `test_saw_cost_zero_raises_error` - edge case kriteria cost bernilai 0 harus menghasilkan error agar tidak terjadi pembagian tidak valid.
