# Jurnal Proses — Tugas 7

## Diskusi pemilihan model konsistensi
- Argumen yang dipertimbangkan:
  - **Eventual Consistency saja sudah cukup**, karena delay replikasi hanya sekitar 2 detik dan
    data akan sama pada akhirnya. **Ditolak:** untuk saldo, urutan operasi menentukan angka akhir.
    Dua pembayaran hampir bersamaan di Jakarta dan Bandung bisa sama-sama lolos berdasarkan
    saldo lama (*double spending*), dan transaksi sah bisa ditolak seperti pada studi kasus
    (lihat README bagian 1.3).
  - **Sequential Consistency untuk seluruh data FoodGo.** **Ditolak:** koordinasi antar server
    Jakarta–Bandung menambah latensi dan menurunkan ketersediaan saat jaringan bermasalah,
    sementara data seperti rating atau popularitas menu tidak butuh jaminan sekuat itu
    (lihat README bagian 1.5).
  - **Perbandingan dengan "jumlah like" di media sosial.** Selisih sementara pada *like* tidak
    merugikan siapa pun, sedangkan selisih pada saldo bisa berarti kerugian uang dan hilangnya
    kepercayaan pelanggan. Ini memperkuat bahwa saldo butuh jaminan lebih kuat
    (lihat README bagian 1.4).

- Kesimpulan akhir & alasan: ...

## Simulasi (jika dikerjakan)
- Hasil skenario naif vs Read-Your-Writes: ...

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |
