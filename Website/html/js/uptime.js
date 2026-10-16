/**
 * Williams Labs — website uptime badges
 *
 * The badges are plain <img> tags served by Uptime Kuma's public badge
 * endpoint (via the Cloudflare Tunnel). No JavaScript data fetching, no CORS,
 * and no extra attack surface. This script only hides the whole panel if the
 * badges can't load (Kuma/tunnel offline) so the page never shows broken images.
 */
(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    var panel = document.getElementById("uptime-panel");
    if (!panel) return;
    var imgs = panel.querySelectorAll("img[data-uptime-badge]");
    var failed = 0;
    imgs.forEach(function (img) {
      img.addEventListener("error", function () {
        failed++;
        if (failed >= imgs.length) panel.hidden = true;
        else img.hidden = true;
      });
    });
  });
})();
