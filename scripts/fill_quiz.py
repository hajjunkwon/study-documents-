#!/usr/bin/env python3
"""Fill the 원소와 화학 결합 quiz blanks on the scanned worksheet."""

import math
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

SRC = Path("/workspace/원소와-화학결합-Quiz-원본.pdf")
OUT_PDF = Path("/workspace/원소와-화학결합-Quiz-정답.pdf")
OUT_DIR = Path("/tmp/filled")
OUT_DIR.mkdir(exist_ok=True)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLUE = (29, 78, 216, 255)
ELEC = (78, 163, 224, 255)
ELEC_EDGE = (43, 123, 185, 255)
NUCLEUS_TEXT = (40, 40, 40, 255)


def font(size):
    return ImageFont.truetype(FONT_PATH, size=size)


def render_pages():
    doc = pymupdf.open(SRC)
    pages = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
        path = OUT_DIR / f"src_{i+1}.png"
        pix.save(str(path))
        pages.append(Image.open(path).convert("RGBA"))
    return pages


def text_center(draw, xy, s, size, fill=BLUE):
    f = font(size)
    x, y = xy
    draw.text((x, y), s, font=f, fill=fill, anchor="mm")


def electrons(draw, cx, cy, radii_counts, r_dot=5.2):
    for r, count in radii_counts:
        for k in range(count):
            ang = math.radians(-90 + k * 360 / count)
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            draw.ellipse(
                (x - r_dot, y - r_dot, x + r_dot, y + r_dot),
                fill=ELEC,
                outline=ELEC_EDGE,
                width=1,
            )


