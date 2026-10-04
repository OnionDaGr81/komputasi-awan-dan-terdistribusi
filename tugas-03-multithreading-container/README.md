# Tugas 3 (Pekan 3) — Efisiensi Proses & Kontainer

**Materi terkait:** Threading, Virtualization, Containers.

## Pembagian Tugas Kelompok

| Anggota | NIM | Bagian yang Dikerjakan |
|---|---|---|
| **Alif** | (103072400133) | Mengerjakan **TODO 3** (pembagian 100 pesanan ke 10 worker thread dan join thread). |
| **Didit** | (103072400071) | Mengerjakan **TODO 1 & TODO 2** (simulasi race condition tanpa lock dan perbaikan dengan `threading.Lock`). |
| **Bastian** | (103072400152) | Menulis `Dockerfile`, build image `python:3.13.7-slim`, dan uji coba Docker container. |
| **Chaesar** | (103072400119) | Menulis analisis pada `README.md`, melengkapi `JURNAL.md`, dan review akhir submission. |

## Studi Kasus

Server FoodGo boros sumber daya karena setiap permintaan pesanan masuk diproses sebagai **proses baru yang berat** (mis. `fork()` proses OS penuh per request). Saat 100 pesanan masuk bersamaan, server kehabisan memori karena tiap proses membawa overhead-nya sendiri.

## Analisis: Kenapa Threading, Bukan Proses Berat? [Chaesar]

1. **Kenapa proses OS penuh (`fork()`) bikin server boros?**
   * Di tingkat sistem operasi, satu proses membawa alokasi memori tersendiri secara utuh (heap, stack, descriptor table, dan PCB di kernel).
   * Saat 100 pesanan masuk bersamaan dan dibuat 100 proses baru, RAM server langsung habis (*Out of Memory*).
   * CPU juga terbebani karena harus terus melakukan pergantian proses yang berat (*context switching* antar-proses).

2. **Kenapa multithreading jauh lebih efisien?**
   * Semua thread berjalan di dalam **satu proses yang sama** dan memakai ruang memori bersama (*shared memory space*).
   * Masing-masing thread hanya butuh memori stack yang sangat kecil, jadi 100 pesanan bisa diproses secara simultan tanpa membuat RAM jebol.
   * Sangat cocok untuk karakteristik pemrosesan pesanan yang banyak waktu tunggu I/O (seperti validasi data atau menunggu database).

3. **Mekanisme Race Condition dan Solusi Lock:**
   * Karena memakai memori bersama, variabel counter `processed_count` jadi rebutan.
   * **Tanpa Lock:** Dari 100 pesanan, hasil yang tercatat **hanya 59 pesanan** (41 pesanan hilang). Ini karena penambahan counter butuh 3 langkah mesin (baca, tambah, simpan). Saat thread berjalan bersamaan, ada thread yang membaca nilai lama yang sama lalu saling menimpa (*lost update*).
   * **Dengan Lock:** Kami memasang `threading.Lock()` dengan `with lock:`. Sekarang tiap thread harus mengantre satu per satu saat menambah angka, sehingga hasilnya selalu konsisten **tepat 100 pesanan**.

4. **Peran Docker Container:**
   * Memaketkan program ke base image resmi yang ringan (**`python:3.13.7-slim`**) agar ukuran container kecil.
   * Memastikan aplikasi berjalan stabil dan menghasilkan output yang sama persis di komputer mana pun tanpa terpengaruh versi Python lokal.

## Tugas Kelompok

1. Implementasikan **simulasi pesanan masuk** di Python (`src/order_simulator.py`) yang memproses banyak pesanan **secara konkuren memakai multithreading** (bukan multiprocessing, bukan sekuensial biasa).
2. Program harus mensimulasikan **race condition yang sengaja dibuat lalu diperbaiki** — buktikan pemahaman kalian tentang `Lock`/sinkronisasi dengan cara:
   - Jalankan dulu versi TANPA lock, tunjukkan hasil counter yang salah (screenshot/log).
   - Perbaiki dengan `threading.Lock()`, tunjukkan hasil counter yang benar.
   - Tulis perbandingan ini di `JURNAL.md`.
