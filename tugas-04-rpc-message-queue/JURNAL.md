# Jurnal Proses — Tugas 4

## Jalur yang dipilih
**Keduanya**
 
Alasan: komunikasi modul Pesanan ke modul Pembayaran (cek_saldo, proses_pembayaran) memakai RPC karena Pesanan tidak bisa melanjutkan tanpa jawaban saat itu juga, sedangkan notifikasi pembayaran_berhasil dari modul Pembayaran ke modul Kurir/Notifikasi memakai Message Queue karena Pembayaran tidak butuh balasan dan harus tetap responsif walau penerimanya sibuk atau mati.

## Pembagian Kerja
 
| Nama | NIM | Yang dikerjakan |
|---|---|---|
| Duarte Sebastian Napitupulu | 103072400152 | consumer.py, client.py, server.py, dokumentasi bukti, analisis jurnal & readme |
| Chaesar Pratama | 103072400119 | publisher.py & Dokumentasi bukti |
| Didit Septa Putra | 103072400071 | Pengujian dan bukti |
| Alif Rifqi Pratama | 103072400133 |  Analisis tambahan, pengujian dan merapikan laporan |

## Catatan Percobaan
 
### Jalur B — skenario normal (10 Oktober 2026, ± 11.26–11.33 WIB)
 
- `publisher.py` dijalankan tanpa consumer: tiga event terkirim, dashboard menunjukkan **Ready: 3** (`bukti/01_dashboard_queue_ready.png`, `bukti/02_terminal_publisher.png`).
- Publisher dan consumer dijalankan berdampingan: tiga event langsung muncul di terminal consumer (`bukti/03_dual_terminal_publisher_consumer.png`).
### Jalur B — skenario consumer mati (10 Oktober 2026, ± 19.08 WIB)
 
1. `consumer.py` dihentikan.
2. `publisher.py` dijalankan dua kali (19:08:05–19:08:12), total 6 event. Keduanya selesai normal (`bukti/no3-01-publisher-consumer-mati.png`).
3. Dashboard: **Ready: 6**, Consumers: 0, Persistent: 6, 418 B (`bukti/no3-02-dashboard-ready6-consumer0.png`).
4. `consumer.py` dinyalakan lagi dan langsung memproses keenam pesan sesuai urutan kirim (`bukti/no3-03-consumer-memproses-6-pesan.png`).
5. Dashboard: **Ready: 0**, Consumers: 1; grafik antrean turun dari 6 ke 0 sekitar 19:09:05 (`bukti/no3-04-dashboard-ready0-consumer1.png`).
### Jalur B — pesan tidak valid (9 Oktober 2026, ± 23.35 WIB)
 
Dari dashboard kami publish `Halo ini bukan json` dan `123`. Consumer mencetak `[!] Pesan tidak valid, dibuang` untuk keduanya dan tetap hidup, lalu memproses pesan valid `{"user_id": "user9", "jumlah": 5000}` (`bukti/Consumer_py_work.png`).
 
### Jalur A — RPC (ISI_TANGGAL, ± ISI_JAM WIB)
 
1. **Normal.** `server.py` dan `client.py` dijalankan berdampingan. Client menunggu ± ISI detik untuk tiap panggilan, lalu menerima saldo 50000 dan hasil pembayaran `sukses` dengan saldo akhir 30000 (`bukti/rpc-01-client-menunggu.png`).
2. **Server mati sebelum dipanggil.** `client.py` dijalankan tanpa server: gagal setelah ISI detik dengan `ISI_NAMA_ERROR` (`bukti/rpc-02-server-mati.png`).
3. **Server mati di tengah proses.** Server dijalankan dengan jeda 10 detik, dimatikan dengan menutup terminalnya (*Kill Terminal*) saat client sedang menunggu `cek_saldo`: client gagal setelah ISI detik dengan `ISI_NAMA_ERROR` (`bukti/rpc-03-server-mati-di-tengah.png`).
## Pertanyaan Wajib (Jalur B): ke mana pesan "hilang sementara" tersimpan saat consumer mati?
 
Pesan tidak hilang dan tidak berada di publisher maupun consumer. Pesan tersimpan **di dalam broker RabbitMQ** (container Docker `mq-rabbitmq-1`), pada queue `pembayaran_berhasil`, dalam status **Ready** — artinya sudah diterima broker dan belum diserahkan ke consumer mana pun.
 
Buktinya dari percobaan kami sendiri:
 
