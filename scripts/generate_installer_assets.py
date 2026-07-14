from __future__ import annotations

"""Generate deterministic installer artwork from Sova's established logo system."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "installer" / "windows" / "assets"
WEB_PUBLIC = ROOT / "website" / "public"


def font(size: int):
    candidates = [Path("C:/Windows/Fonts/segoeuib.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_mark(image: Image.Image, box: tuple[int, int, int, int]) -> None:
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=max(6, (right - left) // 7), fill="#111315", outline="#34d399", width=max(2, (right - left) // 40))
    label_font = font(max(14, (right - left) // 3))
    draw.text(((left + right) // 2, (top + bottom) // 2), "S", anchor="mm", font=label_font, fill="#f5f6f7")
    radius = max(3, (right - left) // 18)
    draw.ellipse((right - radius * 3, bottom - radius * 3, right - radius, bottom - radius), fill="#f97360")


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    icon = Image.new("RGBA", (256, 256), "#111315")
    draw_mark(icon, (12, 12, 244, 244))
    icon.save(ASSETS / "sova.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)
    icon.save(WEB_PUBLIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    wizard = Image.new("RGB", (164, 314), "#111315")
    draw_mark(wizard, (30, 40, 134, 144))
    draw = ImageDraw.Draw(wizard)
    draw.text((82, 180), "SOVA", anchor="mm", font=font(28), fill="#f5f6f7")
    draw.text((82, 214), "0.1", anchor="mm", font=font(15), fill="#34d399")
    wizard.save(ASSETS / "wizard-image.bmp")

    small = Image.new("RGB", (55, 55), "#111315")
    draw_mark(small, (4, 4, 51, 51))
    small.save(ASSETS / "wizard-small.bmp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
