# Tugas 9 (Pekan 9) — Cloud Delivery & Deployment Model

**Materi terkait:** Karakteristik esensial cloud computing (NIST SP 800-145), Deployment Model (Public/Private/Hybrid/Community), Service Model (IaaS/PaaS/SaaS).

> Bagian 2 mata kuliah ini murni **analisis & desain di atas kertas** — tidak ada biaya cloud sama sekali, karena tugas berhenti di tahap rekomendasi, bukan implementasi nyata (implementasi baru mulai Tugas 11).

## Studi Kasus

Pemerintah ingin membangun **Sistem Data Kependudukan** (nama, NIK, alamat, data biometrik) yang:
- Sangat **rahasia** (data pribadi warga negara, diatur UU Perlindungan Data Pribadi).
- Diakses oleh **ribuan instansi** (dukcapil daerah, kepolisian, bank untuk verifikasi KYC) dengan pola akses yang **tidak rata** (lonjakan saat musim pemilu/pendaftaran sekolah).
- Butuh **skalabilitas** agar tidak downtime saat lonjakan akses, tapi **tidak boleh** datanya berada di infrastruktur yang tidak terkendali penuh oleh negara.

## Tugas Kelompok

1. **Rekomendasikan Deployment Model** (Public / Private / Hybrid / Community Cloud) yang paling tepat untuk sistem ini. Jelaskan alasannya berdasarkan **karakteristik NIST** (on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service) dikaitkan dengan kebutuhan kerahasiaan vs skalabilitas.
2. **Rekomendasikan Service Model** (IaaS / PaaS / SaaS) yang tepat untuk komponen-komponen berbeda dari sistem ini (boleh berbeda service model untuk komponen berbeda, mis. database inti vs portal publik untuk pengecekan status).
3. Jelaskan **minimal 2 risiko spesifik** dari pilihan kalian dan mitigasinya (mis. jika Hybrid Cloud dipilih: risiko sinkronisasi data antara private & public segment).
4. Bandingkan singkat dengan **satu alternatif yang kalian tolak** — kenapa alternatif itu kurang tepat (mis. kenapa Public Cloud murni ditolak, atau kenapa Private Cloud murni dianggap kurang skalabel).

## Struktur Submission

```
tugas-09-cloud-delivery-deployment/
├── README.md      # Analisis lengkap (isi dengan poin 1-4 di atas)
├── JURNAL.md
└── bukti/          # (opsional) diagram pendukung
```

## Rubrik Penilaian (Tugas 9)

| Komponen | Bobot | Kriteria |
|---|---|---|
| Ketepatan rekomendasi deployment model | 30% | Argumen berbasis karakteristik NIST, bukan sekadar "private cloud lebih aman" tanpa detail |
| Ketepatan rekomendasi service model | 25% | Pemetaan komponen sistem ke IaaS/PaaS/SaaS masuk akal |
| Analisis risiko & mitigasi | 25% | Risiko spesifik ke konteks data kependudukan (bukan risiko generik) |
| Perbandingan dengan alternatif yang ditolak | 20% | Argumen penolakan jelas dan berdasar |

## Batasan Penggunaan AI (Level 2)

