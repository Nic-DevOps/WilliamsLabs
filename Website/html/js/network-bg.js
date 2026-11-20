/*
  Scroll-linked descent through the network background.

  Single scroll listener + rAF dedupe -- at most one transform write per
  animation frame, regardless of how many scroll events fire. No layout
  reads happen inside the loop (cached values only), so this never
  triggers reflow.
*/
(function () {
  var bg = document.getElementById('network-bg');
  var inner = document.getElementById('network-bg-inner');
  if (!bg || !inner) return;

  // Packet/pulse animations are pure CSS (see network-bg.css), which also
  // handles prefers-reduced-motion for them. Here we only skip the parallax.
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var ticking = false;
  var maxTravel = 0;

  function measure() {
    var innerH = inner.offsetHeight;
    var viewportH = window.innerHeight;
    maxTravel = Math.max(0, innerH - viewportH);
  }

  function update() {
    var doc = document.documentElement;
    var scrollable = Math.max(1, doc.scrollHeight - window.innerHeight);
    var progress = Math.min(1, window.scrollY / scrollable);
    var translateY = -progress * maxTravel;
    inner.style.transform = 'translateY(' + translateY.toFixed(1) + 'px)';
    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  }

  function onResize() {
    measure();
    onScroll();
  }

  measure();
  update();

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onResize, { passive: true });
})();
