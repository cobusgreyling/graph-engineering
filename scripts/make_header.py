#!/usr/bin/env python3
"""Generate README + Open Graph header for Graph Engineering."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_README = ROOT / "assets" / "header.png"
OUT_OG = ROOT / "assets" / "social-preview.png"
OUT_JPG = ROOT / "ge1.jpg"  # keep legacy path working

# Open Graph / Twitter recommended
W, H = 1280, 640

BG_TOP = (13, 17, 23)
BG_BOT = (22, 27, 34)
ACCENT = (88, 166, 255)
GREEN = (63, 185, 80)
CYAN = (57, 197, 207)
PURPLE = (188, 140, 255)
MUTED = (139, 148, 158)
FG = (230, 237, 243)
NODE_BG = (33, 38, 45)
BORDER = (48, 54, 61)
END_FILL = (48, 54, 61)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSRounded.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def gradient_bg() -> Image.Image:
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        c = lerp(BG_TOP, BG_BOT, t)
        for x in range(W):
            # soft blue glow top-left, green hint bottom-right
            gx = x / W
            gy = y / H
            r, g, b = c
            r = min(255, int(r + 18 * (1 - gx) * (1 - gy)))
            g = min(255, int(g + 12 * gx * gy + 8 * (1 - gx) * (1 - gy)))
            b = min(255, int(b + 28 * (1 - gx) * (1 - gy) + 10 * gx))
            px[x, y] = (r, g, b)
    return img


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def node_box(draw, cx, cy, label, fill=NODE_BG, outline=BORDER, text_color=FG, w=150, h=52, f=None):
    x0, y0 = cx - w // 2, cy - h // 2
    rounded_rect(draw, (x0, y0, x0 + w, y0 + h), 12, fill, outline, 2)
    f = f or font(20)
    bbox = draw.textbbox((0, 0), label, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2 - 1), label, fill=text_color, font=f)


def circle_node(draw, cx, cy, label, r=28, fill=END_FILL, outline=MUTED, text_color=MUTED, f=None):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=2)
    f = f or font(16)
    bbox = draw.textbbox((0, 0), label, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2 - 1), label, fill=text_color, font=f)


def arrow(draw, x1, y1, x2, y2, color=ACCENT, width=3):
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    # simple arrowhead
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 12
    left = (x2 - size * math.cos(ang - 0.4), y2 - size * math.sin(ang - 0.4))
    right = (x2 - size * math.cos(ang + 0.4), y2 - size * math.sin(ang + 0.4))
    draw.polygon([ (x2, y2), left, right ], fill=color)


def curved_retry(draw, x_from, y_from, x_to, y_to, color=PURPLE):
    # arc-ish polyline under the graph
    mid_y = y_from + 70
    pts = [
        (x_from, y_from),
        (x_from, mid_y),
        (x_to, mid_y),
        (x_to, y_to),
    ]
    draw.line(pts, fill=color, width=3, joint="curve")
    # arrow at end
    arrow(draw, x_to, mid_y + 8, x_to, y_to + 2, color=color, width=3)
    f = font(15)
    label = "retry"
    bbox = draw.textbbox((0, 0), label, font=f)
    tw = bbox[2] - bbox[0]
    mx = (x_from + x_to) / 2
    draw.text((mx - tw / 2, mid_y + 8), label, fill=color, font=f)


def badge(draw, x, y, text, fill, text_color=FG):
    f = font(15)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 14, 8
    w, h = tw + pad_x * 2, th + pad_y * 2
    rounded_rect(draw, (x, y, x + w, y + h), 999, fill, None)
    draw.text((x + pad_x, y + pad_y - 1), text, fill=text_color, font=f)
    return w + 10


def main() -> None:
    img = gradient_bg()
    # subtle grid
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(0, W, 40):
        od.line((x, 0, x, H), fill=(255, 255, 255, 8), width=1)
    for y in range(0, H, 40):
        od.line((0, y, W, y), fill=(255, 255, 255, 8), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Title
    title_f = font(64)
    sub_f = font(26)
    title = "Graph Engineering"
    bbox = draw.textbbox((0, 0), title, font=title_f)
    tw = bbox[2] - bbox[0]
    title_x = (W - tw) / 2
    title_y = 48
    draw.text((title_x, title_y), title, fill=FG, font=title_f)

    sub = "Zero-dependency Python graph runtime for agent loops"
    bbox = draw.textbbox((0, 0), sub, font=sub_f)
    sw = bbox[2] - bbox[0]
    draw.text(((W - sw) / 2, title_y + 78), sub, fill=MUTED, font=sub_f)

    # Graph layout
    cy = 320
    positions = {
        "start": (160, cy),
        "research": (360, cy),
        "write": (560, cy),
        "verify": (780, cy),
        "end": (1020, cy),
    }

    # edges
    arrow(draw, 188, cy, 285, cy, ACCENT)
    arrow(draw, 435, cy, 485, cy, ACCENT)
    arrow(draw, 635, cy, 705, cy, ACCENT)
    arrow(draw, 855, cy, 990, cy, GREEN)
    curved_retry(draw, 780, cy + 28, 560, cy + 28, PURPLE)

    # edge labels
    lf = font(14)
    draw.text((900, cy - 36), "pass", fill=GREEN, font=lf)

    # nodes
    circle_node(draw, *positions["start"], "start", r=26, fill=(30, 40, 55), outline=ACCENT, text_color=ACCENT)
    node_box(draw, *positions["research"], "research", outline=ACCENT)
    node_box(draw, *positions["write"], "write", outline=CYAN)
    node_box(draw, *positions["verify"], "verify", outline=PURPLE)
    circle_node(draw, *positions["end"], "END", r=30, fill=(28, 50, 36), outline=GREEN, text_color=GREEN)

    # badges (measure then center)
    badge_specs = [
        ("0 deps", (28, 50, 36), GREEN),
        ("Mermaid + ASCII", (24, 36, 55), ACCENT),
        ("pip install simple-graph-agents", (40, 32, 55), PURPLE),
        ("MIT", (40, 40, 48), MUTED),
    ]
    bf = font(15)
    widths = []
    for text, _, _ in badge_specs:
        bb = draw.textbbox((0, 0), text, font=bf)
        widths.append((bb[2] - bb[0]) + 28 + 10)  # pad + gap
    total_w = sum(widths) - 10
    bx = (W - total_w) // 2
    by = 520
    for (text, bg, tc), _ in zip(badge_specs, widths):
        bx += badge(draw, bx, by, text, bg, tc)

    # footer hint
    foot = font(14)
    tip = "github.com/cobusgreyling/graph-engineering"
    bbox = draw.textbbox((0, 0), tip, font=foot)
    fw = bbox[2] - bbox[0]
    draw.text(((W - fw) / 2, H - 36), tip, fill=(70, 78, 90), font=foot)

    OUT_README.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_README, "PNG", optimize=True)
    img.save(OUT_OG, "PNG", optimize=True)
    # JPEG legacy for ge1.jpg
    rgb = img.convert("RGB")
    rgb.save(OUT_JPG, "JPEG", quality=90, optimize=True)
    print(f"Wrote {OUT_README} ({OUT_README.stat().st_size/1024:.0f} KB)")
    print(f"Wrote {OUT_OG} ({OUT_OG.stat().st_size/1024:.0f} KB)")
    print(f"Wrote {OUT_JPG} ({OUT_JPG.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
