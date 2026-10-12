# Jurnal Proses — Tugas 5

## Implementasi Bully
- Kendala saat mengisi TODO 1 (Muhammad Chaesar Pratama): Pemanggilan start_election() dari handler on_message awalnya menahan (blocking) thread socket connection karena jeda timeout 2 detik. Kendala ini diselesaikan dengan menjalankan start_election() di background thread terpisah (daemon=True) sehingga socket receiver tetap responsif menerima pesan lain.
- Kendala saat mengisi TODO 2-4: ...

## Skenario 1: Start normal
- Leader yang terpilih: ...
- Log/observasi: ...

## Skenario 2: Leader dimatikan
- Leader baru yang terpilih: ...
- Berapa lama waktu sampai leader baru terdeteksi: ...

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 12/10/2026 | Gemini | Tanya alur koordinasi Bully Algorithm, penanganan blocking thread pada on_message, dan kerangka analisis jam fisik vs logical clock | Ide pemisahan thread handler dan outline analisis clock drift, totally ordered multicast, serta vector clock | Diolah menjadi kode multithreaded di on_message dan analisis Bagian 2 di README dengan bahasa sendiri |
