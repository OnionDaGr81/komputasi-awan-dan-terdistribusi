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
<<<<<<< HEAD
- Kendala yang muncul pada saat kami ingin menggunakan Docker Dekstop, pada saat melakukan install image Rabbitmq terjadi gangguan sehingga kami tidak dapat menjalankan Docker Dekstop pada Vscode/ tidak dapat saling berkomunikasi.

## Uji "pesan tidak hilang" (khusus Jalur B)
- Langkah uji: matikan consumer → jalankan publisher → nyalakan consumer
- Hasil yang diamati: ... 
=======
- Error saat setup rabbitmq dan menjalankan consumer.py

## Uji "pesan tidak hilang" (khusus Jalur B)
- Langkah uji: matikan consumer → jalankan publisher → nyalakan consumer
- Hasil yang diamati: 

jalankan `publisher.py` dua kali saat `consumer.py` belum dinyalakan.
Setiap kali jalan, publisher mengirim 3 event pembayaran (user1 = 20000, user2 = 40000, user3 = 60000), jadi total ada 6 pesan. Di dashboard RabbitMQ, queue `pembayaran_berhasil` menunjukkan Ready = 6, Unacked = 0, danConsumers = 0. Artinya pesan sudah masuk antrean, tetapi belum ada consumer yang mengambilnya ![no3-01-publisher-consumer-mati.png](image.png) ![no3-02-dashboard-ready6-consumer0.png](image-1.png)

Setelah itu `consumer.py` dinyalakan. Consumer langsung mencetak 6 baris"Kurir menerima notifikasi pembayaran" dengan urutan user1, user2, user3, user1, user2, user3, sama persis dengan urutan saat dikirim ![no3-03-consumer-memproses-6-pesan.png](image-2.png)

Dashboard kemudian menunjukkan Ready = 0 dan Consumers = 1 ![no3-04-dashboard-ready0-consumer1.png](image-3.png)
Jadi tidak ada pesan yang hilang, walaupun consumer sedang mati ketika publisher mengirim

>>>>>>> ae303005b7aadcfe646089f4c1150f7325ca67be

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). "Apa fungsi masing-masing antar jalur RPC dan MQ pada sebuah sistem order food."

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 10/10/2026 | Gemini | "Jelaskan konsep message persistence, peran durable queue pada RabbitMQ, dan alur implementasi Publisher di Python" | AI menjelaskan perbedaan antrean durable dengan persistent message (`delivery_mode=2`), serta fungsi asynchronous decoupling pada message broker. | Mengimplementasikan kode `publisher.py` secara mandiri, menguji pengiriman 3 pesan event ke RabbitMQ lokal di laptop, dan memvalidasi hasilnya lewat dashboard. |