Kebijakan **Level 2 (AI Assisted Idea Generation & Structuring)** berlaku — lihat [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Boleh bertanya ke AI gambaran umum karakteristik NIST/deployment model untuk brainstorming; **tidak boleh** meminta AI menuliskan rekomendasi/analisis akhir yang tinggal ditempel ke `README.md`. Catat pemakaian AI di "Log Penggunaan AI" pada `JURNAL.md`.

- Jawaban yang terasa seperti "template" (bisa dipakai untuk sistem cloud apa saja tanpa menyebut spesifik kependudukan/data pribadi/regulasi) akan dinilai rendah pada komponen ketepatan rekomendasi.
- `README.md` wajib membahas minimal satu skenario tandingan yang kalian buat sendiri (mis. "bagaimana jika instansi daerah tidak punya infrastruktur private cloud sendiri?") beserta jawabannya.

---

## Kontribusi Kelompok

| Nama | NIM | Kontribusi |
|---|---|---|
| Didit Septa Putra | 103072400071 | Rekomendasi Deployment Model berbasis NIST (Bagian 1), perbandingan alternatif yang ditolak (Bagian 4), jurnal diskusi deployment model |
| Alif Rifqi Pratama | 103072400133 | Rekomendasi Service Model IaaS/PaaS/SaaS per komponen (Bagian 2), diagram arsitektur di `bukti/`, jurnal diskusi service model |
| Muhammad Chaesar Pratama | 103072400119 | Analisis risiko spesifik & mitigasi (Bagian 3), skenario tandingan & solusinya (Bagian 5), tabel kontribusi, catatan jurnal risiko |

---

## 1. Rekomendasi Deployment Model: Hybrid Cloud
 
**Rekomendasi:** Sistem Data Kependudukan sebaiknya dibangun di atas **Hybrid Cloud**. Data inti (database induk NIK dan biometrik, kunci enkripsi, serta log audit) berada di **private cloud** yang dikendalikan penuh oleh negara. Lapisan akses yang berskala besar (portal pengecekan status, API gateway verifikasi, dan cache) berjalan di **public cloud** yang berlokasi di Indonesia dan hanya menangani data yang sudah diminimalkan.
 
### Prinsip pembagian: berdasarkan klasifikasi data
 
Pembagian segmen tidak didasarkan pada anggapan bahwa satu jenis cloud "lebih aman", melainkan pada **sifat data dan sifat beban kerjanya**:
 
| Segmen | Isi | Alasan |
|---|---|---|
| Private cloud | Database induk NIK, alamat, biometrik; manajemen kunci enkripsi; log audit | Data pribadi bersifat spesifik dan rahasia; biometrik tidak bisa diganti jika bocor |
| Public cloud (region Indonesia) | Portal cek status, API gateway verifikasi, cache hasil verifikasi, antrean permintaan | Beban naik-turun tajam dan bersifat stateless; hanya memproses data yang sudah diminimalkan atau ditokenisasi |
 
Lonjakan akses saat pemilu, pendaftaran sekolah, dan verifikasi KYC bank sebagian besar berupa permintaan **verifikasi**, misalnya "apakah NIK ini valid dan cocok dengan nama ini". Jawabannya cukup berupa "valid / tidak valid" atau atribut terbatas, bukan data lengkap. Karena itu lonjakan bisa diserap segmen public tanpa membuka database induk ke infrastruktur luar. Ini cara Hybrid mendamaikan kerahasiaan dan skalabilitas.
 
### Analisis berdasarkan lima karakteristik NIST SP 800-145
 
1. **On-demand self-service.** Instansi seperti dukcapil daerah, kepolisian, dan bank perlu mendapat akses (akun, API key, kuota) tanpa antre proses manual yang panjang. Hybrid memungkinkan portal onboarding di segmen public, sementara kebijakan otorisasi dan persetujuan akses ke data inti tetap diputuskan dan dicatat oleh otoritas pusat di segmen private. Kemudahan provisioning tidak berarti kemudahan membuka data.
2. **Broad network access.** Ribuan instansi mengakses dari jaringan yang berbeda-beda. Segmen public memang dirancang untuk akses luas, tetapi segmen private tidak boleh langsung terbuka ke internet. Akses ke data inti hanya lewat gateway terkontrol dengan autentikasi instansi dan jalur khusus antar segmen. Dengan begitu keluasan akses terjadi di lapisan depan, bukan di lapisan data.
3. **Resource pooling.** Pada public cloud, sumber daya fisik digunakan bersama tenant lain (multi-tenancy). Untuk lapisan akses yang hanya memproses data minimal, risiko ini bisa diterima. Untuk data biometrik seluruh warga negara, berbagi infrastruktur fisik dengan pihak lain tidak bisa diterima, sehingga database induk ditempatkan di private cloud yang pool sumber dayanya hanya dipakai institusi pemerintah.
4. **Rapid elasticity.** Ini alasan utama memakai segmen public. Jika seluruh sistem dibangun di private cloud, kapasitas harus disiapkan untuk puncak pemilu atau musim pendaftaran sekolah, lalu menganggur sebagian besar tahun. Dengan Hybrid, kapasitas tambahan di public bisa diperbesar saat lonjakan dan dikecilkan setelahnya, sehingga risiko downtime saat lonjakan berkurang.
5. **Measured service.** Pemakaian tiap instansi dapat diukur dan ditagih sesuai penggunaan, dan metering ini sekaligus mendukung audit: siapa mengakses data apa, kapan, dan berapa kali. Pencatatan akses terhadap data inti dilakukan di segmen private agar jejak audit berada di bawah kendali negara.
### Kaitan dengan kerahasiaan negara dan regulasi
 
Data kependudukan, terutama biometrik, termasuk data pribadi yang bersifat spesifik dan mendapat perlindungan ketat dalam UU Perlindungan Data Pribadi (UU No. 27 Tahun 2022). Pengendali data bertanggung jawab menjaga keamanan dan kerahasiaannya. Selain itu, ketentuan bagi penyelenggara sistem elektronik lingkup publik (PP No. 71 Tahun 2019) menuntut perhatian pada lokasi pengelolaan dan pemrosesan data. Dua hal ini menjadi dasar bahwa **kendali atas data inti tidak boleh dilepas**, sementara kebutuhan skalabilitas dipenuhi di lapisan yang tidak menyimpan data inti.
 
### Kesimpulan poin 1
 
Hybrid Cloud dipilih karena sistem ini menghadapi dua tuntutan yang bertolak belakang: data yang sangat rahasia dan pola akses yang tidak rata. Private cloud memenuhi tuntutan pertama, public cloud memenuhi tuntutan kedua, dan pembagian berdasarkan klasifikasi data membuat keduanya tidak saling mengorbankan.

## 2. Rekomendasi Service Model (IaaS / PaaS / SaaS)

**Rekomendasi:** Sistem Data Kependudukan sebaiknya menggunakan kombinasi **IaaS, PaaS, dan SaaS** sesuai fungsi dan tingkat sensitivitas masing-masing komponen. Pemilihan service model harus mempertimbangkan kebutuhan kendali terhadap infrastruktur, kemudahan pengembangan aplikasi, serta keamanan data pribadi penduduk.

### Prinsip pembagian: berdasarkan fungsi komponen

| Service Model | Komponen Sistem | Alasan |
|---|---|---|
| **IaaS (Infrastructure as a Service)** | Database induk NIK, penyimpanan biometrik, server manajemen kunci enkripsi, dan log audit | Membutuhkan kendali penuh terhadap server, jaringan, penyimpanan, dan konfigurasi keamanan karena menangani data yang sangat sensitif. |
| **PaaS (Platform as a Service)** | API gateway verifikasi, aplikasi portal pengecekan status, sistem antrean permintaan, dan cache | Memudahkan pengembangan, pengelolaan, serta penskalaan aplikasi tanpa harus mengelola infrastruktur server secara langsung. |
| **SaaS (Software as a Service)** | Aplikasi pendukung seperti helpdesk, sistem pelaporan, dan pengelolaan tiket pengaduan | Dapat menggunakan aplikasi siap pakai sehingga pemerintah tidak perlu membangun dan memelihara seluruh perangkat lunak pendukung sendiri. |

### Analisis masing-masing Service Model

**1. Infrastructure as a Service (IaaS)**

IaaS direkomendasikan untuk komponen inti yang membutuhkan kendali infrastruktur secara menyeluruh, terutama database induk NIK, penyimpanan biometrik, dan log audit.

- Pemerintah dapat mengatur server, jaringan, sistem operasi, dan penyimpanan sesuai kebutuhan keamanan.
- Memungkinkan penerapan firewall, enkripsi, dan pembatasan akses secara khusus.
- Infrastruktur dapat ditempatkan pada private cloud sehingga pengelolaan data inti tetap berada di bawah kendali pemerintah.

Dengan demikian, IaaS menjadi pilihan yang tepat untuk komponen yang menyimpan informasi pribadi dan rahasia penduduk.

**2. Platform as a Service (PaaS)**

PaaS direkomendasikan untuk komponen aplikasi yang melayani permintaan verifikasi dari berbagai instansi, seperti API gateway, portal pengecekan status, dan sistem antrean permintaan.

- Pengembang dapat fokus membangun dan memperbarui aplikasi tanpa mengelola server secara langsung.
- Mendukung peningkatan kapasitas secara otomatis ketika terjadi lonjakan permintaan.
- Mempermudah integrasi antarinstansi melalui API yang terkelola.
- Mengurangi beban pemeliharaan infrastruktur aplikasi.

PaaS cocok ditempatkan pada public cloud untuk menangani permintaan dalam jumlah besar, dengan ketentuan bahwa aplikasi hanya memproses data yang telah diminimalkan atau ditokenisasi.

**3. Software as a Service (SaaS)**

SaaS direkomendasikan untuk kebutuhan pendukung yang tidak berhubungan langsung dengan pengolahan database kependudukan, misalnya aplikasi helpdesk, sistem pengaduan masyarakat, dan pengelolaan tiket layanan.

- Pemerintah dapat langsung menggunakan aplikasi yang sudah disediakan oleh penyedia layanan.
- Tidak perlu membangun aplikasi pendukung dari awal.
- Pemeliharaan dan pembaruan aplikasi ditangani oleh penyedia layanan.
- Dapat meningkatkan efisiensi operasional dan pelayanan masyarakat.

Namun, penggunaan SaaS harus dibatasi pada data yang tidak sensitif. Data NIK, biometrik, dan informasi pribadi penduduk tidak boleh disimpan atau diproses melalui layanan SaaS tanpa jaminan keamanan, kepatuhan, dan kewenangan yang sesuai.

### Kaitan dengan Rekomendasi Deployment Model (Hybrid Cloud)

Ketiga service model tersebut dapat diterapkan bersamaan dengan Hybrid Cloud pada poin pertama.

| Lokasi Deployment | Service Model | Komponen |
|---|---|---|
| Private Cloud | IaaS | Database induk NIK, biometrik, kunci enkripsi, dan log audit |
| Public Cloud | PaaS | API gateway, portal pengecekan status, cache, dan sistem antrean |
| Public Cloud / Infrastruktur pemerintah | SaaS | Helpdesk, sistem pengaduan, dan aplikasi pelaporan pendukung |

Penerapan ini memungkinkan pemerintah mempertahankan kendali atas data inti melalui IaaS, memperoleh fleksibilitas pengembangan aplikasi melalui PaaS, serta meningkatkan efisiensi layanan pendukung melalui SaaS.

### Kesimpulan Poin 2

Kombinasi **IaaS, PaaS, dan SaaS** merupakan pilihan yang tepat untuk Sistem Data Kependudukan karena setiap komponen memiliki kebutuhan pengelolaan yang berbeda. IaaS digunakan untuk menjaga kendali dan keamanan infrastruktur data inti, PaaS digunakan untuk mendukung pengembangan serta skalabilitas aplikasi verifikasi, sedangkan SaaS digunakan untuk meningkatkan efisiensi layanan pendukung. Dengan pembagian tersebut, sistem dapat berjalan lebih fleksibel, efisien, dan tetap memperhatikan kerahasiaan data penduduk.

---

## 3. Analisis Risiko Spesifik & Mitigasi

Menggabungkan **Hybrid Cloud** (Bagian 1) dengan pemetaan **IaaS di Private Cloud, PaaS di Public Cloud region Indonesia, dan SaaS untuk layanan pendukung** (Bagian 2) menyelesaikan dilema antara kendali penuh negara dan skalabilitas saat lonjakan akses. Namun, arsitektur lintas segmen ini memunculkan risiko spesifik pada konteks data kependudukan (NIK, alamat, biometrik) serta regulasi **UU No. 27 Tahun 2022 (UU PDP)** dan **PP No. 71 Tahun 2019**. Berikut tiga risiko paling krusial beserta mitigasinya.

### 3.1 Risiko 1: Kebocoran Data Pribadi & Biometrik pada Batas Integrasi (*Bridge*) Private–Public Cloud dan Layanan SaaS Pendukung

- **Deskripsi risiko:** Pada rancangan di atas, *API gateway* verifikasi, *cache* hasil verifikasi, dan sistem antrean berjalan sebagai **PaaS di Public Cloud**, sementara database induk NIK dan biometrik berada di **IaaS Private Cloud**. Jika terjadi kesalahan konfigurasi sinkronisasi, *cache* yang menyimpan atribut kependudukan mentah (NIK, alamat lengkap, atau templat biometrik) di segmen publik, pencatatan *payload* ke *log* PaaS pihak ketiga, atau warga yang tidak sengaja mengunggah foto KTP/NIK ke aplikasi **SaaS helpdesk/pengaduan**, maka data sensitif warga keluar dari kendali penuh negara. Berdasarkan UU PDP, data biometrik (sidik jari, iris, wajah) termasuk **data pribadi bersifat spesifik** yang dampaknya permanen jika bocor karena tidak dapat di-*reset* seperti kata sandi.
- **Mitigasi:**
  1. **Pola *Zero-PII Persistence* di segmen Public Cloud (PaaS):** Lapisan *API gateway* dan portal pengecekan status dirancang *stateless* dan dilarang menyimpan salinan data induk maupun biometrik mentah. Pencocokan biometrik/KYC selalu dieksekusi di dalam *Private Cloud* (IaaS), sedangkan segmen *Public Cloud* hanya meneruskan hasil verifikasi terbatas (*valid/tidak valid* atau skor kecocokan).
  2. **Koneksi privat terenkripsi dengan kendali kunci penuh negara:** Lalu lintas antara PaaS (*Public Cloud* region Indonesia) dan IaaS (*Private Cloud*) wajib melewati jalur privat khusus (*dedicated interconnect* / VPN IPsec) dengan *mutual TLS* (mTLS). Seluruh kunci enkripsi dikelola sepenuhnya pada server manajemen kunci / *Hardware Security Module* (HSM) di *Private Cloud* negara (*Hold Your Own Key*) agar penyedia *Public Cloud* tidak dapat membaca *payload*.
  3. **Redaksi otomatis (*data masking*) & isolasi data pada SaaS:** Menerapkan filter redaksi di *API gateway* agar NIK dan atribut sensitif tidak pernah masuk ke *log* aplikasi PaaS. Pada layanan SaaS *helpdesk*/pengaduan, sistem hanya menyimpan nomor tiket ter-tokenisasi (bukan NIK atau lampiran KTP mentah), sementara dokumen identitas yang perlu diverifikasi diarahkan langsung ke penyimpanan terenkripsi di *Private Cloud*.

### 3.2 Risiko 2: *Bottleneck* & Ketidakkonsistenan Sinkronisasi Lintas Segmen Saat Lonjakan Nasional (Pemilu / PPDB)

- **Deskripsi risiko:** Segmen *Public Cloud* (PaaS) dipilih demi *rapid elasticity* saat musim pemilu, pendaftaran sekolah (PPDB), dan lonjakan KYC bank. Namun, elastisitas ini berisiko menjadi *false elasticity* apabila *API gateway* dan portal di *Public Cloud* mampu melakukan *auto-scale* secara drastis, tetapi jalur penghubung (*interconnect*) dan kapasitas baca database induk di *Private Cloud* (IaaS) mengalami kejenuhan (*bottleneck*). Dampaknya, antrean permintaan menumpuk dan verifikasi KYC maupun layanan dukcapil daerah mengalami *timeout*. Selain itu, keberadaan *cache* hasil verifikasi di *Public Cloud* memunculkan risiko *stale data* — misalnya warga baru memperbarui alamat domisili di dukcapil daerah, tetapi portal PPDB masih membaca domisili lama dari *cache* publik.
- **Mitigasi:**
  1. ***Priority queuing* & pemisahan kuota per jenis instansi:** Sistem antrean permintaan dan *API gateway* (PaaS) menerapkan *rate limiting* dan antrean prioritas terpisah sehingga trafik operasional kritis negara (dukcapil daerah, KPU, kepolisian) memiliki kuota terjamin dan tidak terdampak lonjakan trafik komersial (verifikasi KYC bank/fintech) maupun portal pengecekan publik.
  2. ***Read-replica* di zona Private Cloud & *event-driven cache invalidation*:** Beban verifikasi *read-heavy* saat pemilu/PPDB didistribusikan ke *read-replica* database di dalam *Private Cloud* (IaaS). Untuk *cache* hasil verifikasi non-biometrik di *Public Cloud*, terapkan TTL ketat disertai mekanisme invalidasi berbasis *event* setiap kali dukcapil mencatat pembaruan data induk.
  3. **Redundansi jalur *interconnect* & *graceful degradation*:** Menyediakan minimal dua jalur koneksi privat aktif-aktif (*dual-homed*) antar penyedia jaringan berbeda antara *Public Cloud* region Indonesia dan *Private Cloud*, serta *circuit breaker* / antrean virtual (*waiting room*) pada portal publik agar lonjakan trafik warga tidak menjatuhkan layanan verifikasi inti.

### 3.3 Risiko 3: Penyalahgunaan Akses oleh Ribuan Instansi Konsumen (*Credential Abuse* & *Bulk Scraping*)

- **Deskripsi risiko:** Karakteristik *broad network access* membuka layanan verifikasi bagi ribuan instansi (dukcapil kabupaten/kota, kepolisian, hingga ratusan bank/lembaga keuangan). Jika API key atau kredensial milik satu kantor cabang bank atau instansi daerah bocor, pihak tidak berwenang dapat melakukan penyedotan massal (*bulk scraping*) data NIK melalui jalur *API gateway* yang secara teknis sah.
- **Mitigasi:**
  1. **Prinsip *Least Privilege* sesuai mandat lembaga:** Hak akses dibedakan tegas di level otorisasi *Private Cloud*. Bank hanya memperoleh akses *verification-only* (input NIK + nama/swafoto → output cocok/tidak cocok), bukan akses *read* profil lengkap atau *write*. Operasi ubah/tambah data hanya dimiliki dukcapil sesuai wilayah kerjanya.
  2. **Autentikasi berlapis & pembatasan jaringan:** Mewajibkan sertifikat klien (*mTLS*) per instansi, rotasi API key berkala, serta *IP whitelisting* agar kredensial yang bocor tidak dapat dipakai dari luar jaringan instansi resmi.
  3. ***Immutable audit trail* & deteksi anomali di Private Cloud:** Setiap permintaan verifikasi NIK dicatat pada *log audit* yang dikelola di *Private Cloud* (IaaS) — lengkap dengan identitas instansi, waktu, dan NIK tujuan — disertai deteksi anomali otomatis yang memutus akses seketika jika satu akun instansi memicu lonjakan query tidak wajar (mis. ribuan query NIK berurutan di luar jam kerja).

### Ringkasan Risiko & Mitigasi

| No | Risiko Spesifik | Akar Masalah pada Hybrid Cloud + IaaS/PaaS/SaaS | Mitigasi Utama |
|---|---|---|---|
| 1 | Kebocoran NIK & data biometrik (pelanggaran UU PDP) | Data mentah ter-cache/tercatat di *log* PaaS *Public Cloud* atau masuk ke SaaS *helpdesk* | *Zero-PII persistence* di segmen publik, respons *valid/tidak valid*, mTLS + HSM di *Private Cloud*, *auto-masking log*, tokenisasi tiket SaaS |
| 2 | *Bottleneck* *interconnect* & *stale data* saat pemilu/PPDB | PaaS di *Public Cloud* *auto-scale*, tetapi jalur & DB induk IaaS *Private Cloud* jenuh / *cache* tertinggal | *Priority queuing* per kategori instansi, *read-replica* di *Private Cloud*, *event-driven cache invalidation*, *interconnect* redundan |
| 3 | *Bulk scraping* via kredensial instansi konsumen | Ribuan instansi eksternal (bank, kepolisian, daerah) mengakses *API gateway* | *Least privilege* (bank hanya *verification-only*), mTLS + *IP whitelisting*, *immutable audit trail* di *Private Cloud* + deteksi anomali |

---

## 4. Perbandingan dengan Alternatif yang Ditolak

> *TODO (Didit Septa Putra / Anggota 1): Bandingkan Hybrid Cloud dengan 1 alternatif yang ditolak (misalnya Public Cloud murni atau Private Cloud murni) beserta alasan penolakannya.*

---

## 5. Skenario Tandingan

Untuk menguji ketahanan arsitektur **Hybrid Cloud (IaaS Private + PaaS Public region Indonesia + SaaS pendukung)** pada kondisi lapangan nyata di Indonesia, berikut dua skenario tandingan beserta jawabannya.

### 5.1 Skenario Tandingan 1: Instansi Dukcapil Daerah (terutama Daerah 3T) Tidak Memiliki Infrastruktur Private Cloud Sendiri dan Koneksi Internetnya Tidak Stabil

- **Pertanyaan kritis:** *Jika data induk wajib berada di Private Cloud milik negara, bagaimana jika sebagian besar dinas dukcapil kabupaten/kota — khususnya di wilayah 3T — tidak memiliki data center maupun SDM untuk membangun Private Cloud sendiri, sementara konektivitas internetnya sering terputus?*
- **Jawaban & penyesuaian arsitektur:**
  1. ***Private Cloud* dikelola terpusat secara nasional, bukan per daerah:** Segmen *Private Cloud* (IaaS) dibangun dan dioperasikan terpusat oleh pemerintah pusat (misalnya melalui Pusat Data Nasional / Kemendagri dengan beberapa *availability zone* lintas wilayah untuk *disaster recovery*). Dukcapil daerah **tidak perlu** membangun server *private cloud* sendiri; mereka cukup bertindak sebagai klien yang mengakses layanan pusat melalui jaringan tertutup pemerintah (VPN/intranet pemerintah) dan aplikasi web/API. Model terpusat ini sekaligus mencegah celah keamanan akibat ketimpangan standar infrastruktur antar daerah.
  2. **Mekanisme *store-and-forward* terenkripsi untuk wilayah jaringan tidak stabil:** Untuk kantor dukcapil di daerah dengan koneksi intermiten, perangkat perekaman data kependudukan dan biometrik dapat menggunakan antrean lokal sementara yang terenkripsi penuh (*encrypted offline queue*). Saat koneksi ke *Private Cloud* pusat pulih, data otomatis dikirim dan disinkronkan secara atomik, lalu salinan lokal segera dihapus setelah menerima konfirmasi *commit* dari pusat agar data sensitif warga tidak menumpuk di perangkat daerah.

### 5.2 Skenario Tandingan 2: Gangguan Koneksi Lintas Segmen (*Interconnect*) Terjadi Tepat di Hari Puncak Pemilu atau PPDB

- **Pertanyaan kritis:** *Karena Hybrid Cloud mengandalkan jalur penghubung antara segmen Public Cloud (PaaS) dan Private Cloud negara (IaaS), apa yang terjadi apabila jalur penghubung tersebut mengalami gangguan atau latensi ekstrem tepat di hari puncak pengecekan DPT pemilu atau pendaftaran PPDB?*
- **Jawaban & penyesuaian arsitektur:**
  1. **Isolasi jalur akses instansi inti negara:** Instansi pemerintahan kritis (dukcapil daerah, KPU, kepolisian) diarahkan melalui jalur jaringan privat langsung ke *Private Cloud* tanpa melewati segmen *Public Cloud*. Dengan begitu, gangguan pada segmen publik atau *bridge* publik–privat tidak ikut melumpuhkan layanan operasional inti negara.
  2. **Redundansi jalur ganda & degradasi terkendali (*graceful degradation*):** Jalur *interconnect* antara *Public Cloud* region Indonesia dan *Private Cloud* dirancang aktif-aktif menggunakan minimal dua penyedia jaringan berbeda (*multi-carrier*). Jika kapasitas jalur tetap terdegradasi, sistem antrean dan *API gateway* di segmen publik secara otomatis mengaktifkan ruang tunggu virtual (*virtual waiting room*) untuk portal pengecekan publik serta membatasi laju (*throttling*) verifikasi KYC komersial non-darurat, sehingga kapasitas yang tersisa diprioritaskan bagi layanan kependudukan paling kritis tanpa mengorbankan keamanan maupun integritas database induk di *Private Cloud*.
