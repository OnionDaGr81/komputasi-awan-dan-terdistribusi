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
 
---