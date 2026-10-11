# Tugas 4 (Pekan 4) — Komunikasi Antar Komponen

**Materi terkait:** Remote Procedure Call (RPC), Message-Oriented Middleware (MOM)/Message Queue.

## Studi Kasus

Modul **Pembayaran** dan modul **Pesanan** FoodGo harus berkomunikasi secara reliabel. Untuk beberapa operasi (mis. cek status saldo) respons dibutuhkan **seketika** (sinkron). Untuk operasi lain (mis. kirim notifikasi "pembayaran berhasil" ke modul kurir) sistem **tidak boleh menunggu** — modul pembayaran harus tetap responsif walau modul kurir sedang sibuk/down (asinkron).

## Pilihan Tugas

Kelompok **wajib memilih salah satu jalur** di bawah (boleh mengerjakan keduanya untuk nilai eksplorasi tambahan, tapi minimal satu harus selesai penuh dengan bukti jalan):

### Jalur A — RPC (Sinkron)

Skeleton di folder `rpc/` memakai `xmlrpc` — bagian dari Python standard library, **tidak perlu install apa pun**.

- `rpc/server.py`: mensimulasikan modul Pembayaran, expose fungsi `cek_saldo(user_id)` dan `proses_pembayaran(user_id, jumlah)` lewat RPC.
- `rpc/client.py`: mensimulasikan modul Pesanan yang memanggil fungsi RPC di atas dan menunggu hasilnya.

Jalankan (dua terminal terpisah, di laptop yang sama):
```bash
python3 rpc/server.py      # terminal 1
python3 rpc/client.py      # terminal 2
```

### Jalur B — Message Queue / MOM (Asinkron)

Skeleton di folder `mq/` memakai **RabbitMQ** yang dijalankan **lokal lewat Docker** (image resmi RabbitMQ, gratis, tidak perlu daftar akun apa pun) + library Python `pika`.

```bash
cd mq
docker compose up -d           # jalankan broker RabbitMQ lokal
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 consumer.py            # terminal 1: jalankan dulu consumer (modul kurir)
python3 publisher.py           # terminal 2: kirim event (modul pembayaran)
```

- `mq/publisher.py`: mensimulasikan modul Pembayaran yang mem-publish event `pembayaran_berhasil` tanpa menunggu balasan.
- `mq/consumer.py`: mensimulasikan modul Kurir/Notifikasi yang subscribe dan memproses event tersebut kapan pun siap.

Dashboard manajemen RabbitMQ (untuk lihat antrean secara visual) otomatis aktif di `http://localhost:15672` (login default `guest`/`guest`) — sertakan screenshot dashboard ini sebagai bukti tambahan.

## Tugas Kelompok

1. Lengkapi bagian `# TODO` di jalur yang dipilih.
2. Buktikan program benar-benar berjalan (screenshot 2 terminal berdampingan, atau video).
3. Untuk Jalur B, matikan dulu `consumer.py`, jalankan `publisher.py` beberapa kali, lalu nyalakan `consumer.py` — buktikan pesan **tetap diproses** (tidak hilang) karena antrean menyimpannya. Ini adalah inti pembelajaran *asynchronous decoupling*.
4. Tulis analisis: kenapa jalur ini (RPC atau MQ) cocok untuk skenario yang kalian pilih, dan apa yang terjadi jika dipakai untuk skenario yang salah (mis. RPC dipakai untuk notifikasi kurir → modul pembayaran ikut lambat kalau kurir down).

## TODO pada jalur yang kami pilih

Bagian # TODO pada publisher.py dan consumer.py telah diselesaikan oleh Anggota 1 dan 2. Kode sudah berjalan sesuai fungsinya. 
Berikut adalah # TODO pada publisher.py:
# TODO 1: buat koneksi ke RabbitMQ di localhost (pika.BlockingConnection
    # dengan ConnectionParameters(host="localhost")), lalu buat channel.
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # TODO 2: deklarasikan queue dengan nama QUEUE_NAME (channel.queue_declare),
    # gunakan durable=True supaya pesan tidak hilang walau RabbitMQ restart.
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    for i in range(1, 4):
        pesan = {
            "user_id": f"user{i}",
            "jumlah": 20000 * i,
            "timestamp": time.time(),
        }
        # TODO 3: publish `pesan` (di-encode json) ke QUEUE_NAME memakai
        # channel.basic_publish(...). Cetak log "Event terkirim: ..." setiap publish.
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(pesan),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent  # Pesan disimpan ke disk
            ),
        )
        print(f"[x] Event terkirim: {pesan}")
        time.sleep(1)

    # TODO 4: tutup koneksi (connection.close()) setelah selesai.
    connection.close()
    print("Publisher selesai mengirim event.")

