# Workflow EcoTrack

## Alur pengguna dan transaksi

```mermaid
flowchart LR
    A["Pengguna menunjukkan QR"] --> B["Petugas memindai QR"]
    B --> C{"QR valid?"}
    C -->|Tidak| D["Transaksi ditolak"]
    C -->|Ya| E["Petugas memfoto sampah"]
    E --> F["YOLO mendeteksi kategori"]
    F --> G["Petugas mengonfirmasi hasil"]
    G --> H["Petugas memasukkan berat"]
    H --> I["Sistem menghitung poin"]
    I --> J["Transaksi dan saldo tersimpan"]
```

YOLO bertindak sebagai pemberi rekomendasi. Petugas tetap dapat mengoreksi kategori sebelum transaksi disimpan.

## Alur pengembangan

```mermaid
flowchart TD
    A["Dataset publik 6 kategori"] --> B["Validasi dataset"]
    B --> C["Training YOLO baseline"]
    C --> D["Evaluasi test set"]
    D --> E["Uji foto lokal"]
    E --> F{"Model cukup layak?"}
    F -->|Belum| G["Perbaiki data, augmentasi, atau parameter"]
    G --> C
    F -->|Ya| H["Backend transaksi dan QR"]
    H --> I["Aplikasi mobile"]
    I --> J["Dashboard dan reward"]
    J --> K["Integrasi IoT opsional"]
```

## Ruang lingkup MVP

- Login dan peran pengguna, petugas, serta admin.
- QR unik untuk identitas pengguna.
- Deteksi enam kategori sampah menggunakan YOLO.
- Konfirmasi kategori dan input berat oleh petugas.
- Perhitungan poin dan riwayat transaksi.
- Dashboard ringkas untuk admin.

## Enam kategori awal

- Biodegradable
- Cardboard
- Glass
- Metal
- Paper
- Plastic

Urutan ID kelas wajib mengikuti `data.yaml` asli dari dataset.

