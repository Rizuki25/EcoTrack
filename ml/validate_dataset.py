"""Pemeriksaan ringan untuk struktur dan label dataset YOLO."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import yaml


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data.yaml")
    return parser.parse_args()


def resolve_split(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def validate_split(images_dir: Path, class_count: int) -> tuple[int, int, Counter[int]]:
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Folder gambar tidak ditemukan: {images_dir}")

    labels_dir = images_dir.parent / "labels"
    if not labels_dir.is_dir():
        raise FileNotFoundError(f"Folder label tidak ditemukan: {labels_dir}")

    images = [p for p in images_dir.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES]
    missing_labels = 0
    class_counts: Counter[int] = Counter()

    for image in images:
        relative = image.relative_to(images_dir).with_suffix(".txt")
        label_file = labels_dir / relative
        if not label_file.is_file():
            missing_labels += 1
            continue

        for line_number, line in enumerate(label_file.read_text(encoding="utf-8").splitlines(), 1):
            fields = line.split()
            if len(fields) != 5:
                raise ValueError(f"Format label salah: {label_file}:{line_number}")
            class_id = int(fields[0])
            if not 0 <= class_id < class_count:
                raise ValueError(f"ID kelas di luar rentang: {label_file}:{line_number}")
            coordinates = [float(value) for value in fields[1:]]
            if any(value < 0 or value > 1 for value in coordinates):
                raise ValueError(f"Koordinat bukan format YOLO normalisasi: {label_file}:{line_number}")
            class_counts[class_id] += 1

    return len(images), missing_labels, class_counts


def main() -> None:
    args = parse_args()
    yaml_path = Path(args.data).resolve()
    if not yaml_path.is_file():
        raise FileNotFoundError(f"File konfigurasi tidak ditemukan: {yaml_path}")

    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    names = config.get("names")
    if isinstance(names, list):
        class_names = names
    elif isinstance(names, dict):
        class_names = [names[key] for key in sorted(names, key=lambda item: int(item))]
    else:
        raise ValueError("Bagian names pada data.yaml tidak valid")

    configured_root = Path(config.get("path", "."))
    root = configured_root if configured_root.is_absolute() else yaml_path.parent / configured_root
    root = root.resolve()

    print(f"Dataset: {root}")
    print(f"Kelas ({len(class_names)}): {', '.join(map(str, class_names))}")

    for split_name in ("train", "val", "test"):
        split_value = config.get(split_name)
        if not split_value:
            if split_name == "test":
                print("test: tidak dikonfigurasi (opsional)")
                continue
            raise ValueError(f"Split wajib belum dikonfigurasi: {split_name}")

        images_dir = resolve_split(root, split_value)
        image_count, missing_count, class_counts = validate_split(images_dir, len(class_names))
        readable_counts = ", ".join(
            f"{class_names[class_id]}={class_counts[class_id]}"
            for class_id in range(len(class_names))
        )
        print(
            f"{split_name}: images={image_count}, missing_labels={missing_count}, "
            f"objects=[{readable_counts}]"
        )


if __name__ == "__main__":
    main()