- **Publisher sudah tidak hidup.** Di `no3-01`, kedua eksekusi `publisher.py` sudah berakhir dan prompt terminal sudah kembali. Jadi keenam pesan tidak mungkin "ditahan" oleh publisher.
- **Consumer belum hidup.** Dashboard di `no3-02` menunjukkan Consumers: 0, tetapi Ready: 6. Satu-satunya proses yang masih memegang pesan adalah broker.
- **Yang tersimpan memang pesan kami.** Kolom *Message body bytes* menunjukkan 418 B. Kami hitung ukuran JSON keenam pesan dari timestamp di terminal publisher: 70 + 70 + 70 + 69 + 70 + 69 = 418 byte. Cocok.
- **Tersimpan di disk, bukan hanya di memori.** Kolom *Persistent* menunjukkan 6 dan queue bertanda `durable: true`. Ini akibat langsung dari dua baris di kode kami: `queue_declare(..., durable=True)` dan `delivery_mode=Persistent` saat publish. `TODO3_Publisher.png` juga memperlihatkan `delivery_mode: 2` pada pesan yang kami ambil dari antrean.
- **Pesan baru dihapus setelah di-ack.** Di `no3-04`, Ready baru turun ke 0 bersamaan dengan lonjakan *Consumer ack*. Karena consumer kami memakai `auto_ack=False`, broker menahan pesan sampai `basic_ack` dikirim, bukan sekadar sampai pesan terkirim.
Hal yang awalnya kami kira tetapi ternyata keliru: `durable=True` saja tidak cukup. Opsi itu hanya menyelamatkan *queue*-nya; pesan di dalamnya baru ikut tersimpan ke disk kalau ditandai persistent.
 
Batasan yang kami sadari: `docker-compose.yml` tidak memakai volume, jadi "disk" yang dimaksud adalah penyimpanan milik container. Pesan aman selama container yang sama masih ada, tetapi tidak setelah `docker compose down`. Skenario ini tidak kami uji.
 
## Pertanyaan Wajib (Jalur A): apa yang terjadi pada request RPC jika server mati di tengah proses?
 
Request itu **hilang bersama server**, dan client menerima error tanpa tahu sejauh mana permintaannya sudah dikerjakan.
 
Yang kami amati di percobaan 3 (`bukti/rpc-03-01-server-mati-di-tengah.png`):
 
- **Server sudah menerima request.** Di terminal server muncul log `[server] cek_saldo('user1') diterima, memproses 10.0 detik...`, jadi permintaan sudah sampai dan sedang dikerjakan.
- **Client sedang tertahan.** Terminal client berhenti di baris `Memanggil cek_saldo('user1') ... menunggu respons sinkron` tanpa bisa melakukan hal lain.
- **Saat proses server dimatikan, client ikut gagal.** Client mencetak `[!] GAGAL setelah ISI detik: ISI_NAMA_ERROR`. Tidak ada nilai balik sama sekali, sukses maupun gagal.
- **Tidak ada yang menyimpan request itu.** Ketika `server.py` kami jalankan lagi, request yang terputus tidak dilanjutkan; server mulai dari kosong dan client harus memanggil ulang sendiri. ISI: tulis apa yang kalian lihat saat server dinyalakan lagi.
Perbandingan dengan percobaan 2: ketika server mati *sebelum* dipanggil, client gagal dalam ISI detik dan pasti tidak ada yang diproses. Ketika server mati *di tengah* proses, client sempat menunggu ISI detik lalu gagal, dan dari sisi client kedua kasus berakhir dengan error yang serupa. Padahal keadaannya berbeda: pada kasus kedua, server sudah mulai bekerja.
 
Inilah risiko utama RPC untuk `proses_pembayaran`: bila server mati setelah saldo dipotong tetapi sebelum balasan terkirim, client menerima error padahal uang sudah terpotong. Jika client lalu mencoba ulang, saldo bisa terpotong dua kali. Di kode kami hal ini belum ditangani; penanganannya butuh ID transaksi supaya permintaan ulang bisa dikenali server (idempoten).
 
Bandingkan dengan Jalur B: penerima yang mati tidak membuat pengirim gagal, dan pesan tetap tersimpan di broker sampai penerima hidup lagi.


## Kendala teknis
- Kendala yang muncul pada saat kami ingin menggunakan Docker Dekstop, pada saat melakukan install image Rabbitmq terjadi gangguan sehingga kami tidak dapat menjalankan Docker Dekstop pada Vscode/ tidak dapat saling berkomunikasi.
- AMQPConnectionError karena broker belum jalan

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). 

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 09/10/2026| Chat GPT | "Apa funsgi jalur MQ untuk sistem order food" | AI menjelaskan fungsi jalur MQ adalah supaya modul pembayaran tidak perlu menunggu, pesan lebih terjamin tidak hilang, sistem tetap responsif saat beban tinggi. |
| 10/10/2026 | Gemini | "Jelaskan konsep message persistence, peran durable queue pada RabbitMQ, dan alur implementasi Publisher di Python" | AI menjelaskan perbedaan antrean durable dengan persistent message (`delivery_mode=2`), serta fungsi asynchronous decoupling pada message broker. | Mengimplementasikan kode `publisher.py` secara mandiri, menguji pengiriman 3 pesan event ke RabbitMQ lokal di laptop, dan memvalidasi hasilnya lewat dashboard. |
