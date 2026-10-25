# Tugas 6 (Pekan 6) — Penamaan & Resolusi Lokasi

**Materi terkait:** Flat Naming, Structured Naming (DNS), Distributed Hash Table (DHT)/Chord.

## Studi Kasus

Pelanggan FoodGo kesulitan menemukan alamat IP server kurir yang **dinamis** (kurir berpindah lokasi/jaringan, IP-nya sering berubah). FoodGo butuh cara memetakan **ID Kurir** (identitas tetap) ke **alamat IP terkininya** tanpa server pusat tunggal yang jadi bottleneck/single point of failure.

## Tugas Kelompok

Implementasikan **simulasi Chord DHT** sederhana (single-process, tidak perlu jaringan sungguhan — cukup simulasi struktur data & algoritma di satu program Python) yang memetakan ID Kurir ke alamat IP mereka.

Konsep yang harus terlihat jalan dalam simulasi kalian:
1. **Consistent hashing**: ID Kurir dan ID Node di-hash ke ruang angka yang sama (mis. 0–255 untuk kesederhanaan, `m=8` bit).
2. **Ring topology**: node-node diurutkan melingkar berdasarkan hasil hash-nya.
3. **Lookup**: fungsi `lookup(kurir_id)` yang menemukan node mana yang bertanggung jawab menyimpan mapping ID Kurir tersebut → alamat IP-nya (aturan Chord: node dengan ID hash **terkecil yang lebih besar atau sama dengan** hash key, disebut *successor*).
4. **Perubahan topologi**: simulasikan minimal satu node baru bergabung (`join`) atau satu node keluar (`leave`), tunjukkan bagaimana mapping berpindah tanggung jawab ke node lain.

Skeleton disediakan di `src/chord_simulation.py` dengan fungsi hashing dan struktur ring sudah ada — bagian `lookup()`, `join()`, dan `leave()` sengaja dikosongkan.

### Cara Menjalankan

```bash
python3 src/chord_simulation.py
```

## Tugas Analisis (`README.md`)

1. Jelaskan **kenapa DHT/Chord** lebih cocok untuk kasus ini dibanding **flat naming sederhana** (mis. tabel pusat ID→IP) atau **DNS konvensional** — kaitkan dengan sifat "IP kurir sering berubah" dan kebutuhan tanpa titik gagal tunggal.
2. Gambarkan (boleh pakai Mermaid, lihat Tugas 2) ring topology dari simulasi kalian, tandai node mana yang bertanggung jawab atas ID Kurir mana.
3. Jelaskan apa yang terjadi pada mapping saat sebuah node **keluar** dari ring (siapa yang mengambil alih tanggung jawabnya) — dukung dengan output program.

## Struktur Submission

```
tugas-06-penamaan-dht/
├── README.md      # Analisis + diagram ring
├── JURNAL.md
├── src/
│   └── chord_simulation.py
└── bukti/          # Output program (screenshot/log) untuk skenario join & leave
```

## Rubrik Penilaian (Tugas 6)

| Komponen | Bobot | Kriteria |
|---|---|---|
| Implementasi lookup/join/leave benar | 35% | Consistent hashing & successor lookup sesuai aturan Chord |
| Bukti perubahan topologi (join/leave) | 25% | Output menunjukkan mapping berpindah dengan benar |
| Analisis kenapa DHT vs flat naming/DNS | 25% | Argumen spesifik ke kasus IP kurir dinamis, bukan definisi umum |
| Proses & kontribusi kelompok | 15% | `JURNAL.md`, commit history |

## Batasan Penggunaan AI (Level 2)

