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

Output yang diharapkan:

```
Total pesanan diproses: 100 (seharusnya 100)
SEMUA PESANAN BERHASIL DIPROSES SECARA KONSISTEN (LOCK BEKERJA SEMPURNA)!
```

## Cara Kerja Program

1. `main()` membuat daftar 100 `order_id`, lalu membaginya rata menjadi 10 bagian (10 pesanan per thread).
2. Setiap bagian diberikan ke satu thread pekerja (`Worker-1` sampai `Worker-10`) yang langsung dijalankan dengan `t.start()`.
3. Tiap thread memanggil `process_order()` untuk setiap pesanannya. Di dalamnya ada `time.sleep` acak 1 sampai 10 ms sebagai simulasi kerja nyata (validasi, hitung harga), lalu counter bersama `processed_count` ditambah 1.
4. `main()` menunggu semua thread selesai dengan `t.join()`, lalu membandingkan `processed_count` dengan jumlah pesanan.

Thread benar-benar berjalan bersamaan: semua thread di-`start()` lebih dulu, baru kemudian di-`join()`. Saat satu thread sedang menunggu (sleep), thread lain tetap bekerja. Lock hanya membungkus bagian increment counter, bukan bagian kerja pesanannya, sehingga pemrosesan pesanan tidak berubah menjadi antrean satu per satu.

## Analisis Race Condition

**Apa yang terjadi.** Semua thread memakai satu variabel yang sama, yaitu `processed_count`. Menambah nilainya terdiri dari tiga langkah: baca nilai lama, tambah 1, tulis kembali. Tanpa proteksi, dua thread bisa membaca nilai lama yang sama sebelum salah satunya sempat menulis. Keduanya lalu menulis hasil yang sama, dan satu penambahan hilang.

**Hasil percobaan.** Tanpa lock, counter hanya mencapai **59 dari 100**, artinya 41 pesanan tidak terhitung. Di sistem nyata, ini setara dengan pesanan pelanggan yang sudah diproses tetapi tidak tercatat, atau stok dan saldo yang angkanya salah.

![Race condition](bukti/Race_condition_dengan_code.png)

**Perbaikan.** Bagian baca-tulis counter dibungkus dengan `with lock:`. Lock menjamin hanya satu thread yang boleh berada di bagian itu pada satu waktu, thread lain menunggu giliran. Hasilnya counter selalu **100 dari 100**.

![Lock fixed](bukti/lock_fixed_dengan_code.png)

| | Tanpa Lock | Dengan Lock |
|---|---|---|
| Hasil counter | 59 | 100 |
| Pesanan tidak terhitung | 41 | 0 |
| Konsisten? | Tidak | Ya |

Detail percobaan dan penjelasan langkah demi langkah ada di [JURNAL.md](JURNAL.md).

## Kenapa Threading, Bukan Proses Berat

Masalah di studi kasus: server FoodGo membuat **satu proses OS baru untuk setiap pesanan**. Setiap proses membawa "perlengkapan" sendiri (salinan interpreter, memori, dan data program), sehingga 100 pesanan berarti 100 kali overhead tersebut, dan server kehabisan memori.

Perumpamaannya seperti restoran. Model proses per pesanan sama dengan **membangun dapur baru untuk setiap pesanan**: aman karena tidak saling ganggu, tetapi sangat boros tempat dan lama menyiapkannya. Model thread sama dengan **satu dapur dengan beberapa koki**: semua koki berbagi peralatan dan bahan yang sama, jadi jauh lebih hemat.

| | Proses per pesanan | Thread (solusi kami) |
|---|---|---|
| Memori | Tiap proses punya memori sendiri, 100 pesanan = 100 kali overhead | Semua thread berbagi memori satu proses |
| Biaya membuat | Berat dan lambat | Ringan dan cepat |
| Berbagi data | Sulit, perlu mekanisme khusus antar proses | Mudah, langsung pakai variabel yang sama |
| Risiko | Boros resource | Race condition, perlu lock |

Alasan threading cocok untuk kasus ini:

- **Hemat memori.** Program kami menangani 100 pesanan hanya dengan 1 proses dan 10 thread, bukan 100 proses. Jumlah thread juga tetap (10) berapa pun pesanan yang masuk, sehingga pemakaian resource tidak ikut membengkak.
- **Pekerjaannya banyak menunggu (I/O-bound).** Memproses pesanan sebagian besar berupa menunggu: query database, panggilan ke layanan pembayaran, dan sebagainya (di simulasi diwakili `time.sleep`). Saat satu thread menunggu, Python memberi giliran ke thread lain, sehingga waktu tunggu tidak terbuang. Secara perhitungan kasar, 100 pesanan dengan rata-rata 5,5 ms akan butuh sekitar 550 ms bila sekuensial, tetapi hanya sekitar sepersepuluhnya bila dibagi ke 10 thread.
- **Multiprocessing tidak diperlukan.** Multiprocessing baru unggul untuk pekerjaan yang berat di perhitungan CPU. Untuk pekerjaan yang dominan menunggu, multiprocessing hanya mengulang masalah awal, yaitu banyak proses yang masing-masing memakan memori.

Konsekuensinya, karena thread berbagi memori, data bersama harus dijaga. Itulah sebabnya race condition muncul di percobaan kami dan mengapa `Lock` wajib dipasang pada counter. Jadi threading menukar boros memori dengan kewajiban sinkronisasi, dan untuk kasus FoodGo pertukaran ini menguntungkan.

## Container (Docker)

Program dikemas dengan base image `python:3.13.7-slim`, varian ringan dari image Python resmi. Karena program hanya memakai standard library, `requirements.txt` tidak berisi dependency tambahan.

Container sejalan dengan tema efisiensi di tugas ini: berbeda dengan virtual machine yang membawa sistem operasi lengkap, container berbagi kernel dengan host sehingga lebih ringan dan cepat dijalankan. Selain itu, lingkungan di dalam container selalu sama (versi Python, struktur folder), jadi program berjalan sama di laptop siapa pun maupun di server.

Hasil pengujian: output di dalam container **sama persis** dengan output saat dijalankan langsung di laptop (100 dari 100).

![Docker vs lokal](bukti/Perbandingan_docker_vs_lokal.png)

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
