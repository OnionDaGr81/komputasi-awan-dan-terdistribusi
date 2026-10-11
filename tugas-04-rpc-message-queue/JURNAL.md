# Jurnal Proses — Tugas 4

## Jalur yang dipilih
- [RPC / MQ / keduanya], alasan:

Kami memilih Jalur B (Message Queue) karena skenario notifikasi "pembayaran berhasil" ke modul Kurir bersifat **asinkron*. Modul Pembayaran tidak boleh menunggu balasan dari Kurir. Dengan MQ, jika Kurir sedang sibuk atau mati (down), pesan tetap aman tersimpan di dalam antrean dan tidak hilang. Hal ini sesuai dengan kebutuhan reliabilitas pada studi kasus FoodGo.

## Kendala teknis
- Kendala yang muncul pada saat kami ingin menggunakan Docker Dekstop, pada saat melakukan install image Rabbitmq terjadi gangguan sehingga kami tidak dapat menjalankan Docker Dekstop pada Vscode/ tidak dapat saling berkomunikasi.

## Uji "pesan tidak hilang" (khusus Jalur B)
- Langkah uji: matikan consumer → jalankan publisher → nyalakan consumer
- Hasil yang diamati: 
Berdasarkan pengujian yang telah dilakukan, berikut adalah hasilnya:
  
  1. *Skenario Consumer Mati: Kami mematikan consumer.py terlebih dahulu. Setelah itu, kami menjalankan publisher.py untuk mengirim beberapa pesan. Hasilnya, pesan-pesan tersebut menumpuk di dalam queue pembayaran_berhasil. Hal ini dibuktikan dengan screenshot dashboard RabbitMQ yang menunjukkan status **Ready: 6* (bukti: bukti/ready6-consumer0.png).
  
  2. *Skenario Consumer Dinyalakan*: Setelah pesan menumpuk, kami menyalakan kembali consumer.py. Consumer langsung memproses semua pesan yang ada di antrean satu per satu. Hal ini terlihat di terminal consumer yang menampilkan log penerimaan pesan (bukti: bukti/memproses-6-pesan.png).
  
  3. *Hasil Akhir: Setelah semua pesan diproses, antrean di dashboard RabbitMQ kembali kosong dengan status **Ready: 0* (bukti: bukti/ready0-consumer1.png). Ini membuktikan tidak ada pesan yang hilang dan sistem berhasil menerapkan asynchronous decoupling.

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). 

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 09/10/2026| Chat GPT | "Apa funsgi jalur MQ untuk sistem order food" | AI menjelaskan fungsi jalur MQ adalah supaya modul pembayaran tidak perlu menunggu, pesan lebih terjamin tidak hilang, sistem tetap responsif saat beban tinggi. |
| 10/10/2026 | Gemini | "Jelaskan konsep message persistence, peran durable queue pada RabbitMQ, dan alur implementasi Publisher di Python" | AI menjelaskan perbedaan antrean durable dengan persistent message (`delivery_mode=2`), serta fungsi asynchronous decoupling pada message broker. | Mengimplementasikan kode `publisher.py` secara mandiri, menguji pengiriman 3 pesan event ke RabbitMQ lokal di laptop, dan memvalidasi hasilnya lewat dashboard. |
