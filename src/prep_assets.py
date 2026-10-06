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
    ff = str(FF / "ffmpeg")
    enc = ["-an", "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    # Телефон: узкая петля с моделью по центру (Downloads/hero_bg_loop_final.mp4).
    mob = DL / "hero_bg_loop_final.mp4"
    subprocess.run([ff, "-v", "error", "-y", "-i", str(mob), "-vf", "scale=1600:-2", *enc, str(vid / "hero-mobile.mp4")], check=True)
    subprocess.run([ff, "-v", "error", "-y", "-i", str(mob), "-frames:v", "1", "-vf", "scale=1600:-2", "-q:v", "4",
                    str(ROOT / "assets" / "img" / "hero-poster-mobile.jpg")], check=True)
    # Десктоп: широкий подиум со зрителями (Downloads/b_A_cinematic_luxury_f.mp4).
    # С 8,000 с идёт белая заставка Arena AI — берём первые 240 кадров (0–7,967 с)
    # и склеиваем «вперёд + назад», как мобильную петлю, чтобы стык был незаметен.
    wide = DL / "b_A_cinematic_luxury_f.mp4"
    graph = ("[0:v]trim=end_frame=240,setpts=PTS-STARTPTS,scale=1920:-2,split[a][b];"
             "[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1[v]")
    subprocess.run([ff, "-v", "error", "-y", "-i", str(wide), "-filter_complex", graph, "-map", "[v]", *enc,
                    str(vid / "hero-desktop.mp4")], check=True)
    subprocess.run([ff, "-v", "error", "-y", "-i", str(wide), "-frames:v", "1", "-vf", "scale=1920:-2", "-q:v", "4",
                    str(ROOT / "assets" / "img" / "hero-poster.jpg")], check=True)
    old = vid / "hero.mp4"
    if old.exists():
        old.unlink()
    print("ok:", len(SRC), "models")


if __name__ == "__main__":
    main()
