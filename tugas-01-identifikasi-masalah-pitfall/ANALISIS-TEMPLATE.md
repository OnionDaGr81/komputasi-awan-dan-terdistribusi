# Tugas 1 — Analisis Pitfall FoodGo

**Kelompok:** [nama kelompok]

| Nama | NIM | Kontribusi |
|---|---|---|
| [Didit Septa Putra] | [103072400071] | [The network is reliable] |
| [Chaesar Pratama] | [103072400119] | [Latency is zero] |
| [Alif Rifqi Pratama] | [103072400133] | [Arsitektur Monolitik] |
| [Duarte Sebastian Napitupulu] | [103072400152] | [Single Point of Failure] |

## Pitfall 1: [network is reliable] — ditulis oleh [Didit]

**Bukti di skenario:** [ #network is always reliable, no need for retry ]

**Kenapa ini keliru:** [Kita asumsikan jaringan dapat diandalkan adalah sebuah kekeliruan fatal, karena komunikasi via internet terutama ke gateaway pembayaran pihak ketiga atau koneksi antar proses pasti mengalami ketidak stabilan (fluktuasi), packet loss, atau terputus sesaat (network blip)]

**Dampak ke FoodGo:** [Saat pelanggan memesan makanan di jam makan siang, modul pesanan memanggil modul pembayaran. Jika koneksi jaringan mengalami gangguan sesaat saat pengiriman data, panggilan tersebut langsung gagal total. Pelanggan mengalami kegagalan transaksi, pesanan batal terbuat di sistem, dan restoran tidak menerima pesanan dapur. FoodGo kehilangan pendapatan dari transaksi tersebut hanya karena gangguan jaringan mikro yang sebenarnya bisa pulih dalam hitungan milidetik.]

**Solusi desain awal:** [Menerapkan mekanisme Retry dengan Exponential Backoff dan Jitter. Jika pemanggilan dari modul pesanan ke modul pembayaran gagal akibat koneksi terputus, sistem akan mencoba ulang otomatis dengan jeda bertahap (1s, 2s, 4s) ditambah acakan waktu (jitter) untuk mencegah bentrokan trafik.]

**Trade-off:** [Menerapkan retry berisiko memicu Retry Storm. Jika modul pembayaran sebenarnya sedang lumpuh total saat promo besar, ribuan pesanan yang gagal lalu melakukan retry secara bersamaan justru akan membombardir saluran komunikasi internal FoodGo, memperparah kemacetan trafik jaringan, dan merubuhkan layanan lainnya.]

---

## Pitfall 2: [Latency is zero] — ditulis oleh [Chaesar]

**Bukti di skenario:** [kutip/paraphrase bagian skenario]

**Kenapa ini keliru:** [penjelasan]

**Dampak ke FoodGo:** [mekanisme kegagalan konkret]

**Solusi desain awal:** [usulan solusi]

**Trade-off:** [apa yang dikorbankan/risiko dari solusi ini]

---

## Pitfall 3: [Arsitektur Monolitik] — ditulis oleh [Alif]

**Bukti di skenario:** [kutip/paraphrase bagian skenario]

**Kenapa ini keliru:** [penjelasan]

**Dampak ke FoodGo:** [mekanisme kegagalan konkret]

**Solusi desain awal:** [usulan solusi]

**Trade-off:** [apa yang dikorbankan/risiko dari solusi ini]

---

## Pitfall 4: [Single Point of Failure] — ditulis oleh [Sebastian]

**Bukti di skenario:** [Saat trafik naik, satu server yang menangani semua modul (pesanan, pembayaran, notifikasi kurir) kewalahan]

**Kenapa ini keliru:** [Karena semua beban operasi di tumpuk di satu sistem tanpa adanya controller atau backup]

**Dampak ke FoodGo:** [Respon dari server lambat, banyak timeout, atau bisa juga sampai server down total]

**Solusi desain awal:** [Scaling secara Horizontal dan Load Balancer]

**Trade-off:** [Infrastruktur jauh lebih mahal dan manajemen datanya lebih rumit]

---

## Kesimpulan Kelompok

[Ringkasan: jika FoodGo memperbaiki ketiga pitfall ini, apa arsitektur yang disarankan secara garis besar? Kaitkan dengan Tugas 2.]