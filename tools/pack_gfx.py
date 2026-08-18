#!/usr/bin/env python3
"""Convert an edited PNG strip (from rip_gfx.py) back to a raw L3D GFX file.

Indexed-mode PNGs keep their exact palette indices; RGB(A) PNGs are remapped
to the nearest color in LM3D.PAL. The output must match the original file's
size, so don't resize the strip.

Usage: pack_gfx.py <edited.png> <LM3D.PAL> <output_raw_file>
"""
import sys

from PIL import Image


def load_palette(pal_path):
    raw = open(pal_path, "rb").read()
    return [(v << 2) | (v >> 4) for v in raw]


def main():
    png_path, pal_path, output = sys.argv[1:4]
    img = Image.open(png_path)
    if img.mode == "P":
        data = img.tobytes()
    else:
        palette = load_palette(pal_path)
        img = img.convert("RGB")
        cache = {}
        out = bytearray()
        for rgb in img.getdata():
            if rgb not in cache:
                best, best_d = 0, 1 << 30
                for i in range(256):
                    pr, pg, pb = palette[i * 3:i * 3 + 3]
                    d = (rgb[0] - pr) ** 2 + (rgb[1] - pg) ** 2 + (rgb[2] - pb) ** 2
                    if d < best_d:
                        best, best_d = i, d
                cache[rgb] = best
            out.append(cache[rgb])
        data = bytes(out)
    with open(output, "wb") as f:
        f.write(data)
    print(f"wrote {output} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
