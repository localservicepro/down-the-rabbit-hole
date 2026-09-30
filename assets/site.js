/* Down the Rabbit Hole AUST — nav, mobile panel, reveal, before/after, deferred third parties */
(function () {
  'use strict';
  var header = document.querySelector('.site-header');
  var dd = document.querySelector('.nav-dropdown');
  var hoverCapable = window.matchMedia('(hover: hover)').matches;

  /* Sticky header: transparent over hero, frosted after 40px */
  function onScroll() { if (header) header.classList.toggle('scrolled', window.scrollY > 40); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* Services mega-dropdown: hover (pointer devices) + click/tap + Escape */
  if (dd) {
    var trigger = dd.querySelector('.nav-trigger');
    var byHover = false;
    var open = function () { dd.classList.add('open'); trigger.setAttribute('aria-expanded', 'true'); };
    var close = function () { dd.classList.remove('open'); trigger.setAttribute('aria-expanded', 'false'); byHover = false; };
    if (hoverCapable) {
      dd.addEventListener('mouseenter', function () { if (!dd.classList.contains('open')) { byHover = true; open(); } });
      dd.addEventListener('mouseleave', function () { if (byHover) close(); });
    }
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      if (dd.classList.contains('open') && !byHover) { close(); } else { byHover = false; open(); }
    });
    document.addEventListener('click', function (e) { if (!dd.contains(e.target)) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { close(); closeMobile(); } });
    dd.addEventListener('focusout', function (e) { if (!dd.contains(e.relatedTarget)) close(); });
  }

  /* Mobile slide-in panel with Services accordion */
  var burger = document.querySelector('.nav-burger');
  var panel = document.querySelector('.mobile-panel');
  var backdrop = document.querySelector('.mobile-backdrop');
  function openMobile() {
    if (!panel) return;
    panel.classList.add('open'); backdrop.classList.add('open');
    burger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    var first = panel.querySelector('.mp-close'); if (first) first.focus();
  }
  function closeMobile() {
    if (!panel || !panel.classList.contains('open')) return;
    panel.classList.remove('open'); backdrop.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    burger.focus();
  }
  if (burger && panel) {
    burger.addEventListener('click', openMobile);
    backdrop.addEventListener('click', closeMobile);
    panel.querySelector('.mp-close').addEventListener('click', closeMobile);
    panel.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', closeMobile); });
    var acc = panel.querySelector('.mp-acc');
    if (acc) {
      var sub = panel.querySelector('.mp-sub');
      acc.addEventListener('click', function () {
        var isOpen = sub.classList.toggle('open');
        acc.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    }
  }

  /* Scroll reveal */
  var rv = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window && rv.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    rv.forEach(function (el) { io.observe(el); });
  } else { rv.forEach(function (el) { el.classList.add('in'); }); }

  /* Before / after compare */
  document.querySelectorAll('.ba').forEach(function (ba) {
    var range = ba.querySelector('.ba-range');
    if (!range) return;
    var set = function (v) { ba.style.setProperty('--pos', v + '%'); };
    range.addEventListener('input', function () { set(range.value); });
    set(range.value);
  });
  var thumbs = document.querySelectorAll('.ba-thumb');
  if (thumbs.length) {
    var feat = document.getElementById('ba-featured');
    var before = feat.querySelector('.ba-before'), after = feat.querySelector('.ba-after');
    var cap = document.getElementById('ba-caption');
    thumbs.forEach(function (t) {
      t.addEventListener('click', function () {
        thumbs.forEach(function (x) { x.classList.remove('active'); x.setAttribute('aria-pressed', 'false'); });
        t.classList.add('active'); t.setAttribute('aria-pressed', 'true');
        before.src = t.dataset.before; before.alt = t.dataset.beforeAlt;
        after.src = t.dataset.after; after.alt = t.dataset.afterAlt;
        if (cap) cap.textContent = t.dataset.caption;
        feat.querySelector('.ba-range').value = 50; feat.style.setProperty('--pos', '50%');
      });
    });
  }

  /* Facebook pixel: deferred until after first paint / load */
  function loadPixel() {
    if (window.fbq) return;
    var n = window.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
    if (!window._fbq) window._fbq = n;
    n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
    var s = document.createElement('script'); s.async = true; s.src = 'https://connect.facebook.net/en_US/fbevents.js';
    document.head.appendChild(s);
    window.fbq('init', '25766325546287202');
    window.fbq('track', 'PageView');
  }
  var idle = window.requestIdleCallback || function (cb) { setTimeout(cb, 1500); };
  window.addEventListener('load', function () { idle(loadPixel, { timeout: 4000 }); });
})();
