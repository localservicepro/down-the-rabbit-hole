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

  /* Quote modal: opened by any [data-open-quote] control, closed by Escape, backdrop or the close button */
  var modal = document.getElementById('quote-modal');
  var lastFocus = null;
  function openQuote(e) {
    if (!modal) return;
    if (e) e.preventDefault();
    closeMobile();
    lastFocus = document.activeElement;
    modal.hidden = false;
    requestAnimationFrame(function () { modal.classList.add('show'); });
    document.body.style.overflow = 'hidden';
    var first = modal.querySelector('input:not([type=hidden]):not(.hp)'); if (first) setTimeout(function () { first.focus(); }, 250);
  }
  function closeQuote() {
    if (!modal || modal.hidden) return;
    modal.classList.remove('show');
    setTimeout(function () { modal.hidden = true; }, 250);
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  if (modal) {
    document.querySelectorAll('[data-open-quote]').forEach(function (el) { el.addEventListener('click', openQuote); });
    modal.querySelector('.qm-close').addEventListener('click', closeQuote);
    modal.addEventListener('click', function (e) { if (e.target === modal) closeQuote(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeQuote(); });
    modal.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = modal.querySelectorAll('button, input:not([type=hidden]):not(.hp), select, textarea, a[href]');
      var a = f[0], z = f[f.length - 1];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    });
    if (location.hash === '#quote') openQuote();
  }

  /* Quote forms: native validation, then let the CRM tracking script capture the submit event and redirect */
  document.querySelectorAll('.quote-form').forEach(function (form) {
    var src = form.querySelector('[name=source_page]'); if (src) src.value = location.href;
    var err = form.querySelector('.ferror');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.classList.add('touched');
      var hp = form.querySelector('.hp');
      if (hp && hp.value) { return; }
      if (!form.checkValidity()) {
        err.hidden = false;
        var bad = form.querySelector(':invalid'); if (bad) bad.focus();
        return;
      }
      err.hidden = true;
      var btn = form.querySelector('.fsubmit');
      btn.disabled = true; btn.textContent = 'Sending…';
      if (window.fbq) { try { window.fbq('track', 'Lead'); } catch (x) {} }
      /* The external tracking script listens for this same submit event and sends the fields to the CRM.
         Give its request a moment to leave before navigating. */
      setTimeout(function () { window.location.assign(form.dataset.thankYou || '/thank-you'); }, 700);
    });
    form.querySelectorAll('input, select, textarea').forEach(function (c) {
      c.addEventListener('input', function () { if (form.checkValidity()) err.hidden = true; });
    });
  });

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
