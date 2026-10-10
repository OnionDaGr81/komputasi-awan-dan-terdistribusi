"""
Tugas 3 - Simulasi Pesanan Masuk dengan Multithreading

Skeleton ini sengaja belum lengkap. Isi bagian bertanda TODO.
Jangan mengubah nama fungsi (dipakai untuk pengecekan otomatis oleh asisten).
"""

import threading
import random
import time

NUM_ORDERS = 100        # jumlah pesanan simulasi yang masuk
NUM_WORKERS = 10        # jumlah thread pekerja

# Counter bersama untuk menghitung total pesanan yang berhasil diproses.
# Sengaja rawan race condition jika diakses tanpa proteksi.
processed_count = 0

# TODO 1: Buat objek Lock di sini untuk melindungi `processed_count`.
lock = threading.Lock()


def process_order(order_id: int) -> None:
    """Proses satu pesanan. Dipanggil oleh tiap thread pekerja."""
    global processed_count 

    # Simulasikan kerja nyata (mis. validasi, hitung total harga)
    time.sleep(random.uniform(0.001, 0.01))

    # TODO 2: Tambahkan increment `processed_count` DI SINI.
    with lock:
        curr = processed_count
        time.sleep(0.0001)
        processed_count = curr + 1
    pass


def worker(order_ids: list) -> None:
    """Satu thread pekerja memproses sekumpulan order_id."""
    for order_id in order_ids:
        process_order(order_id)


def main() -> None:
    order_ids = list(range(1, NUM_ORDERS + 1))

    # TODO 3: Bagi `order_ids` menjadi NUM_WORKERS bagian dan jalankan via threading [Alif]
    threads = []
    chunk_size = NUM_ORDERS // NUM_WORKERS

    for i in range(NUM_WORKERS):
        # Pembagian sub-list pesanan untuk masing-masing thread pekerja
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size
        sub_orders = order_ids[start_idx:end_idx]

        # Inisialisasi dan jalankan thread
        t = threading.Thread(target=worker, args=(sub_orders,), name=f"Worker-{i+1}")
        threads.append(t)
        t.start()

    # Tunggu semua thread pekerja selesai sebelum lanjut ke agregasi hasil
    for t in threads:
        t.join()

    print(f"Total pesanan diproses: {processed_count} (seharusnya {NUM_ORDERS})")
    if processed_count != NUM_ORDERS:
        print("RACE CONDITION TERDETEKSI - lengkapi TODO 1 & TODO 2 dengan Lock!")
    else:
        print("SEMUA PESANAN BERHASIL DIPROSES SECARA KONSISTEN (LOCK BEKERJA SEMPURNA)!")


if __name__ == "__main__":
    main()