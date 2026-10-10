# Jurnal Proses — Tugas 4

## Jalur yang dipilih
- [RPC / MQ / keduanya], alasan: ...

## Kendala teknis
- Error saat setup rabbitmq dan menjalankan consumer.py

## Uji "pesan tidak hilang" (khusus Jalur B)
- Langkah uji: matikan consumer → jalankan publisher → nyalakan consumer
- Hasil yang diamati: ...

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 10/10/2026 | Gemini | "Jelaskan konsep message persistence, peran durable queue pada RabbitMQ, dan alur implementasi Publisher di Python" | AI menjelaskan perbedaan antrean durable dengan persistent message (`delivery_mode=2`), serta fungsi asynchronous decoupling pada message broker. | Mengimplementasikan kode `publisher.py` secara mandiri, menguji pengiriman 3 pesan event ke RabbitMQ lokal di laptop, dan memvalidasi hasilnya lewat dashboard. |
