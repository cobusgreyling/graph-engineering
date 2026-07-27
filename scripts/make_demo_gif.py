#!/usr/bin/env python3
"""Render a ~20s terminal-style demo GIF for the README (stdlib + Pillow)."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo.gif"

BG = (13, 17, 23)
FG = (230, 237, 243)
MUTED = (139, 148, 158)
GREEN = (63, 185, 80)
BLUE = (88, 166, 255)
RED = (248, 81, 73)
CYAN = (57, 197, 207)
PURPLE = (188, 140, 255)
BAR = (33, 38, 45)
PANEL = (22, 27, 34)
BORDER = (48, 54, 61)

# Compact for GitHub README bandwidth
W, H = 720, 400
PAD_X, PAD_Y = 22, 52
LINE_H = 18
FPS = 8
TOTAL_FRAMES = 20 * FPS  # 160 frames ≈ 20s


def load_font(size: int = 13) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


# (start_frame, kind, text)
EVENTS: list[tuple[int, str, str]] = [
    (0, "title", "Graph Engineering · simple-graph-agents"),
    (6, "dim", "$ pip install simple-graph-agents"),
    (14, "ok", "Successfully installed simple-graph-agents-0.2.0"),
    (22, "dim", "$ python examples/research_write_verify.py"),
    (30, "accent", "=== ASCII ==="),
    (34, "out", "Graph: research_write_verify  entry: research"),
    (40, "out", "  research --> write --> verify"),
    (44, "out", "  verify -[pass]-> END | -[retry]-> write"),
    (52, "accent", "=== Run ==="),
    (56, "cmd", "[0] → research"),
    (62, "ok", "[research] collected 4 notes"),
    (70, "cmd", "[1] → write"),
    (76, "out", "[write] attempt=1, draft_len=270"),
    (84, "cmd", "[2] → verify"),
    (90, "fail", "[verify] FAIL: needs a second pass"),
    (100, "cmd", "[3] → write"),
    (106, "out", "[write] attempt=2, draft_len=394"),
    (114, "cmd", "[4] → verify"),
    (120, "ok", "[verify] PASS"),
    (126, "cmd", "[5] → END"),
    (134, "accent", "=== Trail ==="),
    (138, "ok", "research → write → verify → write → verify → END"),
    (146, "dim", "passed=True  attempts=2  steps=5  0 deps"),
    (152, "out", "flowchart TD  verify -->|retry| write"),
]

KIND_COLOR = {
    "cmd": BLUE,
    "out": FG,
    "ok": GREEN,
    "fail": RED,
    "dim": MUTED,
    "accent": CYAN,
    "title": PURPLE,
}


def visible_lines_at(frame: int) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    for start, kind, text in EVENTS:
        if frame < start:
            break
        typed = min(len(text), max(0, int((frame - start) * 2.8)))
        if typed == 0 and kind != "title":
            continue
        lines.append((kind, text[:typed]))
    return lines


def draw_chrome(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> None:
    draw.rounded_rectangle((8, 8, W - 8, H - 8), radius=12, fill=PANEL, outline=BORDER)
    draw.rounded_rectangle((8, 8, W - 8, 40), radius=12, fill=BAR)
    draw.rectangle((8, 28, W - 8, 40), fill=BAR)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        x = 28 + i * 16
        draw.ellipse((x, 18, x + 10, 28), fill=c)
    draw.text((W // 2 - 90, 16), "zsh · graph-engineering", fill=MUTED, font=font)


def render_frame(frame: int, font: ImageFont.ImageFont, small: ImageFont.ImageFont) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_chrome(draw, small)

    lines = visible_lines_at(frame)
    max_lines = (H - PAD_Y - 20) // LINE_H
    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    y = PAD_Y
    for kind, text in lines:
        draw.text((PAD_X, y), text, fill=KIND_COLOR.get(kind, FG), font=font)
        y += LINE_H

    if lines and (frame // 4) % 2 == 0:
        last = lines[-1][1]
        bbox = draw.textbbox((PAD_X, 0), last, font=font)
        cx = bbox[2] + 1
        cy = PAD_Y + (len(lines) - 1) * LINE_H
        draw.rectangle((cx, cy + 2, cx + 7, cy + LINE_H - 4), fill=FG)

    draw.text((PAD_X, H - 22), "zero deps · Mermaid · MIT", fill=(70, 78, 90), font=small)
    # Adaptive palette keeps GIF small
    return img.quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    font = load_font(13)
    small = load_font(11)
    frames = [render_frame(i, font, small) for i in range(TOTAL_FRAMES)]
    frames.extend([frames[-1]] * FPS)  # 1s hold

    duration_ms = int(1000 / FPS)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT} ({size_kb:.0f} KB, {len(frames)} frames, ~{len(frames)/FPS:.1f}s)")


if __name__ == "__main__":
    main()
