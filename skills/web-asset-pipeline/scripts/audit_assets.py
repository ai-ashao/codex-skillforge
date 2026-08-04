#!/usr/bin/env python3
"""Report basic web-asset metadata without modifying any files."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path


RASTER_EXTENSIONS = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
VECTOR_EXTENSIONS = {".svg"}
IGNORED_DIRS = {".git", ".next", "coverage", "dist", "node_modules"}


def png_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) >= 24 and data.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", data[16:24])
    return None


def gif_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) >= 10 and data[:6] in {b"GIF87a", b"GIF89a"}:
        return struct.unpack("<HH", data[6:10])
    return None


def jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    index = 2
    while index + 9 <= len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            break
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if index + 2 > len(data):
            break
        length = struct.unpack(">H", data[index:index + 2])[0]
        if length < 2 or index + length > len(data):
            break
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF} and length >= 7:
            height, width = struct.unpack(">HH", data[index + 3:index + 7])
            return width, height
        index += length
    return None


def webp_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
        return width, height
    if chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
        width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return width, height
    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def svg_dimensions(data: bytes) -> tuple[int, int] | None:
    text = data.decode("utf-8", errors="ignore")[:8192]
    view_box = re.search(r"\bviewBox\s*=\s*['\"]\s*[-+\d.]+\s+[-+\d.]+\s+([-+\d.]+)\s+([-+\d.]+)", text, re.I)
    if view_box:
        return round(float(view_box.group(1))), round(float(view_box.group(2)))
    width = re.search(r"\bwidth\s*=\s*['\"]\s*(\d+(?:\.\d+)?)", text, re.I)
    height = re.search(r"\bheight\s*=\s*['\"]\s*(\d+(?:\.\d+)?)", text, re.I)
    if width and height:
        return round(float(width.group(1))), round(float(height.group(1)))
    return None


def dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    readers = {
        ".png": png_dimensions,
        ".gif": gif_dimensions,
        ".jpeg": jpeg_dimensions,
        ".jpg": jpeg_dimensions,
        ".webp": webp_dimensions,
        ".svg": svg_dimensions,
    }
    reader = readers.get(path.suffix.lower())
    return reader(data) if reader else None


def classify(path: Path, size: int, image_dimensions: tuple[int, int] | None) -> list[str]:
    flags: list[str] = []
    extension = path.suffix.lower()
    if extension in {".png", ".jpg", ".jpeg"} and size > 250_000:
        flags.append("review modern format")
    if size > 1_000_000:
        flags.append("review size")
    if extension == ".gif":
        flags.append("review animation format")
    if extension == ".svg" and size > 100_000:
        flags.append("review SVG payload")
    if image_dimensions and max(image_dimensions) > 2400:
        flags.append("review rendered size")
    if extension == ".avif":
        flags.append("dimensions unavailable")
    return flags


def record(path: Path) -> dict[str, object] | None:
    if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
        return None
    extension = path.suffix.lower()
    if extension not in RASTER_EXTENSIONS | VECTOR_EXTENSIONS:
        return None
    size = path.stat().st_size
    image_dimensions = dimensions(path)
    return {
        "path": str(path),
        "bytes": size,
        "format": extension.lstrip("."),
        "dimensions": f"{image_dimensions[0]}x{image_dimensions[1]}" if image_dimensions else None,
        "review": classify(path, size, image_dimensions),
    }


def scan(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        item = record(path)
        if item:
            records.append(item)
    return records


def markdown(records: list[dict[str, object]]) -> str:
    lines = ["| Asset | Bytes | Format | Dimensions | Review |", "| --- | ---: | --- | --- | --- |"]
    for record in records:
        review = "; ".join(record["review"]) or "—"
        lines.append(f"| `{record['path']}` | {record['bytes']} | {record['format']} | {record['dimensions'] or 'unknown'} | {review} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit image and SVG assets without modifying them.")
    parser.add_argument("paths", nargs="*", type=Path, help="Asset files or directories to scan.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    paths = args.paths or [Path("public"), Path("assets"), Path("images"), Path("src/assets")]
    existing = [path for path in paths if path.exists()]
    if not existing:
        parser.error("none of the requested paths exists")
    records: list[dict[str, object]] = []
    for path in existing:
        if path.is_dir():
            records.extend(scan(path))
        else:
            item = record(path)
            if item:
                records.append(item)
    records = list({record["path"]: record for record in records}.values())
    print(json.dumps(records, indent=2) if args.format == "json" else markdown(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
