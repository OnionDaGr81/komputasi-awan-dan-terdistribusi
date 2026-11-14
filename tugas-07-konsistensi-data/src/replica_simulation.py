"""
Tugas 7 (opsional) - Simulasi Replikasi Dua Server (Jakarta & Bandung)

Mensimulasikan delay replikasi dan masalah inconsistent read,
lalu memperbaikinya dengan mekanisme Read-Your-Writes sederhana.
"""

import time
import threading

REPLICATION_DELAY = 2.0  # detik, simulasi lambatnya sinkronisasi antar server
POLL_INTERVAL = 0.1
MAX_WAIT = 5.0

T0 = time.time()


def ts() -> str:
    """[BARU] Timestamp relatif (detik sejak program mulai) supaya delay terlihat."""
    return f"t={time.time() - T0:4.1f}s"

class Replica:
    def __init__(self, name: str):
        self.name = name
        self.saldo: dict[str, float] = {}
        self.last_write_version: dict[str, int] = {}
        self.lock = threading.Lock()

    def write(self, user_id: str, saldo_baru: float, version: int):
        with self.lock:
            # Tolak versi lama: kalau replika sudah punya versi lebih baru
            # (mis. hasil sinkron paksa), pesan replikasi yang telat jangan menimpanya.
            if version <= self.last_write_version.get(user_id, 0):
                print(f"[{ts()}] [{self.name}] Abaikan replikasi versi {version} (sudah punya versi lebih baru/sama)")
                return
            self.saldo[user_id] = saldo_baru
            self.last_write_version[user_id] = version
        print(f"[{ts()}] [{self.name}] WRITE saldo {user_id} = {saldo_baru} (versi {version})")

    def read(self, user_id: str) -> float:
        with self.lock:
            return self.saldo.get(user_id, 0.0)

    def version(self, user_id: str) -> int:
        with self.lock:
            return self.last_write_version.get(user_id, 0)

class ReplicationSystem:
    def __init__(self):
        self.jakarta = Replica("Jakarta")
        self.bandung = Replica("Bandung")
        self.version_counter = 0

    def top_up(self, user_id: str, jumlah: float) -> int:
        """Top-up selalu ditulis dulu ke server Jakarta (mis. server terdekat pelanggan)."""
        self.version_counter += 1
        version = self.version_counter
        saldo_baru = self.jakarta.read(user_id) + jumlah
        self.jakarta.write(user_id, saldo_baru, version)

        # TODO 1: replikasi ke Bandung TERTUNDA (simulasikan dengan
        print(f"[{ts()}] [Jakarta] Kirim replikasi versi {version} ke Bandung (tiba ~{REPLICATION_DELAY} detik lagi)")
        timer = threading.Timer(
            REPLICATION_DELAY,
            self.bandung.write,
            args=(user_id, saldo_baru, version),
        )
        timer.daemon = True  # supaya program tetap bisa selesai walau timer belum jalan
        timer.start()
        return version

    def baca_saldo_naif(self, user_id: str, server: str) -> float:
        """Baca saldo TANPA mekanisme Read-Your-Writes - bisa saja stale."""
        replica = self.jakarta if server == "Jakarta" else self.bandung
        return replica.read(user_id)
    
    def baca_saldo_read_your_writes(self, user_id: str, server: str, versi_minimal: int,
                                    strategi: str = "redirect") -> float:
        """TODO 2: implementasikan Read-Your-Writes -
        jika replika yang dituju versi datanya < versi_minimal (client pernah
        melihat versi lebih baru sebelumnya), tunggu/redirect ke replika yang
        sudah punya versi tersebut (di sini cukup simulasikan dengan polling
        sampai versi replika >= versi_minimal, atau redirect ke Jakarta)."""
        replica = self.jakarta if server == "Jakarta" else self.bandung
        versi_lokal = replica.version(user_id)
 
        # Kasus normal: replika sudah cukup baru -> aman baca lokal
        if versi_lokal >= versi_minimal:
            print(f"[{ts()}] [{replica.name}] Versi lokal {versi_lokal} >= versi_minimal {versi_minimal} -> baca lokal")
            return replica.read(user_id)
 
        print(f"[{ts()}] [{replica.name}] STALE terdeteksi: versi lokal {versi_lokal} < versi_minimal {versi_minimal}")
 
        if strategi == "tunggu":
            batas = time.time() + MAX_WAIT
            while time.time() < batas:
                if replica.version(user_id) >= versi_minimal:
                    print(f"[{ts()}] [{replica.name}] Replikasi tiba (versi {replica.version(user_id)}) -> baca lokal")
                    return replica.read(user_id)
                time.sleep(POLL_INTERVAL)
            print(f"[{ts()}] [{replica.name}] Timeout menunggu replikasi -> fallback redirect ke Jakarta")
 
        # strategi "redirect" (atau fallback dari "tunggu")
        print(f"[{ts()}] [{replica.name}] Redirect pembacaan ke Jakarta")
        return self.jakarta.read(user_id)
    
