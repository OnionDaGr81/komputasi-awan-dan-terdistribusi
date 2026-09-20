# Jurnal Proses — Tugas 1

> Isi jurnal ini selama proses diskusi berlangsung, bukan ditulis ulang rapi di akhir. Tulis dengan gaya bebas — poin diskusi, kebuntuan, perubahan pikiran.

## [18 September diskusi 1]
- Peserta: [ Bastian, Chaesar, Didit, ALif Rifqi]
- Poin diskusi: Mengusulkan solusi dan mendiskusikan trade off dari solusi yang di usulkan
- Perbedaan pendapat (jika ada): -

## [Tanggal diskusi 2]
- ...

## Review Silang
- Sebastian mengomentari analisis Alif: Bagaimana solusi horizontal scaling saja mungkin tidak cukup, dan harus di barengi dengan load balancer agar lebih efektif.

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 18 September | Gemini | "Halo! Tolong jelaskan tugas ini dong, saya masih kurang ngerti huhu." | "Kumpulkan kelompokmu, baca ulang skenario FoodGo bersama-sama, lalu langsung booking siapa mau bahas masalah jaringan (network), siapa mau bahas masalah timeout, dan siapa mau bahas masalah server monolitik." | Identifikasi 4 pitfall untuk tiap anggota kelompok |
| 18 September | Claude | "Bantu arahkan bagianku, *Latency is Zero*, dengan fokus pada kutipan 'tidak ada timeout sama sekali' dan 'menunggu tanpa batas waktu' saat modul pesanan memanggil modul pembayaran." | AI memberi pertanyaan pemandu untuk tiap bagian template. **(1) Kenapa asumsi keliru:** komunikasi antar-service selalu punya delay fisik (network hop, serialisasi, pemrosesan di penerima). Beda "lambat" dan "macet selamanya" bila tanpa timeout, dan latency tidak konstan. **(2) Dampak ke FoodGo:** telusuri rantai sebab-akibat, yaitu thread/koneksi yang menunggu tanpa batas menahan resource (thread pool, koneksi DB, memori), lalu pada 1000 request bersamaan di jam makan siang memicu *thread starvation* / *resource exhaustion* hingga server crash. **(3) Solusi awal:** timeout eksplisit di setiap pemanggilan antar-service, *circuit breaker* agar request gagal cepat, dan panggilan async/non-blocking. **(4) Trade-off:** timeout terlalu pendek menyebabkan false positive, timeout terlalu panjang sama saja tanpa timeout, dan circuit breaker menambah kompleksitas serta butuh tuning. | Menggunakan pertanyaan pemandu sebagai kerangka penulisan bagian *Latency is Zero*, lalu mengembangkannya dengan riset sendiri terkait thread starvation dan circuit breaker. |
(20 September 2026) Masalah 3 (Kategori Desain): Arsitektur Monolitik
Fokus untuk anggota 3: Membedah kutipan tentang semua modul (pesanan, pembayaran, notifikasi) yang disatukan dalam "satu proses monolitik yang sama".
buatkan saya bukti dari skenario nya, kenapa ini keliru, dampak ke food go, solusi desain awal, dan juga trade off nya