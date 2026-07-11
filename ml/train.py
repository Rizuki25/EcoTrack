"""Melatih baseline YOLO untuk enam kategori sampah EcoTrack."""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data.yaml", help="Lokasi data.yaml")
    parser.add_argument("--model", default="yolo11n.pt", help="Bobot/model awal")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default=None, help="Contoh: 0, cpu, atau mps")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--name", default="ecotrack-baseline")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    if not data_path.is_file():
        raise FileNotFoundError(
            f"{data_path} tidak ditemukan. Salin data.example.yaml menjadi "
            "data.yaml dan sesuaikan path serta urutan kelasnya."
        )

    model = YOLO(args.model)
    train_args = {
        "data": str(data_path),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "project": "runs/detect",
        "name": args.name,
        "seed": 42,
        "deterministic": True,
        "plots": True,
    }
    if args.device:
        train_args["device"] = args.device

    model.train(**train_args)


if __name__ == "__main__":
    main()