def pesan_makanan(saldo: float, harga: float) -> str:
    return "BERHASIL" if saldo >= harga else "DITOLAK (saldo kurang)"


def main():
    system = ReplicationSystem()
    user_id = "user1"
    harga = 45000
 
    print("=== Skenario NAIF (tanpa Read-Your-Writes) ===")
    system.top_up(user_id, 50000)
    time.sleep(0.5)  # pelanggan langsung pesan makanan < REPLICATION_DELAY detik kemudian
    saldo = system.baca_saldo_naif(user_id, "Bandung")
    print(f"[{ts()}] Baca saldo dari Bandung (naif): {saldo}")
    print(f"[{ts()}] Pesan makanan Rp{harga:,.0f}: {pesan_makanan(saldo, harga)}")
    print("-> Harusnya 50000, tapi karena delay replikasi, hasilnya 0 (BUG: inconsistent read)")
 
    time.sleep(REPLICATION_DELAY + 0.5)
    print(f"[{ts()}] Setelah replikasi selesai, Bandung (naif): {system.baca_saldo_naif(user_id, 'Bandung')}"
          " -> baru konsisten 'pada akhirnya' (eventual)")
    # TODO 3: panggil baca_saldo_read_your_writes dan tunjukkan hasilnya SELALU benar
    # walau dipanggil segera setelah top_up (< REPLICATION_DELAY detik).
    print("\n=== Skenario dengan Read-Your-Writes (strategi: redirect) ===")
    versi_terakhir = system.top_up(user_id, 20000)   # saldo seharusnya 70000
    print(f"[{ts()}] Client menyimpan token sesi: versi_minimal = {versi_terakhir}")
    time.sleep(0.5)
    print(f"[{ts()}] (cek) Bandung naif saat ini masih: {system.baca_saldo_naif(user_id, 'Bandung')}")
    saldo = system.baca_saldo_read_your_writes(user_id, "Bandung", versi_terakhir, strategi="redirect")
    print(f"[{ts()}] Baca saldo (RYW-redirect): {saldo} -> {'BENAR' if saldo == 70000 else 'SALAH'}")
 
    time.sleep(REPLICATION_DELAY + 0.5)
 
    print("\n=== Skenario dengan Read-Your-Writes (strategi: tunggu/polling) ===")
    versi_terakhir = system.top_up(user_id, 10000)   # saldo seharusnya 80000
    print(f"[{ts()}] Client menyimpan token sesi: versi_minimal = {versi_terakhir}")
    time.sleep(0.5)
    saldo = system.baca_saldo_read_your_writes(user_id, "Bandung", versi_terakhir, strategi="tunggu")
    print(f"[{ts()}] Baca saldo (RYW-tunggu): {saldo} -> {'BENAR' if saldo == 80000 else 'SALAH'}")
 
    print("\nKesimpulan: pembacaan naif bisa stale, sedangkan Read-Your-Writes SELALU"
          " mengembalikan saldo terbaru milik client walau dibaca < REPLICATION_DELAY detik setelah top-up.")


if __name__ == "__main__":
    main()
