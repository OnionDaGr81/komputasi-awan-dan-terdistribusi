# Tugas 5 (Pekan 5) — Koordinasi & Konsensus

**Materi terkait:** Physical/Logical Clock, Election Algorithm (Bully/Raft).

## Studi Kasus

Terjadi konflik urutan waktu pada pesanan FoodGo (dua server mencatat urutan pesanan berbeda karena jam tidak sinkron), dan sistem membutuhkan satu **"Node Leader"** untuk mengelola antrean pesanan pusat agar tidak terjadi konflik pemrosesan ganda.

## Tugas Kelompok

Implementasikan simulasi **Bully Algorithm** untuk memilih leader di antara **5 node virtual** yang berjalan sebagai 5 proses Python terpisah di laptop yang sama (tiap node = satu proses di port berbeda, komunikasi lewat TCP socket di `localhost`).

Skeleton yang disediakan (`src/node.py`) sudah menangani bagian **infrastruktur jaringan** (membuka socket, menerima & mengirim pesan antar node) — bagian **algoritma Bully sendiri sengaja dikosongkan** (`# TODO`), karena itu inti pembelajaran tugas ini.

### Aturan Bully Algorithm yang harus diimplementasikan

1. Node yang mendeteksi leader tidak merespons (atau saat start pertama kali) mengirim pesan `ELECTION` ke semua node dengan ID **lebih besar** darinya.
2. Jika ada node ber-ID lebih besar yang merespons `OK`, node yang memulai election **berhenti mencalonkan diri** dan menunggu pesan `COORDINATOR`.
3. Jika **tidak ada** node ber-ID lebih besar yang merespons dalam batas waktu tertentu, node tersebut menjadi leader dan mem-broadcast `COORDINATOR` ke semua node lain.
4. Semua node mencatat siapa leader saat ini.

### Cara Menjalankan

Buka 5 terminal terpisah (satu per node):
```bash
python3 src/node.py --id 1 --port 5001 --peers 5002,5003,5004,5005
python3 src/node.py --id 2 --port 5002 --peers 5001,5003,5004,5005
python3 src/node.py --id 3 --port 5003 --peers 5001,5002,5004,5005
python3 src/node.py --id 4 --port 5004 --peers 5001,5002,5003,5005
python3 src/node.py --id 5 --port 5005 --peers 5001,5002,5003,5004
```

### Skenario Wajib Diuji & Dicatat

1. **Start normal**: nyalakan node 1–5 hampir bersamaan, catat siapa yang terpilih jadi leader (harusnya node ber-ID tertinggi, yaitu node 5).
2. **Leader mati**: matikan (Ctrl+C) proses node leader (node 5), amati node lain mendeteksi leader hilang dan memicu election baru. Catat leader baru yang terpilih (harusnya node 4).
3. Simpan log terminal (screenshot atau `> log_nodeX.txt` redirect) dari kedua skenario ke folder `bukti/`.

## Struktur Submission

```
tugas-05-koordinasi-konsensus/
├── README.md      # Analisis: kenapa perlu leader, kenapa Bully (vs Raft), hasil 2 skenario
├── JURNAL.md
├── src/
│   └── node.py
└── bukti/          # Log/screenshot skenario start normal & leader mati
```

## Rubrik Penilaian (Tugas 5)

| Komponen | Bobot | Kriteria |
|---|---|---|
| Implementasi Bully Algorithm benar | 35% | Election, OK, COORDINATOR message bekerja sesuai aturan algoritma |
| Bukti skenario leader mati → re-election | 30% | Log jelas menunjukkan leader baru terpilih otomatis |
| Analisis (kenapa perlu leader, trade-off Bully vs Raft) | 20% | Dikaitkan ke masalah urutan pesanan di skenario FoodGo |
| Proses & kontribusi kelompok | 15% | `JURNAL.md`, commit history |

## Batasan Penggunaan AI (Level 2)

