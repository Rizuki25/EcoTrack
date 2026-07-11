# EcoTrack

EcoTrack adalah sistem bank sampah digital berbasis QR Code dan YOLO. Petugas memindai QR pengguna, mendeteksi kategori sampah dari foto, memasukkan berat, lalu sistem menghitung poin dan menyimpan transaksi.

## Status proyek

Tahap saat ini: **baseline machine learning**.

Prioritas pengerjaan:

1. Siapkan dataset Garbage Detection — 6 Waste Categories.
2. Validasi struktur dan label dataset.
3. Latih baseline YOLO.
4. Uji model pada foto sampah nyata.
5. Setelah model layak, implementasikan transaksi QR dan backend.
6. Tambahkan aplikasi pengguna, dashboard admin, reward, dan IoT secara bertahap.

## Struktur

```text
ecotrack/
├── docs/               Dokumentasi workflow dan rencana proyek
├── ml/                 Training, evaluasi, dan inferensi YOLO
├── backend/            API, autentikasi, transaksi, dan poin
├── mobile/             Aplikasi pengguna dan petugas
└── admin-dashboard/    Dashboard admin
```

## Mulai dari baseline YOLO

Jika proyek berada di `D:/Kerjaan/EcoTrack` dan folder `GARBAGE CLASSIFICATION` sudah tersedia di root proyek, konfigurasi `ml/data.yaml` sudah langsung menunjuk ke dataset tersebut. Lewati langkah 1–4 dan mulai dari instalasi dependensi.

1. Ekstrak dataset ke `ml/data/raw/garbage-detection/`.
2. Pastikan dataset memiliki `train/images`, `train/labels`, `valid/images`, dan `valid/labels`.
3. Salin `ml/data.example.yaml` menjadi `ml/data.yaml`.
4. Sesuaikan `path` dan urutan `names` berdasarkan `data.yaml` asli dari dataset.
5. Buat virtual environment dan instal dependensi:

   ```powershell
   cd ml
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

6. Periksa dataset:

   ```powershell
   python validate_dataset.py --data data.yaml
   ```

7. Latih baseline:

   ```powershell
   python train.py --data data.yaml --model yolo11n.pt --epochs 50
   ```

8. Uji model terbaik pada foto:

   ```powershell
   python predict.py --weights runs/detect/ecotrack-baseline/weights/best.pt --source data/local-test
   ```

Bobot model pralatih dapat diunduh otomatis oleh Ultralytics pada penggunaan pertama sehingga langkah itu memerlukan internet.

## Kriteria baseline selesai

- Dataset lolos pemeriksaan struktur dan label.
- Training selesai tanpa error dan menghasilkan `best.pt`.
- Metrik validation tersimpan.
- Model dapat melakukan prediksi pada gambar test.
- Beberapa hasil foto lokal ditinjau secara visual.

## Catatan dataset saat ini

Pemeriksaan awal menemukan distribusi kelas antar-split yang sangat tidak seimbang. Kelas `GLASS` tidak muncul pada test set, sedangkan `PAPER` dan `PLASTIC` hanya memiliki sedikit objek pada validation set. Baseline masih dapat dijalankan untuk memastikan pipeline bekerja, tetapi split perlu diseimbangkan ulang sebelum metrik dipakai sebagai hasil evaluasi final.
