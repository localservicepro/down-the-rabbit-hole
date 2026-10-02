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
  /* Run fn on the visitor's first interaction, or `ms` after the load event, whichever comes first.
     Keeps third-party scripts and the hero video off the critical path. */
  function whenIdleOrInteracted(fn, ms) {
    var done = false, evs = ['pointerdown', 'keydown', 'touchstart', 'scroll', 'mousemove'];
    function run() { if (done) return; done = true; evs.forEach(function (e) { window.removeEventListener(e, run, { passive: true }); }); fn(); }
    evs.forEach(function (e) { window.addEventListener(e, run, { passive: true, once: true }); });
    var later = function () { setTimeout(run, ms); };
    if (document.readyState === 'complete') later(); else window.addEventListener('load', later);
  }

  var hv = document.querySelector('.hero-video');
  if (hv) {
    var conn = navigator.connection || {};
    var okData = !conn.saveData && !/2g/.test(conn.effectiveType || '');
    var okMotion = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (okData && okMotion) {
      var startVideo = function () {
        hv.preload = 'auto';
        hv.addEventListener('canplay', function () { hv.classList.add('ready'); var p = hv.play(); if (p && p.catch) p.catch(function () {}); }, { once: true });
        hv.load();
      };
      /* Phones: wait for a first interaction (or 5s) so the 700KB video never competes with the first paint. */
      if (window.matchMedia('(max-width: 760px)').matches) whenIdleOrInteracted(startVideo, 5000);
      else window.addEventListener('load', startVideo);
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
  function loadLead() { try { return JSON.parse(sessionStorage.getItem('dtrh_lead') || '{}') || {}; } catch (x) { return {}; } }
  function saveLead(d) { try { sessionStorage.setItem('dtrh_lead', JSON.stringify(d)); } catch (x) {} }
  function firstName(full) { var f = (full || '').trim().split(/\s+/)[0] || ''; return f ? f.charAt(0).toUpperCase() + f.slice(1) : ''; }
  /* ServiceM8: the server function creates the job (step 1) or adds the qualifying answers (step 2). */
  function sendToServiceM8(form) {
    if (!window.fetch) return Promise.resolve();
    var fields = {};
    new FormData(form).forEach(function (v, k) { if (typeof v === 'string') fields[k] = v; });
    var qualify = form.dataset.step === 'qualify', lead = loadLead();
    var payload = { step: qualify ? 'qualify' : 'quote', fields: fields, page: location.href };
    if (qualify && lead.sm8) { payload.job = lead.sm8.job; payload.token = lead.sm8.token; }
    if (!qualify) payload.photos = (form._photos || []).map(function (p) { return { data: p.data }; });
    return fetch('/api/quote', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && j.ok && j.job && j.token) { var l = loadLead(); l.sm8 = { job: j.job, token: j.token }; saveLead(l); } })
      .catch(function () {});
  }

  /* Photo picker: shrink each photo in the browser (max 1600px JPEG) so uploads are quick and fit the request limit. */
  var MAX_PHOTOS = 5, PHOTO_BUDGET = 3500000;
  function shrink(file) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        try {
          var draw = function (max, q) {
            var s = Math.min(1, max / Math.max(img.naturalWidth, img.naturalHeight));
            var c = document.createElement('canvas');
            c.width = Math.round(img.naturalWidth * s); c.height = Math.round(img.naturalHeight * s);
            c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
            return c.toDataURL('image/jpeg', q);
          };
          var data = draw(1600, 0.8);
          if (data.length > 900000) data = draw(1280, 0.72);
          URL.revokeObjectURL(url); resolve(data);
        } catch (e) { URL.revokeObjectURL(url); reject(e); }
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error('decode')); };
      img.src = url;
    });
  }
  document.querySelectorAll('[data-photos]').forEach(function (box) {
    var form = box.closest('.quote-form'), input = box.querySelector('.photo-input'),
        list = box.querySelector('.photo-list'), msg = box.querySelector('.photo-msg');
    form._photos = [];
    function say(t) { msg.textContent = t || ''; msg.hidden = !t; }
    function render() {
      list.innerHTML = '';
      form._photos.forEach(function (p, i) {
        var li = document.createElement('li'), im = document.createElement('img'), rm = document.createElement('button');
        im.src = p.data; im.alt = 'Photo ' + (i + 1); im.width = 72; im.height = 72;
        rm.type = 'button'; rm.className = 'photo-rm'; rm.setAttribute('aria-label', 'Remove photo ' + (i + 1)); rm.textContent = '×';
        rm.addEventListener('click', function () { form._photos.splice(i, 1); render(); say(''); });
        li.appendChild(im); li.appendChild(rm); list.appendChild(li);
      });
      box.classList.toggle('has-photos', form._photos.length > 0);
    }
    input.addEventListener('change', function () {
      var files = [].slice.call(input.files || []).filter(function (f) { return /^image\//.test(f.type) || /\.(jpe?g|png|webp|heic|heif)$/i.test(f.name); });
      input.value = '';
      if (!files.length) return;
      var room = MAX_PHOTOS - form._photos.length;
      if (room <= 0) { say('You can add up to ' + MAX_PHOTOS + ' photos.'); return; }
      if (files.length > room) say('Only the first ' + room + ' photo' + (room > 1 ? 's were' : ' was') + ' added (up to ' + MAX_PHOTOS + ').'); else say('Preparing photos…');
      var skipped = 0;
      files.slice(0, room).reduce(function (chain, f) {
        return chain.then(function () {
          return shrink(f).then(function (data) {
            var used = form._photos.reduce(function (n, p) { return n + p.data.length; }, 0);
            if (used + data.length > PHOTO_BUDGET) { skipped++; return; }
            form._photos.push({ data: data }); render();
          }, function () { skipped++; });
        });
      }, Promise.resolve()).then(function () {
        say(skipped ? skipped + ' photo' + (skipped > 1 ? 's' : '') + ' could not be added. Try a JPEG or PNG, or fewer photos.' : (files.length > room ? msg.textContent : ''));
      });
    });
  });

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
    if (btn) { btn.disabled = true; btn.textContent = (form._photos && form._photos.length) ? 'Uploading photos…' : 'Sending…'; }
    var dest = form.dataset.thankYou || '/thank-you';
    var ret = form.querySelector('[name=returning_customer]:checked');
    if (ret) {
      /* Step 1: remember who this is for the thank-you message and step 2 (this tab only, never in the URL). */
      var val = function (n) { var el = form.querySelector('[name=' + n + ']'); return el ? el.value.trim() : ''; };
      saveLead({ name: val('full_name'), email: val('email'), phone: val('phone'), returning: ret.value });
      if (ret.value === 'No' && form.dataset.next) dest = form.dataset.next;
    }
    if (form.dataset.step === 'qualify') { var l = loadLead(); l.qualified = true; saveLead(l); }
    else if (window.fbq) { try { window.fbq('track', 'Lead'); } catch (x) {} }
    /* Send to ServiceM8 (server function) and give the CRM tracking script a moment, then move on.
       The page waits for the upload so photos are not cut off, but never longer than 25 seconds. */
    var went = false;
    var go = function () { if (!went) { went = true; window.location.assign(dest); } };
    var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
    Promise.all([ensureTracker().then(function () { return wait(900); }), Promise.race([sendToServiceM8(form), wait(25000)])]).then(go, go);
    setTimeout(go, 30000);
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
    ensureTracker().then(function () {
      var ev;
      try { ev = new SubmitEvent('submit', { bubbles: true, cancelable: true, submitter: btn }); }
      catch (x) { ev = document.createEvent('Event'); ev.initEvent('submit', true, true); }
      form.dispatchEvent(ev);
    });
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

  /* "Used us before?" Yes sends straight through; No goes on to a few quick questions, so relabel the button. */
  document.querySelectorAll('.quote-form [name=returning_customer]').forEach(function (r) {
    r.addEventListener('change', function () {
      var form = quoteFormOf(r), lbl = form && form.querySelector('.fsubmit-label');
      if (lbl && !form.dataset.sending) lbl.textContent = r.value === 'No' ? 'Next: a few quick questions' : 'Send my quote request';
    });
  });

  /* Step 2 (qualifying questions): greet by name and carry the contact details over so the CRM matches the contact. */
  var qd = document.querySelector('.qualify-form');
  if (qd) {
    var lead = loadLead(), box = qd.querySelector('.qf-contact');
    if (lead.email || lead.phone) {
      ['full_name', 'email', 'phone'].forEach(function (k) {
        var el = qd.querySelector('[name=' + k + ']'), v = lead[k === 'full_name' ? 'name' : k];
        if (el && v) el.value = v;
      });
      var t = document.getElementById('qd-title'), fn = firstName(lead.name);
      if (t && fn) t.textContent = 'Thanks, ' + fn + '. Just a few quick questions';
    } else if (box) {
      /* Opened directly, without step 1: ask for contact details here instead. */
      box.hidden = false;
      box.querySelectorAll('input').forEach(function (i) { i.required = true; });
    }
  }

  /* Thank-you page: personal message for returning and new customers. */
  var tyTitle = document.getElementById('ty-title');
  if (tyTitle) {
    var ld = loadLead(), name = firstName(ld.name), tyLead = document.getElementById('ty-lead');
    if (ld.returning === 'Yes') {
      tyTitle.textContent = name ? 'Thanks for coming back, ' + name + '!' : 'Thanks for coming back!';
      if (tyLead) tyLead.textContent = 'Great to hear from you again. Michael has your request and will be in touch during business hours to get you booked in. If it is urgent, text 0423 720 317.';
    } else if (ld.returning === 'No') {
      tyTitle.textContent = name ? 'Thanks, ' + name + ', your quote request is in' : 'Thanks, your quote request is in';
      if (tyLead) tyLead.textContent = (ld.qualified ? 'Thanks for answering those questions. ' : '') + 'Welcome to Down the Rabbit Hole AUST. Michael will review your details and come back to you with a clear, upfront quote during business hours. If it is urgent, text 0423 720 317.';
    }
  }

  /* Review widget: load the reputation script, then the iframe, only when the section nears the viewport. */
  document.querySelectorAll('[data-review-widget]').forEach(function (box) {
    var frame = box.querySelector('iframe[data-src]');
    if (!frame) return;
    function start() {
      if (box.dataset.started) return; box.dataset.started = '1';
      var go = function () { frame.src = frame.getAttribute('data-src'); };
      frame.addEventListener('load', function () {
        /* the widget script sizes the iframe; once it has, drop the placeholder height */
        setTimeout(function () { if (frame.style.height || frame.getAttribute('height')) box.classList.add('loaded'); }, 1500);
      });
      if (document.querySelector('script[data-review-widget-js]')) { go(); return; }
      var sc = document.createElement('script');
      sc.src = box.getAttribute('data-script'); sc.async = true; sc.setAttribute('data-review-widget-js', '');
      sc.onload = go; sc.onerror = go;
      document.body.appendChild(sc);
    }
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) { if (es.some(function (e) { return e.isIntersecting; })) { io.disconnect(); start(); } }, { rootMargin: '600px 0px' });
      io.observe(box);
    } else { start(); }
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
  /* CRM tracking script (external-tracking.js). It initialises immediately when loaded after the page is
     ready and attaches to every form (plus a MutationObserver for later forms), so it is loaded lazily too.
     A quote submit waits for it (ensureTracker) so no submission is missed. */
  var trackerPromise = null;
  function ensureTracker() {
    if (trackerPromise) return trackerPromise;
    var id = document.documentElement.getAttribute('data-tracking-id');
    if (!id) return (trackerPromise = Promise.resolve());
    trackerPromise = new Promise(function (resolve) {
      var s = document.createElement('script');
      s.src = 'https://app.downtherabbitholeaust.com/js/external-tracking.js';
      s.setAttribute('data-tracking-id', id);
      s.async = true;
      s.onload = function () { setTimeout(resolve, 50); };
      s.onerror = function () { resolve(); };
      setTimeout(resolve, 4000);
      document.head.appendChild(s);
    });
    return trackerPromise;
  }
  whenIdleOrInteracted(function () { ensureTracker(); loadPixel(); }, 5000);
})();