Dan berikut merupakan # TODO pada consumer.py:
# TODO 1: proses pesan
    user_id = pesan.get("user_id")
    jumlah = pesan.get("jumlah")
    print(f"[x] Kurir menerima notifikasi pembayaran untuk {user_id} sejumlah {jumlah}")

    # TODO 2: kirim acknowledgement supaya pesan dihapus dari antrean
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    # TODO 3: koneksi, channel, deklarasi queue yang sama, daftarkan callback
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Ambil 1 pesan dulu, baru ambil berikutnya setelah di-ack
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False,
    )

    print("Menunggu event dari antrean 'pembayaran_berhasil'... (Ctrl+C untuk berhenti)")

    # TODO 4: mulai mendengarkan antrean
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nConsumer dihentikan.")
        channel.stop_consuming()
    finally:
        connection.close()

## Bukti program kami benar-benar berjalan

Bukti program berjalan dapat dilihat pada folder bukti/. Terdapat screenshot terminal publisher.py dan consumer.py yang menunjukkan proses pengiriman dan penerimaan pesan.

## Uji pesan tidak hilang

1. Langkah 1: Matikan consumer.py (simulasi Kurir sedang down).
2. Langkah 2: Jalankan publisher.py beberapa kali.
3. Bukti 1: Buka dashboard RabbitMQ. Terlihat pesan menumpuk di queue pembayaran_berhasil dengan status Ready: 6. (Sertakan nama file screenshot-nya, misal: bukti/dashboard_menumpuk.png).
4. Langkah 3: Nyalakan kembali consumer.py.
5. Bukti 2: Di terminal Consumer, terlihat pesan diproses satu per satu ([x] Kurir menerima notifikasi...). (Sertakan nama file screenshot-nya, misal: bukti/terminal_consumer.png).
6. Kesimpulan: Tidak ada pesan yang hilang. Ini membuktikan asynchronous decoupling berhasil.

## Hasil analisis pada program

A. Mengapa Message Queue (MQ) Cocok?
    Karena MQ bersifat asinkron dan decoupling. Modul Pembayaran tidak perlu menunggu balasan dari Kurir. Kalau Kurir sibuk atau mati, pesan tetap aman di queue. Pembayaran tetap responsif.

B. Apa yang Terjadi Jika Pakai RPC?
    RPC bersifat sinkron (blocking). Jika dipakai untuk notifikasi Kurir, modul Pembayaran akan macet/lambat karena harus menunggu balasan Kurir. Jika Kurir mati, modul Pembayaran ikut error/gagal. Ini melanggar prinsip reliabilitas di studi kasus.

## Struktur Submission

```
tugas-04-rpc-message-queue/
├── README.md      # Analisis: kenapa sinkron/asinkron, hasil uji "pesan tidak hilang"
├── JURNAL.md
├── rpc/            # Jalur A (jika dikerjakan)
├── mq/             # Jalur B (jika dikerjakan)
└── bukti/
```

## Rubrik Penilaian (Tugas 4)

| Komponen | Bobot | Kriteria |
|---|---|---|
| Implementasi berjalan (minimal 1 jalur) | 35% | RPC call sukses dapat balasan, ATAU pesan MQ sukses dikonsumsi |
| Bukti *asynchronous decoupling* (khusus Jalur B) / bukti sinkron blocking (Jalur A) | 25% | Skenario consumer mati lalu nyala lagi (B), atau bukti client menunggu response (A) |
| Analisis pemilihan pola komunikasi | 25% | Justifikasi tepat berdasarkan kebutuhan sinkron vs asinkron di skenario |
| Proses & kontribusi kelompok | 15% | `JURNAL.md`, commit history |

## Batasan Penggunaan AI (Level 2)

Kebijakan **Level 2 (AI Assisted Idea Generation & Structuring)** berlaku — lihat [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Boleh bertanya konsep umum RPC/message queue ke AI; **tidak boleh** meminta AI menuliskan isi `# TODO` di `rpc/server.py`, `rpc/client.py`, `mq/publisher.py`, atau `mq/consumer.py`. Catat pemakaian AI di "Log Penggunaan AI" pada `JURNAL.md`.

- `JURNAL.md` wajib menjelaskan apa yang terjadi pada request RPC jika server mati di tengah proses (Jalur A), atau ke mana pesan "hilang sementara" tersimpan saat consumer mati (Jalur B) — jawaban generik/hafalan istilah tanpa mengaitkan ke hasil percobaan sendiri akan dinilai rendah.
