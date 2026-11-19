// Filters the homepage project cards by topic.
// Each card lists its topics in a space-separated data-topics attribute;
// each filter button names one topic in data-filter ("all" shows everything).
// The chosen filter is kept in the URL hash (e.g. #projects/powershell) so it can be linked to.
(function () {
  var bar = document.getElementById('project-filters');
  var grid = document.getElementById('project-grid');
  var status = document.getElementById('filter-status');
  if (!bar || !grid) return;

  var buttons = Array.prototype.slice.call(bar.querySelectorAll('.filter-btn'));
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));

  function topicsOf(card) {
    return (card.getAttribute('data-topics') || '').split(/\s+/);
  }

  // Show how many projects each topic has, and drop buttons with none.
  buttons.forEach(function (btn) {
    var f = btn.getAttribute('data-filter');
    var n = f === 'all' ? cards.length : cards.filter(function (c) {
      return topicsOf(c).indexOf(f) !== -1;
    }).length;
    if (n === 0) { btn.hidden = true; return; }
    var count = document.createElement('span');
    count.className = 'filter-count';
    count.textContent = n;
    btn.appendChild(count);
  });

  function apply(filter, updateHash) {
    var known = buttons.some(function (b) { return b.getAttribute('data-filter') === filter && !b.hidden; });
    if (!known) filter = 'all';

    var shown = 0;
    cards.forEach(function (card) {
      var match = filter === 'all' || topicsOf(card).indexOf(filter) !== -1;
      card.hidden = !match;
      if (match) shown++;
    });

    var label = 'All';
    buttons.forEach(function (b) {
      var on = b.getAttribute('data-filter') === filter;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on) label = b.firstChild.textContent;
    });

    if (status) {
      status.textContent = filter === 'all'
        ? ''
        : 'Showing ' + shown + ' of ' + cards.length + ' projects tagged ' + label + '.';
    }

    if (updateHash && window.history && history.replaceState) {
      history.replaceState(null, '', filter === 'all' ? '#projects' : '#projects/' + filter);
    }
  }

  bar.addEventListener('click', function (e) {
    var btn = e.target.closest('.filter-btn');
    if (btn) apply(btn.getAttribute('data-filter'), true);
  });

  function fromHash() {
    var m = /^#projects\/([a-z-]+)$/.exec(location.hash);
    if (m) {
      apply(m[1], false);
      var section = document.getElementById('projects');
      if (section) section.scrollIntoView();
    } else {
      apply('all', false);
    }
  }

  window.addEventListener('hashchange', fromHash);
  // Wait for the full page (background, uptime badges) so the scroll lands in the right place.
  if (document.readyState === 'complete') fromHash();
  else window.addEventListener('load', fromHash);
})();
