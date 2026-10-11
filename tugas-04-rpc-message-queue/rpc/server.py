"""
Tugas 4 - Jalur A: RPC Server (simulasi modul Pembayaran)
Memakai xmlrpc.server dari Python standard library - tidak perlu install apa pun.
"""

import time
from xmlrpc.server import SimpleXMLRPCServer

# Simulasi "database" saldo user
saldo_user = {
    "user1": 50000,
    "user2": 120000,
}

# Server sengaja dibuat "sibuk" 5 detik per panggilan, supaya terlihat
# bahwa client ikut menunggu, dan ada waktu untuk mematikan server di tengah proses.
LAMA_PROSES = 5


def cek_saldo(user_id: str) -> float:
    """Kembalikan saldo user_id saat ini."""
    # TODO 1: kembalikan saldo dari dict `saldo_user`.
    print(f"[server] cek_saldo({user_id}) diterima, memproses {LAMA_PROSES} detik...")
    time.sleep(LAMA_PROSES)

    # Keputusan kami: user tidak dikenal -> error, bukan return 0.
    # (saldo 0 artinya "user ada tapi tidak punya uang", itu hal yang berbeda)
    if user_id not in saldo_user:
        raise ValueError(f"user {user_id} tidak ditemukan")

    print(f"[server] cek_saldo({user_id}) selesai, balasan dikirim")
    return saldo_user[user_id]


def proses_pembayaran(user_id: str, jumlah: float) -> dict:
    """Kurangi saldo user sejumlah `jumlah`. Kembalikan status hasil."""
    # TODO 2: validasi saldo cukup, kurangi saldo, kembalikan status.
    print(f"[server] proses_pembayaran({user_id}, {jumlah}) diterima")

    if user_id not in saldo_user:
        raise ValueError(f"user {user_id} tidak ditemukan")

    if saldo_user[user_id] < jumlah:
        return {"status": "gagal", "saldo_akhir": saldo_user[user_id]}

    saldo_user[user_id] = saldo_user[user_id] - jumlah
    print(f"[server] saldo {user_id} SUDAH DIPOTONG, sisa {saldo_user[user_id]}")

    print(f"[server] menyiapkan balasan {LAMA_PROSES} detik...")
    time.sleep(LAMA_PROSES)

    print("[server] proses_pembayaran selesai, balasan dikirim")
    return {"status": "sukses", "saldo_akhir": saldo_user[user_id]}


def main():
    # TODO 3: buat server di localhost port 8000, daftarkan kedua fungsi, lalu jalankan.
    server = SimpleXMLRPCServer(("localhost", 8000))
    server.register_function(cek_saldo)
    server.register_function(proses_pembayaran)
    print("RPC server modul Pembayaran berjalan di port 8000...")
    server.serve_forever()


if __name__ == "__main__":
    main()