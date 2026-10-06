# -*- coding: utf-8 -*-
"""Видео для сайта из роликов H3 (first-look-ai-models/video) и смонтированного фильма.
Запуск: %LOCALAPPDATA%\\claude-tools\\rembg-env\\Scripts\\python.exe src/prep_video.py
  assets/video/home-desktop.mp4, home-mobile.mp4 — фон главной: 3 ролика без подписей, мягкие переходы
  assets/video/first-look-film-ru.mp4 / -en.mp4, clip-casting/-travel/-shoot.mp4 — раздел «видео»
  assets/img/video/*.jpg — постеры
"""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FF = Path(r'C:\Users\LEOVO\ffmpeg\ffmpeg-8.1.1-essentials_build\bin')
SRC = Path(r'C:\Users\LEOVO\Desktop\Chat_Figma\first-look-ai-models\video')
DL = Path(r'C:\Users\LEOVO\Downloads\first-look-video')
V = ROOT / 'assets' / 'video'
P = ROOT / 'assets' / 'img' / 'video'
ENC = ['-an', '-c:v', 'libx264', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']
GRADE = 'eq=contrast=1.04:saturation=0.9:gamma=0.98,colorbalance=bs=0.03:bm=0.01'
CLIPS = [('clip-casting', DL / '1-hailuo-trim.mp4'), ('clip-travel', SRC / '2.mp4'), ('clip-shoot', SRC / '3.mp4')]


def ff(*args):
    subprocess.run([str(FF / 'ffmpeg'), '-v', 'error', '-y', *map(str, args)], check=True)


def dur(p):
    return float(subprocess.check_output([str(FF / 'ffprobe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)]))


def poster(src, dst, t=1.0, w=1280):
    ff('-ss', t, '-i', src, '-frames:v', 1, '-vf', f'scale={w}:-2,{GRADE}', '-q:v', 4, dst)


def main():
    V.mkdir(parents=True, exist_ok=True)
    P.mkdir(parents=True, exist_ok=True)
    # отдельные ролики для раздела «видео»
    for name, src in CLIPS:
        ff('-i', src, '-vf', f'scale=1280:-2,fps=24,{GRADE}', *ENC, '-crf', 25, V / f'{name}.mp4')
        poster(src, P / f'{name}.jpg', t=min(3.0, dur(src) - 0.5))
    for lang in ('ru', 'en'):
        src = DL / f'first-look-film-{lang}.mp4'
        ff('-i', src, '-vf', 'scale=1280:-2', *ENC, '-crf', 24, V / f'first-look-film-{lang}.mp4')
        poster(src, P / f'first-look-film-{lang}.jpg', t=19.6)
    # фон главной: ролики подряд, переходы через растворение, без подписей
    d = [dur(s) for _, s in CLIPS]
    xf = 0.8
    chain = []
    for k in range(3):
        chain.append(f'[{k}:v]scale=1920:1080:flags=lanczos,fps=24,setsar=1,format=yuv420p,{GRADE},setpts=PTS-STARTPTS[v{k}]')
    o1 = d[0] - xf
    o2 = o1 + d[1] - xf
    chain.append(f'[v0][v1]xfade=transition=fade:duration={xf}:offset={o1:.3f}[a]')
    chain.append(f'[a][v2]xfade=transition=fadeblack:duration={xf}:offset={o2:.3f}[b]')
    chain.append('[b]split[d][m]')
    chain.append('[m]crop=ih*9/16:ih,scale=720:1280[mob]')
    args = []
    for _, s in CLIPS:
        args += ['-i', s]
    ff(*args, '-filter_complex', ';'.join(chain), '-map', '[d]', *ENC, '-crf', 27, V / 'home-desktop.mp4',
       '-map', '[mob]', *ENC, '-crf', 27, V / 'home-mobile.mp4')
    poster(V / 'home-desktop.mp4', ROOT / 'assets' / 'img' / 'home-poster.jpg', t=1.0, w=1920)
    poster(V / 'home-mobile.mp4', ROOT / 'assets' / 'img' / 'home-poster-mobile.jpg', t=1.0, w=720)
    for f in sorted(V.glob('*.mp4')):
        print(f.name, '%.1f МБ' % (f.stat().st_size / 1e6), '%.1f с' % dur(f))


if __name__ == '__main__':
    main()
