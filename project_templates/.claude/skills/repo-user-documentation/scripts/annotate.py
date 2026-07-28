#!/usr/bin/env python3
"""
annotate.py — apply ITC-teal arrows, boxes, and number labels to screenshots.

Requirements:
    pip install pillow

Spec JSON format:
{
  "annotations": [
    {
      "image": "sv/dashboard/overview--default.png",
      "items": [
        {"type": "box",    "x": 100, "y": 200, "w": 300, "h": 80},
        {"type": "arrow",  "from": [500, 300], "to": [400, 240]},
        {"type": "number", "x": 450, "y": 220, "n": 1},
        {"type": "text",   "x": 200, "y": 180, "text": "Click here"}
      ]
    }
  ]
}

Default color is ITC-teal (#0F766E). Override per-item with "color".
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ITC_TEAL = "#0F766E"
STROKE = 4
FONT_SIZE = 22



def load_font(size: int = FONT_SIZE) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_box(draw: ImageDraw.ImageDraw, item: dict[str, Any], color: str) -> None:
    x, y, w, h = item["x"], item["y"], item["w"], item["h"]
    draw.rectangle([x, y, x + w, y + h], outline=color, width=STROKE)


def draw_arrow(draw: ImageDraw.ImageDraw, item: dict[str, Any], color: str) -> None:
    fx, fy = item["from"]
    tx, ty = item["to"]
    draw.line([(fx, fy), (tx, ty)], fill=color, width=STROKE)
    # Arrowhead
    angle = math.atan2(ty - fy, tx - fx)
    size = 16
    left = (tx - size * math.cos(angle - math.pi / 6), ty - size * math.sin(angle - math.pi / 6))
    right = (tx - size * math.cos(angle + math.pi / 6), ty - size * math.sin(angle + math.pi / 6))
    draw.polygon([(tx, ty), left, right], fill=color)


def draw_number(draw: ImageDraw.ImageDraw, item: dict[str, Any], color: str, font: ImageFont.ImageFont) -> None:
    x, y, n = item["x"], item["y"], item["n"]
    r = 18
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=color)
    text = str(n)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw / 2, y - th / 2 - 2), text, fill="white", font=font)


def draw_text(draw: ImageDraw.ImageDraw, item: dict[str, Any], color: str, font: ImageFont.ImageFont) -> None:
    # White-filled rounded rect behind the text for legibility.
    text = item["text"]
    x, y = item["x"], item["y"]
    bbox = draw.textbbox((x, y), text, font=font)
    pad = 6
    draw.rectangle([bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad], fill="white", outline=color, width=2)
    draw.text((x, y), text, fill=color, font=font)



DISPATCH = {
    "box": draw_box,
    "arrow": draw_arrow,
    "number": draw_number,
    "text": draw_text,
}


def annotate_one(src: Path, dst: Path, items: list[dict[str, Any]]) -> None:
    img = Image.open(src).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font()
    for item in items:
        t = item.get("type")
        color = item.get("color", ITC_TEAL)
        if t in ("number", "text"):
            DISPATCH[t](draw, item, color, font)
        elif t in DISPATCH:
            DISPATCH[t](draw, item, color)
        else:
            print(f"Unknown annotation type: {t!r}", file=sys.stderr)
    composed = Image.alpha_composite(img, overlay).convert("RGB")
    dst.parent.mkdir(parents=True, exist_ok=True)
    composed.save(dst, format="PNG")


def cmd_apply(args) -> int:
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    ok, failed = 0, 0
    for entry in spec.get("annotations", []):
        rel = entry["image"]
        src = input_dir / rel
        dst = output_dir / rel
        if not src.exists():
            print(f"  ✗ missing input: {src}", file=sys.stderr)
            failed += 1
            continue
        try:
            annotate_one(src, dst, entry.get("items", []))
            print(f"  ✓ {rel}")
            ok += 1
        except Exception as e:
            print(f"  ✗ {rel}: {e}", file=sys.stderr)
            failed += 1
    print(f"Done: {ok} ok, {failed} failed")
    return 0 if failed == 0 else 1



def main() -> int:
    p = argparse.ArgumentParser(prog="annotate")
    sub = p.add_subparsers(dest="cmd", required=True)
    ap = sub.add_parser("apply", help="Apply an annotation spec to screenshots.")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    args = p.parse_args()
    if args.cmd == "apply":
        return cmd_apply(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
