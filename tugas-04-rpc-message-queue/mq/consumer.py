"""
Tugas 4 - Jalur B: Consumer (simulasi modul Kurir/Notifikasi)
Jalankan file ini SEBELUM publisher.py untuk uji normal, atau SESUDAHNYA
untuk membuktikan pesan tetap tersimpan di antrean (asynchronous decoupling).
"""

import pika
import json

QUEUE_NAME = "pembayaran_berhasil"

def callback(ch, method, properties, body):
    try:
        pesan = json.loads(body)
        if not isinstance(pesan, dict):
            raise ValueError("isi pesan bukan JSON object")
    except ValueError as e:  # json.JSONDecodeError & UnicodeDecodeError termasuk ValueError
        print(f"[!] Pesan tidak valid, dibuang: {body!r} ({e})")
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        return

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


if __name__ == "__main__":
    main()