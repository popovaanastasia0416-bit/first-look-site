/* FIRST LOOK — поведение сайта: шапка, меню, фильтры, путь фотосессии, форма заявки. */
(function () {
  "use strict";
  var doc = document, body = doc.body;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* шапка: прозрачная на видео, тёмная после прокрутки */
  var header = doc.querySelector("[data-header]");
  function onScroll() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 40);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* мобильное меню */
  var burger = doc.querySelector("[data-burger]");
  function closeMenu() {
    body.classList.remove("menu-open");
    if (burger) burger.setAttribute("aria-expanded", "false");
  }
  if (burger) {
    burger.addEventListener("click", function () {
      var open = body.classList.toggle("menu-open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    doc.querySelectorAll("[data-mobile-menu] a").forEach(function (a) { a.addEventListener("click", closeMenu); });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMenu(); });
  }

  /* «Наверх» — работает и там, где нет якоря #top */
  doc.querySelectorAll("[data-top]").forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });
  });

  /* видео первого экрана */
  var video = doc.querySelector("[data-hero-video]"), vt = doc.querySelector("[data-video-toggle]");
  if (video && vt) {
    if (reduce) { video.pause(); vt.classList.add("is-paused"); }
    else {
      var p = video.play();
      if (p && p.catch) p.catch(function () { vt.classList.add("is-paused"); });
    }
    vt.addEventListener("click", function () {
      if (video.paused) { video.play(); vt.classList.remove("is-paused"); } else { video.pause(); vt.classList.add("is-paused"); }
    });
  }

  /* фильтры каталога */
  doc.querySelectorAll("[data-filters]").forEach(function (bar) {
    var section = bar.closest(".filter-bar").nextElementSibling;
    var cards = section.querySelectorAll(".m-card");
    var count = section.querySelector("[data-count]"), empty = section.querySelector("[data-empty]");
    bar.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-filter]");
      if (!btn) return;
      var f = btn.getAttribute("data-filter"), shown = 0;
      bar.querySelectorAll(".pill").forEach(function (p) { p.classList.toggle("is-on", p === btn); });
      cards.forEach(function (c) {
        var ok = f === "all" || c.getAttribute("data-cats").split(" ").indexOf(f) > -1;
        c.classList.toggle("is-hidden", !ok);
        if (ok) shown++;
      });
      if (count) count.textContent = shown;
      if (empty) empty.hidden = shown > 0;
      try { history.replaceState(null, "", f === "all" ? location.pathname : "?filter=" + f); } catch (err) {}
    });
    var q = new URLSearchParams(location.search).get("filter");
    if (q) { var b = bar.querySelector('[data-filter="' + q + '"]'); if (b) b.click(); }
  });

  /* путь фотосессии: шаги сменяются по кругу, пока блок на экране */
  doc.querySelectorAll("[data-path]").forEach(function (path) {
    var steps = path.querySelectorAll(".step"), active = 0, timer = null;
    function render() {
      path.setAttribute("data-active", active);
      steps.forEach(function (s, i) {
        s.classList.toggle("is-on", i <= active);
        s.classList.toggle("is-act", i === active);
        s.classList.toggle("is-done", i < active);
      });
    }
    function tick() { active = (active + 1) % steps.length; render(); timer = setTimeout(tick, active === steps.length - 1 ? 2800 : 2200); }
    render();
    if (reduce) { active = steps.length - 1; render(); return; }
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) {
        if (x.isIntersecting && !timer) timer = setTimeout(tick, 1600);
        if (!x.isIntersecting && timer) { clearTimeout(timer); timer = null; }
      });
    }, { threshold: 0.35 });
    io.observe(path);
    steps.forEach(function (s, i) { s.addEventListener("click", function () { clearTimeout(timer); active = i; render(); timer = setTimeout(tick, 4000); }); });
  });

  /* кнопки «Заказать / Арендовать»: выбирают услугу и модель в форме и прокручивают к ней */
  var form = doc.querySelector("[data-form]");
  function prefill(service, model) {
    if (!form) return;
    if (service) { var r = form.querySelector('input[name="service"][value="' + service + '"]'); if (r) r.checked = true; }
    var mf = form.querySelector("[data-model-field]"), mp = form.querySelector("[data-picked-model]");
    if (model && mf && mp) { mf.value = model; mp.hidden = false; mp.querySelector("b").textContent = model; }
  }
  doc.addEventListener("click", function (e) {
    var a = e.target.closest("[data-service],[data-model],[data-scroll-request]");
    if (!a || !form) return;
    prefill(a.getAttribute("data-service"), a.getAttribute("data-model"));
    if (a.getAttribute("href") === "#request") {
      e.preventDefault();
      closeMenu();
      doc.getElementById("request").scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
      setTimeout(function () { var n = form.querySelector('input[name="name"]'); if (n) n.focus({ preventScroll: true }); }, reduce ? 0 : 700);
    }
  });

  /* форма: проверка и переход на «Заявка отправлена» */
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      var name = form.elements.name, email = form.elements.email;
      var nf = name.closest(".field"), ef = email.closest(".field");
      nf.classList.toggle("is-err", !name.value.trim());
      ef.classList.toggle("is-err", !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim()));
      if (nf.classList.contains("is-err")) { ok = false; name.focus(); }
      else if (ef.classList.contains("is-err")) { ok = false; email.focus(); }
      if (!ok) return;
      try { sessionStorage.setItem("fl-name", name.value.trim()); } catch (err) {}
      location.href = form.getAttribute("action");
    });
    form.querySelectorAll("input").forEach(function (i) {
      i.addEventListener("input", function () { var f = i.closest(".field"); if (f) f.classList.remove("is-err"); });
    });
  }

  /* «Заявка отправлена»: обращаемся по имени */
  var thanks = doc.querySelector("[data-thanks-text]");
  if (thanks) {
    try {
      var nm = sessionStorage.getItem("fl-name");
      if (nm) thanks.textContent = nm + ", " + thanks.textContent.charAt(0).toLowerCase() + thanks.textContent.slice(1);
    } catch (err) {}
  }

  /* мягкое появление блоков */
  if (!reduce && "IntersectionObserver" in window) {
    var els = doc.querySelectorAll(".sec-head,.svc,.plan,.faq-item,.intro-in>*,.how-list li,.other-svc");
    var ro = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add("is-in"); ro.unobserve(x.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (el) { el.classList.add("reveal"); ro.observe(el); });
  }
})();
