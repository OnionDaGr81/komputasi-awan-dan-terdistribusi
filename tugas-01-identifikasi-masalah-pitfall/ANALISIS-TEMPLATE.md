# Tugas 1 — Analisis Pitfall FoodGo

**Kelompok:** [nama kelompok]

| Nama | NIM | Kontribusi |
|---|---|---|
| [Didit Septa Putra] | [103072400071] | [The network is reliable] |
| [Chaesar Pratama] | [103072400119] | [Latency is zero] |
| [Alif Rifqi Pratama] | [103072400133] | [Arsitektur Monolitik] |
| [Duarte Sebastian Napitupulu] | [103072400152] | [Single Point of Failure] |

## Pitfall 1: [network is reliable] — ditulis oleh [Didit]

**Bukti di skenario:** "#network is always reliable, no need for retry"

**Kenapa ini keliru:** Kita asumsikan jaringan dapat diandalkan adalah sebuah kekeliruan fatal, karena komunikasi via internet terutama ke gateaway pembayaran pihak ketiga atau koneksi antar proses pasti mengalami ketidak stabilan (fluktuasi), packet loss, atau terputus sesaat (network blip)

**Dampak ke FoodGo:** Saat pelanggan memesan makanan di jam makan siang, modul pesanan memanggil modul pembayaran. Jika koneksi jaringan mengalami gangguan sesaat saat pengiriman data, panggilan tersebut langsung gagal total. Pelanggan mengalami kegagalan transaksi, pesanan batal terbuat di sistem, dan restoran tidak menerima pesanan dapur. FoodGo kehilangan pendapatan dari transaksi tersebut hanya karena gangguan jaringan mikro yang sebenarnya bisa pulih dalam hitungan milidetik.

**Solusi desain awal:** Menerapkan mekanisme Retry dengan Exponential Backoff dan Jitter. Jika pemanggilan dari modul pesanan ke modul pembayaran gagal akibat koneksi terputus, sistem akan mencoba ulang otomatis dengan jeda bertahap (1s, 2s, 4s) ditambah acakan waktu (jitter) untuk mencegah bentrokan trafik.

**Trade-off:** Menerapkan retry berisiko memicu Retry Storm. Jika modul pembayaran sebenarnya sedang lumpuh total saat promo besar, ribuan pesanan yang gagal lalu melakukan retry secara bersamaan justru akan membombardir saluran komunikasi internal FoodGo, memperparah kemacetan trafik jaringan, dan merubuhkan layanan lainnya.

---

## Pitfall 2: Latency is zero — ditulis oleh Chaesar

**Bukti di skenario:** "Tidak ada timeout sama sekali yang terjadi antar-service. Modul pesanan manggil modul pembayaran, lalu menunggu tanpa ada batas waktu sama sekali."

**Kenapa ini keliru:** Kode dalam FoodGo memeperlakukan pemanggilan antar modul seolah-olah pemanggilan fungsi local akan selalu terbalas secara instant dan tanpa latensi sama sekali. Padahal yang sebenarnya terjadi adalah network call yang memiliki latensi dan sering kali tidak konsisten. Sehingga asumsi "Latency is zero" membuat developer tidak membuat atau luput akan skenario tersebut. Di dunia nyata latensi bisa melonjak karena beban server, kongesti jaringan, atau service tujuan yang lambat merespon. Sehungga tanpa timeout, sistem tidak memiliki mekanisme untuk membedakan "sedang lambat" atau "gagal total".

**Dampak ke FoodGo:**
- Saat trafik naik pada jam makan siang atau pun promo, modul pembayaran melambat dan memyebabkan modul pesanan menunggu tanpa batas, thread jadi menumpuk karena tidak pernah dilepas.
- Karena semua modul berjalan dalam satu proses monolitik yang sama tanpa isolasi, thread yang tersangkut menunggu pembayaran tetap terikat pada thread pool web server yang sama dan bukan berjalan di proses atau antrean terpisah. Akibatnya, yang habis bukan cuma "koneksi ke pembayaran", tapi thread pool itu sendiri, sehingga request pesanan dan notifikasi kurir yang sebenarnya tidak berkaitan dengan pembayaran pun ikut tidak kebagian thread.
- Request dari pengguna jadi tertahan, sehingga mengakibatkan gejala "aplikasi lambat", request timeout" di sisi pengguna.
- Hal ini berdampak pada server, server akan kehabisan resource sehingga menyebabkan harus direstart secara manual terus menerus.
- Kegagalan pada satu modul jadi akar permasalahan ke seluruh sistem, bukan hanya mengganggu fitur pembayaran saja.

**Solusi desain awal:** 
- Menambahkan timeout secara eksplisit pada setiap pemanggilan antar-service, misalnya modul pesanan ke modul pembayaran diberi batas waktu tunggu 3–5 detik, dengan nilai yang disesuaikan dari hasil sample pengukuran latensi nyata, bukan angka yang ditebak-tebak.
- Menerapkan circuit breaker pada sisi pemanggil sehingga jika modul pembayaran berulang kali timeout, sistem berhenti mencoba sementara dan langsung gagal cepat, bukan terus menumpuk request yang ada.
- Menambahkan retry dengan backoff terbatas untuk kegagalan yang sifatnya sementara, misalnya pengguna beberapa kali terkena timeout maka sistem akan otomatis membatalkannya dan tidak melakukan retry tanpa batas.
- Untuk tim kecil seperti FoodGo, prioritas paling utama adalah menambahkan timeout terlebih dahulu, karena biayanya murah dan langsung mencegah resource habis. "Circuit breaker" dan "retry with backoff" seperti yang sudah dibahas tadi bisa menyusul sebagai patch baru dan perlahan.

