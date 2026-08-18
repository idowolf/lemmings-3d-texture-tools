#!/usr/bin/env python3
"""Rip all raw (non-RNC) Lemmings 3D GFX image files to editable indexed PNGs.

Every file is headerless 8bpp palette-indexed pixels; only the width differs
by type (per the community format spec). Height = filesize / width. Each file
is saved as a single PNG strip with the game palette embedded — edit it and
convert back to raw with pack_gfx.py. 64px-wide strips are stacks of 64x64
tiles (objects, animation frames, etc.).

Special case: SKY files of exactly 64000 bytes are 320x200 fullscreen images;
other sizes are 1024-wide panoramas.

Usage: rip_gfx.py <GFX_dir> <output_dir>
"""
import os
import sys
from glob import glob

from PIL import Image

WIDTHS = {
    "TEXTURE": 64,
    "LAND": 128,
    "SKY": 1024,
    "BGRD": 320,
    "SEA": 64,
    "OBJ": 64,
    "ANIMOBJ": 64,
    "SIGNS": 64,
    "TRAPS": 64,
    "WALLS": 64,
}


def load_palette(pal_path):
    raw = open(pal_path, "rb").read()
    return [(v << 2) | (v >> 4) for v in raw]


def main():
    gfx_dir, out_root = sys.argv[1], sys.argv[2]
    palette = load_palette(os.path.join(gfx_dir, "LM3D.PAL"))
    os.makedirs(out_root, exist_ok=True)

    for path in sorted(glob(os.path.join(gfx_dir, "*"))):
        name = os.path.basename(path)
        base = name.split(".")[0].upper()
        ext = name.split(".")[-1]
        if base not in WIDTHS or not ext.isdigit():
            continue
        raw = open(path, "rb").read()
        width = WIDTHS[base]
        if base == "SKY" and len(raw) == 64000:
            width = 320
        if len(raw) % width:
            print(f"  SKIP {name}: size {len(raw)} not divisible by width {width}")
            continue
        height = len(raw) // width
        img = Image.frombytes("P", (width, height), raw)
        img.putpalette(palette)
        img.save(os.path.join(out_root, name + ".png"))
        print(f"  {name}: {width}x{height}")


if __name__ == "__main__":
    main()
