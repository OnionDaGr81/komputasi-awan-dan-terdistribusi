# Jurnal Proses — Tugas 9

## Diskusi deployment model
- Opsi yang dipertimbangkan dan kenapa akhirnya memilih salah satu:
  - **Public Cloud murni:** Sempat dipertimbangkan karena unggul di *rapid elasticity* saat lonjakan pemilu/PPDB dan tidak perlu belanja kapasitas puncak sendiri. **Ditolak** karena database induk NIK dan data biometrik (data pribadi spesifik menurut UU PDP) tidak boleh berada di infrastruktur *multi-tenant* di luar kendali penuh negara, dan biometrik tidak bisa di-*reset* jika bocor.
  - **Private Cloud murni:** Memenuhi kendali penuh negara, tetapi tidak efisien jika seluruh lapisan akses publik ikut ditanggung *private cloud* karena kapasitas harus disediakan sebesar puncak pemilu/PPDB lalu menganggur di hari biasa.
  - **Hybrid Cloud (dipilih):** Membagi sistem berdasarkan klasifikasi data dan pola beban — database induk NIK, biometrik, kunci enkripsi (HSM), dan *log audit* tetap dikunci di *Private Cloud* milik negara, sedangkan lapisan verifikasi yang *stateless* dan fluktuatif (portal cek status, *API gateway*, *cache* hasil verifikasi, antrean) berjalan di *Public Cloud* region Indonesia dengan data yang sudah diminimalkan/ditokenisasi.

## Diskusi service model per komponen
- **IaaS (di Private Cloud):** Dipilih untuk database induk NIK, penyimpanan biometrik, server manajemen kunci enkripsi, dan *log audit* agar pemerintah memegang kendali penuh atas server, jaringan, firewall, enkripsi, dan kepatuhan regulasi (UU PDP & PP No. 71 Tahun 2019).
- **PaaS (di Public Cloud region Indonesia):** Dipilih untuk *API gateway* verifikasi, portal pengecekan status, *cache*, dan sistem antrean permintaan karena memudahkan *auto-scaling* dan integrasi API ribuan instansi tanpa harus mengelola infrastruktur server secara manual.
- **SaaS (aplikasi pendukung):** Dibatasi khusus untuk layanan non-inti seperti *helpdesk*, sistem pengaduan masyarakat, dan pelaporan tiket supaya efisien dan cepat dipakai, dengan catatan ketat tidak boleh menyimpan data NIK/biometrik mentah.

## Diskusi risiko & skenario tandingan
- Risiko yang sempat dibahas lalu disaring:
  - Risiko generik seperti "serangan DDoS" atau "human error" tidak dijadikan poin utama karena bisa muncul di sistem apa pun; fokus diarahkan ke risiko yang spesifik muncul akibat batas integrasi Hybrid Cloud pada data kependudukan & biometrik (UU PDP), *bottleneck* jalur *interconnect* saat lonjakan pemilu/PPDB, serta penyalahgunaan akses API oleh ribuan instansi konsumen (KYC bank/daerah).
- Pertimbangan skenario tandingan:
  - Mengangkat kondisi nyata ketimpangan infrastruktur & koneksi dukcapil daerah (daerah 3T) agar jelas bahwa *Private Cloud* negara dikelola terpusat (tingkat nasional), bukan dibebankan ke masing-masing pemda, ditambah skenario gangguan *interconnect* saat hari puncak pemilu/PPDB untuk menguji ketahanan arsitektur Hybrid Cloud.

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 21/11/2026 | Gemini | Brainstorming pembagian tugas kelompok 3 orang untuk Tugas 9 (Deployment Model, Service Model, Risiko & Skenario Tandingan) sesuai bobot rubrik | Saran membagi tugas menjadi 3 peran: Anggota 1 (Deployment Model NIST + Alternatif Ditolak), Anggota 2 (Service Model per komponen), Anggota 3 (Risiko Spesifik, Skenario Tandingan & Finalisasi) | Disepakati oleh kelompok dan dituangkan ke tabel `Kontribusi Kelompok` di `README.md` dengan pembagian Didit (Bagian 1 & 4), Alif (Bagian 2), dan Chaesar (Bagian 3, 5, & finalisasi) |
| 21/11/2026 | Gemini | Brainstorming contoh risiko spesifik arsitektur Hybrid Cloud pada sistem data kependudukan (UU PDP, biometrik, KYC bank, lonjakan pemilu/PPDB) serta ide skenario tandingan | Saran memfokuskan risiko pada batas integrasi (*bridge*) Private–Public Cloud, *false elasticity* / *bottleneck* jalur *interconnect* & *stale cache*, serta *credential abuse* antar instansi; serta skenario tandingan keterbatasan infrastruktur daerah 3T dan gangguan *interconnect* saat hari puncak | Diolah dan diselaraskan dengan rancangan Bagian 1 (Hybrid Cloud, region Indonesia, PP 71/2019) dan Bagian 2 (IaaS Private, PaaS Public, SaaS helpdesk) menjadi Bagian 3, Bagian 5 di `README.md`, serta rangkuman proses di `JURNAL.md` |
