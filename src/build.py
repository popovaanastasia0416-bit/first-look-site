"""Собирает статический сайт FIRST LOOK (RU в корне, EN в /en/).
Запуск из корня репозитория: python src/build.py
"""
import html
import json
import shutil
from pathlib import Path

from data import CAT, DOC_ORDER, DOCS, MODELS, SERVICE_ORDER, SERVICES, T

ROOT = Path(__file__).resolve().parent.parent
VERSION = "15"  # поднимать при правке css/js, чтобы браузер не брал старое из кэша
e = html.escape


# ── пути ─────────────────────────────────────────────────────────────────
def page_path(lang, slug):
    """slug: '' (главная), 'models', 'model/elena-voss', 'services/license', 'docs/privacy', 'thanks', '404'"""
    base = ROOT if lang == "ru" else ROOT / "en"
    return base / ("index.html" if not slug else f"{slug}.html")


def href(lang, cur, slug, anchor=""):
    """Относительная ссылка со страницы cur на slug (работает и на github.io/подпапке, и локально)."""
    depth = cur.count("/") + (1 if lang == "en" else 0)
    up = "../" * depth
    target = ("index.html" if not slug else f"{slug}.html") if lang == "ru" else ("en/" + ("index.html" if not slug else f"{slug}.html"))
    return f"{up}{target}" + (f"#{anchor}" if anchor else "")


def asset(lang, cur, path):
    depth = cur.count("/") + (1 if lang == "en" else 0)
    return "../" * depth + "assets/" + path


def other_lang(lang, cur):
    o = T[lang]["other"]
    depth = cur.count("/") + (1 if lang == "en" else 0)
    up = "../" * depth
    target = ("index.html" if cur in ("", "404") else f"{cur}.html")
    return up + (target if o == "ru" else "en/" + target)


def lang_switch(lang, cur, cls="lang-switch"):
    """Переключатель RU / EN: текущий язык подсвечен, второй ведёт на ту же страницу."""
    other = other_lang(lang, cur)
    ru = '<span class="is-on" aria-current="true">RU</span>' if lang == "ru" else f'<a href="{other}" hreflang="ru" lang="ru">RU</a>'
    en = '<span class="is-on" aria-current="true">EN</span>' if lang == "en" else f'<a href="{other}" hreflang="en" lang="en">EN</a>'
    return f'<div class="{cls}" role="group" aria-label="Language">{ru}{en}</div>'


# ── иконки ───────────────────────────────────────────────────────────────
ICON = {
    "Instagram": '<svg viewBox="0 0 20 20" fill="none"><rect x="3" y="3" width="14" height="14" rx="4" stroke="currentColor" stroke-width="1.4"/><circle cx="10" cy="10" r="3.2" stroke="currentColor" stroke-width="1.4"/><circle cx="14.2" cy="5.8" r=".9" fill="currentColor"/></svg>',
    "Telegram": '<svg viewBox="0 0 20 20" fill="none"><path d="M17 3.5 2.8 9.2l4.8 1.7M17 3.5l-2.4 13-7-5.6M17 3.5l-9.4 7.4.6 4.3 2.2-2.5" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/></svg>',
    "TikTok": '<svg viewBox="0 0 20 20" fill="none"><path d="M11.5 3v9.8a2.9 2.9 0 1 1-2.9-2.9M11.5 3c.4 2.3 1.9 3.8 4.3 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "Pinterest": '<svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="1.4"/><path d="M9.2 7.2c2.6-.8 4.4 1.2 3.4 3.4-.6 1.3-2.2 1.6-3 .6m.6-2.6-2 7.8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
    "up": '<svg viewBox="0 0 14 14" fill="none"><path d="M7 12V2.5M3 6l4-4 4 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "down": '<svg viewBox="0 0 16 16" fill="none"><path d="M8 2.5V12M4 8.5l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "upload": '<svg viewBox="0 0 16 16" fill="none"><path d="M8 13.5V4M4 7.5l4-4 4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "check": '<svg viewBox="0 0 20 20" fill="none"><path d="M5.5 10.5 8.5 13.5 14.5 7" stroke="#0a0a0a" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "jacket": '<svg viewBox="0 0 24 24" fill="none"><path d="M8.5 3 4.5 5l-2 13.5 3 .5 1-7.5v9h11v-9l1 7.5 3-.5-2-13.5-4-2c-.7 1.2-2 1.8-3.5 1.8S9.2 4.2 8.5 3Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M12 4.8v15.7M6.5 19.2h11" stroke="currentColor" stroke-width="1.2"/></svg>',
    "arrow": '<svg viewBox="0 0 16 16" fill="none"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "back": '<svg viewBox="0 0 16 16" fill="none"><path d="M13 8H3M7 4 3 8l4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "plus": '<svg viewBox="0 0 20 20" fill="none"><path d="M10 4v12M4 10h12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
    "pause": '<svg viewBox="0 0 16 16" fill="none"><path d="M5.5 3.5v9M10.5 3.5v9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    "play": '<svg viewBox="0 0 16 16" fill="none"><path d="M5 3.5v9l7.5-4.5z" fill="currentColor"/></svg>',
}


