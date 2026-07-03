#!/usr/bin/env python3
"""Download copyright-free section images (Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import shutil
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

DOWNLOADS: dict[str, tuple[str, str]] = {
    "promotions.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "appetizers.webp": (PEX.format(id="248444"), "Pexels #248444"),
    "sushi-519-fusion.webp": (PEX.format(id="2092500"), "Pexels #2092500"),
    "sushi-classic-rolls.webp": (PEX.format(id="2092500"), "Pexels #2092500"),
    "sushi-signature-rolls.webp": (PEX.format(id="2092500"), "Pexels #2092500"),
    "sushi-sashimi.webp": (PEX.format(id="2092500"), "Pexels #2092500"),
    "food-vegetarian.webp": (PEX.format(id="1128678"), "Pexels #1128678"),
    "food-burgers-sandwiches.webp": (PEX.format(id="1639565"), "Pexels #1639565"),
    "food-jamaican.webp": (PEX.format(id="2702674"), "Pexels #2702674"),
    "food-soups-salads.webp": (PEX.format(id="539451"), "Pexels #539451"),
    "food-pasta.webp": (PEX.format(id="4518843"), "Pexels #4518843"),
    "food-desserts.webp": (PEX.format(id="291528"), "Pexels #291528"),
    "food-entrees.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "food-kids.webp": (PEX.format(id="1640777"), "Pexels #1640777"),
    "food-sides.webp": (PEX.format(id="410648"), "Pexels #410648"),
    "food-lunch-99.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "classic-cocktails.webp": (PEX.format(id="1267325"), "Pexels #1267325"),
    "beers.webp": (PEX.format(id="1552630"), "Pexels #1552630"),
    "signature-cocktails.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "shots-shooters.webp": (PEX.format(id="696218"), "Pexels #696218"),
    "hot-beverages.webp": (PEX.format(id="302899"), "Pexels #302899"),
    "non-alcoholics.webp": (PEX.format(id="1199957"), "Pexels #1199957"),
    "wine.webp": (PEX.format(id="602750"), "Pexels #602750"),
    "on-the-rocks.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "hero-bar.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "hero-food.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "hero-sushi.webp": (PEX.format(id="2092500"), "Pexels #2092500"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "appetizers": "appetizers.webp",
    "sushi-519-fusion": "sushi-519-fusion.webp",
    "sushi-classic-rolls": "sushi-classic-rolls.webp",
    "sushi-signature-rolls": "sushi-signature-rolls.webp",
    "sushi-sashimi": "sushi-sashimi.webp",
    "food-vegetarian": "food-vegetarian.webp",
    "food-burgers-sandwiches": "food-burgers-sandwiches.webp",
    "food-jamaican": "food-jamaican.webp",
    "food-soups-salads": "food-soups-salads.webp",
    "food-pasta": "food-pasta.webp",
    "food-desserts": "food-desserts.webp",
    "food-entrees": "food-entrees.webp",
    "food-kids": "food-kids.webp",
    "food-sides": "food-sides.webp",
    "food-lunch-99": "food-lunch-99.webp",
    "classic-cocktails": "classic-cocktails.webp",
    "beers": "beers.webp",
    "signature-cocktails": "signature-cocktails.webp",
    "shots-shooters": "shots-shooters.webp",
    "hot-beverages": "hot-beverages.webp",
    "non-alcoholics": "non-alcoholics.webp",
    "wine": "wine.webp",
    "on-the-rocks": "on-the-rocks.webp",
}

FALLBACK = "food-entrees.webp"


def img(name: str) -> str:
    return f"images/{name}"


def download_one(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def ensure_images() -> list[str]:
    credits: list[str] = []
    for filename, (url, credit) in DOWNLOADS.items():
        if download_one(filename, url):
            credits.append(f"- {filename} — {credit}")

    fallback_path = IMAGES_DIR / FALLBACK
    for section, image_file in SECTIONS.items():
        target = IMAGES_DIR / image_file
        if not target.exists() and fallback_path.exists():
            shutil.copy2(fallback_path, target)
            print(f"FALLBACK {image_file} <- {FALLBACK}")

    return credits


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"').strip("'") if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip() or "TTMenus Menu System" in body:
        body = (
            "<p>519 Restaurant &amp; Bar at C3 Centre, San Fernando — sushi, "
            "fusion dining, cocktails, and full bar menu.</p>"
        )
    text = (
        "---\n"
        'title: "519 Restaurant & Bar"\n'
        f"image: {img('hero-bar.webp')}\n"
        "images:\n"
        f"    - image: {img('hero-bar.webp')}\n"
        f"    - image: {img('hero-sushi.webp')}\n"
        f"    - image: {img('hero-food.webp')}\n"
        f"    - image: {img('signature-cocktails.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('hero-bar.webp')}\n"
        f"    - image: {img('hero-sushi.webp')}\n"
        f"    - image: {img('signature-cocktails.webp')}\n"
        f"    - image: {img('hero-food.webp')}\n"
        f"    - image: {img('food-entrees.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    credits = ensure_images()
    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (Pexels License — free to use):\n"
        + "\n".join(dict.fromkeys(credits))
        + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
