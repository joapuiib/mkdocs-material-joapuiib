/* Tooltips for cross-references to figures and tables (a.xref).
 *
 * The tooltip reuses the markup and styles of MaterialX tooltips
 * (.md-tooltip2), so it looks the same as footnote and link previews.
 *
 *   - Target in the same page: cloned from the DOM.
 *   - Target in another page: the page is fetched (and cached) and the
 *     target is cloned from it.
 *
 * Each reference gets a preview icon (button.xref__toggle) next to it:
 *   - Hover devices: hovering or focusing the link shows the preview. The
 *     icon is only a hint (clicking it pins the preview).
 *   - Touch devices (no hover): tapping the link follows it, tapping the
 *     icon opens the preview. Tapping outside or ESC closes it.
 *
 * Events are delegated on the document, so it keeps working with instant
 * navigation.
 */
(function () {
  "use strict";

  var HIDE_DELAY = 250;   // ms the tooltip stays after the pointer leaves
  var GAP = 16;           // px between host and tooltip
  var LOADING = "xref--loading";  // host class while the preview loads

  var pages = new Map();  // page URL (no hash) -> Promise<Document|null>
  var sequence = 0;

  var TOGGLE = "xref__toggle";
  var LABEL = "Mostra la vista prèvia";

  var current = null;     // { host, toggle, node, token, pinned }
  var hideTimer = null;

  function noHover() {
    return window.matchMedia && window.matchMedia("(hover: none)").matches;
  }

  function loadPage(url) {
    if (!pages.has(url)) {
      pages.set(url, fetch(url)
        .then(function (r) { return r.ok ? r.text() : null; })
        .then(function (text) {
          return text ? new DOMParser().parseFromString(text, "text/html") : null;
        })
        .catch(function () { return null; }));
    }
    return pages.get(url);
  }

  /* Absolute URLs for src/href, so a clone from another page keeps working. */
  function absolutize(root, base) {
    root.querySelectorAll("[src], [href]").forEach(function (el) {
      ["src", "href"].forEach(function (attr) {
        var value = el.getAttribute(attr);
        if (value && !/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(value)) {
          el.setAttribute(attr, new URL(value, base).toString());
        }
      });
    });
  }

  function findTarget(host) {
    var url = new URL(host.href, location.href);
    var id = decodeURIComponent(url.hash.slice(1));
    if (!id) return Promise.resolve(null);

    var samePage = url.origin === location.origin && url.pathname === location.pathname;
    if (samePage) {
      return Promise.resolve(document.getElementById(id));
    }

    url.hash = "";
    return loadPage(url.toString()).then(function (doc) {
      if (!doc) return null;
      var target = doc.getElementById(id);
      if (target) absolutize(target, url);
      return target;
    });
  }

  function build(target) {
    var clone = target.cloneNode(true);
    clone.removeAttribute("id");
    clone.querySelectorAll("[id]").forEach(function (el) { el.removeAttribute("id"); });
    clone.querySelectorAll("img").forEach(function (img) {
      img.setAttribute("loading", "eager");
    });

    var node = document.createElement("div");
    node.className = "md-tooltip2 xref-tooltip";
    node.setAttribute("role", "dialog");
    node.id = "__xref_tooltip_" + sequence++;

    var inner = document.createElement("div");
    inner.className = "md-tooltip2__inner md-typeset";
    inner.appendChild(clone);
    node.appendChild(inner);
    return node;
  }

  function place(host, node) {
    var rect = host.getBoundingClientRect();
    var height = node.firstElementChild.getBoundingClientRect().height;
    var above = rect.top >= window.innerHeight / 2;

    node.style.setProperty("--md-tooltip-host-x", (rect.left + window.scrollX) + "px");
    node.style.setProperty("--md-tooltip-host-y", (rect.top + window.scrollY) + "px");
    node.style.setProperty("--md-tooltip-x", (rect.width / 2) + "px");
    node.style.setProperty("--md-tooltip-y",
      (above ? -GAP - height : GAP + rect.height) + "px");
    node.classList.toggle("md-tooltip2--top", above);
    node.classList.toggle("md-tooltip2--bottom", !above);
  }

  /* Wrap each reference with its preview icon, so they never break apart. */
  function enhance() {
    document.querySelectorAll("a.xref[href]").forEach(function (host) {
      var next = host.nextElementSibling;
      if (next && next.classList.contains(TOGGLE)) return;

      var group = document.createElement("span");
      group.className = "xref-group";
      host.parentNode.insertBefore(group, host);
      group.appendChild(host);

      var toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = TOGGLE;
      toggle.setAttribute("aria-label", LABEL);
      toggle.setAttribute("aria-expanded", "false");
      /* With hover, focusing the link already shows the preview. */
      if (!noHover()) toggle.tabIndex = -1;
      group.appendChild(toggle);
    });
  }

  function toggleOf(host) {
    var next = host.nextElementSibling;
    return next && next.classList.contains(TOGGLE) ? next : null;
  }

  function open(host, pinned) {
    if (!pinned && noHover()) return;
    cancelHide();
    if (current && current.host === host) {
      if (pinned) current.pinned = true;
      return;
    }
    close();

    var token = {};
    var toggle = toggleOf(host);
    current = { host: host, toggle: toggle, node: null, token: token, pinned: !!pinned };
    host.classList.add(LOADING);
    if (toggle) toggle.setAttribute("aria-expanded", "true");

    findTarget(host).then(function (target) {
      if (!current || current.token !== token) return;
      if (!target) {
        host.classList.remove(LOADING);
        if (toggle) toggle.setAttribute("aria-expanded", "false");
        return;
      }

      var node = build(target);
      current.node = node;
      document.body.appendChild(node);

      place(host, node);

      /* Keep the loading cursor until every image in the preview is ready. */
      var pending = 0;
      function settle() {
        if (--pending === 0 && current && current.token === token) {
          host.classList.remove(LOADING);
        }
      }
      node.querySelectorAll("img").forEach(function (img) {
        if (!img.complete) {
          pending++;
          img.addEventListener("load", function () { place(host, node); settle(); });
          img.addEventListener("error", settle);
        }
      });
      if (pending === 0) host.classList.remove(LOADING);

      host.setAttribute("aria-describedby", node.id);
      if (toggle) toggle.setAttribute("aria-controls", node.id);
      requestAnimationFrame(function () {
        node.classList.add("md-tooltip2--active");
      });
    });
  }

  function close() {
    cancelHide();
    if (!current) return;
    var host = current.host;
    var node = current.node;
    var toggle = current.toggle;
    current = null;

    host.classList.remove(LOADING);
    host.removeAttribute("aria-describedby");
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
      toggle.removeAttribute("aria-controls");
    }
    if (node) {
      node.classList.remove("md-tooltip2--active");
      setTimeout(function () { node.remove(); }, HIDE_DELAY);
    }
  }

  function scheduleHide() {
    if (current && current.pinned) return;
    cancelHide();
    hideTimer = setTimeout(close, HIDE_DELAY);
  }

  function cancelHide() {
    if (hideTimer) {
      clearTimeout(hideTimer);
      hideTimer = null;
    }
  }

  function toggleAt(el) {
    return el && el.closest ? el.closest("." + TOGGLE) : null;
  }

  /* The reference for an event target: the link itself or its icon. */
  function hostOf(el) {
    if (!el || !el.closest) return null;
    var toggle = toggleAt(el);
    if (toggle) return toggle.previousElementSibling;
    return el.closest("a.xref");
  }

  function inTooltip(el) {
    return el && el.closest ? el.closest(".xref-tooltip") : null;
  }

  document.addEventListener("mouseover", function (e) {
    var host = hostOf(e.target);
    if (host) open(host);
    else if (inTooltip(e.target)) cancelHide();
  });

  document.addEventListener("mouseout", function (e) {
    if (hostOf(e.target) || inTooltip(e.target)) scheduleHide();
  });

  document.addEventListener("focusin", function (e) {
    var host = hostOf(e.target);
    if (host) open(host);
  });

  document.addEventListener("focusout", function (e) {
    if (hostOf(e.target)) scheduleHide();
  });

  document.addEventListener("click", function (e) {
    var toggle = toggleAt(e.target);
    if (toggle) {
      e.preventDefault();
      var host = toggle.previousElementSibling;
      if (current && current.host === host && current.pinned) close();
      else open(host, true);
    } else if (current && current.pinned && !inTooltip(e.target)) {
      close();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape" || !current) return;
    var toggle = current.pinned ? current.toggle : null;
    var inside = inTooltip(document.activeElement);
    close();
    if (toggle && inside) toggle.focus();
  });

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(enhance);
  } else {
    enhance();
  }

  /* Hide on navigation (instant loading keeps the document alive). */
  window.addEventListener("hashchange", close);
  if (window.location$ && window.location$.subscribe) {
    window.location$.subscribe(close);
  }
})();
