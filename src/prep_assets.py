"""Готовит фото моделей и видео первого экрана для сайта FIRST LOOK.
Запуск: %LOCALAPPDATA%\claude-tools\rembg-env\Scripts\python.exe src/prep_assets.py
"""
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "models"
GEN = Path(r"C:\Users\LEOVO\Desktop\Chat_Figma\first-look-ai-models")
DL = Path(r"C:\Users\LEOVO\Downloads")
FF = Path(r"C:\Users\LEOVO\ffmpeg\ffmpeg-8.1.1-essentials_build\bin")

NEW = ["elena-voss", "noor-delacroix", "priya-anand", "saskia-lund", "amara-solheim", "theo-marchetti",
       "noah-kessler", "dario-esposito", "rasmus-voight", "julien-marceau", "felix-aurelio"]
SRC = {}
for i, slug in enumerate(NEW, 1):
    SRC[slug] = (GEN / f"portraits/portraits-01-11/portrait-{i:02d}.png", GEN / f"fashion/fashion-01-11/fashion-{i:02d}.png")
# В архиве fashion-five файлы 01 и 02 перепутаны: 01 — Talia, 02 — Mika.
FIVE = DL / "first-look-second-photos"
F5 = GEN / "fashion-five/fashion-five-01-05"
SRC["mika-sorensen"] = (FIVE / "01-mika-sorensen.png", F5 / "fashion-02.png")
SRC["talia-renard"] = (FIVE / "02-talia-renard.png", F5 / "fashion-01.png")
SRC["ines-kovac"] = (FIVE / "03-ines-kovac.png", F5 / "fashion-03.png")
SRC["kian-ashford"] = (FIVE / "04-kian-ashford.png", F5 / "fashion-04.png")
SRC["emil-vantongeren"] = (FIVE / "05-emil-vantongeren.png", F5 / "fashion-05.png")


def save(src, dst, w=900, h=1200):
    im = Image.open(src).convert("RGB")
    im = im.resize((w, h), Image.LANCZOS) if im.size != (w, h) else im
    im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, (p, f) in SRC.items():
        save(p, OUT / f"{slug}-portrait.jpg")
        save(f, OUT / f"{slug}-full.jpg")
    vid = ROOT / "assets" / "video"
    vid.mkdir(parents=True, exist_ok=True)
    src = DL / "hero_bg_loop_final.mp4"
    subprocess.run([str(FF / "ffmpeg"), "-v", "error", "-y", "-i", str(src), "-an", "-vf", "scale=1600:-2",
                    "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(vid / "hero.mp4")], check=True)
    subprocess.run([str(FF / "ffmpeg"), "-v", "error", "-y", "-i", str(src), "-frames:v", "1",
                    "-vf", "scale=1600:-2", "-q:v", "4", str(ROOT / "assets" / "img" / "hero-poster.jpg")], check=True)
    print("ok:", len(SRC), "models")


if __name__ == "__main__":
    main()
