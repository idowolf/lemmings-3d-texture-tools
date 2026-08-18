#!/usr/bin/env python3
"""Pack edited PNGs back into a Lemmings 3D TEXTURE.xxx file.

Reads NNN.png files from a directory (as produced by rip_textures.py),
converts each back to raw 64x64 palette indices, and writes them at the
matching 4096-byte offsets of the output file. PNGs that are still in
indexed mode keep their exact indices; RGB(A) PNGs (e.g. after editing in
a tool that flattened the palette) are remapped to the nearest palette
color. Index 0 is transparent on faces flagged transparent in BLK.xxx, so
avoid introducing index 0 unless you mean it.

Usage: pack_textures.py <png_dir> <LM3D.PAL> <original_TEXTURE_file> <output_file>
"""
import os
import sys
from glob import glob

from PIL import Image

TEX_W = TEX_H = 64
TEX_SIZE = TEX_W * TEX_H


def load_palette(pal_path):
    raw = open(pal_path, "rb").read()
    return [(v << 2) | (v >> 4) for v in raw]


def nearest_index(rgb, palette):
    best, best_d = 0, 1 << 30
    for i in range(256):
        pr, pg, pb = palette[i * 3:i * 3 + 3]
        d = (rgb[0] - pr) ** 2 + (rgb[1] - pg) ** 2 + (rgb[2] - pb) ** 2
        if d < best_d:
            best, best_d = i, d
    return best


def to_indices(img, palette, cache):
    if img.mode == "P":
        return img.tobytes()
    img = img.convert("RGB")
    out = bytearray()
    for rgb in img.getdata():
        if rgb not in cache:
            cache[rgb] = nearest_index(rgb, palette)
        out.append(cache[rgb])
    return bytes(out)


def main():
    png_dir, pal_path, original, output = sys.argv[1:5]
    palette = load_palette(pal_path)
    data = bytearray(open(original, "rb").read())
    cache = {}
    for path in sorted(glob(os.path.join(png_dir, "[0-9][0-9][0-9].png"))):
        idx = int(os.path.splitext(os.path.basename(path))[0])
        img = Image.open(path)
        if img.size != (TEX_W, TEX_H):
            sys.exit(f"{path}: must be {TEX_W}x{TEX_H}, got {img.size}")
        data[idx * TEX_SIZE:(idx + 1) * TEX_SIZE] = to_indices(img, palette, cache)
        print(f"packed {idx:03d} <- {path}")
    with open(output, "wb") as f:
        f.write(data)
    print(f"wrote {output} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