**Trade-off:** 
- Menentukan angka timeout itu sendiri tidak mudah karena kalau terlalu pendek, transaksi yang sebenarnya valid tapi cuma lambat bisa ikut dianggap gagal. Kalau terlalu panjang, efek penumpukan tetap terjadi meski lebih lambat.
- Circuit breaker menambah kompleksitas logika dan state serta membutuhkan tenaga yang lebih untuk merealisasikannya.
- Kombinasi timeout dan retry meningkatkan resiko terjadinya duplikasi dalam transaksi, misalnya kalau pembayaran sebenarnya sudah berhasil di sisi server tapi responsnya yang terlambat diterima. Ini membutuhkan mekanisme khusus di modul pembayaran supaya sistem tahu kalau ada permintaan yang persis sama dikirim dua kali.

---

## Pitfall 3: [Arsitektur Monolitik] — ditulis oleh [Alif]

**Bukti di skenario:** "Semua modul seperti pesanan, pembayaran, dan notifikasi disatukan dalam satu proses monolitik yang sama."

**Kenapa ini keliru:** Arsitektur monolitik tidak selalu salah. Untuk sistem kecil, monolit justru bisa lebih sederhana. Namun, dalam konteks FoodGo yang memiliki fungsi seperti pemesanan, pembayaran, dan notifikasi, penyatuan seluruh fungsi menjadi satu proses dapat menjadi masalah ketika sistem berkembang.

**Dampak ke FoodGo:** 
- Downtime lebih luas. Gangguan pada aplikasi utama dapat menyebabkan beberapa fitur ikut tidak tersedia.
- Sulit dikembangkan. Developer harus berhati-hati ketika mengubah satu modul karena dapat memengaruhi modul lain.
- Scalling tidak efisien. Seluruh aplikasi perlu ditingkatkan kapasitasnya meskipun hanya satu fungsi yang mengalami peningkatan beban.
- Deployment lebih berisiko. Perubahan pada pembayaran misalnya harus melakukan deployment aplikasi utama.
- Maintenance lebih sulit. Semakin besarkode aplikasi, semakin sulit memahami hubungan antar bagian.
- Performa dapat terganggu. Proses berat pada satu modul dapat menggunakan resource yang juga dibutuhkan modul lain.

**Solusi desain awal:**
Solusi yang dapat digunakan adalah memisahkan tanggung jawab setiap modul, tetapi tidak harus langsung membuat microservices yang sangat kompleks. Untuk tahap awal, FoodGo dapat menggunakan pendekatan modular monolith. Setiap modul memiliki tanggung jawab yang jelas dan sebisa mungkin tidak mencampurkan logika bisnisnya. Contoh:
- Order Module: Membuat pesanan, mengubah status pesanan, melihat detail pesanan, mengelola status makanan.
- Payment Module: Proses pembayaran, validasi pembayaran, status pembayaran, transaksi pembayaran.
- Notification Module: Notifikasi pesanan, notifikasi pembayaran, notifikasi perubahan status.

**Trade-off:** 
Jika kita menggunakan sistem Modular monolith maka resikonya:
- Modul masih berada dalam satu aplikasi, sehingga kegagalan pada aplikasi utama masih dapat berdampak ke beberapa modul.
- Scaling belum sepenuhnya independen karena aplikasi masih dideploy sebagai satu kesatuan.
- Seiring sistem semakin besar, kode tetap berpotensi menjadi kompleks.
- Membutuhkan disiplin tinggi agar batas antar-modul tetap terjaga.

Jika kita menggunakan sistem Microservices maka resikonya:
- Arsitektur menjadi lebih kompleks karena setiap service harus dikelola secara terpisah.
- Membutuhkan infrastruktur tambahan seperti API gateway, message broker, monitoring, dan service discovery.
- Komunikasi antar-service melalui jaringan dapat menimbulkan latency dan kegagalan komunikasi.
- Debugging lebih sulit karena satu proses bisnis dapat melibatkan beberapa service.
Deployment, monitoring, dan maintenance membutuhkan effort yang lebih besar.

---

## Pitfall 4: [Single Point of Failure] — ditulis oleh [Sebastian]

**Bukti di skenario:** Saat trafik naik, satu server yang menangani semua modul (pesanan, pembayaran, notifikasi kurir) kewalahan.

**Kenapa ini keliru:** Karena semua beban operasi di tumpuk di satu sistem tanpa adanya controller atau backup. Sistem juga tidak memiliki cara untuk membatasi dan manajemen resource, sehingga jika satu modul menghabiskan resource, modul lain juga akan berhenti. Sistem juga sayangnya tidak mengetahui batas kemampuannya sendiri, sehingga sistem akan memaksakan diri memproses request yang baru dan melebihi batas resource dan akhirnya crash total.

**Dampak ke FoodGo:** Respon dari server lambat, banyak timeout, atau bisa juga sampai server down total.

**Solusi desain awal:** Scaling secara Horizontal dan Load Balancer.

**Trade-off:** Infrastruktur jauh lebih mahal dan manajemen datanya lebih rumit.

---

## Kesimpulan Kelompok

[Ringkasan: jika FoodGo memperbaiki ketiga pitfall ini, apa arsitektur yang disarankan secara garis besar? Kaitkan dengan Tugas 2.]