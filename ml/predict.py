"""Menjalankan inferensi YOLO pada gambar, folder, video, atau webcam."""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", required=True, help="Lokasi best.pt")
    parser.add_argument("--source", required=True, help="Gambar, folder, video, atau 0")
    parser.add_argument("--conf", type=float, default=0.35)
    parser.add_argument("--imgsz", type=int, default=640)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weights = Path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"Bobot model tidak ditemukan: {weights}")

    source: str | int = 0 if args.source == "0" else args.source
    model = YOLO(str(weights))
    model.predict(
        source=source,
        conf=args.conf,
        imgsz=args.imgsz,
        save=True,
        project="runs/predict",
        name="ecotrack",
    )


if __name__ == "__main__":
    main()

