# Lemmings 3D Texture Tools

Small Python tools for extracting, viewing, editing, and repacking the raw
palette-indexed graphics used by the DOS version of **Lemmings 3D**.

This repository contains tools only. It does **not** contain the game,
installer, palettes, textures, or other copyrighted assets. You must supply
your own legally obtained copy.

## What is supported

- Split each `TEXTURE.xxx` file into editable 64×64 indexed PNG files.
- Generate a contact sheet for every texture set.
- Repack edited PNG files into a `TEXTURE.xxx` file.
- Convert other raw GFX files—including skies, terrain, signs, objects,
  animated objects, traps, walls, seas, and backgrounds—to indexed PNG strips.
- Convert an edited PNG strip back to the game's raw format.
- Preserve exact palette indices when an image remains in indexed (`P`) mode.
- Map RGB edits to the nearest color in `LM3D.PAL` when necessary.

The tools were tested against the DOS CD release. Texture extraction followed
by repacking without edits produces a byte-identical file.

## Requirements

- Python 3.9 or newer
- [Pillow](https://pillow.readthedocs.io/)
- Your own extracted `GFX` directory containing `LM3D.PAL`

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Extract block textures

```bash
python tools/rip_textures.py /path/to/L3D/GFX textures
```

For each `TEXTURE.xxx`, this creates:

```text
textures/
├── TEXTURE.000/
│   ├── 000.png
│   ├── 001.png
│   └── ...
└── TEXTURE.000.sheet.png
```

Each numbered PNG is one 64×64 block-face texture. The number is its index in
the source file and corresponds to references in the game's block data.

## Repack edited block textures

Keep edited files at 64×64 pixels. For safety, write to a new file first:

```bash
python tools/pack_textures.py \
  textures/TEXTURE.000 \
  /path/to/L3D/GFX/LM3D.PAL \
  /path/to/L3D/GFX/TEXTURE.000 \
  output/TEXTURE.000
```

Only numbered PNG files present in the input folder are replaced; all other
texture slots are copied from the original file.

## Extract other raw graphics

```bash
python tools/rip_gfx.py /path/to/L3D/GFX gfx_png
```

The result is one indexed PNG strip per supported source file. Widths are
inferred from the file family; height is calculated from file size.

Repack an edited strip with:

```bash
python tools/pack_gfx.py \
  gfx_png/SKY.000.png \
  /path/to/L3D/GFX/LM3D.PAL \
  output/SKY.000
```

Do not resize strips: these files have no image header, so their dimensions
are implied by the game and file family.

## Editing notes

- The palette contains 256 RGB triplets stored as VGA 6-bit values.
- Indexed PNGs preserve game palette indices exactly. Prefer an editor that
  can retain indexed mode and its palette.
- RGB/RGBA images are quantized to the nearest game-palette color during
  packing. This is convenient, but may not choose the semantic index expected
  by special effects.
- Palette index `0` can act as transparency on faces carrying the relevant
  game flag. Avoid introducing it accidentally.
- Some assets are vertical frame strips. For example, many 64-pixel-wide
  animated files contain consecutive 64×64 frames.
- The RNC-compressed UI files and sprite/font formats are outside the current
  scope of these tools.

## Legal

Lemmings and Lemmings 3D are trademarks/properties of their respective owners.
This is an independent interoperability and modding project and is not
affiliated with or endorsed by them. Do not redistribute original game data.

The source code in this repository is available under the MIT License.
