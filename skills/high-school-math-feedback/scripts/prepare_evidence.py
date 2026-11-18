"""Render selected PDF pages or crop an image for local visual review."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


def select_pages(spec, page_count):
    selected = set()
    for part in spec.split(","):
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", part.strip())
        if not match:
            raise ValueError("页码格式应为 1,3-5")
        first, last = int(match[1]), int(match[2] or match[1])
        if not 1 <= first <= last <= page_count:
            raise ValueError("页码超出文件范围")
        selected.update(range(first, last + 1))
    return sorted(selected)


def parse_crop(value):
    try:
        left, top, right, bottom = (float(part) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("裁切格式应为 左,上,右,下") from exc
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise argparse.ArgumentTypeError("裁切坐标须在 0 到 1 之间")
    return left, top, right, bottom


def write_images(image, prefix, rows, cols):
    overview = prefix.with_suffix(".png")
    image.save(overview)
    filenames = [overview.name]
    if rows == cols == 1:
        return filenames
    width, height = image.size
    if rows > height or cols > width:
        raise ValueError("图像尺寸太小，无法按指定行列切分")
    for row in range(rows):
        for col in range(cols):
            # A little overlap preserves symbols near a tile boundary.
            left = max(0, int((col - 0.08) * width / cols))
            top = max(0, int((row - 0.08) * height / rows))
            right = min(width, int((col + 1.08) * width / cols))
            bottom = min(height, int((row + 1.08) * height / rows))
            tile = prefix.with_name(f"{prefix.name}-r{row + 1}c{col + 1}.png")
            image.crop((left, top, right, bottom)).save(tile)
            filenames.append(tile.name)
    return filenames


def read_text_layer(page, target):
    from pypdf.errors import PdfReadError

    try:
        text = page.extract_text() or ""
    except (PdfReadError, UnicodeError, NotImplementedError, ValueError):
        return {"status": "unavailable"}
    safe_text = text.encode("utf-8", errors="replace").decode("utf-8")
    target.write_text(safe_text, encoding="utf-8")
    status = "present" if safe_text.strip() else "empty"
    return {"status": status, "file": target.name, "replaced_invalid_characters": safe_text != text}


def prepare(args):
    from PIL import Image, ImageOps

    source = Path(args.source).resolve(strict=True)
    output = Path(args.out).resolve()
    reader = None
    renderer = None
    if source.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        renderer = args.pdftoppm or shutil.which("pdftoppm")
        if not renderer or not Path(renderer).is_file():
            raise ValueError("缺少 pdftoppm，可使用宿主渲染器或用 --pdftoppm 指定可执行文件")
        reader = PdfReader(source)
    page_count = len(reader.pages) if reader is not None else 1
    selected = select_pages(args.pages, page_count)
    with source.open("rb") as stream:
        source_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    output.mkdir(parents=True, exist_ok=False)
    pages = []
    for number in selected:
        prefix = output / f"page-{number:03}"
        input_image = source
        if reader is not None:
            subprocess.run(
                [str(renderer), "-f", str(number), "-l", str(number), "-r", str(args.dpi),
                 "-singlefile", "-png", str(source), str(prefix)],
                check=True, capture_output=True, timeout=120,
            )
            input_image = prefix.with_suffix(".png")
        with Image.open(input_image) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
        if args.crop:
            left, top, right, bottom = args.crop
            box = (round(left * image.width), round(top * image.height),
                   round(right * image.width), round(bottom * image.height))
            if box[0] == box[2] or box[1] == box[3]:
                raise ValueError("裁切范围小于一个像素")
            image = image.crop(box)
        entry = {"page": number, "images": write_images(image, prefix, args.rows, args.cols)}
        if reader is not None:
            entry["text_layer"] = read_text_layer(
                reader.pages[number - 1], prefix.with_name(f"{prefix.name}-text-layer.txt")
            )
        pages.append(entry)
    manifest = {
        "schema": 1, "status": "prepared_for_visual_review", "source_file": source.name,
        "source_sha256": source_hash, "total_pages": page_count, "selected_pages": selected,
        "crop_normalized": args.crop, "network_used": False, "pages": pages,
    }
    pending = output / "manifest.pending"
    pending.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(output / "manifest.json")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="PDF 或单张图片")
    parser.add_argument("--out", required=True, help="新输出目录")
    parser.add_argument("--pages", default="1", help="页码，格式如 1,3-5")
    parser.add_argument("--dpi", type=int, default=220)
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--cols", type=int, default=1)
    parser.add_argument("--crop", type=parse_crop)
    parser.add_argument("--pdftoppm", help="Poppler pdftoppm 的绝对路径")
    args = parser.parse_args()
    if not 120 <= args.dpi <= 350 or not 1 <= args.rows <= 6 or not 1 <= args.cols <= 3:
        parser.error("dpi 须为 120—350，rows 为 1—6，cols 为 1—3")
    try:
        manifest = prepare(args)
    except ModuleNotFoundError as exc:
        parser.exit(2, f"当前 Python 缺少 {exc.name}，可使用宿主 PDF 或图像工具。\n")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"准备材料失败：{exc}\n")
    print(json.dumps({"status": manifest["status"], "pages": manifest["selected_pages"],
                      "manifest": str(Path(args.out) / "manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
