/**
 * Williams Labs — live infrastructure status widget
 *
 * Polls a small JSON status API (see status-api/app.py) that sits in front
 * of Prometheus on the monitoring VM and is exposed publicly through a
 * Cloudflare Tunnel. This script never talks to Prometheus or Grafana
 * directly — only to that narrow status endpoint — so nothing about the
 * homelab's internal topology is exposed to the browser.
 *
 * Usage: include this file and add a container:
 *   <div id="status-widget" data-status-url="https://status.williamslabs.ca/api/status"></div>
 * Configure the endpoint via the data-status-url attribute, or by setting
 * window.WL_STATUS_URL before this script loads.
 */
(function () {
  "use strict";

  var POLL_INTERVAL_MS = 30000;
  var FETCH_TIMEOUT_MS = 6000;

  function fetchWithTimeout(url, ms) {
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, ms);
    return fetch(url, { signal: controller.signal, cache: "no-store" })
      .finally(function () { clearTimeout(timer); });
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function relativeTime(iso) {
    if (!iso) return "unknown";
    var then = new Date(iso).getTime();
    if (isNaN(then)) return "unknown";
    var diff = Math.max(0, Math.floor((Date.now() - then) / 1000));
    if (diff < 10) return "just now";
    if (diff < 60) return diff + "s ago";
    if (diff < 3600) return Math.floor(diff / 60) + "m ago";
    return Math.floor(diff / 3600) + "h ago";
  }

  function renderOffline(container, message) {
    container.innerHTML =
      '<div class="status-widget-head"><h3>Infrastructure Status</h3></div>' +
      '<div class="status-banner offline">' +
      '<span class="dot-indicator dot-unknown"></span>' +
      escapeHtml(message || "Status feed unreachable — the monitoring VM may be offline or the tunnel is down.") +
      "</div>";
  }

  function renderStatus(container, data) {
    var devices = Array.isArray(data.devices) ? data.devices : [];
    var upCount = devices.filter(function (d) { return d.up; }).length;

    var head =
      '<div class="status-widget-head">' +
      "<h3>Infrastructure Status</h3>" +
      '<span class="status-meta">' + upCount + "/" + devices.length +
      " devices up &middot; updated " + escapeHtml(relativeTime(data.generated_at)) + "</span>" +
      "</div>";

    if (!devices.length) {
      container.innerHTML = head +
        '<div class="status-banner">No devices reported by the status feed.</div>';
      return;
    }

    var rows = devices.map(function (d) {
      var dotClass = d.up === true ? "dot-up" : d.up === false ? "dot-down" : "dot-unknown";
      var stateLabel = d.up === true ? "UP" : d.up === false ? "DOWN" : "UNKNOWN";
      return "<tr>" +
        "<td><span class=\"dot-indicator " + dotClass + "\"></span>" + escapeHtml(d.name || d.instance || "unknown") + "</td>" +
        "<td>" + escapeHtml(d.site || "—") + "</td>" +
        "<td>" + stateLabel + "</td>" +
        "<td>" + escapeHtml(d.detail || "—") + "</td>" +
        "</tr>";
    }).join("");

    container.innerHTML = head +
      '<table class="status-table">' +
      "<thead><tr><th>Device</th><th>Site</th><th>State</th><th>Detail</th></tr></thead>" +
      "<tbody>" + rows + "</tbody>" +
      "</table>";
  }

  function initWidget(container) {
    var url = container.getAttribute("data-status-url") || window.WL_STATUS_URL;
    if (!url) {
      renderOffline(container, "No status endpoint configured.");
      return;
    }

    function poll() {
      fetchWithTimeout(url, FETCH_TIMEOUT_MS)
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.json();
        })
        .then(function (data) { renderStatus(container, data); })
        .catch(function () {
          renderOffline(container);
        });
    }

    poll();
    setInterval(poll, POLL_INTERVAL_MS);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var widgets = document.querySelectorAll("[data-status-widget]");
    widgets.forEach(initWidget);
  });
})();
