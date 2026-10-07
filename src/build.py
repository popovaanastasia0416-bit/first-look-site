"""Собирает многостраничный сайт FIRST LOOK по структуре models1.co.uk (RU в корне, EN в /en/).
Запуск из корня репозитория: python src/build.py
Прежний генератор лендинга сохранён в src/build_landing_old.py.
"""
import html
import json
import shutil
from pathlib import Path

from content import C, EYES, HAIR
from data import DOC_ORDER, DOCS, MODELS, SERVICE_ORDER, SERVICES, T

ROOT = Path(__file__).resolve().parent.parent
VERSION = "42"  # поднимать при правке css/js
e = html.escape


# ── пути ─────────────────────────────────────────────────────────────────
def up(lang, cur):
    return "../" * (cur.count("/") + (1 if lang == "en" else 0))


def href(lang, cur, slug, anchor=""):
    target = ("index.html" if not slug else f"{slug}.html")
    return up(lang, cur) + ("" if lang == "ru" else "en/") + target + (f"#{anchor}" if anchor else "")


def asset(lang, cur, path):
    return up(lang, cur) + "assets/" + path


def other(lang, cur):
    o = "en" if lang == "ru" else "ru"
    target = "index.html" if cur in ("", "404") else f"{cur}.html"
    return up(lang, cur) + ("" if o == "ru" else "en/") + target


# ── иконки ───────────────────────────────────────────────────────────────
I = {
    "search": '<svg viewBox="0 0 24 24" fill="none"><circle cx="10.5" cy="10.5" r="6.5" stroke="currentColor" stroke-width="1.8"/><path d="m15.5 15.5 5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    "heart": '<svg class="h-full" viewBox="0 0 24 24"><path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2Z" fill="currentColor"/></svg>',
    "heart_o": '<svg class="h-line" viewBox="0 0 24 24" fill="none"><path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2Z" stroke="currentColor" stroke-width="1.5"/></svg>',
    "burger": '<svg viewBox="0 0 28 24" fill="none"><path d="M2 5h24M2 12h24M2 19h24" stroke="currentColor" stroke-width="1.8"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none"><path d="m4 4 16 16M20 4 4 20" stroke="currentColor" stroke-width="1.6"/></svg>',
    "grid": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="2" y="2" width="5" height="5"/><rect x="9.5" y="2" width="5" height="5"/><rect x="17" y="2" width="5" height="5"/><rect x="2" y="9.5" width="5" height="5"/><rect x="9.5" y="9.5" width="5" height="5"/><rect x="17" y="9.5" width="5" height="5"/><rect x="2" y="17" width="5" height="5"/><rect x="9.5" y="17" width="5" height="5"/><rect x="17" y="17" width="5" height="5"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="12" r="4.2" stroke="currentColor" stroke-width="1.6"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/></svg>',
    "tg": '<svg viewBox="0 0 24 24" fill="none"><path d="M21 4 3 11.2l6 2.1M21 4l-3 16-8.8-6.7M21 4 9.2 13.3l.7 5.4 2.8-3.1" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
    "tt": '<svg viewBox="0 0 24 24" fill="none"><path d="M14 3v12a3.5 3.5 0 1 1-3.5-3.5M14 3c.5 2.8 2.3 4.6 5.2 4.8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    "play": '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>',
    "down": '<svg viewBox="0 0 24 24" fill="none"><path d="M12 4v16m-6-6 6 6 6-6" stroke="currentColor" stroke-width="1.4"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="14" stroke="currentColor" stroke-width="1.4"/><path d="m3 6 9 7 9-7" stroke="currentColor" stroke-width="1.4"/></svg>',
}


def nav_href(lang, cur, key):
    return href(lang, cur, key)


# ── каркас ───────────────────────────────────────────────────────────────
def models_js(lang, cur):
    return [{"slug": m[0], "name": m[1].lower(), "sex": m[2], "img": asset(lang, cur, f"img/models/{m[0]}-{cover(m[0])}.jpg"),
             "url": href(lang, cur, "model/" + m[0])} for m in MODELS]


