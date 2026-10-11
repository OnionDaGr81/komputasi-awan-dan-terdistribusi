"""
Tugas 4 - Jalur A: RPC Client (simulasi modul Pesanan)
Jalankan server.py di terminal lain terlebih dahulu.
"""

import xmlrpc.client
import time


def main():
    # TODO 1: buat ServerProxy ke http://localhost:8000
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000")

    start = time.time()
    try:
        print("Memanggil cek_saldo('user1') ... menunggu respons sinkron")
        # TODO 2: panggil cek_saldo dan cetak hasil + waktu tunggu
        saldo = proxy.cek_saldo("user1")
        print(f"  -> saldo user1 = {saldo} (menunggu {time.time() - start:.1f} detik)")

        start = time.time()
        print("Memanggil proses_pembayaran('user1', 20000) ...")
        # TODO 3: panggil proses_pembayaran dan cetak hasilnya
        hasil = proxy.proses_pembayaran("user1", 20000)
        print(f"  -> hasil = {hasil} (menunggu {time.time() - start:.1f} detik)")

    except Exception as e:
        # Masuk ke sini kalau panggilan gagal, mis. server mati sebelum dipanggil
        # ATAU mati di tengah proses.
        print(f"  [!] GAGAL setelah menunggu {time.time() - start:.1f} detik")
        print(f"      Error: {type(e).__name__}: {e}")
        print("      Client tidak mendapat balasan apa pun dari server.")


if __name__ == "__main__":
    main()