"""
Tugas 5 - Simulasi Node untuk Bully Algorithm

Infrastruktur jaringan (socket server/client) sudah disediakan.
Logika Bully Algorithm (bagian # TODO) harus kalian lengkapi sendiri.

Contoh menjalankan (5 terminal terpisah):
    python3 node.py --id 1 --port 5001 --peers 5002,5003,5004,5005
    python3 node.py --id 2 --port 5002 --peers 5001,5003,5004,5005
    ... dst untuk id 3, 4, 5
"""

import argparse
import socket
import threading
import time

ELECTION_TIMEOUT = 2.0  # detik menunggu balasan OK sebelum menyatakan diri leader

_print_lock = threading.Lock()


def log(node_id: int, text: str):
    """Print dengan timestamp (HH:MM:SS.mmm) dan lock, supaya baris dari banyak
    thread tidak saling menempel dan durasi bisa diukur dari log."""
    now = time.time()
    stamp = time.strftime("%H:%M:%S", time.localtime(now)) + f".{int(now * 1000) % 1000:03d}"
    with _print_lock:
        print(f"{stamp} [Node {node_id}] {text}", flush=True)


class Node:
    def __init__(self, node_id: int, port: int, peers: dict):
        self.node_id = node_id
        self.port = port
        # peers: dict {peer_id: peer_port} untuk semua node LAIN
        self.peers = peers
        self.leader_id = None
        self.lock = threading.Lock()

        # State bersama untuk Bully Algorithm
        self.received_ok = threading.Event()           # ada OK dari node ber-ID lebih tinggi
        self.coordinator_received = threading.Event()  # ada COORDINATOR yang sah
        self.is_electing = False                       # node sedang menjalankan election

    # ---------- Infrastruktur jaringan (SUDAH LENGKAP, jangan diubah) ----------

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", self.port))
        server.listen()
        print(f"[Node {self.node_id}] Listening di port {self.port}")
        while True:
            conn, _ = server.accept()
            threading.Thread(target=self.handle_connection, args=(conn,), daemon=True).start()

    def handle_connection(self, conn: socket.socket):
        with conn:
            data = conn.recv(1024).decode()
            if not data:
                return
            sender_id, msg_type = data.split(":")
            self.on_message(int(sender_id), msg_type)

    def send_message(self, target_port: int, msg_type: str) -> bool:
        """Kirim pesan ke node lain. Return False jika node target tidak merespons (dianggap mati)."""
        try:
            with socket.create_connection(("localhost", target_port), timeout=1.0) as s:
                s.sendall(f"{self.node_id}:{msg_type}".encode())
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False

    # ---------- Logika Bully Algorithm ----------

    def _start_election_async(self):
        # Election dijalankan di thread terpisah agar thread penerima pesan tidak
        # tertahan selama ELECTION_TIMEOUT.
        threading.Thread(target=self.start_election, daemon=True).start()

    def on_message(self, sender_id: int, msg_type: str):
        """Dipanggil setiap kali node ini menerima pesan dari node lain."""
        # TODO 1: tangani ELECTION, OK, COORDINATOR
        if msg_type == "ELECTION":
            log(self.node_id, f"Menerima 'ELECTION' dari Node {sender_id}")
            if self.node_id > sender_id:
                target_port = self.peers.get(sender_id, 5000 + sender_id)
                self.send_message(target_port, "OK")
                log(self.node_id, f"Mengirim 'OK' ke Node {sender_id}")

                with self.lock:
                    i_am_leader = self.leader_id == self.node_id
                if i_am_leader:
                    # Saya sudah leader: cukup beri tahu pengirim, tidak perlu
                    # election ulang (mencegah COORDINATOR dikirim berkali-kali).
                    self.send_message(target_port, "COORDINATOR")
                    log(self.node_id, f"Sudah leader, mengirim ulang 'COORDINATOR' ke Node {sender_id}")
                else:
                    self._start_election_async()

        elif msg_type == "OK":
            self.received_ok.set()
            log(self.node_id, f"Menerima 'OK' dari Node {sender_id}. Ada node lebih tinggi yang aktif.")

        elif msg_type == "COORDINATOR":
            if sender_id < self.node_id:
                # Aturan Bully: node yang lebih tinggi tidak tunduk ke node yang
                # lebih rendah. Tolak, lalu "bully" dengan election sendiri.
                log(self.node_id, f"Menolak 'COORDINATOR' dari Node {sender_id} (ID lebih rendah), memulai election")
                self._start_election_async()
                return
            with self.lock:
                self.leader_id = sender_id
                self.is_electing = False
            self.coordinator_received.set()
            log(self.node_id, f"Menerima 'COORDINATOR' dari Node {sender_id}. Leader terpilih: Node {sender_id}")

        elif msg_type == "PING":
            # Heartbeat dari monitor_leader: koneksi berhasil sudah cukup sebagai
            # tanda hidup. Tidak dicetak agar log tidak dibanjiri PING.
            pass

        else:
            log(self.node_id, f"Pesan tidak dikenal '{msg_type}' dari Node {sender_id}, diabaikan")

    def start_election(self):
        """Dipanggil saat node ini mendeteksi leader tidak ada / tidak merespons."""
        # TODO 2: kirim ELECTION ke peer ber-ID lebih besar, tunggu OK.
        with self.lock:
            if self.is_electing:
                return
            self.is_electing = True
            self.received_ok.clear()
            self.coordinator_received.clear()

        higher_peers = {pid: p for pid, p in self.peers.items() if pid > self.node_id}
        log(self.node_id, f"Memulai election ke node lebih tinggi: {sorted(higher_peers)}")

        for pid, port in sorted(higher_peers.items()):
            sent = self.send_message(port, "ELECTION")
            log(self.node_id, f"Mengirim 'ELECTION' ke Node {pid}: {'terkirim' if sent else 'gagal, node mati'}")

        got_ok = bool(higher_peers) and self.received_ok.wait(timeout=ELECTION_TIMEOUT)

        # Selama menunggu, bisa saja node lebih tinggi sudah mengumumkan diri
        # (COORDINATOR datang tanpa OK, mis. node itu baru menyala). Jangan
        # lanjut menyatakan diri leader kalau leader sah sudah diketahui.
        if self.coordinator_received.is_set():
            return

        if not got_ok:
            log(self.node_id, "Tidak ada 'OK' dari node lebih tinggi, saya jadi leader")
            self.declare_leader()
            return

        log(self.node_id, "Ada 'OK', berhenti mencalonkan diri, menunggu 'COORDINATOR'")
        if self.coordinator_received.wait(timeout=ELECTION_TIMEOUT * 2):
            return  # leader sudah diumumkan, election selesai

        # Node yang membalas OK ikut mati sebelum mengumumkan diri -> ulangi.
        log(self.node_id, "'COORDINATOR' tidak datang, mengulang election")
        with self.lock:
            self.is_electing = False
        self.start_election()

    def declare_leader(self):
        """Node ini menyatakan dirinya leader dan memberi tahu semua node lain."""
        # TODO 3: set leader_id = node_id, broadcast COORDINATOR ke semua peer.
        with self.lock:
            self.leader_id = self.node_id
            self.is_electing = False
        self.coordinator_received.set()
        log(self.node_id, "SAYA LEADER, broadcast 'COORDINATOR' ke semua node")
        for pid, port in sorted(self.peers.items()):
            sent = self.send_message(port, "COORDINATOR")
            log(self.node_id, f"Mengirim 'COORDINATOR' ke Node {pid}: {'terkirim' if sent else 'gagal, node mati'}")

    def monitor_leader(self):
        """Loop periodik: cek apakah leader masih hidup, trigger election jika mati."""
        while True:
            time.sleep(3)
            # TODO 4: ping leader, mulai election jika leader mati.
            with self.lock:
                current_leader = self.leader_id
                electing = self.is_electing

            if current_leader is None or current_leader == self.node_id or electing:
                continue

            target_port = self.peers.get(current_leader)
            leader_alive = target_port is not None and self.send_message(target_port, "PING")
            if leader_alive:
                continue

            with self.lock:
                # Jangan hapus leader baru yang mungkin baru saja diterima.
                if self.leader_id != current_leader:
                    continue
                self.leader_id = None

            log(self.node_id, f"Leader Node {current_leader} tidak merespons (PING gagal). Memulai election baru.")
            self.start_election()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peers", type=str, required=True,
                        help="daftar port peer dipisah koma, mis. 5002,5003,5004,5005")
    args = parser.parse_args()

    # Asumsi konvensi port: id N selalu di port 5000+N (lihat contoh perintah di README).
    peer_ports = [int(p) for p in args.peers.split(",")]
    peers = {port - 5000: port for port in peer_ports}

    node = Node(args.id, args.port, peers)

    threading.Thread(target=node.start_server, daemon=True).start()
    threading.Thread(target=node.monitor_leader, daemon=True).start()

    time.sleep(1)  # beri waktu semua node lain start dulu sebelum election awal
    node.start_election()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()