def fill_page1(im):
    d = ImageDraw.Draw(im)
    # Periodic table group x centers
    xs = {
        1: 233,
        2: 350,
        13: 471,
        14: 591,
        15: 712,
        16: 833,
        17: 954,
        18: 1075,
    }
    # period blank y
    y1, y2, y3, y4 = 360, 468, 588, 708
    p1 = {1: "H", 18: "He"}
    p2 = {1: "Li", 2: "Be", 13: "B", 14: "C", 15: "N", 16: "O", 17: "F", 18: "Ne"}
    p3 = {1: "Na", 2: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar"}
    p4 = {1: "K", 2: "Ca"}
    for g, s in p1.items():
        text_center(d, (xs[g], y1), s, 22)
    for g, s in p2.items():
        text_center(d, (xs[g], y2), s, 22)
    for g, s in p3.items():
        text_center(d, (xs[g], y3), s, 22)
    for g, s in p4.items():
        text_center(d, (xs[g], y4), s, 22)

    # names table
    left_x, right_x = 388, 924
    names_left = ["Fe", "Cu", "Br", "Sn", "Ba", "Au", "Pb"]
    names_right = ["Ni", "Zn", "Ag", "I", "Pt", "Hg"]
    y0, h = 801, (1218 - 801) / 7
    for i, s in enumerate(names_left):
        text_center(d, (left_x, y0 + (i + 0.5) * h), s, 24)
    for i, s in enumerate(names_right):
        text_center(d, (right_x, y0 + (i + 0.5) * h), s, 24)

    # molecular formulas
    mol_x = [322, 680, 1037]
    mol_y = [1380, 1440]
    mols = [
        ["H₂O", "CO₂", "C₄H₁₀"],
        ["H₂O₂", "NH₃", "CH₄"],
    ]
    for r, row in enumerate(mols):
        for c, s in enumerate(row):
            text_center(d, (mol_x[c], mol_y[r]), s, 24)
    return im


def fill_page2(im):
    d = ImageDraw.Draw(im)
    cat_x, an_x = 400, 952
    # header 94-153, then 15 equal data rows down to 1047
    h = (1047 - 153) / 15
    bounds = [153 + i * h for i in range(16)]
    cations = [
        "H⁺", "Li⁺", "Na⁺", "K⁺", "Ag⁺", "Be²⁺", "Mg²⁺",
        "Ca²⁺", "Zn²⁺", "Ba²⁺", "Fe²⁺", "Cu²⁺", "Pb²⁺", "Al³⁺", "Fe³⁺",
    ]
    anions = [
        "F⁻", "Cl⁻", "Br⁻", "I⁻", "O²⁻", "S²⁻", None,
        "NH₄⁺", "OH⁻", "NO₃⁻", "CH₃COO⁻", "HCO₃⁻", "MnO₄⁻", "CO₃²⁻", "SO₄²⁻",
    ]
    for i, s in enumerate(cations):
        y = (bounds[i] + bounds[i + 1]) / 2
        size = 22 if "CH₃" not in (anions[i] or "") else 20
        text_center(d, (cat_x, y), s, 22)
        if anions[i]:
            text_center(d, (an_x, y), anions[i], 20 if len(anions[i]) >= 6 else 22)

    # electron diagrams
    atoms = [
        # F: 9+, 2,7
        ((432, 1257), "9+", [(22, 2), (40, 7)]),
        # Na: 11+, 2,8,1
        ((632, 1260), "11+", [(21, 2), (36, 8), (52, 1)]),
        # Mg: 12+, 2,8,2
        ((833, 1260), "12+", [(21, 2), (36, 8), (52, 2)]),
        # Cl: 17+, 2,8,7
        ((1034, 1260), "17+", [(21, 2), (36, 8), (52, 7)]),
    ]
    ions = [
        # F-: 9+, 2,8
        ((432, 1476), "9+", [(22, 2), (40, 8)]),
        # Na+: 11+, 2,8
        ((633, 1476), "11+", [(22, 2), (40, 8)]),
        # Mg2+: 12+, 2,8
        ((834, 1477), "12+", [(22, 2), (40, 8)]),
        # Cl-: 17+, 2,8,8
        ((1035, 1481), "17+", [(21, 2), (36, 8), (52, 8)]),
    ]
    for (cx, cy), label, shells in atoms + ions:
        text_center(d, (cx, cy), label, 15, fill=NUCLEUS_TEXT)
        electrons(d, cx, cy, shells)
    return im


def fill_page3(im):
    d = ImageDraw.Draw(im)
    # acids: H+ col ~384, anion ~507
    # bases: cation ~947, OH ~1072
    acid_rows = [
        (180, "2H⁺", "SO₄²⁻", "Na⁺", "OH⁻"),
        (240, "H⁺", "Cl⁻", "K⁺", "OH⁻"),
        (300, "H⁺", "NO₃⁻", "Ca²⁺", "2OH⁻"),
        (359, "H⁺", "CH₃COO⁻", "NH₄⁺", "OH⁻"),
        (419, "2H⁺", "CO₃²⁻", "Mg²⁺", "2OH⁻"),
    ]
    for y, h, an, cat, oh in acid_rows:
        text_center(d, (384, y), h, 20)
        text_center(d, (507, y), an, 18 if len(an) >= 6 else 20)
        text_center(d, (947, y), cat, 20)
        text_center(d, (1072, y), oh, 20)

    # ionic compounds: 13 equal rows 590-1365
    h = (1365 - 590) / 13
    formulas = [
        ("NaCl", "Na⁺", "Cl⁻"),
        ("KNO₃", "K⁺", "NO₃⁻"),
        ("KMnO₄", "K⁺", "MnO₄⁻"),
        ("AgNO₃", "Ag⁺", "NO₃⁻"),
        ("NH₄NO₃", "NH₄⁺", "NO₃⁻"),
        ("NH₄Cl", "NH₄⁺", "Cl⁻"),
        ("MgO", "Mg²⁺", "O²⁻"),
        ("CaCl₂", "Ca²⁺", "2Cl⁻"),
        ("Ca(NO₃)₂", "Ca²⁺", "2NO₃⁻"),
        ("CaCO₃", "Ca²⁺", "CO₃²⁻"),
        ("CuSO₄", "Cu²⁺", "SO₄²⁻"),
        ("CuCl₂", "Cu²⁺", "2Cl⁻"),
        ("Fe₂O₃", "2Fe³⁺", "3O²⁻"),
    ]
    ion_x = 172
    before_arrow, mid, after = 590, 780, 980
    for i, (form, cat, an) in enumerate(formulas):
        y = 590 + (i + 0.5) * h
        text_center(d, (ion_x, y), form, 20)
        text_center(d, (before_arrow, y), form, 18)
        text_center(d, (mid, y), cat, 20)
        text_center(d, (after, y), an, 20)
    return im


def main():
    p1, p2, p3 = render_pages()
    p1 = fill_page1(p1)
    p2 = fill_page2(p2)
    p3 = fill_page3(p3)
    filled = [p1, p2, p3]
    rgb = []
    for i, im in enumerate(filled, 1):
        path = OUT_DIR / f"filled_{i}.png"
        out = im.convert("RGB")
        out.save(path, quality=95)
        rgb.append(out)
        print("wrote", path, out.size)

    # PDF at ~150 dpi-ish from 2x A4
    rgb[0].save(
        OUT_PDF,
        save_all=True,
        append_images=rgb[1:],
        resolution=150,
    )
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
