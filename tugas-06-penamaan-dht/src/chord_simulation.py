"""
Tugas 6 - Simulasi Chord DHT (single-process, tanpa jaringan sungguhan)

Fungsi hashing & struktur data ring sudah disediakan.
Lengkapi TODO untuk lookup(), join(), dan leave().
"""

import hashlib

M_BITS = 8               # ruang identifier 0..255 (disederhanakan dari Chord asli yang pakai 160-bit)
RING_SIZE = 2 ** M_BITS


def hash_id(key: str) -> int:
    """Hash string (ID node atau ID kurir) ke ruang identifier 0..RING_SIZE-1."""
    digest = hashlib.sha1(key.encode()).digest()
    return int.from_bytes(digest, "big") % RING_SIZE

def in_range(k: int, a: int, b: int) -> bool:
    """True kalau k berada di (a, b] pada ring melingkar."""
    if a < b:
        return a < k <= b
    return k > a or k <= b   # rentang melewati batas 255 -> 0

class ChordRing:
    def __init__(self):
        # node_id (hasil hash) -> alamat IP node tersebut
        self.nodes: dict[int, str] = {}
        # key kurir (hasil hash) -> IP kurir yang disimpan node yang bertanggung jawab
        self.data: dict[int, tuple[str, str]] = {}  # hash -> (kurir_id, ip_kurir)

    def join(self, node_name: str, node_ip: str):
        """Tambahkan node baru ke ring. Pindahkan data yang seharusnya
        menjadi tanggung jawab node baru ini dari successor lamanya."""
        node_id = hash_id(node_name)

        # TODO 2: cari successor LAMA dari node_id ini (successor sebelum node
        # baru bergabung, gunakan find_successor() dengan node_id INI dikecualikan
        # dulu dari self.nodes saat mencari).
        # Join pertama: ring masih kosong
        if not self.nodes:
            self.nodes[node_id] = node_ip
            print(f"[Join] Node '{node_name}' (id={node_id}) adalah node pertama, ring dibuat")
            return
        old_succ = self.find_successor(node_id)


        # TODO 1: tambahkan node_id -> node_ip ke self.nodes.
        # Cek tabrakan ID node
        if node_id in self.nodes:
            print(f"[Peringatan] Tabrakan ID node: '{node_name}' (id={node_id}) sudah dipakai. Join dibatalkan.")
            return
        self.nodes[node_id] = node_ip

        # TODO 3: pindahkan semua key di self.data yang seharusnya menjadi
        # tanggung jawab node baru (key dengan hash <= node_id, tapi masih
        # dipegang oleh successor lama) ke bawah tanggung jawab node baru.
        # (Untuk simulasi sederhana, cukup print log siapa mengambil alih apa -
        # tidak perlu benar-benar memindahkan struktur data kompleks.)
       
        others = sorted(i for i in self.nodes if i != node_id)
        preds = [i for i in others if i < node_id]
        pred = preds[-1] if preds else others[-1]

        print(f"[Join] Node '{node_name}' (id={node_id}) bergabung, alamat {node_ip}, "
              f"pred={pred}, successor lama={old_succ}")

        moved = [h for h in self.data if in_range(h, pred, node_id)]
        if not moved:
            print("       Tidak ada key yang berpindah")
        for h in moved:
            print(f"       Key hash={h} ({self.data[h][0]}): Node {old_succ} -> Node {node_id}")

    def leave(self, node_name: str):
        """Keluarkan sebuah node dari ring. Data yang dipegangnya harus
        berpindah ke successor-nya."""
        node_id = hash_id(node_name)

        # TODO 4: hapus node_id dari self.nodes.
        # TODO 5: cari successor BARU untuk tiap key yang tadinya dipegang
        # node ini, pindahkan ke successor tersebut.
        print(f"[TODO] Node '{node_name}' (id={node_id}) keluar dari ring")

    def find_successor(self, key_hash: int) -> int | None:
        """Cari node_id dengan nilai hash TERKECIL yang >= key_hash
        (successor menurut aturan Chord). Jika tidak ada, wrap-around
        ke node dengan hash terkecil di ring (karena ring melingkar)."""
        # TODO 6: implementasikan logika successor di atas menggunakan
        # self.nodes.keys(). Kembalikan node_id (bukan IP).
        if not self.nodes:
            return None

        # Urutkan ID node dari kecil ke besar
        sorted_nodes = sorted(self.nodes.keys())

        # Cari node pertama yang nilainya >= key_hash
        for node_id in sorted_nodes:
            if node_id >= key_hash:
                return node_id

        # Kalau key lebih besar dari semua node, wrap-around ke node terkecil
        return sorted_nodes[0]

    def register_kurir(self, kurir_id: str, ip_kurir: str):
        """Simpan mapping ID Kurir -> IP di node yang bertanggung jawab."""
        key_hash = hash_id(kurir_id)
        # TODO 7: panggil find_successor(key_hash) untuk menentukan node
        # penanggung jawab, lalu simpan (kurir_id, ip_kurir) ke self.data[key_hash].
        target_node = self.find_successor(key_hash)
        if target_node is None:
            print(f"[Register Gagal] Ring masih kosong untuk kurir '{kurir_id}'")
            return

        # Cek tabrakan hash antar-kurir berbeda di ruang 0-255
        if key_hash in self.data and self.data[key_hash][0] != kurir_id:
            old_kurir = self.data[key_hash][0]
            print(f"[Peringatan] Tabrakan hash antara {kurir_id} dan {old_kurir} pada hash {key_hash}")

        # Simpan atau perbarui IP kurir jika berubah
        self.data[key_hash] = (kurir_id, ip_kurir)
        print(f"[Register] Kurir '{kurir_id}' (hash={key_hash}) disimpan di Node {target_node} -> IP: {ip_kurir}")

    def lookup(self, kurir_id: str) -> str | None:
        """Cari alamat IP terkini untuk sebuah ID Kurir."""
        key_hash = hash_id(kurir_id)
        # TODO 8: gunakan find_successor(key_hash) untuk menemukan node
        # penanggung jawab, lalu kembalikan ip_kurir dari self.data jika ada.
        target_node = self.find_successor(key_hash)
        if target_node is None:
            return None

        # Kembalikan IP jika kurir terdaftar, selain itu None
        if key_hash in self.data:
            stored_id, ip_kurir = self.data[key_hash]
            if stored_id == kurir_id:
                return ip_kurir

        return None


