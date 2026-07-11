"""Membuat split train/validation/test yang lebih seimbang tanpa mengubah sumber."""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SOURCE_SPLITS = ("train", "valid", "test")
OUTPUT_SPLITS = ("train", "valid", "test")
ROBOFLOW_SUFFIX = re.compile(r"_(?:jpg|jpeg|png)\.rf\.[^.]+$", re.IGNORECASE)


@dataclass(frozen=True)
class Sample:
    image: Path
    label: Path
    classes: frozenset[int]
    group: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Root dataset asli")
    parser.add_argument("--output", required=True, help="Root dataset hasil")
    parser.add_argument("--train", type=float, default=0.70)
    parser.add_argument("--val", type=float, default=0.15)
    parser.add_argument("--test", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--mode",
        choices=("hardlink", "copy"),
        default="hardlink",
        help="Hardlink hemat ruang; copy membuat salinan independen",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def normalized_ratios(args: argparse.Namespace) -> dict[str, float]:
    values = [args.train, args.val, args.test]
    if any(value <= 0 for value in values):
        raise ValueError("Semua rasio harus lebih besar dari nol")
    total = sum(values)
    return dict(zip(OUTPUT_SPLITS, (value / total for value in values)))


def group_key(image: Path) -> str:
    return ROBOFLOW_SUFFIX.sub("", image.stem).lower()


def read_samples(source: Path, class_count: int) -> list[Sample]:
    samples: list[Sample] = []
    seen_images: set[str] = set()

    for split in SOURCE_SPLITS:
        images_dir = source / split / "images"
        labels_dir = source / split / "labels"
        if not images_dir.is_dir() or not labels_dir.is_dir():
            raise FileNotFoundError(f"Split tidak lengkap: {source / split}")

        for image in images_dir.rglob("*"):
            if image.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            fingerprint = image.name.lower()
            if fingerprint in seen_images:
                raise ValueError(f"Nama gambar duplikat ditemukan: {image.name}")
            seen_images.add(fingerprint)

            relative = image.relative_to(images_dir).with_suffix(".txt")
            label = labels_dir / relative
            if not label.is_file():
                raise FileNotFoundError(f"Label tidak ditemukan: {label}")

            classes: set[int] = set()
            for line_number, line in enumerate(label.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                fields = line.split()
                if len(fields) != 5:
                    raise ValueError(f"Format label salah: {label}:{line_number}")
                class_id = int(fields[0])
                if not 0 <= class_id < class_count:
                    raise ValueError(f"ID kelas di luar rentang: {label}:{line_number}")
                classes.add(class_id)

            samples.append(Sample(image, label, frozenset(classes), group_key(image)))

    return samples


def assign_groups(
    samples: list[Sample], ratios: dict[str, float], class_count: int, seed: int
) -> dict[str, list[Sample]]:
    grouped: dict[str, list[Sample]] = defaultdict(list)
    for sample in samples:
        grouped[sample.group].append(sample)

    total_images = len(samples)
    total_class_images: Counter[int] = Counter()
    group_vectors: dict[str, Counter[int]] = {}
    for key, members in grouped.items():
        vector: Counter[int] = Counter()
        for member in members:
            vector.update(member.classes)
        group_vectors[key] = vector
        total_class_images.update(vector)

    rng = random.Random(seed)
    keys = list(grouped)
    rng.shuffle(keys)
    keys.sort(
        key=lambda key: (
            sum(
                group_vectors[key][class_id] / max(total_class_images[class_id], 1)
                for class_id in range(class_count)
            ),
            len(grouped[key]),
        ),
        reverse=True,
    )

    target_images = {split: total_images * ratios[split] for split in OUTPUT_SPLITS}
    target_classes = {
        split: {
            class_id: total_class_images[class_id] * ratios[split]
            for class_id in range(class_count)
        }
        for split in OUTPUT_SPLITS
    }
    current_images = Counter()
    current_classes: dict[str, Counter[int]] = {
        split: Counter() for split in OUTPUT_SPLITS
    }
    assignments: dict[str, list[Sample]] = {split: [] for split in OUTPUT_SPLITS}

    def global_cost(candidate_split: str, key: str) -> float:
        size = len(grouped[key])
        vector = group_vectors[key]
        cost = 0.0
        for split in OUTPUT_SPLITS:
            added_size = size if split == candidate_split else 0
            image_delta = current_images[split] + added_size - target_images[split]
            # Prioritaskan rasio jumlah gambar, lalu seimbangkan kehadiran kelas.
            cost += 5.0 * (image_delta / max(target_images[split], 1.0)) ** 2
            for class_id in range(class_count):
                added_class = vector[class_id] if split == candidate_split else 0
                class_delta = (
                    current_classes[split][class_id]
                    + added_class
                    - target_classes[split][class_id]
                )
                cost += (class_delta / max(target_classes[split][class_id], 1.0)) ** 2
        return cost

    for key in keys:
        chosen = min(OUTPUT_SPLITS, key=lambda split: (global_cost(split, key), split))
        members = grouped[key]
        assignments[chosen].extend(members)
        current_images[chosen] += len(members)
        current_classes[chosen].update(group_vectors[key])

    for split in OUTPUT_SPLITS:
        rng.shuffle(assignments[split])
    return assignments


def summarize(assignments: dict[str, list[Sample]], names: list[str]) -> dict[str, object]:
    result: dict[str, object] = {}
    for split, samples in assignments.items():
        image_presence: Counter[int] = Counter()
        object_counts: Counter[int] = Counter()
        for sample in samples:
            image_presence.update(sample.classes)
            for line in sample.label.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    object_counts[int(line.split()[0])] += 1
        result[split] = {
            "images": len(samples),
            "images_per_class": {
                names[class_id]: image_presence[class_id] for class_id in range(len(names))
            },
            "objects_per_class": {
                names[class_id]: object_counts[class_id] for class_id in range(len(names))
            },
        }
    return result


def materialize(
    assignments: dict[str, list[Sample]], output: Path, mode: str, names: list[str]
) -> None:
    if output.exists():
        raise FileExistsError(
            f"Output sudah ada: {output}. Hapus atau pilih folder output lain secara manual."
        )

    for split in OUTPUT_SPLITS:
        (output / split / "images").mkdir(parents=True)
        (output / split / "labels").mkdir(parents=True)

    for split, samples in assignments.items():
        for sample in samples:
            destination_image = output / split / "images" / sample.image.name
            destination_label = output / split / "labels" / sample.label.name
            if mode == "hardlink":
                try:
                    os.link(sample.image, destination_image)
                    os.link(sample.label, destination_label)
                except OSError:
                    if destination_image.exists():
                        destination_image.unlink()
                    if destination_label.exists():
                        destination_label.unlink()
                    shutil.copy2(sample.image, destination_image)
                    shutil.copy2(sample.label, destination_label)
            else:
                shutil.copy2(sample.image, destination_image)
                shutil.copy2(sample.label, destination_label)

    data = {
        "path": output.as_posix(),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": len(names),
        "names": names,
    }
    (output / "data.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def main() -> None:
    args = parse_args()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    ratios = normalized_ratios(args)

    source_config = yaml.safe_load((source / "data.yaml").read_text(encoding="utf-8"))
    raw_names = source_config.get("names")
    if isinstance(raw_names, list):
        names = [str(name) for name in raw_names]
    elif isinstance(raw_names, dict):
        names = [str(raw_names[key]) for key in sorted(raw_names, key=lambda key: int(key))]
    else:
        raise ValueError("names pada data.yaml sumber tidak valid")

    samples = read_samples(source, len(names))
    assignments = assign_groups(samples, ratios, len(names), args.seed)
    summary = summarize(assignments, names)
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if args.dry_run:
        print("Dry run selesai; belum ada file yang dibuat.")
        return

    materialize(assignments, output, args.mode, names)
    (output / "split-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Dataset seimbang dibuat di: {output}")


if __name__ == "__main__":
    main()