# ── общие блоки ──────────────────────────────────────────────────────────
def head(lang, cur, title, desc, body_class=""):
    t = T[lang]
    alt = "en/" if lang == "ru" else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{asset(lang, cur, 'img/hero-poster.jpg')}">
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" href="{asset(lang, cur, 'img/favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset(lang, cur, 'css/site.css')}?v={VERSION}">
</head>
<body id="top" class="{body_class}">
<a class="skip" href="#main">{'К содержимому' if lang == 'ru' else 'Skip to content'}</a>
"""


def nav_target(lang, cur, key):
    return {
        "models": href(lang, cur, "models"),
        "photoshoot": href(lang, cur, "services/photoshoot"),
        "pricing": href(lang, cur, "", "pricing"),
        "process": href(lang, cur, "", "process"),
        "faq": href(lang, cur, "", "faq"),
    }[key]


def header(lang, cur, transparent=False, has_req=True):
    t = T[lang]
    book = "#request" if has_req else href(lang, cur, "", "request")
    links = "".join(f'<a href="{nav_target(lang, cur, k)}">{e(v)}</a>' for k, v in t["nav"])
    return f"""<header class="site-header{' is-transparent' if transparent else ''}" data-header>
  <div class="wrap header-in">
    <a class="logo" href="{href(lang, cur, '')}">FIRST LOOK</a>
    <nav class="main-nav" aria-label="main">{links}</nav>
    <div class="header-actions">
      {lang_switch(lang, cur)}
      <a class="btn btn-white btn-sm" href="{book}" data-scroll-request>{e(t['book'])}</a>
      <button class="burger" type="button" aria-label="{e(t['menu'])}" aria-expanded="false" data-burger><span></span><span></span></button>
    </div>
  </div>
  <div class="mobile-menu" data-mobile-menu>
    <nav>{links}<a href="{href(lang, cur, '', 'faq')}">{'Вопросы' if lang == 'ru' else 'FAQ'}</a></nav>
    <a class="btn btn-chrome" href="{book}" data-scroll-request>{e(t['book'])}</a>
    {lang_switch(lang, cur, 'lang-switch lang-switch-lg')}
  </div>
</header>
"""


def sec_head(eyebrow, title, aside=None, tag="h2"):
    """Мелкие подписи над заголовками она убрала в макете — eyebrow передаём None."""
    a = f'<p class="sec-aside">{e(aside)}</p>' if aside else ""
    eb = f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ""
    return f'<div class="sec-head"><div>{eb}<{tag} class="h2">{e(title)}</{tag}></div>{a}</div>'


def request_block(lang, cur):
    t = T[lang]
    chips = "".join(
        f'<label class="chip-opt"><input type="radio" name="service" value="{k}"{" checked" if i == 0 else ""}><span>{e(v)}</span></label>'
        for i, (k, v) in enumerate(t["need_opts"]))
    contacts = "".join(
        f'<div class="contact-row"><span>{k}</span><a href="{h}">{e(v)}</a></div>'
        for k, v, h in [("EMAIL", t["email"], "mailto:" + t["email"]), ("TELEGRAM", t["tg"], "https://t.me/" + t["tg"][1:]), ("INSTAGRAM", t["ig"], "https://instagram.com/" + t["ig"][1:])])
    return f"""<section class="request" id="request">
  <div class="wrap request-in">
    <div class="request-copy">
      <p class="eyebrow">{e(t['req_eyebrow'])}</p>
      <h2 class="h-xl">{e(t['req_h'])}</h2>
      <p class="muted lead">{e(t['req_p'])}</p>
      <div class="contacts">{contacts}</div>
    </div>
    <form class="form-card" data-form action="{href(lang, cur, 'thanks')}" novalidate>
      <p class="label">{e(t['need'])}</p>
      <div class="chips">{chips}</div>
      <input type="hidden" name="model" value="" data-model-field>
      <p class="picked-model" data-picked-model hidden>{e(t['f_model'])}: <b></b></p>
      <label class="field"><input name="name" placeholder="{e(t['f_name'])}" autocomplete="name"><span class="err">{e(t['f_err_name'])}</span></label>
      <label class="field"><input name="email" type="email" placeholder="{e(t['f_email'])}" autocomplete="email"><span class="err">{e(t['f_err_email'])}</span></label>
      <label class="field"><input name="brand" placeholder="{e(t['f_brand'])}" autocomplete="organization"></label>
      <label class="field"><textarea name="task" rows="3" placeholder="{e(t['f_task'])}"></textarea></label>
      <button class="btn btn-chrome btn-block" type="submit">{e(t['f_send'])}</button>
      <p class="note">{e(t['f_note'])}<a href="{href(lang, cur, 'docs/privacy')}">{e(t['f_note_link'])}</a>.</p>
    </form>
  </div>
</section>
"""


def footer(lang, cur):
    t = T[lang]
    soc = "".join(f'<a class="soc" href="{h}" aria-label="{n}" aria-disabled="true">{ICON[n]}</a>' for n, h in t["socials"])
    navl = "".join(f'<a href="{nav_target(lang, cur, k)}">{e(v)}</a>' for k, v in t["col_nav_items"])
    srv = "".join(f'<a href="{href(lang, cur, "services/" + k)}">{e(SERVICES[k][lang]["title"])}</a>' for k in SERVICE_ORDER)
    docs = "".join(f'<a href="{href(lang, cur, "docs/" + k)}">{e(DOCS[k][lang][0])}</a>' for k in DOC_ORDER)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-cols">
      <div class="foot-brand"><p class="label">{e(t['agency'])}</p><p class="muted">{e(t['about'])}</p><div class="socials">{soc}</div></div>
      <div class="foot-col"><p class="label">{e(t['col_nav'])}</p>{navl}</div>
      <div class="foot-col"><p class="label">{e(t['col_srv'])}</p>{srv}</div>
      <div class="foot-col"><p class="label">{e(t['col_doc'])}</p>{docs}</div>
    </div>
  </div>
  <div class="wordmark" aria-hidden="true"><span>FIRST LOOK</span></div>
</footer>
"""


def tail(lang, cur):
    return f"""<script>window.FL={json.dumps({'lang': lang})};</script>
<script src="{asset(lang, cur, 'js/site.js')}?v={VERSION}" defer></script>
</body>
</html>
"""


# ── карточка модели ──────────────────────────────────────────────────────
def card(lang, cur, m):
    slug, name, sex, cats, look, age, height = m
    t = T[lang]
    tags = " · ".join([CAT[lang][sex]] + [CAT[lang][c] for c in cats])
    look_v = look[0] if lang == "ru" else look[1]
    data_cats = " ".join([sex] + cats)
    return f"""<a class="m-card" href="{href(lang, cur, 'model/' + slug)}" data-cats="{data_cats}">
  <div class="m-media">
    <img class="m-portrait" src="{asset(lang, cur, f'img/models/{slug}-portrait.jpg')}" alt="{e(name)}" loading="lazy" width="900" height="1200">
    <img class="m-full" src="{asset(lang, cur, f'img/models/{slug}-full.jpg')}" alt="" loading="lazy" width="900" height="1200">
    <dl class="m-params">
      <div><dt>{e(t['m_height'])}</dt><dd>{height} {t['m_cm']}</dd></div>
      <div><dt>{e(t['m_age'])}</dt><dd>{age}</dd></div>
      <div><dt>{e(t['m_look'])}</dt><dd>{e(look_v)}</dd></div>
      <div><dt>{e(t['m_license'])}</dt><dd>{e(t['m_license_v'])}</dd></div>
    </dl>
  </div>
  <p class="m-name">{e(name)}</p>
  <p class="m-tags">{e(tags)}</p>
</a>"""


def filters(lang):
    keys = ["all", "women", "men", "editorial", "ecommerce", "beauty"]
    return '<div class="filters" role="tablist" data-filters>' + "".join(
        f'<button class="pill{" is-on" if k == "all" else ""}" type="button" data-filter="{k}">{e(CAT[lang][k])}</button>' for k in keys) + "</div>"


def roster(lang, cur, heading_tag="h2", show_all_link=True):
    t = T[lang]
    cards = "".join(card(lang, cur, m) for m in MODELS)
    link = f'<a class="link-arrow" href="{href(lang, cur, "models")}">{e(t["all_models"])}{ICON["arrow"]}</a>' if show_all_link else ""
    return f"""<div class="filter-bar"><div class="wrap">{filters(lang)}</div></div>
<section class="roster" id="models">
  <div class="wrap">
    <div class="roster-head"><{heading_tag} class="h2">{e(t['roster_h'])}</{heading_tag}></div>
    <div class="grid" data-grid>{cards}</div>
    <p class="empty" data-empty hidden>{e(t['empty'])}</p>
    {link}
  </div>
</section>
"""


# ── анимированный путь фотосессии ────────────────────────────────────────
def process(lang, cur):
    t = T[lang]
    s = t["scene"]
    img = lambda slug, kind: asset(lang, cur, f"img/models/{slug}-{kind}.jpg")
    scenes = [
        f"""<div class="sc sc-upload">
  <div class="tile"><span class="ic">{ICON['jacket']}</span><span class="tl">{e(s['front'])}</span><span class="ok">{ICON['check']}</span></div>
  <div class="tile"><span class="ic">{ICON['jacket']}</span><span class="tl">{e(s['back'])}</span><span class="ok">{ICON['check']}</span></div>
  <div class="bar"><i></i><span>{ICON['upload']}{e(s['upload'])}</span><b><em class="p0">0%</em><em class="p1">100%</em></b></div>
</div>""",
        f"""<div class="sc sc-pick">
  <div class="thumbs"><img src="{img('elena-voss', 'portrait')}" alt="" loading="lazy"><img src="{img('ines-kovac', 'portrait')}" alt="" loading="lazy"><img class="sel" src="{img('saskia-lund', 'portrait')}" alt="" loading="lazy"><span class="ring"></span><span class="ok">{ICON['check']}</span></div>
  <div class="chips-s">{''.join(f'<span>{e(c)}</span>' for c in s['chips'])}</div>
  <p class="picked">{e(s['picked'])}</p>
</div>""",
        f"""<div class="sc sc-gen">
  <img src="{img('saskia-lund', 'full')}" alt="" loading="lazy"><i class="veil"></i><i class="scan"></i>
  <span class="status"><i></i><em class="s-up">{e(s['st_up'])}</em><em class="s-act">{e(s['st_act'])}</em><em class="s-done">{e(s['st_done'])}</em></span>
</div>""",
        f"""<div class="sc sc-files">
  <img class="f0" src="{img('saskia-lund', 'portrait')}" alt="" loading="lazy"><img class="f2" src="{img('saskia-lund', 'full')}" alt="" loading="lazy"><img class="f1" src="{img('saskia-lund', 'full')}" alt="" loading="lazy">
  <span class="files">{e(s['files'])}{ICON['down']}</span>
</div>""",
    ]
    steps = "".join(
        f"""<li class="step" data-step="{i}"><span class="node"></span><div class="scene">{scenes[i]}</div><p class="num">0{i + 1}</p><h3>{e(h)}</h3><p class="muted">{e(p)}</p></li>"""
        for i, (h, p) in enumerate(t["steps"]))
    return f"""<section class="process" id="process">
  <div class="wrap">
    {sec_head(None, t['process_h'], t['process_aside'])}
    <ol class="path" data-path><i class="track"></i><i class="track-fill"></i>{steps}</ol>
  </div>
</section>
"""


def pricing(lang, cur):
    t = T[lang]
    plans = ""
    for key, name, price, per, desc, feats, cta, hl in t["plans"]:
        fl = "".join(f"<li>{e(f)}</li>" for f in feats)
        badge = f'<span class="badge">{e(t["popular"])}</span>' if hl else ""
        plans += f"""<div class="plan{' is-hl' if hl else ''}"><div class="plan-top"><p class="plan-name">{e(name)}</p>{badge}</div>
<p class="price"><b>{e(price)}</b><span>{e(per)}</span></p><p class="muted">{e(desc)}</p><ul class="checks">{fl}</ul>
<a class="btn {'btn-white' if hl else 'btn-outline'} btn-block" href="#request" data-service="{key}">{e(cta)}</a></div>"""
    return f"""<section class="pricing" id="pricing"><div class="wrap">{sec_head(None, t['pricing_h'])}<div class="plans">{plans}</div></div></section>"""


def faq(lang):
    t = T[lang]
    items = "".join(f'<details class="faq-item"><summary><span>{e(q)}</span>{ICON["plus"]}</summary><p>{e(a)}</p></details>' for q, a in t["faq"])
    return f"""<section class="faq" id="faq"><div class="wrap">{sec_head(None, t['faq_h'])}<div class="faq-list">{items}</div></div></section>"""


# ── страницы ─────────────────────────────────────────────────────────────
def page_home(lang):
    t, cur = T[lang], ""
    svc = []
    for i in (1, 2):
        pts = "".join(f"<li>{e(p)}</li>" for p in t[f"svc{i}_pts"])
        link = href(lang, cur, "models") if i == 1 else "#request"
        extra = "" if i == 1 else ' data-service="photoshoot"'
        more = href(lang, cur, "services/license" if i == 1 else "services/photoshoot")
        svc.append(f"""<article class="svc{' svc-chrome' if i == 2 else ''}">
  <div class="svc-top"><span class="svc-n">0{i}</span><span class="tag">{e(t[f'svc{i}_tag'])}</span></div>
  <h3 class="h-svc"><a href="{more}">{e(t[f'svc{i}_h'])}</a></h3><p class="svc-p">{e(t[f'svc{i}_p'])}</p>
  <ul class="dash">{pts}</ul>
  <div class="svc-bot"><b>{e(t[f'svc{i}_price'])}</b><a class="btn {'btn-dark' if i == 2 else 'btn-outline'}" href="{link}"{extra}>{e(t[f'svc{i}_cta'])}</a></div>
</article>""")
    body = f"""{head(lang, cur, 'FIRST LOOK — ' + ('агентство ИИ-моделей' if lang == 'ru' else 'AI model agency'), t['hero_sub'], 'home')}
{header(lang, cur, transparent=True)}
<main id="main">
<section class="hero">
  <video class="hero-video" autoplay muted loop playsinline preload="auto" poster="{asset(lang, cur, 'img/hero-poster.jpg')}" data-hero-video
    data-desktop="{asset(lang, cur, 'video/hero-desktop.mp4')}" data-mobile="{asset(lang, cur, 'video/hero-mobile.mp4')}"
    data-poster-desktop="{asset(lang, cur, 'img/hero-poster.jpg')}" data-poster-mobile="{asset(lang, cur, 'img/hero-poster-mobile.jpg')}">
    <source src="{asset(lang, cur, 'video/hero-desktop.mp4')}" type="video/mp4">
  </video>
  <i class="hero-shade"></i>
  <div class="hero-in">
    <h1 class="hero-title">FIRST<br>LOOK</h1>
    <p class="hero-sub">{e(t['hero_sub'])}</p>
    <div class="hero-cta"><a class="btn btn-white" href="#models">{e(t['hero_cta1'])}</a><a class="btn btn-outline" href="#process">{e(t['hero_cta2'])}</a></div>
  </div>
  <a class="scroll-hint" href="#intro"><i></i>{e(t['scroll'])}</a>
  <button class="video-toggle" type="button" aria-label="{e(t['sound_on'])}" data-video-toggle>{ICON['pause']}{ICON['play']}</button>
</section>
<section class="intro" id="intro"><div class="wrap intro-in"><h2 class="h2 h-intro">{e(t['intro_h'])}</h2><p class="muted lead">{e(t['intro_p'])}</p></div></section>
<section class="services" id="services"><div class="wrap">{sec_head(None, t['services_h'], t['services_aside'])}<div class="svc-grid">{''.join(svc)}</div></div></section>
{roster(lang, cur, show_all_link=False)}
{process(lang, cur)}
{pricing(lang, cur)}
{faq(lang)}
{request_block(lang, cur)}
</main>
{footer(lang, cur)}
{tail(lang, cur)}"""
    return body


def page_models(lang):
    t, cur = T[lang], "models"
    return f"""{head(lang, cur, t['models_h'] + ' — FIRST LOOK', t['models_p'])}
{header(lang, cur)}
<main id="main" class="page">
<section class="page-hero"><div class="wrap"><p class="crumbs"><a href="{href(lang, cur, '')}">FIRST LOOK</a> / {e(t['models_h'])}</p><h1 class="h-xl">{e(t['models_h'])}</h1><p class="muted lead narrow">{e(t['models_p'])}</p></div></section>
{roster(lang, cur, heading_tag='h2', show_all_link=False)}
{request_block(lang, cur)}
</main>
{footer(lang, cur)}
{tail(lang, cur)}"""


def page_model(lang, i):
    t = T[lang]
    slug, name, sex, cats, look, age, height = MODELS[i]
    cur = "model/" + slug
    tags = "".join(f'<span class="chip">{e(CAT[lang][c])}</span>' for c in [sex] + cats)
    prev_m, next_m = MODELS[i - 1], MODELS[(i + 1) % len(MODELS)]
    same = [m for m in MODELS if m[2] == sex and m[0] != slug]
    more = "".join(card(lang, cur, m) for m in (same[i % 3:] + same[:i % 3])[:4])
    look_v = look[0] if lang == "ru" else look[1]
    age_v = f"{age} {t['m_years']}".strip()
    rows = "".join(f'<div class="stat"><span>{e(k)}</span><b>{e(v)}</b></div>' for k, v in [
        (t["m_look"], look_v), (t["m_age"], age_v), (t["m_height"], f"{height} {t['m_cm']}"), (t["m_license"], t["m_license_v"]), (t["m_excl"], t["m_excl_v"])])
    img = lambda k: asset(lang, cur, f"img/models/{slug}-{k}.jpg")
    return f"""{head(lang, cur, f'{name} — FIRST LOOK', t['m_about'].format(name=name))}
{header(lang, cur)}
<main id="main" class="page">
<section class="model wrap">
  <div class="model-gallery">
    <figure><img src="{img('portrait')}" alt="{e(name)} — {e(t['m_portrait'])}" width="900" height="1200"></figure>
    <figure><img src="{img('full')}" alt="{e(name)} — {e(t['m_full'])}" width="900" height="1200" loading="lazy"></figure>
  </div>
  <aside class="model-info">
    <a class="back" href="{href(lang, cur, 'models')}">{ICON['back']}{e(t['m_back'])}</a>
    <h1 class="model-name">{e(name)}</h1>
    <div class="chips-row">{tags}</div>
    <p class="muted">{e(t['m_about'].format(name=name))}</p>
    <div class="stats">{rows}</div>
    <a class="btn btn-chrome btn-block" href="#request" data-service="license" data-model="{e(name)}">{e(t['m_rent'])}</a>
    <a class="btn btn-outline btn-block" href="#request" data-service="photoshoot" data-model="{e(name)}">{e(t['m_shoot'])}</a>
    <div class="pager"><a href="{href(lang, cur, 'model/' + prev_m[0])}">{ICON['back']}{e(prev_m[1])}</a><a href="{href(lang, cur, 'model/' + next_m[0])}">{e(next_m[1])}{ICON['arrow']}</a></div>
  </aside>
</section>
<section class="more"><div class="wrap"><div class="roster-head"><h2 class="h2">{e(t['m_more'])}</h2><a class="link-arrow" href="{href(lang, cur, 'models')}">{e(t['all_models'])}{ICON['arrow']}</a></div><div class="grid">{more}</div></div></section>
{request_block(lang, cur)}
</main>
{footer(lang, cur)}
{tail(lang, cur)}"""


def page_service(lang, key):
    t, s = T[lang], SERVICES[key][lang]
    cur = "services/" + key
    imgs = "".join(f'<img src="{asset(lang, cur, f"img/models/{p}.jpg")}" alt="" loading="lazy" width="900" height="1200">' for p in SERVICES[key]["img"])
    incl = "".join(f"<li>{e(x)}</li>" for x in s["incl"])
    if s["how"]:
        how = "".join(f'<li><span class="num">0{i + 1}</span><h3>{e(h)}</h3><p class="muted">{e(p)}</p></li>' for i, (h, p) in enumerate(s["how"]))
        how_block = f'<section class="how"><div class="wrap">{sec_head(None, t["how"])}<ol class="how-list">{how}</ol></div></section>'
    else:
        how_block = process(lang, cur)
    others = "".join(
        f'<a class="other-svc" href="{href(lang, cur, "services/" + k)}"><span>{e(SERVICES[k][lang]["title"])}</span><b>{e(SERVICES[k][lang]["price"])}</b>{ICON["arrow"]}</a>'
        for k in SERVICE_ORDER if k != key)
    video = ""
    if key == "video":
        video = f'<div class="svc-video"><video autoplay muted loop playsinline poster="{asset(lang, cur, "img/hero-poster.jpg")}"><source src="{asset(lang, cur, "video/hero-desktop.mp4")}" type="video/mp4"></video></div>'
    return f"""{head(lang, cur, s['title'] + ' — FIRST LOOK', s['lead'])}
{header(lang, cur)}
<main id="main" class="page">
<section class="page-hero svc-hero"><div class="wrap">
  <p class="crumbs"><a href="{href(lang, cur, '')}">FIRST LOOK</a> / {e(t['col_srv'])} / {e(s['title'])}</p>
  <div class="svc-hero-in">
    <div><h1 class="h-xl">{e(s['title'])}</h1><p class="muted lead">{e(s['lead'])}</p>
      <div class="svc-price"><span class="label">{e(t['price_from'])}</span><b>{e(s['price'])}</b><span class="muted">{e(s['per'])}</span></div>
      <a class="btn btn-chrome" href="#request" data-service="{s['plan']}">{e(t['order'])}</a></div>
    <div class="svc-collage">{imgs}</div>
  </div>
</div></section>
{video}
<section class="incl"><div class="wrap incl-in"><h2 class="h2">{e(t['included'])}</h2><ul class="checks big">{incl}</ul></div></section>
{how_block}
<section class="others"><div class="wrap"><p class="label">{e(t['col_srv'])}</p><div class="other-list">{others}</div></div></section>
{request_block(lang, cur)}
</main>
{footer(lang, cur)}
{tail(lang, cur)}"""


def page_doc(lang, key):
    t = T[lang]
    title, parts = DOCS[key][lang]
    cur = "docs/" + key
    body = "".join(f"<h2>{e(h)}</h2><p>{e(p)}</p>" for h, p in parts)
    nav = "".join(f'<a class="{"is-on" if k == key else ""}" href="{href(lang, cur, "docs/" + k)}">{e(DOCS[k][lang][0])}</a>' for k in DOC_ORDER)
    upd = "Обновлено 6 октября 2026" if lang == "ru" else "Updated 6 October 2026"
    return f"""{head(lang, cur, title + ' — FIRST LOOK', title)}
{header(lang, cur, has_req=False)}
<main id="main" class="page">
<section class="doc wrap"><aside class="doc-nav"><p class="label">{e(t['col_doc'])}</p>{nav}</aside>
<article class="doc-body"><p class="crumbs"><a href="{href(lang, cur, '')}">FIRST LOOK</a> / {e(title)}</p><h1 class="h-xl">{e(title)}</h1><p class="muted">{upd}</p>{body}</article></section>
</main>
{footer(lang, cur)}
{tail(lang, cur)}"""


def page_simple(lang, cur, h, p):
    t = T[lang]
    return f"""{head(lang, cur, h + ' — FIRST LOOK', p)}
{header(lang, cur, has_req=False)}
<main id="main" class="page">
<section class="simple"><div class="wrap"><h1 class="h-xl">{e(h)}</h1><p class="muted lead narrow" data-thanks-text>{e(p)}</p>
<div class="hero-cta"><a class="btn btn-white" href="{href(lang, cur, '')}">{e(t['home'])}</a><a class="btn btn-outline" href="{href(lang, cur, 'models')}">{e(t['to_models'])}</a></div></div></section>
</main>
{footer(lang, cur)}
{tail(lang, cur)}"""


# ── сборка ───────────────────────────────────────────────────────────────
def write(lang, slug, text):
    p = page_path(lang, slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    for d in ["model", "services", "docs", "en"]:
        shutil.rmtree(ROOT / d, ignore_errors=True)
    n = 0
    for lang in ("ru", "en"):
        t = T[lang]
        write(lang, "", page_home(lang)); n += 1
        write(lang, "models", page_models(lang)); n += 1
        for i in range(len(MODELS)):
            write(lang, "model/" + MODELS[i][0], page_model(lang, i)); n += 1
        for k in SERVICE_ORDER:
            write(lang, "services/" + k, page_service(lang, k)); n += 1
        for k in DOC_ORDER:
            write(lang, "docs/" + k, page_doc(lang, k)); n += 1
        write(lang, "thanks", page_simple(lang, "thanks", t["thanks_h"], t["thanks_p"])); n += 1
        if lang == "ru":
            write(lang, "404", page_simple(lang, "404", t["nf_h"], t["nf_p"])); n += 1
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("pages:", n)


if __name__ == "__main__":
    main()
