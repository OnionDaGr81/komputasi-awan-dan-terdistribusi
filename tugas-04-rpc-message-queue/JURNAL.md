# Jurnal Proses — Tugas 4

## Jalur yang dipilih
- [RPC / MQ / keduanya], alasan: Kelompok kami memilih jalur MQ,Karena:
1. Modul Pembayaran tidak perlu menunggu

Setelah pembayaran berhasil, modul Pembayaran dapat mengirim pesan ke Message Queue dan langsung melanjutkan proses lainnya. Modul Pembayaran tidak perlu menunggu modul Kurir selesai memproses notifikasi.

2. Pesan lebih terjamin tidak hilang

Jika dikonfigurasi dengan durable queue, pesan persisten, dan pengakuan penerimaan (acknowledgment), pesan dapat tetap tersimpan ketika modul Kurir sedang down dan diproses setelah modul tersebut kembali aktif.

3. Sistem tetap responsif saat beban tinggi

Jika banyak pesanan masuk secara bersamaan, pesan dapat mengantre dan diproses oleh modul penerima secara bertahap. Modul Pembayaran tidak harus menunggu semua notifikasi selesai dikirim.

## Kendala teknis
- Kendala yang muncul pada saat kami ingin menggunakan Docker Dekstop, pada saat melakukan install image Rabbitmq terjadi gangguan sehingga kami tidak dapat menjalankan Docker Dekstop pada Vscode/ tidak dapat saling berkomunikasi.

## Uji "pesan tidak hilang" (khusus Jalur B)
- Langkah uji: matikan consumer → jalankan publisher → nyalakan consumer
- Hasil yang diamati: ... 

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). "Apa fungsi masing-masing antar jalur RPC dan MQ pada sebuah sistem order food."

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |
