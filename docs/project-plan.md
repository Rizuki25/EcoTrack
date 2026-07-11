# Rencana Implementasi

## Fase 1 — Baseline ML

- [ ] Dataset ditempatkan di `ml/data/raw/garbage-detection/`.
- [ ] `ml/data.yaml` disesuaikan dengan dataset asli.
- [ ] Struktur gambar, label, dan ID kelas tervalidasi.
- [ ] Distribusi enam kelas pada train/validation/test diseimbangkan ulang.
- [ ] Baseline YOLO dilatih.
- [ ] Precision, recall, mAP50, dan mAP50-95 dicatat.
- [ ] Prediksi test set dan foto lokal diperiksa secara visual.

## Fase 2 — Perbaikan model

- [ ] Analisis confusion matrix dan kelas yang paling sering salah.
- [ ] Bandingkan baseline dengan augmentasi mosaic/copy-paste.
- [ ] Simpan konfigurasi serta bobot model terbaik.
- [ ] Tetapkan confidence threshold untuk aplikasi.

## Fase 3 — Backend dan QR

- [ ] Autentikasi berbasis peran.
- [ ] QR pengguna dan validasi token.
- [ ] Endpoint prediksi YOLO.
- [ ] Transaksi setoran, detail item, berat, dan poin.
- [ ] Audit log untuk koreksi dan pembatalan.

## Fase 4 — Mobile dan dashboard

- [ ] Aplikasi pengguna: QR, saldo, riwayat, dan reward.
- [ ] Aplikasi petugas: scan QR, kamera, konfirmasi, dan input berat.
- [ ] Dashboard admin: kategori, tarif, transaksi, dan laporan.

## Fase 5 — IoT opsional

- [ ] ESP32 dan load cell untuk berat otomatis.
- [ ] Sensor kapasitas tempat sampah.
- [ ] Servo pemilah jika desain mekanik memungkinkan.