Kebijakan **Level 2 (AI Assisted Idea Generation & Structuring)** berlaku — lihat [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Boleh bertanya konsep umum consistent hashing/Chord ke AI; **tidak boleh** meminta AI menuliskan isi `# TODO` di `src/chord_simulation.py` (`find_successor`, `join`, `leave`, dst). Catat pemakaian AI di "Log Penggunaan AI" pada `JURNAL.md`.

- `README.md` wajib menelusuri manual (langkah demi langkah) bagaimana `lookup()` menemukan successor untuk salah satu ID Kurir contoh yang dipakai di `chord_simulation.py` — bukan cuma menempelkan output program.


---

## 3. Apa yang terjadi saat node keluar?
 
**Skenario.** `node-jakarta-1` (id 177) keluar dari ring. Node ini memegang rentang `(136, 177]`. Pada data awal tidak ada kurir di rentang itu (hash yang ada: 28, 50, 116, 132), sehingga leave tidak akan memperlihatkan perpindahan apa pun. Karena itu sebelum leave kami mendaftarkan `kurir-005` (hash 175), yang jatuh di rentang Node 177.
 
**Output program** (`bukti/output-lengkap-leave.txt`):
 
```
--- Sebuah node keluar ---
[Register] Kurir 'kurir-005' (hash=175) disimpan di Node 177 -> IP: 192.168.1.14
SEBELUM leave: kurir-005 (hash=175) -> Node 177, IP 192.168.1.14
[Leave] Node 'node-jakarta-1' (id=177) keluar dari ring, pred=136, successor baru=40
       Key hash=175 (kurir-005): Node 177 -> Node 40
SESUDAH leave: kurir-005 (hash=175) -> Node 40, IP 192.168.1.14
kurir-001 -> 192.168.1.10
kurir-002 -> 192.168.1.11
```
 
**Siapa yang mengambil alih?** Successor dari node yang keluar, yaitu node berikutnya searah jarum jam. Setelah 177 dihapus, ring menjadi `[40, 102, 123, 136]`. Untuk key 175:
1. Cek Node 40: 40 ≥ 175? Tidak.
2. Cek Node 102: 102 ≥ 175? Tidak.
3. Cek Node 123: 123 ≥ 175? Tidak.
4. Cek Node 136: 136 ≥ 175? Tidak.
5. Tidak ada node ≥ 175, maka **wrap-around** ke node terkecil: **Node 40**.
Rentang Node 40 melebar dari `(177, 40]` menjadi `(136, 40]`, karena predecessor-nya sekarang Node 136.
 
**Yang tidak berubah:**
- IP `kurir-005` tetap 192.168.1.14; yang berubah hanya node penanggung jawabnya, jadi `lookup()` tetap berhasil.
- Kurir lain tidak berpindah: `kurir-001` tetap di Node 102, `kurir-002` tetap di Node 40, `kurir-003` di Node 136, `kurir-012` di Node 123. Hanya key di rentang node yang keluar yang terdampak.
| Kurir | Hash | Sebelum leave | Sesudah leave |
|---|---|---|---|
| kurir-005 | 175 | Node 177 | **Node 40** (wrap-around) |
| kurir-003 | 132 | Node 136 | Node 136 (tidak berubah) |
| kurir-012 | 116 | Node 123 | Node 123 (tidak berubah) |
| kurir-001 | 50 | Node 102 | Node 102 (tidak berubah) |
| kurir-002 | 28 | Node 40 | Node 40 (tidak berubah) |
 
**Catatan implementasi.** Di `leave()`, rentang key yang dipegang node dihitung dulu dengan `in_range(h, pred, node_id)` *sebelum* node dihapus. Setelah `del self.nodes[node_id]`, `find_successor(node_id)` dipanggil untuk mendapat successor baru; karena node itu sudah tidak ada, fungsi otomatis melompat ke node berikutnya (termasuk wrap-around). `self.data` tidak perlu diubah karena di simulasi ini penanggung jawab key selalu ditentukan ulang oleh `find_successor()`. Ini sama dengan asumsi Chord bahwa node yang keluar baik-baik menyerahkan datanya ke successor sebelum pergi.
 
---

## Penelusuran Manual lookup()

*Penulis: Muhammad Chaesar Pratama (103072400119)*

Berikut penelusuran manual pencarian successor pada ring Chord DHT dengan ruang identifier 0–255 ($m = 8$ bit). Nilai hash dihitung menggunakan SHA-1 modulo 256.

### 1. Hash Node pada Ring Awal
Empat node awal yang bergabung beserta hasil hash-nya:
- `node-bandung-1` $\to$ **40**
- `node-jakarta-2` $\to$ **102**
- `node-surabaya-1` $\to$ **136**
- `node-jakarta-1` $\to$ **177**

Urutan posisi node di ring: **[40, 102, 136, 177]**

### 2. Penelusuran Langkah demi Langkah untuk `kurir-001`
1. **Hitung hash key:**
   `hash_id("kurir-001")` menghasilkan nilai **50**.
2. **Cari successor:**
   Successor dicari dengan memilih node pertama yang nilainya $\ge$ hash key (50) pada urutan ring:
   - Cek Node 40: $40 \ge 50$ (False, lanjut ke node berikutnya)
   - Cek Node 102: $102 \ge 50$ (True, kondisi terpenuhi)
3. **Hasil:**
   Successor dari `kurir-001` adalah **Node 102** (`node-jakarta-2`). Data mapping IP `kurir-001` disimpan dan di-lookup dari node ini.

### 3. Penelusuran Kasus Lain
- **Key lebih kecil dari node pertama (`kurir-002`):**
  Hash `kurir-002` bernilai **28**. Karena $40 \ge 28$, successor-nya langsung jatuh ke **Node 40**.
- **Wrap-around (key lebih besar dari semua node):**
  Jika terdapat key dengan hash **200**, seluruh node di ring ($40, 102, 136, 177$) nilainya lebih kecil dari 200. Karena topologi ring berbentuk lingkaran, pencarian berputar kembali ke node terkecil yaitu **Node 40**.