Kebijakan **Level 2 (AI Assisted Idea Generation & Structuring)** berlaku — lihat [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Boleh bertanya ke AI tentang gambaran umum algoritma election; **tidak boleh** meminta AI menuliskan isi `# TODO` di `src/node.py` (logika `on_message`, `start_election`, `declare_leader`, `monitor_leader`). Catat pemakaian AI di "Log Penggunaan AI" pada `JURNAL.md`.

- `README.md` wajib menjelaskan kenapa Bully Algorithm selalu memilih node ber-ID tertinggi yang masih hidup, dan apa kelemahannya dibanding algoritma lain (mis. jumlah pesan yang dikirim saat election, single point of failure sebelum leader baru terpilih) — bukan sekadar definisi generik.

---

# Laporan Analisis & Pembagian Tugas Kelompok

## Bagian 1: Kenapa FoodGo Perlu Leader
*(Akan dilengkapi oleh Duarte Sebastian Napitupulu)*

---

## Bagian 2: Akar Masalah — Jam Fisik, Logical Clock, dan Urutan Pesanan
*Penulis: Muhammad Chaesar Pratama (103072400119)*

### 1. Masalah Jam Fisik pada Server FoodGo (Clock Drift, Presisi, dan Akurasi)
- **Clock Drift**: Jam perangkat keras di setiap server digerakkan oleh kristal kuarsa yang dipengaruhi suhu dan tegangan listrik. Akibatnya, jam Server 1 dan Server 2 tidak berdetik dengan kecepatan yang persis sama dan mengalami pergeseran waktu (*clock drift* dengan laju batas `rho`).
- **Precision (pi) vs Accuracy (alpha)**: 
  - *Precision (pi)*: Deviasi waktu antar server di dalam sistem cluster (`|C_i - C_j| <= pi`).
  - *Accuracy (alpha)*: Deviasi waktu jam server terhadap standar waktu luar/UTC (`|C_i - UTC| <= alpha`).
- **Dampak pada FoodGo**: Jika dua pelanggan memesan menu yang sama di server berbeda dalam waktu yang berdekatan, perbedaan jam fisik antar server dapat memicu kesalahan stempel waktu (*timestamp*), sehingga urutan pemrosesan pesanan menjadi tertukar.

### 2. Kenapa Sinkronisasi Jam Fisik Saja Tidak Cukup
- Protokol sinkronisasi jam fisik (seperti NTP) memiliki keterbatasan latensi jaringan (*jitter* dan asimetri transmisi), sehingga selalu ada margin kesalahan waktu.
- **Poin Kunci (Slide 7)**: Dalam sistem terdistribusi, kebutuhan utama bukanlah mengetahui jam fisik persis (*wall-clock time*), melainkan **kesepakatan urutan kejadian (*agreement on event ordering*)**. Mengetahui apakah Pesanan A masuk *sebelum* Pesanan B jauh lebih penting daripada jam absolutnya.

### 3. Solusi Lamport Logical Clock & Relasi Happened-Before
- Leslie Lamport (1978) memperkenalkan relasi **happened-before** (`->`):
  1. Jika event `a` terjadi sebelum `b` pada proses yang sama, maka `a -> b`.
  2. Jika `a` adalah event pengiriman pesan dan `b` adalah penerimaan pesan tersebut, maka `a -> b`.
  3. Bersifat transitif: jika `a -> b` dan `b -> c`, maka `a -> c`.
- **Aturan Pembaruan Clock**:
  - Setiap event lokal: jam lokal bertambah `C_i = C_i + 1`.
  - Saat kirim pesan: sertakan nilai `C_i`.
  - Saat terima pesan: perbarui jam lokal `C_j = max(C_j, C_msg) + 1`.
  - Jika timestamp sama, Process ID digunakan sebagai penentu urutan (*tie-breaker*).

### 4. Totally Ordered Multicast & Analogi Pesanan FoodGo
- **Konsep**: Seluruh server mengeksekusi urutan transaksi yang identik dengan mem-broadcast pesan ber-timestamp Lamport dan menempatkannya di antrean lokal. Transaksi hanya dieksekusi jika berada di urutan terdepan dan semua server telah membalas ACK.
- **Analogi FoodGo**: Pada promo *flash sale* menu sisa 1 porsi, Pelanggan X checkout di Server 1 dan Pelanggan Y checkout di Server 2. Totally ordered multicast memastikan seluruh server memproses dalam urutan yang sama, sehingga tidak terjadi *double booking* atau stok minus.

### 5. Batasan Lamport Clock & Solusi Vector Clock
- **Kelemahan Lamport**: Hubungannya bersifat satu arah (`a -> b` maka `C(a) < C(b)`). Jika `C(a) < C(b)`, kita tidak bisa memastikan apakah `a` menyebabkan `b`, karena bisa saja kedua event terjadi bersamaan secara independen (*concurrent*).
- **Vector Clock**: Setiap server memelihara vektor integer `V_i[1..N]`. Dengan vektor ini, sistem dapat membuktikan kausalitas dua arah (`a -> b <=> V(a) < V(b)`) dan mendeteksi secara akurat jika ada konflik pemesanan yang bersifat konkruen.

### 6. Alasan Memilih Koordinator/Leader dibanding Logical Clock di Semua Node
- **Overhead Jaringan Ringan**: Totally ordered multicast membutuhkan broadcast ke seluruh server dan pengumpulan ACK (`O(N^2)` pesan per transaksi). Dengan adanya Leader, worker cukup berkomunikasi langsung ke Leader (`O(1)` pesan).
- **Antrean Terpusat FIFO**: Leader bertindak sebagai *single source of truth* untuk nomor urut pesanan tanpa perlu logika antrean terdistribusi yang rumit di tiap node.
- **Toleransi Kegagalan Otomatis**: Risiko *single point of failure* (SPOF) diselesaikan dengan **Bully Algorithm**. Jika node leader mati, node-node aktif secara otomatis memilih leader baru (ID tertinggi yang hidup) dan sistem segera pulih.

---

## Bagian 3: Kenapa Bully Selalu Memilih ID Tertinggi + Kelemahannya
*(Akan dilengkapi oleh Duarte Sebastian Napitupulu)*

---

## Bagian 4: Perbandingan Bully vs Ring, ZooKeeper, Raft
*(Akan dilengkapi oleh Didit Septa Putra)*

---

## Bagian 5: Hasil Skenario Start Normal & Leader Mati + Observasi
*(Akan dilengkapi oleh Alif Rifqi Pratama)*

---

## Bagian 6: Tabel Kontribusi

| Nama | NIM | Kontribusi |
|---|---|---|
| Muhammad Chaesar Pratama | 103072400119 | Implementasi TODO 1 (`on_message`), desain state bersama (`received_ok`, `is_electing`), dan analisis Bagian 2 (Jam Fisik, Logical Clock, dan Urutan Pesanan) |
| Didit Septa Putra | 103072400071 | Implementasi TODO 2 & 3 (`start_election`, `declare_leader`), analisis Bagian 4 (Bully vs Ring, ZooKeeper, Raft) 
| Alif Rifqi Pratama | 103072400133 | Implementasi TODO 4 (`monitor_leader`), pengujian skenario 1 & 2, dokumentasi bukti |
| Duarte Sebastian Napitupulu | 103072400152 | Integrasi kode, analisis Bagian 1 & 3, rekap JURNAL, submission |