def head(lang, cur, title, desc, cls=""):
    c = C[lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:image" content="{asset(lang, cur, 'img/home-poster.jpg')}">
<meta name="theme-color" content="#000000">
<link rel="icon" href="{asset(lang, cur, 'img/favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset(lang, cur, 'css/site.css')}?v={VERSION}">
</head>
<body class="{cls}">
<a class="skip" href="#main">{e(c['skip'])}</a>
"""


def lang_switch(lang, cur):
    o = other(lang, cur)
    ru = '<span class="on">ru</span>' if lang == "ru" else f'<a href="{o}" hreflang="ru">ru</a>'
    en = '<span class="on">en</span>' if lang == "en" else f'<a href="{o}" hreflang="en">en</a>'
    return f'<div class="lang">{ru}<i>/</i>{en}</div>'


def header(lang, cur, model_back=None):
    c = C[lang]
    if model_back:
        right = (f'<a class="ico" href="{model_back}" aria-label="{e(c["grid"])}">{I["grid"]}</a>'
                 f'<a class="ico" href="{model_back}" data-back aria-label="{e(c["close"])}">{I["close"]}</a>')
        return f'<header class="hdr hdr-model"><div class="hdr-ico">{lang_switch(lang, cur)}{right}</div></header>'
    return f"""<header class="hdr">
  <a class="hdr-logo" href="{href(lang, cur, '')}">{e(c['brand'])}</a>
  <div class="hdr-ico">
    {lang_switch(lang, cur)}
    <button class="ico" type="button" data-open="search" aria-label="{e(c['search'])}">{I['search']}</button>
    <a class="ico fav-ico" href="{href(lang, cur, 'favourites')}" aria-label="{e(c['fav'])}">{I['heart']}<b data-fav-count></b></a>
    <button class="ico" type="button" data-open="menu" aria-label="{e(c['menu'])}">{I['burger']}</button>
  </div>
</header>
"""


def overlays(lang, cur):
    c = C[lang]
    links = "".join(f'<a href="{nav_href(lang, cur, k)}">{e(v)}</a>' for k, v in c["nav"])
    return f"""<div class="ov" data-ov="menu" aria-hidden="true">
  <button class="ov-close ico" type="button" data-close aria-label="{e(c['close'])}">{I['close']}</button>
  <nav class="ov-menu"><a href="{href(lang, cur, '')}">{e(c['home'])}</a>{links}<a href="{href(lang, cur, 'favourites')}">{e(c['fav'])}</a></nav>
</div>
<div class="ov" data-ov="search" aria-hidden="true">
  <button class="ov-close ico" type="button" data-close aria-label="{e(c['close'])}">{I['close']}</button>
  <div class="ov-search"><input type="search" placeholder="{e(c['search_ph'])}" data-search-input autocomplete="off" aria-label="{e(c['search'])}"><div class="ov-results" data-search-results></div><p class="ov-none" data-search-none hidden>{e(c['search_none'])}</p></div>
</div>
"""


def footer(lang, cur):
    c = C[lang]
    docs = " | ".join(f'<a href="{href(lang, cur, "docs/" + k)}">{e(DOCS[k][lang][0].upper())}</a>' for k in DOC_ORDER)
    faq = f'<a href="{href(lang, cur, "about")}#faq">{"ВОПРОСЫ" if lang == "ru" else "FAQ"}</a>'
    addr = "<br>".join(e(a.upper()) for a in c["address"])
    return f"""<footer class="ftr">
  <p class="ftr-addr">{addr}</p>
  <div class="ftr-legal"><p>{docs} | {faq}</p><p>{e(c['ai_note'])} | {e(c['legal'])}</p></div>
  <div class="ftr-soc"><a href="https://t.me/{c['tg'][1:]}" aria-label="Telegram">{I['tg']}</a><a href="#" aria-label="TikTok" aria-disabled="true">{I['tt']}</a></div>
</footer>
"""


def tail(lang, cur):
    data = {"lang": lang, "models": models_js(lang, cur), "applyUrl": href(lang, cur, "apply"),
            "t": {k: C[lang][k] for k in ("fav_add", "fav_remove")}}
    return f"""<script>window.FL={json.dumps(data, ensure_ascii=False)};</script>
<script src="{asset(lang, cur, 'js/site.js')}?v={VERSION}" defer></script>
</body>
</html>
"""


def page(lang, cur, title, desc, body, cls="", model_back=None):
    return head(lang, cur, title, desc, cls) + header(lang, cur, model_back) + overlays(lang, cur) + body + footer(lang, cur) + tail(lang, cur)


# ── карточки и панели ────────────────────────────────────────────────────
# у этих моделей первым остаётся прежний студийный портрет, новый кадр идёт в конец галереи
KEEP_FIRST_PORTRAIT = {"saskia-lund", "priya-anand", "talia-renard", "noor-delacroix",
                       "emil-vantongeren", "noah-kessler", "felix-aurelio"}


def cover(slug):
    return "portrait" if slug in KEEP_FIRST_PORTRAIT else "look"


def m_stats(lang, m):
    slug, name, sex, cats, look, age, height = m
    c = C[lang]
    li = 0 if lang == "ru" else 1
    if lang == "ru":
        yrs = "год" if age % 10 == 1 and age % 100 != 11 else "года" if 2 <= age % 10 <= 4 and not 12 <= age % 100 <= 14 else "лет"
    else:
        yrs = ""
    return [(c["st"]["height"], f"{height} {c['cm']}"), (c["st"]["age"], f"{age} {yrs}".strip()),
            (c["st"]["look"], look[li]), (c["st"]["hair"], HAIR[slug][li]), (c["st"]["eyes"], EYES[slug][li]),
            (c["st"]["license"], c["lic_v"])]


_VOW = set("аеёиоуыэюяaeiouy")
_KEEP = set("йьъ")
_EN_HY = {"scandinavian": "scan-di-na-vian", "mediterranean": "med-i-ter-ra-nean", "californian": "cal-i-for-nian",
          "african": "af-ri-can", "american": "amer-i-can", "southern": "south-ern", "european": "eu-ro-pean"}


def _hy_word(w):
    """Мягкие переносы по слогам для узкой панели при наведении (браузеры на Windows сами по-русски не переносят)."""
    low = w.lower()
    if low in _EN_HY:
        parts, i = [], 0
        for chunk in _EN_HY[low].split("-"):
            parts.append(w[i:i + len(chunk)]); i += len(chunk)
        return "­".join(parts)
    if len(w) < 7 or not any(ch in _VOW for ch in low):
        return w
    # между соседними гласными: одна согласная уходит на новую строку (ла-ми), из группы — первая остаётся (нав-ский),
    # й и ь/ъ всегда остаются на строке (пей-ский, италь-ян)
    n, vow = len(w), [i for i, ch in enumerate(low) if ch in _VOW]
    cuts = []
    for p, q in zip(vow, vow[1:]):
        cons = low[p + 1:q]
        if not cons or "-" in cons:
            continue
        if len(cons) == 1:
            c = p + 1
        else:
            c = p + 2
            while c < q and low[c] in _KEEP:
                c += 1
            if c >= q:
                continue
        if c - (cuts[-1] if cuts else 0) >= 2 and n - c >= 2:
            cuts.append(c)
    out, prev = [], 0
    for c in cuts:
        out.append(w[prev:c]); prev = c
    out.append(w[prev:])
    return "­".join(out)


def hy(text):
    import re
    return re.sub(r"[A-Za-zА-Яа-яЁё]+", lambda m: _hy_word(m.group(0)), text)


def dl(rows):
    return "<dl>" + "".join(f"<div><dt>{e(k)}</dt><dd>{e(hy(v))}</dd></div>" for k, v in rows) + "</dl>"


def tile(lang, cur, m):
    slug, name, cats = m[0], m[1], m[3]
    c = C[lang]
    return f"""<article class="tile" data-cats="{' '.join(cats)}" data-slug="{slug}">
  <a class="tile-link" href="{href(lang, cur, 'model/' + slug)}"><span class="tile-img"><img src="{asset(lang, cur, f'img/models/{slug}-{cover(slug)}.jpg')}" alt="{e(name)}" loading="lazy" width="900" height="1200"></span><span class="tile-name">{e(name.lower())}</span></a>
  <button class="tile-fav" type="button" data-fav="{slug}" aria-label="{e(c['fav_add'])}">{I['heart_o']}{I['heart']}</button>
  <div class="tile-info" aria-hidden="true">{dl(m_stats(lang, m)[:5])}<p class="tile-big">{e(name.lower())}</p></div>
</article>"""


def side(word, nav_html=""):
    # «women» у Models 1 — 220 px; длинные слова уменьшаем, чтобы помещались по высоте экрана
    size = max(40, min(220, int(640 / (len(word) * 0.56))))
    return f'<aside class="side"><h1 class="side-word" style="--sw:{size}px">{e(word)}</h1><div class="side-nav">{nav_html}</div></aside>'


def board_nav(lang):
    c = C[lang]
    cats = "".join(f'<button type="button" class="{"on" if k == "all" else ""}" data-filter="{k}">{e(v)}</button>' for k, v in c["cats"])
    return f'<button class="ico side-search" type="button" data-open="search" aria-label="{e(c["search"])}">{I["search"]}</button><nav data-filters>{cats}</nav>'


# ── страницы ─────────────────────────────────────────────────────────────
def p_home(lang):
    c, cur = C[lang], ""
    links = "".join(f'<a href="{nav_href(lang, cur, k)}">{e(v)}</a>' for k, v in c["nav"])
    body = f"""<main id="main" class="home">
  <video class="home-video" autoplay muted loop playsinline preload="auto" poster="{asset(lang, cur, 'img/home-poster.jpg')}" data-home-video
    data-desktop="{asset(lang, cur, 'video/home-desktop.mp4')}" data-mobile="{asset(lang, cur, 'video/home-mobile.mp4')}"
    data-poster-desktop="{asset(lang, cur, 'img/home-poster.jpg')}" data-poster-mobile="{asset(lang, cur, 'img/home-poster-mobile.jpg')}">
    <source src="{asset(lang, cur, 'video/home-desktop.mp4')}" type="video/mp4"></video>
  <i class="home-shade"></i>
  <div class="home-top">{lang_switch(lang, cur)}<button class="ico" type="button" data-open="search" aria-label="{e(c['search'])}">{I['search']}</button></div>
  <div class="home-center"><h1 class="home-logo">{e(c['brand'])}</h1><nav class="home-nav">{links}</nav></div>
</main>
"""
    title = "FIRST LOOK — " + ("агентство ИИ-моделей" if lang == "ru" else "AI model agency")
    return head(lang, cur, title, T[lang]["hero_sub"], "is-home") + overlays(lang, cur) + body + tail(lang, cur)


def p_board(lang, sex):
    c, cur = C[lang], sex
    tiles = "".join(tile(lang, cur, m) for m in MODELS if m[2] == sex)
    body = f'<main id="main" class="board">{side(c["board"][sex], board_nav(lang))}<section class="grid" data-grid>{tiles}</section></main>'
    return page(lang, cur, f'{c["board"][sex]} — FIRST LOOK', T[lang]["models_p"], body, "is-board")


def p_model(lang, i):
    c = C[lang]
    m = MODELS[i]
    slug, name, sex = m[0], m[1], m[2]
    cur = "model/" + slug
    img = lambda k: asset(lang, cur, f"img/models/{slug}-{k}.jpg")
    # обложка выдуманного журнала — вторым кадром, если она есть
    mag = (f'\n    <figure><img src="{img("cover")}" alt="{e(name)}" width="900" height="1200" loading="lazy"></figure>'
           if (ROOT / "assets" / "img" / "models" / f"{slug}-cover.jpg").exists() else "")
    q = name.replace(" ", "+")
    body = f"""<main id="main" class="mp">
  <aside class="mp-info">
    <h1 class="mp-name">{e(name.lower())}</h1>
    {dl(m_stats(lang, m))}
    <div class="mp-actions">
      <a href="{href(lang, cur, 'apply')}?service=license&amp;model={q}">{I['mail']}<span>{e(c['rent'])}</span></a>
      <button type="button" data-fav="{slug}" data-fav-label>{I['heart_o']}{I['heart']}<span>{e(c['fav_add'])}</span></button>
      <a href="{href(lang, cur, 'apply')}?service=photoshoot&amp;model={q}">{I['down']}<span>{e(c['shoot'])}</span></a>
    </div>
  </aside>
  <div class="mp-gallery">
    <figure><img src="{img(cover(slug))}" alt="{e(name)}" width="900" height="1200"></figure>{mag}
    <figure><img src="{img('full')}" alt="{e(name)}" width="900" height="1200" loading="lazy"></figure>
    <figure><img src="{img('look' if cover(slug) == 'portrait' else 'portrait')}" alt="{e(name)}" width="900" height="1200" loading="lazy"></figure>
  </div>
</main>
"""
    return page(lang, cur, f"{name.lower()} — FIRST LOOK", T[lang]["m_about"].format(name=name), body, "is-model",
                model_back=href(lang, cur, sex))


def p_services(lang):
    c, cur = C[lang], "services"
    tiles = ""
    for k in SERVICE_ORDER:
        s = SERVICES[k][lang]
        imgsrc = asset(lang, cur, f"img/models/{SERVICES[k]['img'][0]}.jpg")
        incl = "<ul>" + "".join(f"<li>{e(x)}</li>" for x in s["incl"][:4]) + "</ul>"
        tiles += f"""<article class="tile tile-svc">
  <a class="tile-link" href="{href(lang, cur, 'services/' + k)}"><span class="tile-img"><img src="{imgsrc}" alt="" loading="lazy" width="900" height="1200"></span><span class="tile-name">{e(s['title'].lower())}<em>{e(s['price'])}</em></span></a>
  <div class="tile-info" aria-hidden="true">{incl}<p class="tile-big">{e(s['title'].lower())}</p></div>
</article>"""
    body = f'<main id="main" class="board">{side(c["services_h"])}<section class="grid" data-grid>{tiles}</section></main>'
    return page(lang, cur, f'{c["services_h"]} — FIRST LOOK', T[lang]["services_aside"], body, "is-board")


def p_service(lang, k):
    c = C[lang]
    s = SERVICES[k][lang]
    cur = "services/" + k
    rows = [(("стоимость" if lang == "ru" else "price"), f"{s['price']} {s['per']}")]
    incl = "".join(f"<li>{e(x)}</li>" for x in s["incl"])
    gallery = "".join(f'<figure><img src="{asset(lang, cur, f"img/models/{p}.jpg")}" alt="" width="900" height="1200" loading="lazy"></figure>' for p in SERVICES[k]["img"])
    body = f"""<main id="main" class="mp">
  <aside class="mp-info">
    <h1 class="mp-name">{e(s['title'].lower())}</h1>
    <p class="mp-lead">{e(s['lead'])}</p>
    {dl(rows)}
    <ul class="mp-list">{incl}</ul>
    <div class="mp-actions"><a href="{href(lang, cur, 'apply')}?service={s['plan']}">{I['mail']}<span>{e(c['form_h'])}</span></a></div>
  </aside>
  <div class="mp-gallery">{gallery}</div>
</main>
"""
    return page(lang, cur, f"{s['title'].lower()} — FIRST LOOK", s["lead"], body, "is-model", model_back=href(lang, cur, "services"))


def p_video(lang):
    c, cur = C[lang], "video"
    items = ""
    for key, title, meta in c["video_items"]:
        src = f"{key}-{lang}" if key == "first-look-film" else key
        items += f"""<article class="vtile" tabindex="0" data-video="{asset(lang, cur, f'video/{src}.mp4')}">
  <span class="vtile-media"><video muted loop playsinline preload="none" poster="{asset(lang, cur, f'img/video/{src}.jpg')}"><source src="{asset(lang, cur, f'video/{src}.mp4')}" type="video/mp4"></video><i class="vtile-play">{I['play']}</i></span>
  <span class="tile-name">{e(title)}<em>{e(meta)}</em></span>
</article>"""
    body = f"""<main id="main" class="board">{side(c['video_h'])}<section class="vgrid">{items}</section></main>
<div class="lightbox" data-lightbox aria-hidden="true"><button class="ov-close ico" type="button" data-close aria-label="{e(c['close'])}">{I['close']}</button><video controls playsinline></video></div>
"""
    return page(lang, cur, f'{c["video_h"]} — FIRST LOOK', T[lang]["hero_sub"], body, "is-board")


def p_about(lang):
    c, t, cur = C[lang], T[lang], "about"
    tabs = "".join(f'<a href="#{k}" class="{"on" if i == 0 else ""}" data-tab="{k}">{e(v)}</a>' for i, (k, v) in enumerate(c["about_tabs"]))
    agency = "".join(f"<h2>{e(h)}</h2><p>{e(p)}</p>" for h, p in c["about_sections"])
    steps = "".join(f"<li><b>0{i + 1}</b><h3>{e(h.lower())}</h3><p>{e(p)}</p></li>" for i, (h, p) in enumerate(t["steps"]))
    plans = "".join(f'<div class="plan"><p class="plan-n">{e(n.lower())}</p><p class="plan-p">{e(pr)} <span>{e(per)}</span></p><p>{e(d)}</p></div>'
                    for _, n, pr, per, d, *_ in t["plans"])
    faq = "".join(f'<details><summary>{e(q.lower())}</summary><p>{e(a)}</p></details>' for q, a in t["faq"])
    body = f"""<main id="main" class="about">
  <figure class="about-img"><img src="{asset(lang, cur, 'img/models/saskia-lund-full.jpg')}" alt="" width="900" height="1200"></figure>
  <div class="about-head">
    <h1 class="about-title">{e(c['about_h'])}</h1>
    <nav class="about-tabs" data-tabs>{tabs}</nav>
  </div>
  <div class="about-body">
    <section class="about-pane on" id="agency" data-pane="agency">{agency}</section>
    <section class="about-pane" id="process" data-pane="process"><h2>{e(c['process_h'])}</h2><ol class="steps">{steps}</ol><h2>{e(c['prices_h'])}</h2><div class="plans">{plans}</div></section>
    <section class="about-pane" id="faq" data-pane="faq">{faq}</section>
  </div>
</main>
"""
    return page(lang, cur, f'{c["about_h"]} — FIRST LOOK', c["about_sections"][0][1], body, "is-about")


def form(lang, cur):
    c = C[lang]
    chips = "".join(f'<label class="chip"><input type="radio" name="service" value="{k}"{" checked" if i == 0 else ""}><span>{e(v)}</span></label>'
                    for i, (k, v) in enumerate(c["need_opts"]))
    return f"""<form class="form" data-form action="{href(lang, cur, 'thanks')}" novalidate>
  <p class="form-label">{e(c['need'])}</p>
  <div class="chips">{chips}</div>
  <input type="hidden" name="model" data-model-field>
  <p class="picked" data-picked hidden>{e(c['f_model'])}: <b></b></p>
  <label class="field"><input name="name" placeholder="{e(c['f_name'])}" autocomplete="name"><span class="err">{e(c['f_err_name'])}</span></label>
  <label class="field"><input name="email" type="email" placeholder="{e(c['f_email'])}" autocomplete="email"><span class="err">{e(c['f_err_email'])}</span></label>
  <label class="field"><input name="brand" placeholder="{e(c['f_brand'])}" autocomplete="organization"></label>
  <label class="field"><textarea name="task" rows="1" placeholder="{e(c['f_task'])}"></textarea></label>
  <button class="btn" type="submit">{e(c['f_send'])}</button>
  <p class="note">{e(c['f_note'])}<a href="{href(lang, cur, 'docs/privacy')}">{e(c['f_note_link'])}</a>.</p>
</form>"""


def p_apply(lang):
    c, cur = C[lang], "apply"
    lst = "".join(f"<li>{e(x)}</li>" for x in c["apply_list"])
    ex = "".join(f'<figure><img src="{asset(lang, cur, f"img/apply/{i}.jpg")}" alt="" width="600" height="800" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>'
                 for i, cap in enumerate(c["apply_examples"], 1))
    body = f"""<main id="main" class="apply">
  <section class="apply-top">
    <div class="apply-copy"><h1 class="big-title">{e(c['apply_h'])}</h1><h2>{e(c['apply_sub'])}</h2><ul>{lst}</ul></div>
    <div class="apply-ex">{ex}</div>
  </section>
  <a class="scroll-hint" href="#form">{e(c['apply_scroll'])}{I['down']}</a>
  <section class="apply-form" id="form"><h2>{e(c['form_h'])}</h2>{form(lang, cur)}</section>
</main>
"""
    return page(lang, cur, f'{c["apply_h"]} — FIRST LOOK', c["apply_sub"], body, "is-apply")


def p_contact(lang):
    c, cur = C[lang], "contact"
    cols = "".join(f'<div><p>{e(k)}</p><a href="mailto:{v}">{e(v)}</a></div>' for k, v in c["contact_cols"])
    body = f"""<main id="main" class="contact">
  <section class="contact-hero"><img src="{asset(lang, cur, 'img/contact.jpg')}" alt="" width="1920" height="1080"><h1 class="big-title">{e(c['contact_h'])}</h1></section>
  <p class="contact-addr">{"<br>".join(e(a) for a in c['address'])}<br><a href="https://t.me/{c['tg'][1:]}">telegram {e(c['tg'])}</a></p>
  <div class="contact-cols">{cols}</div>
</main>
"""
    return page(lang, cur, f'{c["contact_h"]} — FIRST LOOK', c["contact_h"], body, "is-contact")


def p_fav(lang):
    c, cur = C[lang], "favourites"
    body = f"""<main id="main" class="board">{side(c['fav_h'])}<section class="fav-wrap"><div class="grid" data-fav-grid></div>
<p class="fav-empty" data-fav-empty hidden>{e(c['fav_empty'])}</p>
<a class="btn fav-send" href="{href(lang, cur, 'apply')}" data-fav-send hidden>{e(c['fav_send'])}</a></section></main>
<template data-tile-tpl>{"".join(tile(lang, cur, m) for m in MODELS)}</template>
"""
    return page(lang, cur, f'{c["fav_h"]} — FIRST LOOK', c["fav_h"], body, "is-board")


def p_doc(lang, k):
    title, parts = DOCS[k][lang]
    cur = "docs/" + k
    body_html = "".join(f"<h2>{e(h)}</h2><p>{e(p)}</p>" for h, p in parts)
    nav = "".join(f'<a class="{"on" if d == k else ""}" href="{href(lang, cur, "docs/" + d)}">{e(DOCS[d][lang][0].lower())}</a>' for d in DOC_ORDER)
    body = f'<main id="main" class="board">{side(title.lower(), "<nav>" + nav + "</nav>")}<article class="doc">{body_html}</article></main>'
    return page(lang, cur, f"{title} — FIRST LOOK", title, body, "is-board is-doc")


def p_simple(lang, cur, h, p):
    c = C[lang]
    body = f"""<main id="main" class="simple"><h1 class="big-title">{e(h)}</h1><p data-thanks-text>{e(p)}</p>
<nav class="simple-nav"><a href="{href(lang, cur, '')}">{e(c['to_home'])}</a><a href="{href(lang, cur, 'women')}">{e(c['to_women'])}</a><a href="{href(lang, cur, 'men')}">{e(c['to_men'])}</a></nav></main>"""
    return page(lang, cur, f"{h} — FIRST LOOK", p, body, "is-simple")


# ── сборка ───────────────────────────────────────────────────────────────
def write(lang, slug, text):
    p = (ROOT if lang == "ru" else ROOT / "en") / ("index.html" if not slug else f"{slug}.html")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    for d in ["model", "services", "docs", "en"]:
        shutil.rmtree(ROOT / d, ignore_errors=True)
    for f in ["models.html", "services.html"]:
        (ROOT / f).unlink(missing_ok=True)
    n = 0
    for lang in ("ru", "en"):
        c = C[lang]
        pages = [("", p_home(lang)), ("women", p_board(lang, "women")), ("men", p_board(lang, "men")),
                 ("services", p_services(lang)), ("about", p_about(lang)),
                 ("apply", p_apply(lang)), ("contact", p_contact(lang)), ("favourites", p_fav(lang)),
                 ("thanks", p_simple(lang, "thanks", c["thanks_h"], c["thanks_p"]))]
        pages += [("model/" + MODELS[i][0], p_model(lang, i)) for i in range(len(MODELS))]
        pages += [("services/" + k, p_service(lang, k)) for k in SERVICE_ORDER]
        pages += [("docs/" + k, p_doc(lang, k)) for k in DOC_ORDER]
        if lang == "ru":
            pages.append(("404", p_simple(lang, "404", c["nf_h"], c["nf_p"])))
        for slug, text in pages:
            write(lang, slug, text)
            n += 1
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("pages:", n)


if __name__ == "__main__":
    main()
