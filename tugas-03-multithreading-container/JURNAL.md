# Jurnal Proses - Tugas 3

## Percobaan tanpa Lock
- Hasil `processed_count` yang didapat: **59 dari 100** (sering berubah-ubah antara 50–96 pada beberapa kali percobaan eksekusi, memicu pesan *"RACE CONDITION TERDETEKSI"*).
- Kenapa bisa meleset (jelaskan mekanisme race condition dengan kata sendiri):
  Di Python, ekspresi penambahan nilai `processed_count += 1` tampak seperti satu baris instruksi sederhana, namun di tingkat *bytecode/CPU execution*, operasi ini terdiri dari tiga langkah terpisah (*non-atomic operations*):
  1. **LOAD_GLOBAL (Read):** Mengambil nilai `processed_count` saat ini dari memori.
  2. **BINARY_OP (Modify):** Menambahkan nilai tersebut dengan 1.
  3. **STORE_GLOBAL (Write):** Menyimpan kembali nilai hasil penambahan ke alamat memori variabel global.

  Ketika 10 worker thread berjalan secara simultan (konkuren), terjadi *interleaving* (tumpang tindih waktu eksekusi). Misalnya, Thread A dan Thread B sama-sama membaca `processed_count = 10`. Keduanya lalu menghitung `10 + 1 = 11`. Kemudian Thread A menulis nilai 11 ke memori, disusul Thread B yang juga menulis nilai 11 ke memori. Seharusnya dua pesanan menghasilkan nilai 12, tetapi karena saling menimpa (*lost update*), satu pesanan hilang dari catatan counter.

## Percobaan dengan Lock
- Hasil `processed_count` setelah perbaikan: **100 dari 100 (selalu tepat dan konsisten pada setiap pengujian)**.
- Penjelasan perbaikan:
  Kami mengimplementasikan mekanisme *Mutual Exclusion (Mutex)* menggunakan objek `lock = threading.Lock()`. Bagian penambahan counter dilindungi menggunakan context manager `with lock:`. Dengan mekanisme ini, hanya ada satu thread yang diperbolehkan memasuki *critical section* untuk membaca, mengubah, dan menyimpan nilai `processed_count`. Thread lain yang ingin melakukan hal serupa diwajibkan mengantre (*blocked*) hingga lock dilepaskan. Hal ini menjamin sifat *atomicity* sehingga tidak ada data pembaruan yang tertimpa (*lost update*).

## Kendala Docker
- Error yang ditemui saat `docker build`/`docker run` dan cara memperbaikinya: "Virtualization support not detected" dan cara memperbaikinya adalah dengan jalankan "wsl --install" di terminal windows powershell

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline - bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 04/10/2026 | Gemini | "Jelaskan konsep race condition pada operasi counter multithreading di Python dan pembagian tugas kelompok 4 orang" | AI menjelaskan konsep non-atomic read-modify-write, cara kerja mutex lock di Python, dan menyarankan struktur pembagian kerja kelompok. | Kelompok kami membagi tugas berdasarkan 4 peran (Alif mengerjakan batching worker, Bastian menangani lock, Didit mengurus Docker, Chaesar menyusun jurnal dan analisis). Kode ditulis dan diuji coba sendiri di laptop. |
