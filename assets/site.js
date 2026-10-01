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

  /* Mega-dropdowns (Services, Blog): hover (pointer devices) + click/tap + Escape, one open at a time */
  var dropdowns = Array.prototype.slice.call(document.querySelectorAll('.nav-dropdown'));
  var closeAll = function () { dropdowns.forEach(function (d) { d.classList.remove('open'); d.querySelector('.nav-trigger').setAttribute('aria-expanded', 'false'); d.byHover = false; }); };
  dropdowns.forEach(function (dd) {
    var trigger = dd.querySelector('.nav-trigger');
    var open = function () { closeAll(); dd.classList.add('open'); trigger.setAttribute('aria-expanded', 'true'); };
    var close = function () { dd.classList.remove('open'); trigger.setAttribute('aria-expanded', 'false'); dd.byHover = false; };
    if (hoverCapable) {
      dd.addEventListener('mouseenter', function () { if (!dd.classList.contains('open')) { open(); dd.byHover = true; } });
      dd.addEventListener('mouseleave', function () { if (dd.byHover) close(); });
    }
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      if (dd.classList.contains('open') && !dd.byHover) { close(); } else { open(); dd.byHover = false; }
    });
    dd.addEventListener('focusout', function (e) { if (!dd.contains(e.relatedTarget)) close(); });
  });
  if (dropdowns.length) {
    document.addEventListener('click', function (e) { if (!dropdowns.some(function (d) { return d.contains(e.target); })) closeAll(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeAll(); closeMobile(); } });
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
    panel.querySelectorAll('.mp-acc').forEach(function (acc) {
      var sub = document.getElementById(acc.getAttribute('aria-controls'));
      acc.addEventListener('click', function () {
        var isOpen = sub.classList.toggle('open');
        acc.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    });
  }

  /* Hero background video: load after first paint, only when motion and data allow */
  var hv = document.querySelector('.hero-video');
  if (hv) {
    var conn = navigator.connection || {};
    var okData = !conn.saveData && !/2g/.test(conn.effectiveType || '');
    var okMotion = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (okData && okMotion) {
      window.addEventListener('load', function () {
        hv.preload = 'auto';
        hv.addEventListener('canplay', function () { hv.classList.add('ready'); var p = hv.play(); if (p && p.catch) p.catch(function () {}); }, { once: true });
        hv.load();
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

  /* Quote forms. The CRM tracking script (external-tracking.js) listens for submit events on the page and
     may stop them or cancel their default. To stay independent of it we:
     1. catch the submit button click in the capture phase on window (runs before every other listener),
     2. validate, then dispatch our own submit event so the tracking script can still read the fields,
     3. redirect to the thank-you page on a timer that no other listener can cancel. */
  function quoteFormOf(el) { return el && el.closest ? el.closest('.quote-form') : null; }
  function showError(form, show) { var err = form.querySelector('.ferror'); if (err) err.hidden = !show; }
  function startSend(form) {
    if (form.dataset.sending) return false;
    form.classList.add('touched');
    var hp = form.querySelector('.hp input');
    if (hp && hp.value) {
      /* Honeypot filled: almost certainly a bot. Show the thank-you page but do not pass the submission on. */
      form.dataset.sending = '1';
      setTimeout(function () { window.location.assign(form.dataset.thankYou || '/thank-you'); }, 300);
      return false;
    }
    if (!form.checkValidity()) {
      showError(form, true);
      var bad = form.querySelector(':invalid');
      if (bad && bad.classList.contains('ms-value')) { var ms = bad.closest('[data-ms]'); openMs(ms, true); ms.querySelector('.ms-toggle').focus(); }
      else if (bad) bad.focus();
      return false;
    }
    showError(form, false);
    form.dataset.sending = '1';
    var btn = form.querySelector('.fsubmit');
    if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
    if (window.fbq) { try { window.fbq('track', 'Lead'); } catch (x) {} }
    var dest = form.dataset.thankYou || '/thank-you';
    setTimeout(function () { window.location.assign(dest); }, 800);
    setTimeout(function () { if (location.pathname.indexOf('thank-you') === -1) window.location.href = dest; }, 2500);
    return true;
  }
  window.addEventListener('click', function (e) {
    var btn = e.target && e.target.closest ? e.target.closest('.quote-form .fsubmit') : null;
    if (!btn) return;
    var form = quoteFormOf(btn);
    e.preventDefault();
    if (!startSend(form)) { e.stopImmediatePropagation(); return; }
    /* Let the tracking script see a real submit event with the values in place. A synthetic submit does
       not trigger native navigation, so nothing else has to be cancelled. */
    var ev;
    try { ev = new SubmitEvent('submit', { bubbles: true, cancelable: true, submitter: btn }); }
    catch (x) { ev = document.createEvent('Event'); ev.initEvent('submit', true, true); }
    form.dispatchEvent(ev);
  }, true);
  window.addEventListener('submit', function (e) {
    var form = quoteFormOf(e.target);
    if (!form) return;
    e.preventDefault(); /* never let the browser navigate with the field values in the URL */
    if (form.dataset.sending) return; /* our own dispatched event: pass it on to other listeners */
    if (!startSend(form)) e.stopImmediatePropagation(); /* Enter key on an invalid form */
  }, true);
  /* Multi-select "Service needed": checkboxes write one comma-separated value into the named field,
     so the CRM receives a single service_needed value. */
  function openMs(ms, open) {
    var t = ms.querySelector('.ms-toggle'), p = ms.querySelector('.ms-panel');
    t.setAttribute('aria-expanded', open ? 'true' : 'false'); p.hidden = !open;
  }
  document.querySelectorAll('[data-ms]').forEach(function (ms) {
    var toggle = ms.querySelector('.ms-toggle'), summary = ms.querySelector('.ms-summary'), value = ms.querySelector('.ms-value');
    var boxes = ms.querySelectorAll('.ms-opt input');
    function sync() {
      var picked = [].filter.call(boxes, function (b) { return b.checked; }).map(function (b) { return b.value; });
      value.value = picked.join(', ');
      ms.classList.toggle('has-value', picked.length > 0);
      summary.textContent = !picked.length ? 'Select…' : picked.length <= 2 ? picked.join(', ') : picked.length + ' services selected';
      value.dispatchEvent(new Event('input', { bubbles: true }));
    }
    toggle.addEventListener('click', function () { openMs(ms, toggle.getAttribute('aria-expanded') !== 'true'); });
    boxes.forEach(function (b) { b.addEventListener('change', sync); });
    ms.querySelector('.ms-done').addEventListener('click', function () { openMs(ms, false); toggle.focus(); });
    ms.addEventListener('keydown', function (e) { if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { e.stopPropagation(); openMs(ms, false); toggle.focus(); } });
    document.addEventListener('click', function (e) { if (!ms.contains(e.target)) openMs(ms, false); });
  });
  document.querySelectorAll('.quote-form').forEach(function (form) {
    var src = form.querySelector('[name=source_page]'); if (src) src.value = location.href;
    form.querySelectorAll('input, select, textarea').forEach(function (c) {
      c.addEventListener('input', function () { if (form.checkValidity()) showError(form, false); });
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
