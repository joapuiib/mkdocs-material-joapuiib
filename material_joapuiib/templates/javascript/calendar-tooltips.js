/* Calendar tooltips.
 *
 * Two interaction modes:
 *   - Hover/focus (pointer/keyboard): shows transiently. Pointer leave or
 *     blur hides.
 *   - Click/Enter/Space/Tap: pins the tooltip open. Stays until the host is
 *     activated again, the user clicks outside, ESC is pressed, or the page
 *     scrolls/resizes.
 *
 * Accessibility:
 *   - Pinned tooltip captures Tab so focus cycles through links/buttons
 *     inside the popover.
 *   - ESC closes a pinned tooltip and returns focus to the host cell.
 */
(function () {
  "use strict";

  var GUTTER = 8;     // px between host and tooltip
  var EDGE = 8;       // px clamp from viewport edges
  var FOCUSABLE_SELECTOR =
    "a[href], button, [tabindex]:not([tabindex='-1']), input, select, textarea";

  var current = null;          // currently visible tooltip (HTMLElement)
  var currentHost = null;      // host element for current tooltip
  var pinned = false;          // is the current tooltip pinned?

  function show(host, pin) {
    var id = host.getAttribute("data-cal-tip");
    if (!id) return;
    var tip = document.getElementById(id);
    if (!tip) return;

    if (current && current !== tip) hide();

    current = tip;
    currentHost = host;
    pinned = !!pin;

    tip.removeAttribute("hidden");
    /* eslint-disable-next-line no-unused-expressions */
    tip.offsetHeight; // force layout so the transition runs
    tip.classList.add("is-open");
    tip.classList.toggle("is-pinned", pinned);
    host.setAttribute("aria-expanded", "true");

    requestAnimationFrame(function () { position(host, tip); });
  }

  function hide(refocusHost) {
    if (!current) return;
    var prevHost = currentHost;
    current.classList.remove("is-open", "is-pinned");
    current.setAttribute("hidden", "hidden");
    if (currentHost) currentHost.removeAttribute("aria-expanded");
    current = null;
    currentHost = null;
    pinned = false;
    if (refocusHost && prevHost && typeof prevHost.focus === "function") {
      prevHost.focus();
    }
  }

  function position(host, tip) {
    var rect = host.getBoundingClientRect();
    var tipRect = tip.getBoundingClientRect();

    var top = rect.bottom + GUTTER;
    if (top + tipRect.height > window.innerHeight - EDGE) {
      top = rect.top - tipRect.height - GUTTER;
    }
    var left = rect.left + rect.width / 2 - tipRect.width / 2;
    left = Math.max(EDGE, Math.min(left, window.innerWidth - tipRect.width - EDGE));

    tip.style.top = Math.round(top) + "px";
    tip.style.left = Math.round(left) + "px";
  }

  function isInsideTooltip(node) {
    while (node && node !== document.body) {
      if (node.classList && node.classList.contains("md-calendar-tooltip")) return true;
      node = node.parentNode;
    }
    return false;
  }

  function focusables(tip) {
    return Array.prototype.slice.call(tip.querySelectorAll(FOCUSABLE_SELECTOR));
  }

  function bind(host) {
    // Pointer: skip transient open on touch — the synthetic click that
    // follows already pins the tooltip, and pointerleave fires immediately
    // when the finger lifts otherwise.
    host.addEventListener("pointerenter", function (e) {
      if (e.pointerType === "touch") return;
      if (pinned) return;
      show(host, false);
    });

    host.addEventListener("pointerleave", function (e) {
      if (e.pointerType === "touch") return;
      if (pinned) return;
      hide();
    });

    host.addEventListener("focus", function () {
      if (pinned) return;
      show(host, false);
    });

    host.addEventListener("blur", function (e) {
      if (pinned) return;
      // Keep the tooltip alive when focus moved into it (e.g., to follow
      // a link inside the popover).
      if (isInsideTooltip(e.relatedTarget)) return;
      hide();
    });

    host.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (pinned && currentHost === host) {
        hide(true);
        return;
      }
      show(host, true);
    });

    host.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        if (pinned && currentHost === host) hide(true);
        else show(host, true);
      }
    });
  }

  function init() {
    var hosts = document.querySelectorAll("[data-cal-tip]");
    for (var i = 0; i < hosts.length; i++) bind(hosts[i]);
  }

  // Click-outside closes a pinned tooltip.
  document.addEventListener("click", function (e) {
    if (!pinned) return;
    if (currentHost && currentHost.contains(e.target)) return;
    if (isInsideTooltip(e.target)) return;
    hide();
  });

  // Hide on scroll/resize — fixed positioning would otherwise drift.
  window.addEventListener("scroll", function () { hide(); }, { passive: true });
  window.addEventListener("resize", function () { hide(); }, { passive: true });

  // Global keyboard handling: focus trap inside pinned tooltip + Esc dismiss.
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && current) {
      hide(true);
      return;
    }
    if (e.key !== "Tab" || !pinned || !current) return;

    var fs = focusables(current);
    if (fs.length === 0) {
      // Nothing focusable inside — keep focus on the host.
      e.preventDefault();
      if (currentHost) currentHost.focus();
      return;
    }
    var first = fs[0];
    var last = fs[fs.length - 1];
    var active = document.activeElement;
    var insideTip = isInsideTooltip(active);
    var onHost = active === currentHost;

    if (!e.shiftKey) {
      if (onHost || active === last) {
        e.preventDefault();
        first.focus();
      }
      // Otherwise: let the browser advance focus inside the tooltip.
    } else {
      if (onHost || active === first || !insideTip) {
        e.preventDefault();
        last.focus();
      }
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
