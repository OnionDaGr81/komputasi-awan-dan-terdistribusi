# Jurnal Proses — Tugas 2

## [25 September 2026]
- Opsi arsitektur yang dipertimbangkan: SOA atau Pub=Sub? Akhirnya kita sepakat menggunakan kombinasi keduanya
- Kenapa akhirnya pilih [SOA/Pub-Sub]: 
- Revisi diagram (versi 1 → versi 2, apa yang berubah dan kenapa): ...

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 25 September 2026 |  Gemini | Halo, tolong jelasin ide dari tugas ini dong! dan saya sama kelompok saya jobdesknya ngapain aja. | Kalian diminta merancang ulang arsitektur FoodGo menggunakan gaya Service-Oriented Architecture (SOA), Publish-Subscribe (Pub-Sub), atau kombinasi keduanya. Tujuannya agar modul Pesanan, Pembayaran, Kurir, dan Resto bisa berdiri sendiri, berkomunikasi melalui network/broker, dan tidak saling mengunci. | Pembagian tugas |
| 25 September 2026 | Gemini | Bantu saya brainstorming outline untuk soal nomor 4. Berdasarkan diagram SOA + Pub-Sub kelompok kami, poin-poin apa saja yang perlu dianalisis terkait penyelesaian masalah coupling dan trade-off arsitekturnya? | AI menyarankan kerangka analisis yang dibagi dua: (1) Penyelesaian coupling dilihat dari pemisahan deployment tiap service (SOA) dan antrean pesan di Message Broker (Pub-Sub) saat salah satu modul restart, serta (2) Trade-off dilihat dari kerumitan debugging alur asinkron, jeda konsistensi data, network latency, dan ketergantungan pada broker. | Mengembangkan poin-poin outline tersebut menjadi paragraf analisis lengkap dengan kalimat sendiri dan menyesuaikannya dengan nama komponen di diagram kelompok (seperti event OrderPaid, Service stock resto, dan Service Kurir/Notifikasi). |