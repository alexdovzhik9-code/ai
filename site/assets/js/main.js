/* Romantik Hotel Namenlos & Fischerwiege — site behaviour.
   No dependencies. Every feature degrades to plain HTML if this file fails. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------------------------------------------------- mobile navigation */
  var toggle = document.getElementById('navToggle');
  var panel = document.getElementById('navPanel');

  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.setAttribute('aria-label', open ? 'Menü öffnen' : 'Menü schließen');
      panel.classList.toggle('is-open', !open);
    });

    // Close on Escape and when a link is followed.
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Menü öffnen');
        panel.classList.remove('is-open');
        toggle.focus();
      }
    });
    panel.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        toggle.setAttribute('aria-expanded', 'false');
        panel.classList.remove('is-open');
      }
    });
  }

  /* ------------------------------------------------ header scroll state */
  var header = document.getElementById('siteHeader');
  if (header) {
    var stick = function () {
      header.classList.toggle('is-stuck', window.scrollY > 24);
    };
    stick();
    window.addEventListener('scroll', stick, { passive: true });
  }

  /* ------------------------------------------------------- theme toggle */
  var themeBtn = document.getElementById('themeToggle');
  if (themeBtn) {
    var systemDark = window.matchMedia('(prefers-color-scheme: dark)');

    var current = function () {
      return document.documentElement.dataset.theme ||
             (systemDark.matches ? 'dark' : 'light');
    };
    var paint = function () {
      themeBtn.dataset.mode = current();
    };

    paint();
    systemDark.addEventListener('change', paint);

    themeBtn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('hn-theme', next); } catch (e) {}
      paint();
    });
  }

  /* --------------------------------------------------- reveal on scroll */
  var revealables = document.querySelectorAll('[data-reveal]');

  if (!revealables.length) {
    // nothing to do
  } else if (reduceMotion.matches || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(revealables, function (el) {
      el.classList.add('is-visible');
    });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });

    Array.prototype.forEach.call(revealables, function (el, i) {
      el.style.transitionDelay = Math.min(i % 4, 3) * 70 + 'ms';
      observer.observe(el);
    });

    // Safety net: whatever is already on screen once everything has loaded is
    // shown outright, so a missed observer callback can never hide content.
    window.addEventListener('load', function () {
      Array.prototype.forEach.call(revealables, function (el) {
        var box = el.getBoundingClientRect();
        if (box.top < window.innerHeight && box.bottom > 0) {
          el.classList.add('is-visible');
          observer.unobserve(el);
        }
      });
    });
  }

  /* ------------------------------------------------------- accordions */
  Array.prototype.forEach.call(
    document.querySelectorAll('.accordion__trigger'),
    function (trigger) {
      trigger.addEventListener('click', function () {
        var open = trigger.getAttribute('aria-expanded') === 'true';
        var panelEl = document.getElementById(trigger.getAttribute('aria-controls'));
        trigger.setAttribute('aria-expanded', String(!open));
        if (panelEl) panelEl.hidden = open;
      });
    }
  );

  /* ------------------------------------- date fields: sane minimum dates */
  var today = new Date().toISOString().slice(0, 10);
  var arrival = document.querySelectorAll('input[name="anreise"]');
  var departure = document.querySelectorAll('input[name="abreise"]');

  Array.prototype.forEach.call(arrival, function (from) {
    from.min = today;
    from.addEventListener('change', function () {
      Array.prototype.forEach.call(departure, function (to) {
        to.min = from.value || today;
        if (to.value && to.value <= from.value) to.value = '';
      });
    });
  });
  Array.prototype.forEach.call(departure, function (to) { to.min = today; });

  /* ------------------------- carry the hero search over to the long form */
  var params = new URLSearchParams(window.location.search);
  ['anreise', 'abreise', 'personen', 'haus'].forEach(function (key) {
    var value = params.get(key);
    if (!value) return;
    var field = document.querySelector('#anfrage [name="' + key + '"]');
    if (field) field.value = value;
  });

  /* -------------------------------------------------------- footer year */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
