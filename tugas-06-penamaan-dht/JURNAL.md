# Jurnal Proses — Tugas 6

## Implementasi find_successor
- Kesalahan pertama yang ditemui (mis. lupa wrap-around di ring):
  1. Lupa wrap-around: kalau hash kurir lebih besar dari semua ID node (misal hash 200), fungsi loop sampai habis dan mengembalikan None. Padahal di ring melingkar seharusnya balik ke node pertama.
  2. Urutan dict: dict di Python urutannya sesuai urutan input, bukan angka numerik. Kalau langsung di-loop tanpa disortir, pencarian successor jadi salah.
  3. Operator perbandingan: harus `>=` bukan `>`, supaya kalau hash kurir sama persis dengan ID node, node itu sendiri yang ambil alih.
  4. Ring kosong: waktu awal sebelum ada node yang join, fungsi harus return None supaya join pertama tidak error.

- Cara memperbaikinya:
  1. Tambah `if not self.nodes: return None` di awal fungsi.
  2. Urutkan key node dengan `sorted(self.nodes.keys())`.
  3. Cek dengan kondisi `if node_id >= key_hash: return node_id`.
  4. Tambah `return sorted_nodes[0]` di akhir fungsi untuk menangani wrap-around.

## Skenario join/leave
- Hasil sebelum & sesudah node baru bergabung: ...
- Hasil sebelum & sesudah node keluar: ...

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 22/10/2026 | Gemini | Diskusi logika find_successor Chord, aturan wrap-around, penanganan ring kosong, dan contoh penelusuran manual hash SHA-1 | Penjelasan konsep successor (node terkecil yang >= key), wrap-around ke node pertama, dan contoh hitungan hash mod 256 | Diimplementasikan ke find_successor, register_kurir, dan lookup di chord_simulation.py, serta ditulis ke bagian penelusuran manual README |
