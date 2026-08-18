#!/usr/bin/env python3
"""Rip Lemmings 3D texture files to editable indexed PNGs.

TEXTURE.xxx files are headerless 8bpp palette-indexed images: 100 chunks of
4096 bytes, each one a 64x64 block-face texture. LM3D.PAL holds 256 RGB
triplets in VGA 6-bit range (0-63).

Usage: rip_textures.py <GFX_dir> <output_dir>
Outputs per TEXTURE file: one indexed PNG per 64x64 texture, plus a
10x10 contact sheet (8x upscaled) for browsing.
"""
import os
import sys
from glob import glob

from PIL import Image

TEX_W = TEX_H = 64
TEX_SIZE = TEX_W * TEX_H


def load_palette(pal_path):
    raw = open(pal_path, "rb").read()
    assert len(raw) == 768, f"unexpected palette size {len(raw)}"
    # Scale 6-bit VGA (0-63) to 8-bit, replicating high bits like VGA DACs do
    return [(v << 2) | (v >> 4) for v in raw]


def rip_file(path, palette, out_root):
    raw = open(path, "rb").read()
    if len(raw) % TEX_SIZE:
        print(f"  WARNING: {path} size {len(raw)} not a multiple of 4096")
    count = len(raw) // TEX_SIZE
    name = os.path.basename(path)
    out_dir = os.path.join(out_root, name)
    os.makedirs(out_dir, exist_ok=True)

    cols = 10
    rows = (count + cols - 1) // cols
    sheet = Image.new("P", (cols * TEX_W, rows * TEX_H))
    sheet.putpalette(palette)

    for i in range(count):
        img = Image.frombytes("P", (TEX_W, TEX_H), raw[i * TEX_SIZE:(i + 1) * TEX_SIZE])
        img.putpalette(palette)
        img.save(os.path.join(out_dir, f"{i:03d}.png"))
        sheet.paste(img, ((i % cols) * TEX_W, (i // cols) * TEX_H))

    sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
    sheet.convert("RGB").save(os.path.join(out_root, f"{name}.sheet.png"))
    print(f"  {name}: {count} textures")


def main():
    gfx_dir, out_root = sys.argv[1], sys.argv[2]
    palette = load_palette(os.path.join(gfx_dir, "LM3D.PAL"))
    os.makedirs(out_root, exist_ok=True)
    for path in sorted(glob(os.path.join(gfx_dir, "TEXTURE.*"))):
        rip_file(path, palette, out_root)


if __name__ == "__main__":
    main()
