# Jurnal Proses — Tugas 5

## Implementasi Bully
- **Kendala TODO 1 (Muhammad Chaesar Pratama):** Pemanggilan `start_election()` dari handler `on_message` awalnya menahan (blocking) thread socket connection karena jeda timeout 2 detik. Kendala ini diselesaikan dengan menjalankan `start_election()` di background thread terpisah (`daemon=True`) sehingga socket receiver tetap responsif menerima pesan lain.
- **Kendala TODO 2–3 (Didit Septa Putra):** Beberapa thread election berbagi satu flag `is_electing`. Thread baru menyalakan flag itu lagi, sehingga thread lama mengira `COORDINATOR` belum datang dan mengulang election. Akibatnya, di log versi awal Node 5 menyatakan diri leader sampai 8 kali. Diperbaiki dengan `threading.Event` (`coordinator_received`) yang di-reset setiap election dimulai, dan node yang sudah menjadi leader cukup mengirim ulang `COORDINATOR` tanpa election baru.
- **Kendala TODO 4 (Alif Rifqi Pratama):** `monitor_leader` sempat terdefinisi dua kali (stub kosong dan versi lengkap) di `node.py`. Stub lama sudah dihapus.
- **Kendala integrasi (Duarte Sebastian Napitupulu):**
  - `COORDINATOR` dari node ber-ID lebih rendah awalnya diterima begitu saja. Di log lama, Node 5 sempat mencatat "Leader terpilih: Node 2", dan di run lain malah mem-PING Node 1 sebagai leader. Diperbaiki dengan menolak `COORDINATOR` dari ID lebih rendah, lalu menjalankan election sendiri.
  - Node yang sudah menerima `COORDINATOR` dari node lebih tinggi tetap menyatakan diri leader setelah timeout. Diperbaiki dengan memeriksa `coordinator_received` sebelum `declare_leader()`.
  - Log hasil redirect `>` di PowerShell tersimpan dalam UTF-16 dan banyak baris menempel karena print dari banyak thread. Diperbaiki dengan fungsi `log()` (timestamp + lock), menjalankan `python -u ... | tee` dari Git Bash, dan tidak mencetak `PING` lagi agar log tidak membengkak.
## Skenario 1: Start normal
- **Leader yang terpilih:** Node 5 (kelima node sepakat paling lambat pukul 20:11:11.380).
- **Log/observasi:**
  - Node dinyalakan berjeda sekitar 2 detik, sehingga Node 1 sempat menyatakan diri leader (20:11:03.230) karena semua `ELECTION`-nya gagal ke node yang belum hidup.
  - `COORDINATOR` dari Node 1 ditolak oleh Node 2, 3, 4, dan 5. Node 5 lalu mengambil alih sebagai leader akhir.
  - Bukti: `bukti_skenario1`.
## Skenario 2: Leader dimatikan
- **Leader baru yang terpilih:** Node 4 (`SAYA LEADER` pukul 20:21:37.625).
- **Berapa lama waktu sampai leader baru terdeteksi:**
  - Kematian Node 5 pertama kali terdeteksi oleh Node 2 pukul 20:21:33.417.
  - ≈ 4,2 detik dari deteksi pertama sampai Node 4 menjadi leader.
  - ≈ 7,3 detik sampai semua node mencatat Node 4 (Node 3, pukul 20:21:40.679).
  - Ditambah 0–3 detik antara Ctrl+C dan deteksi (interval monitor).
- **Catatan:** Run skenario 2 pertama tidak valid. Yang mati saat itu Node 1, bukan Node 5, dan tidak ada log Node 4 menjadi leader. Skenario diulang setelah perbaikan kode.
- **Pesan setelah Node 5 mati:** `ELECTION` 6 terkirim + 4 gagal, `OK` 6, `COORDINATOR` 4 terkirim + 1 gagal.
- Bukti: `bukti/skenario2/`.


## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 12/10/2026 | Gemini | Tanya alur koordinasi Bully Algorithm, penanganan blocking thread pada on_message, dan kerangka analisis jam fisik vs logical clock | Ide pemisahan thread handler dan outline analisis clock drift, totally ordered multicast, serta vector clock | Diolah menjadi kode multithreaded di on_message dan analisis Bagian 2 di README dengan bahasa sendiri |