3. Paketkan program ke dalam **Docker container** (`Dockerfile` disediakan skeleton-nya, lengkapi bagian yang kosong).
4. Jalankan container di laptop, buktikan program tetap berjalan benar di dalam container (screenshot/video di `bukti/`).

## Skeleton yang Disediakan

- `src/order_simulator.py` — kerangka program dengan `# TODO` di bagian logika inti (worker function, penggunaan lock, agregasi hasil). **Kalian wajib mengisi bagian TODO sendiri** — ini bagian penilaian utama.
- `requirements.txt` — kosong/minimal (program ini sengaja hanya pakai standard library Python, tidak perlu dependency eksternal).
- `Dockerfile` — kerangka dengan beberapa baris `# TODO`, lengkapi agar image bisa di-build dan dijalankan.

## Cara Menjalankan (Setelah Skeleton Dilengkapi)

Tanpa Docker (langsung di laptop, untuk debugging cepat):
```bash
cd tugas-03-multithreading-container
python3 src/order_simulator.py
```

Dengan Docker (wajib untuk submission akhir):
```bash
cd tugas-03-multithreading-container
docker build -t foodgo-order-sim .
docker run --rm foodgo-order-sim
```

## Struktur Submission

```
tugas-03-multithreading-container/
├── README.md          # Analisis: race condition, perbaikan, kenapa threading (bukan multiprocessing/proses OS)
├── JURNAL.md           # Log sebelum/sesudah lock, error yang ditemui saat build Docker
├── Dockerfile
├── requirements.txt
├── src/
│   └── order_simulator.py
└── bukti/              # Screenshot/video: hasil counter salah (tanpa lock), hasil benar (dengan lock), container jalan
    ├── 01_race_condition.png              # Output terminal tanpa lock (hasil 59)
    ├── Race_condition_dengan_code.png     # Kode tanpa lock dan hasil terminalnya
    ├── 02_lock_fixed.png                  # Output terminal setelah diberi lock (hasil 100)
    ├── lock_fixed_dengan_code.png         # Kode dengan lock dan hasil terminalnya
    └── Perbandingan_docker_vs_lokal.png   # Bukti perbandingan container Docker vs lokal
```

## Rubrik Penilaian (Tugas 3)

| Komponen | Bobot | Kriteria |
|---|---|---|
| Implementasi multithreading benar | 30% | Worker benar-benar konkuren (bukan `time.sleep` yang menyamarkan sekuensial), pakai `threading` |
| Bukti race condition & perbaikan lock | 25% | Ada bukti nyata (log/screenshot) sebelum & sesudah, bukan cuma klaim di teks |
| Dockerfile & eksekusi container | 20% | Image ter-build, container jalan dan hasilkan output yang sama seperti tanpa Docker |
| Analisis (kenapa threading, bukan proses berat) | 15% | Mengaitkan balik ke masalah "server boros resource" di studi kasus |
| Proses & kontribusi kelompok | 10% | `JURNAL.md`, commit history |

## Batasan Penggunaan AI (Level 2)

Kebijakan **Level 2 (AI Assisted Idea Generation & Structuring)** berlaku — lihat [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Boleh bertanya ke AI soal opsi umum menangani race condition (mis. "apa saja cara sinkronisasi thread di Python"); **tidak boleh** meminta AI menuliskan isi bagian `# TODO` di `order_simulator.py`/`Dockerfile`. Catat pemakaian AI di "Log Penggunaan AI" pada `JURNAL.md`.

- Bagian `# TODO` di `order_simulator.py` dan `Dockerfile` sengaja dikosongkan — solusi yang identik persis antar kelompok (termasuk nama variabel, komentar) akan diperiksa lebih lanjut.
- `JURNAL.md` wajib menunjukkan bukti nyata percobaan **sebelum** (race condition muncul) dan **sesudah** (`Lock()` dipasang) — bukan cuma klaim tanpa data pembanding.
