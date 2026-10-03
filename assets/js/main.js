/* VinFast eBus — site interactions (vanilla, no dependencies) */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var EDGE = 8; // px tolerance for sub-pixel snap positions

  function each(list, fn) {
    Array.prototype.forEach.call(list, fn);
  }

  // Dots are only rendered when there is something to paginate
  function renderDots(container, count, onClick) {
    if (!container) return [];
    container.innerHTML = '';
    container.hidden = count < 2;
    var dots = [];
    for (var i = 0; i < count && count > 1; i++) {
      var dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'dots__dot';
      dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      dot.addEventListener('click', onClick.bind(null, i));
      container.appendChild(dot);
      dots.push(dot);
    }
    return dots;
  }

  /* ---------- Mobile header menu ---------- */
  function initHeader() {
    var header = document.querySelector('[data-header]');
    var toggle = header && header.querySelector('[data-header-toggle]');
    if (!toggle) return;

    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }

  /* ---------- Fade slider ([data-fader]) ----------
     Every element with data-fade-slide="n" belongs to slide n, so the text
     and the image of one slide may live in different containers. */
  function initFader(root) {
    var slides = root.querySelectorAll('[data-fade-slide]');
    var count = 0;
    each(slides, function (el) { count = Math.max(count, Number(el.dataset.fadeSlide) + 1); });
    if (!count) return;

    var current = 0;
    var dots = renderDots(root.querySelector('[data-fade-dots]'), count, go);
    var prevs = root.querySelectorAll('[data-fade-prev]');
    var nexts = root.querySelectorAll('[data-fade-next]');
    var loop = root.hasAttribute('data-fade-loop');

    function go(index) {
      current = loop ? (index + count) % count : Math.max(0, Math.min(count - 1, index));
      each(slides, function (el) {
        var active = Number(el.dataset.fadeSlide) === current;
        el.classList.toggle('is-active', active);
        el.setAttribute('aria-hidden', String(!active));
      });
      dots.forEach(function (dot, i) { dot.classList.toggle('is-active', i === current); });
      if (!loop) {
        each(prevs, function (b) { b.disabled = current === 0; });
        each(nexts, function (b) { b.disabled = current === count - 1; });
      }
    }

    each(prevs, function (b) { b.addEventListener('click', function () { go(current - 1); }); });
    each(nexts, function (b) { b.addEventListener('click', function () { go(current + 1); }); });

    // Swipe on touch devices
    var startX = null;
    root.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    root.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) go(current + (dx < 0 ? 1 : -1));
      startX = null;
    });

    go(0);
  }

  /* ---------- Scroll-snap carousels ([data-carousel]) ---------- */
  function initCarousel(root) {
    var track = root.querySelector('[data-carousel-track]');
    if (!track) return null;

    var prevs = root.querySelectorAll('[data-carousel-prev]');
    var nexts = root.querySelectorAll('[data-carousel-next]');
    var dotsBox = root.querySelector('[data-carousel-dots]');
    var start = Number(root.dataset.carouselStart || 0);
    var dots = [];

    function slides() {
      return Array.prototype.filter.call(track.children, function (el) { return !el.hidden; });
    }

    function step() {
      var items = slides();
      if (items.length < 2) return track.clientWidth;
      return items[1].offsetLeft - items[0].offsetLeft;
    }

    function index() {
      var max = track.scrollWidth - track.clientWidth;
      if (max > EDGE && track.scrollLeft >= max - EDGE) return slides().length - 1;
      return Math.round(track.scrollLeft / step());
    }

    function scrollToIndex(i, instant) {
      // 'instant' (not 'auto') so CSS scroll-behavior: smooth doesn't animate it
      track.scrollTo({ left: i * step(), behavior: instant || reduceMotion ? 'instant' : 'smooth' });
    }

    function update() {
      var max = track.scrollWidth - track.clientWidth;
      each(prevs, function (b) { b.disabled = track.scrollLeft <= EDGE; });
      each(nexts, function (b) { b.disabled = track.scrollLeft >= max - EDGE; });
      var current = index();
      dots.forEach(function (dot, i) { dot.classList.toggle('is-active', i === current); });
    }

    function refresh(startIndex) {
      dots = renderDots(dotsBox, slides().length, scrollToIndex);
      track.scrollLeft = 0;
      if (startIndex) scrollToIndex(startIndex, true);
      update();
    }

    each(prevs, function (b) { b.addEventListener('click', function () { scrollToIndex(index() - 1); }); });
    each(nexts, function (b) { b.addEventListener('click', function () { scrollToIndex(index() + 1); }); });

    var ticking = false;
    track.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { update(); ticking = false; });
    }, { passive: true });
    window.addEventListener('resize', update);

    enableMouseDrag(track, scrollToIndex, index);
    refresh(start);
    return { refresh: refresh };
  }

  // Lets desktop mouse users drag carousels (some have no arrows on desktop)
  function enableMouseDrag(track, scrollToIndex, index) {
    var startX = 0;
    var startScroll = 0;
    var dragging = false;
    var moved = false;

    track.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      if (track.scrollWidth <= track.clientWidth) return;
      dragging = true;
      moved = false;
      startX = e.clientX;
      startScroll = track.scrollLeft;
    });

    window.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) < 5) return;
      if (!moved) {
        moved = true;
        track.classList.add('is-dragging');
      }
      track.scrollLeft = startScroll - dx;
    });

    window.addEventListener('pointerup', function () {
      if (!dragging) return;
      dragging = false;
      if (!moved) return;
      track.classList.remove('is-dragging');
      scrollToIndex(index());
    });

    // Swallow the click that ends a drag so links/buttons don't fire
    track.addEventListener('click', function (e) {
      if (!moved) return;
      e.preventDefault();
      e.stopPropagation();
      moved = false;
    }, true);
    track.addEventListener('dragstart', function (e) { e.preventDefault(); });
  }

  /* ---------- EB12 / EB8 switcher ([data-model-switch]) ---------- */
  function initModelSwitch(carousels) {
    each(document.querySelectorAll('[data-model-switch]'), function (section) {
      var tabs = section.querySelectorAll('[data-model-tab]');
      var carouselRoot = section.querySelector('[data-carousel]');

      function select(model) {
        each(tabs, function (tab) {
          tab.setAttribute('aria-selected', String(tab.dataset.modelTab === model));
        });
        each(section.querySelectorAll('[data-model]'), function (el) {
          el.hidden = el.dataset.model !== model;
        });
        var carousel = carousels.get(carouselRoot);
        if (carousel) carousel.refresh();
      }

      each(tabs, function (tab) {
        tab.addEventListener('click', function () { select(tab.dataset.modelTab); });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initHeader();
    each(document.querySelectorAll('[data-fader]'), initFader);

    var carousels = new Map();
    each(document.querySelectorAll('[data-carousel]'), function (root) {
      carousels.set(root, initCarousel(root));
    });

    initModelSwitch(carousels);
  });
})();
