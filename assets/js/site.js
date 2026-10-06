/* FIRST LOOK — поведение сайта по образцу models1.co.uk:
   меню и поиск поверх размытой страницы, избранное, фильтры, панель параметров при наведении,
   появление фото на странице модели, видео, вкладки «агентства», форма заявки. */
(function () {
  "use strict";
  var doc = document, body = doc.body, FL = window.FL || { models: [], t: {} };
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || doc).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); };

  /* ── оверлеи: меню, поиск ─────────────────────────── */
  function openOv(name) {
    var ov = $('[data-ov="' + name + '"]'); if (!ov) return;
    ov.classList.add("on"); ov.setAttribute("aria-hidden", "false"); body.classList.add("ov-open");
    if (name === "search") { var i = $("[data-search-input]"); setTimeout(function () { i.focus(); }, 60); renderSearch(""); }
  }
  function closeOv() {
    $$(".ov.on, .lightbox.on").forEach(function (o) { o.classList.remove("on"); o.setAttribute("aria-hidden", "true"); });
    body.classList.remove("ov-open");
    var lv = $(".lightbox video"); if (lv) lv.pause();
  }
  doc.addEventListener("click", function (e) {
    var o = e.target.closest("[data-open]"); if (o) { e.preventDefault(); openOv(o.getAttribute("data-open")); return; }
    if (e.target.closest("[data-close]") || e.target.classList.contains("ov") || e.target.classList.contains("lightbox")) closeOv();
  });
  doc.addEventListener("keydown", function (e) { if (e.key === "Escape") closeOv(); });

  /* ── гигантское вертикальное слово: 220 px как у Models 1, длинные слова ужимаем по высоте экрана ── */
  function fitSide() {
    $$(".side-word").forEach(function (el) {
      if (getComputedStyle(el).writingMode.indexOf("vertical") < 0) { el.style.fontSize = ""; return; }
      el.style.fontSize = "220px";
      var avail = window.innerHeight - el.getBoundingClientRect().top - 16 + window.scrollY * 0;
      var h = el.scrollHeight;
      if (h > avail) el.style.fontSize = Math.max(40, Math.floor(220 * avail / h)) + "px";
    });
  }
  fitSide();
  window.addEventListener("resize", fitSide);
  if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(fitSide);

  /* ── поиск по моделям ─────────────────────────────── */
  var sIn = $("[data-search-input]"), sRes = $("[data-search-results]"), sNone = $("[data-search-none]");
  function renderSearch(q) {
    if (!sRes) return;
    q = (q || "").trim().toLowerCase();
    var list = FL.models.filter(function (m) { return !q || m.name.indexOf(q) > -1; });
    sRes.innerHTML = list.map(function (m) { return '<a href="' + m.url + '"><img src="' + m.img + '" alt="" loading="lazy">' + m.name + "</a>"; }).join("");
    sNone.hidden = list.length > 0;
  }
  if (sIn) {
    sIn.addEventListener("input", function () { renderSearch(sIn.value); });
    sIn.addEventListener("keydown", function (e) { if (e.key === "Enter") { var a = $("a", sRes); if (a) location.href = a.href; } });
  }

  /* ── избранное (сохраняется в браузере) ────────────── */
  var KEY = "fl-favs";
  function favs() { try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; } }
  function saveFavs(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
  function paintFavs() {
    var f = favs();
    $$("[data-fav]").forEach(function (b) {
      var on = f.indexOf(b.getAttribute("data-fav")) > -1;
      b.classList.toggle("is-fav", on);
      b.setAttribute("aria-label", on ? FL.t.fav_remove : FL.t.fav_add);
      var lab = b.hasAttribute("data-fav-label") && $("span", b); if (lab) lab.textContent = on ? FL.t.fav_remove : FL.t.fav_add;
    });
    $$("[data-fav-count]").forEach(function (c) { c.textContent = f.length ? f.length : ""; });
  }
  doc.addEventListener("click", function (e) {
    var b = e.target.closest("[data-fav]"); if (!b) return;
    e.preventDefault(); e.stopPropagation();
    var s = b.getAttribute("data-fav"), f = favs(), i = f.indexOf(s);
    if (i > -1) f.splice(i, 1); else f.push(s);
    saveFavs(f); paintFavs(); renderFavPage();
  });
  function renderFavPage() {
    var grid = $("[data-fav-grid]"); if (!grid) return;
    var tpl = $("[data-tile-tpl]"), f = favs();
    grid.innerHTML = "";
    f.forEach(function (s) { var t = tpl.content.querySelector('.tile[data-slug="' + s + '"]'); if (t) grid.appendChild(t.cloneNode(true)); });
    $("[data-fav-empty]").hidden = f.length > 0;
    var send = $("[data-fav-send]");
    if (send) {
      send.hidden = !f.length;
      var names = f.map(function (s) { var m = FL.models.filter(function (x) { return x.slug === s; })[0]; return m ? m.name : s; });
      send.href = FL.applyUrl + "?service=license&model=" + encodeURIComponent(names.join(", "));
    }
    paintFavs(); flipTiles();
  }
  renderFavPage(); paintFavs();

  /* ── фильтры доски ────────────────────────────────── */
  $$("[data-filters]").forEach(function (bar) {
    var grid = $("[data-grid]"); if (!grid) return;
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("[data-filter]"); if (!b) return;
      var f = b.getAttribute("data-filter");
      $$("[data-filter]", bar).forEach(function (x) { x.classList.toggle("on", x === b); });
      $$(".tile", grid).forEach(function (t) { t.classList.toggle("is-hidden", f !== "all" && t.getAttribute("data-cats").split(" ").indexOf(f) < 0); });
      flipTiles();
      try { history.replaceState(null, "", f === "all" ? location.pathname : "?filter=" + f); } catch (err) {}
    });
    var q = new URLSearchParams(location.search).get("filter");
    if (q) { var b = $('[data-filter="' + q + '"]', bar); if (b) b.click(); }
  });

  /* ── панель при наведении, как у Models 1: в первом ряду — под карточкой,
        дальше — справа от фото, в последней колонке — слева ── */
  function flipTiles() {
    $$(".grid").forEach(function (grid) {
      var gr = grid.getBoundingClientRect(), tiles = $$(".tile:not(.is-hidden)", grid);
      var top0 = tiles.length ? tiles[0].getBoundingClientRect().top : 0;
      tiles.forEach(function (t) {
        var r = t.getBoundingClientRect();
        t.classList.toggle("below", Math.abs(r.top - top0) < 4);
        t.classList.toggle("flip", r.right + r.width + 120 > gr.right + 8);
      });
    });
  }
  flipTiles();
  window.addEventListener("resize", flipTiles);

  /* ── страница модели: фото проявляются при прокрутке, «закрыть» = назад ── */
  var gal = $$(".mp-gallery img");
  if (gal.length) {
    if ("IntersectionObserver" in window && !reduce) {
      var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add("in"); io.unobserve(x.target); } }); }, { rootMargin: "0px 0px -6% 0px" });
      gal.forEach(function (i) { io.observe(i); });
    } else gal.forEach(function (i) { i.classList.add("in"); });
  }
  $$("[data-back]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (doc.referrer && doc.referrer.indexOf(location.host) > -1 && history.length > 1) { e.preventDefault(); history.back(); }
    });
  });

  /* ── видео: на главной выбор ролика, в разделе — превью при наведении и просмотр ── */
  var hv = $("[data-home-video]");
  if (hv) {
    var phone = window.matchMedia("(max-width: 760px), (orientation: portrait)");
    var pick = function () {
      var k = phone.matches ? "mobile" : "desktop";
      if (hv.getAttribute("data-cur") === k) return;
      hv.setAttribute("data-cur", k); hv.poster = hv.getAttribute("data-poster-" + k);
      hv.src = hv.getAttribute("data-" + k); hv.load();
      if (!reduce) { var p = hv.play(); if (p && p.catch) p.catch(function () {}); }
    };
    pick();
    if (phone.addEventListener) phone.addEventListener("change", pick);
    if (reduce) hv.pause();
  }
  var lb = $("[data-lightbox]");
  $$(".vtile").forEach(function (t) {
    var v = $("video", t);
    t.addEventListener("mouseenter", function () { if (!reduce) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } });
    t.addEventListener("mouseleave", function () { v.pause(); });
    var open = function () {
      if (!lb) return;
      var lv = $("video", lb); lv.src = t.getAttribute("data-video"); lb.classList.add("on"); lb.setAttribute("aria-hidden", "false"); body.classList.add("ov-open");
      var p = lv.play(); if (p && p.catch) p.catch(function () {});
    };
    t.addEventListener("click", open);
    t.addEventListener("keydown", function (e) { if (e.key === "Enter") open(); });
  });

  /* ── вкладки «агентства» ──────────────────────────── */
  var tabs = $("[data-tabs]");
  if (tabs) {
    var show = function (k, push) {
      $$("[data-tab]", tabs).forEach(function (a) { a.classList.toggle("on", a.getAttribute("data-tab") === k); });
      $$("[data-pane]").forEach(function (p) { p.classList.toggle("on", p.getAttribute("data-pane") === k); });
      if (push) try { history.replaceState(null, "", "#" + k); } catch (e) {}
    };
    tabs.addEventListener("click", function (e) { var a = e.target.closest("[data-tab]"); if (!a) return; e.preventDefault(); show(a.getAttribute("data-tab"), true); });
    var h = location.hash.replace("#", "");
    if (h && $('[data-pane="' + h + '"]')) show(h, false);
  }

  /* ── форма заявки: подстановка услуги и модели из ссылки, проверка, переход ── */
  var form = $("[data-form]");
  if (form) {
    var qs = new URLSearchParams(location.search), sv = qs.get("service"), md = qs.get("model");
    if (sv) { var r = $('input[name="service"][value="' + sv + '"]', form); if (r) r.checked = true; }
    if (md) { $("[data-model-field]", form).value = md; var pk = $("[data-picked]", form); pk.hidden = false; $("b", pk).textContent = md; }
    if ((sv || md) && location.hash !== "#form") { var fs = $("#form"); if (fs) setTimeout(function () { fs.scrollIntoView({ behavior: reduce ? "auto" : "smooth" }); }, 250); }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var n = form.elements.name, m = form.elements.email, nf = n.closest(".field"), mf = m.closest(".field");
      nf.classList.toggle("is-err", !n.value.trim());
      mf.classList.toggle("is-err", !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(m.value.trim()));
      if (nf.classList.contains("is-err")) { n.focus(); return; }
      if (mf.classList.contains("is-err")) { m.focus(); return; }
      try { sessionStorage.setItem("fl-name", n.value.trim()); } catch (err) {}
      location.href = form.getAttribute("action");
    });
    $$("input", form).forEach(function (i) { i.addEventListener("input", function () { var f = i.closest(".field"); if (f) f.classList.remove("is-err"); }); });
  }
  var th = $("[data-thanks-text]");
  if (th && /thanks/.test(location.pathname)) {
    try { var nm = sessionStorage.getItem("fl-name"); if (nm) th.textContent = nm + ", " + th.textContent.charAt(0).toLowerCase() + th.textContent.slice(1); } catch (err) {}
  }
})();