def main():
    ring = ChordRing()

    # Skenario awal: 4 node bergabung
    ring.join("node-jakarta-1", "10.0.0.1")
    ring.join("node-jakarta-2", "10.0.0.2")
    ring.join("node-bandung-1", "10.0.0.3")
    ring.join("node-surabaya-1", "10.0.0.4")

    # Daftarkan beberapa kurir
    ring.register_kurir("kurir-001", "192.168.1.10")
    ring.register_kurir("kurir-002", "192.168.1.11")
    ring.register_kurir("kurir-003", "192.168.1.12")
    ring.register_kurir("kurir-012", "192.168.1.13")

    print("\n--- Lookup sebelum perubahan topologi ---")
    print("kurir-001 ->", ring.lookup("kurir-001"))
    print("kurir-002 ->", ring.lookup("kurir-002"))

    print("\n--- Node baru bergabung ---")
    kurir = "kurir-012"
    h = hash_id(kurir)
    print(f"SEBELUM join: {kurir} (hash={h}) -> Node {ring.find_successor(h)}, IP {ring.lookup(kurir)}")
    ring.join("node-medan-1", "10.0.0.5")
    print(f"SESUDAH join: {kurir} (hash={h}) -> Node {ring.find_successor(h)}, IP {ring.lookup(kurir)}")
    print("kurir-001 ->", ring.lookup("kurir-001"))

    print("\n--- Sebuah node keluar ---")
    ring.leave("node-jakarta-1")
    print("kurir-001 ->", ring.lookup("kurir-001"))
    print("kurir-002 ->", ring.lookup("kurir-002"))
    

if __name__ == "__main__":
    main()
