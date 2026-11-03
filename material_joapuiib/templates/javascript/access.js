/*
 * Client side of material-joapuiib/access.
 *
 * Decrypts protected pages with WebCrypto, keeps credentials in
 * localStorage/sessionStorage and renders the login UI.
 * Time windows are soft: they use the visitor's clock.
 */
(function () {
  "use strict";

  var cfgEl = document.getElementById("__access");
  if (!cfgEl) return;
  var cfg = JSON.parse(cfgEl.textContent);
  var S = cfg.strings;

  var enc = new TextEncoder();
  var dec = new TextDecoder();
  var subtle = window.crypto && window.crypto.subtle;

  var STORE = "access";
  var PREVIEW = "access:preview";
  var DAY = 24 * 3600 * 1000;

  /* ------------------------------------------------------------------ utils */

  function fmt(text, vars) {
    return text.replace(/\{(\w+)\}/g, function (_, k) {
      return vars && k in vars ? vars[k] : "";
    });
  }

  function boxDate(box, attr) {
    if (!box.dataset[attr]) return "";
    return new Date(Date.parse(box.dataset[attr])).toLocaleString(
      document.documentElement.lang || undefined,
      { dateStyle: "long", timeStyle: "short", timeZoneName: "short", timeZone: cfg.timezone });
  }

  /* Compact "start → end" line with icons; the full sentence is the aria-label. */
  function windowLine(box) {
    var start = boxDate(box, "accessStart");
    var end = boxDate(box, "accessEnd");
    var sentence = fmt(start && end ? S.window_range
      : start ? S.window_from : S.window_until, { start: start, end: end });
    var line = h("span", { class: "access__window", "aria-label": sentence });
    [["start", start], ["end", end]].forEach(function (item) {
      if (!item[1]) return;
      var icon = h("span", { class: "access__window-icon", "aria-hidden": "true" });
      icon.innerHTML = cfg.icons[item[0]];
      line.appendChild(h("span", { class: "access__window-item" }, icon, item[1]));
    });
    return line;
  }

  function h(tag, attrs) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "class") node.className = attrs[k];
      else if (k.slice(0, 2) === "on") node.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== false && attrs[k] != null) node.setAttribute(k, attrs[k]);
    });
    var append = function (child) {
      if (child == null || child === false) return;
      if (Array.isArray(child)) return child.forEach(append);
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    };
    for (var i = 2; i < arguments.length; i++) append(arguments[i]);
    return node;
  }

  function b64d(s) {
    var bin = atob(s);
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  function b64e(bytes) {
    var s = "";
    for (var i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
    return btoa(s);
  }

  function hex(buf) {
    return Array.prototype.map.call(new Uint8Array(buf), function (b) {
      return b.toString(16).padStart(2, "0");
    }).join("");
  }

  function baseUrl() {
    var conf = document.getElementById("__config");
    var base = conf ? JSON.parse(conf.textContent).base : ".";
    return new URL(base + "/", location.href);
  }

  /* ----------------------------------------------------------------- crypto */

  async function pbkdf2(secret, saltB64) {
    var material = await subtle.importKey(
      "raw", enc.encode(secret), "PBKDF2", false, ["deriveBits"]);
    var bits = await subtle.deriveBits({
      name: "PBKDF2", hash: "SHA-256", salt: b64d(saltB64),
      iterations: cfg.iterations,
    }, material, 256);
    return new Uint8Array(bits);
  }

  /* Rejects when the key is wrong (GCM tag mismatch). */
  async function open(keyBytes, blob) {
    var key = await subtle.importKey("raw", keyBytes, "AES-GCM", false, ["decrypt"]);
    var plain = await subtle.decrypt(
      { name: "AES-GCM", iv: blob.slice(0, 12) }, key, blob.slice(12));
    return new Uint8Array(plain);
  }

  async function userId(name) {
    var digest = await subtle.digest(
      "SHA-256", enc.encode("access:uid:" + cfg.salt + ":" + name));
    return hex(digest).slice(0, 32);
  }

  /* ---------------------------------------------------------------- storage */

  function readStore(area) {
    try {
      var data = JSON.parse(area.getItem(STORE) || "{}");
      var now = Date.now();
      if (data.user && data.user.exp && data.user.exp < now) delete data.user;
      data.keys = (data.keys || []).filter(function (k) { return !k.exp || k.exp > now; });
      return data;
    } catch (e) { return { keys: [] }; }
  }

  function writeStore(area, data) {
    try { area.setItem(STORE, JSON.stringify(data)); } catch (e) { /* private mode */ }
  }

  function stored() {
    var local = readStore(window.localStorage);
    var session = readStore(window.sessionStorage);
    return {
      user: session.user || local.user || null,
      keys: session.keys.concat(local.keys),
    };
  }

  function expiry(remember) {
    return remember ? Date.now() + cfg.rememberDays * DAY : 0;
  }

  function saveUser(name, key, remember) {
    clearUser();
    var area = remember ? window.localStorage : window.sessionStorage;
    var data = readStore(area);
    data.user = { name: name, key: b64e(key), exp: expiry(remember) };
    writeStore(area, data);
  }

  function saveKey(key, remember) {
    var area = remember ? window.localStorage : window.sessionStorage;
    var data = readStore(area);
    var enc64 = b64e(key);
    data.keys = data.keys.filter(function (k) { return k.k !== enc64; });
    data.keys.push({ k: enc64, exp: expiry(remember) });
    writeStore(area, data);
  }

  function clearUser() {
    [window.localStorage, window.sessionStorage].forEach(function (area) {
      var data = readStore(area);
      delete data.user;
      writeStore(area, data);
    });
  }

  function removeKeys(encoded) {
    [window.localStorage, window.sessionStorage].forEach(function (area) {
      var data = readStore(area);
      data.keys = data.keys.filter(function (k) { return encoded.indexOf(k.k) < 0; });
      writeStore(area, data);
    });
  }

  function clearAll() {
    window.localStorage.removeItem(STORE);
    window.sessionStorage.removeItem(STORE);
  }

  /* ---------------------------------------------------------------- session */

  var dev = null;            // dev.json (serve only)
  var preview = null;        // 'reveal' | 'real' | 'user:<name>'
  var session = null;        // { name, keyring }
  var sessionLoaded = null;  // promise

  async function loadKeyring(name, key) {
    var uid = await userId(name);
    var resp = await fetch(new URL("access/keyrings/" + uid + ".bin", baseUrl()));
    if (!resp.ok) throw new Error("credentials");
    var blob = new Uint8Array(await resp.arrayBuffer());
    var plain = await open(key, blob);  // throws on a wrong password
    return JSON.parse(dec.decode(plain));
  }

  async function loadSession() {
    session = null;
    var mode = preview;
    if (mode && mode.indexOf("user:") === 0) {
      var who = mode.slice(5);
      if (dev && dev.users[who]) {
        session = { name: who, keyring: await loadKeyring(who, b64d(dev.users[who].key)) };
      }
      return;
    }
    var saved = stored().user;
    if (!saved) return;
    try {
      session = { name: saved.name, keyring: await loadKeyring(saved.name, b64d(saved.key)) };
    } catch (e) {
      if (e.message === "credentials" || e.name === "OperationError") clearUser();
    }
  }

  function ensureSession() {
    if (!sessionLoaded) sessionLoaded = loadSession();
    return sessionLoaded;
  }

  function resetSession() {
    sessionLoaded = null;
    return ensureSession();
  }

  async function login(name, password, remember) {
    name = name.trim().toLowerCase();
    var key = await pbkdf2(name + "\u0000" + password, cfg.saltUser);
    await loadKeyring(name, key);  // validates the credentials
    saveUser(name, key, remember);
    if (preview && preview.indexOf("user:") === 0) setPreview("real");
    await resetSession();
    refreshAll();
  }

  function logout() {
    clearAll();
    location.reload();
  }

  /* ------------------------------------------------------------------ pages */

  function payloadOf(box) {
    if (!box._payload) {
      box._payload = JSON.parse(box.querySelector(".access__payload").textContent);
    }
    return box._payload;
  }

  function windowState(box) {
    var now = Date.now();
    var start = box.dataset.accessStart && Date.parse(box.dataset.accessStart);
    var end = box.dataset.accessEnd && Date.parse(box.dataset.accessEnd);
    if (start && now < start) return "before";
    if (end && now >= end) return "after";
    return "open";
  }

  /* Every key that can decrypt this page, with where it came from. */
  async function candidates(box) {
    var out = [];
    var payload = payloadOf(box);
    var pid = box.dataset.accessPage;

    if (cfg.dev && preview === "reveal" && box.dataset.accessDev) {
      out.push({ cek: b64d(box.dataset.accessDev), src: "dev", bypass: true });
    }
    if (payload.o) out.push({ cek: b64d(payload.o), src: "open", bypass: false });

    await ensureSession();
    var entry = session && session.keyring.pages[pid];
    if (entry) out.push({ cek: b64d(entry.k), src: "user", bypass: !!entry.b });

    var keys = stored().keys;
    for (var i = 0; i < keys.length; i++) {
      for (var j = 0; j < payload.w.length; j++) {
        try {
          var cek = await open(b64d(keys[i].k), b64d(payload.w[j].w));
          out.push({ cek: cek, src: "pw", bypass: !!payload.w[j].b, key: keys[i].k });
        } catch (e) { /* not this one */ }
      }
    }
    return out;
  }

  async function evaluate(box) {
    if (!subtle) return showLocked(box, "no_crypto");
    clearTimeout(box._timer);
    var cands = await candidates(box);
    var state = windowState(box);
    var usable = cands.filter(function (c) { return c.bypass || state === "open"; })[0];
    if (usable) return unlock(box, usable, state);
    showLocked(box, state === "open" ? "locked" : state, cands.length > 0);
  }

  async function unlock(box, cand, state) {
    var html;
    try {
      html = dec.decode(await open(cand.cek, b64d(payloadOf(box).c)));
    } catch (e) {
      return showLocked(box, "locked");
    }
    var content = box.querySelector(".access__content");
    var locked = box.querySelector(".access__locked");
    var fresh = box.dataset.accessState !== "unlocked";

    content.innerHTML = "";
    var bar = buildBar(box, cand, state);
    if (bar) content.appendChild(bar);
    var body = h("div", { class: "access__body" });
    body.innerHTML = html;
    content.appendChild(body);
    content.hidden = false;
    locked.hidden = true;
    box.dataset.accessState = "unlocked";

    // Re-lock when the window closes.
    var end = box.dataset.accessEnd && Date.parse(box.dataset.accessEnd);
    if (end && !cand.bypass && state === "open") {
      box._timer = setTimeout(function () { evaluate(box); }, Math.min(end - Date.now(), 2147483647));
    }

    if (fresh) {
      if (box.dataset.accessKind !== "section") buildToc(body);
      if (window.document$) window.document$.next(document);
    }
  }

  function buildBar(box, cand, state) {
    var parts = [];
    if (cfg.dev && cand.src === "dev") {
      parts.push(h("span", { class: "access__note" }, S.dev_banner));
    } else if (cand.src === "pw") {
      parts.push(h("span", { class: "access__note" }, S.unlocked_password));
    }
    if (cand.bypass && state !== "open" && cand.src !== "dev") {
      parts.push(h("span", { class: "access__note" }, S.unlocked_exception, " ", windowLine(box)));
    }
    if (cand.src === "pw") {
      if (cfg.share) {
        var share = h("button", { type: "button", class: "access__btn" }, S.share);
        share.addEventListener("click", function () {
          var link = location.origin + location.pathname + location.search +
            "#!access=" + encodeURIComponent(cand.key);
          navigator.clipboard.writeText(link).then(function () {
            share.textContent = S.share_copied;
          });
        });
        parts.push(share);
      }
      parts.push(h("button", {
        type: "button", class: "access__btn", onclick: function () { pageLogout(box); },
      }, S.page_logout));
    }
    return parts.length ? h("div", { class: "access__bar" }, parts) : null;
  }

  /* Forget every stored password that opens this page, then reload. */
  async function pageLogout(box) {
    var payload = payloadOf(box);
    var drop = [];
    var keys = stored().keys;
    for (var i = 0; i < keys.length; i++) {
      for (var j = 0; j < payload.w.length; j++) {
        try {
          await open(b64d(keys[i].k), b64d(payload.w[j].w));
          drop.push(keys[i].k);
        } catch (e) { /* not this one */ }
      }
    }
    removeKeys(drop);
    location.reload();
  }

  function showLocked(box, reason, hadAccess) {
    var content = box.querySelector(".access__content");
    var locked = box.querySelector(".access__locked");
    content.hidden = true;
    content.innerHTML = "";
    locked.hidden = false;
    box.dataset.accessState = "locked";

    var ui = locked.querySelector(".access__ui");
    ui.innerHTML = "";
    var payload = payloadOf(box);
    var message;
    var isSection = box.dataset.accessKind === "section";
    if (box.dataset.accessAuthor) {
      ui.appendChild(h("p", { class: "access__msg" }, S.author_only));
      return;
    } else if (reason === "before" || reason === "after") {
      message = windowLine(box);
    } else {
      message = isSection ? S.locked_text_section : S.locked_text;
    }
    ui.appendChild(h("p", { class: "access__msg" }, message));

    if (reason === "before") {
      var count = h("p", { class: "access__countdown" });
      ui.appendChild(count);
      var start = Date.parse(box.dataset.accessStart);
      var tick = function () {
        if (!box.isConnected) return;
        var left = start - Date.now();
        if (left <= 0) return evaluate(box);
        count.textContent = fmt(S.countdown, { time: duration(left) });
        box._timer = setTimeout(tick, 1000);
      };
      tick();
    }

    if (payload.w.length) {
      ui.appendChild(buildPasswordForm(box));
    }
    if (box.dataset.accessUsers && cfg.users) {
      if (session && !hadAccess) {
        ui.appendChild(h("p", { class: "access__msg" }, fmt(isSection ? S.not_allowed_section : S.not_allowed, { user: session.name })));
      } else if (!session) {
        ui.appendChild(h("p", { class: "access__msg" }, S.locked_user));
        ui.appendChild(h("button", {
          type: "button", class: "access__btn access__btn--primary", onclick: openDialog,
        }, S.login));
      }
    }
  }

  function duration(ms) {
    var total = Math.floor(ms / 1000);
    var d = Math.floor(total / 86400);
    var rest = total % 86400;
    var pad = function (n) { return String(n).padStart(2, "0"); };
    var clock = pad(Math.floor(rest / 3600)) + ":" + pad(Math.floor((rest % 3600) / 60)) +
      ":" + pad(rest % 60);
    return d ? d + "d " + clock : clock;
  }

  function buildPasswordForm(box) {
    var input = h("input", {
      type: "password", class: "access__input", autocomplete: "current-password",
      placeholder: S.password, "aria-label": S.password, required: "",
    });
    var show = h("input", { type: "checkbox" });
    show.addEventListener("change", function () {
      input.type = show.checked ? "text" : "password";
    });
    var remember = h("input", { type: "checkbox" });
    var error = h("p", { class: "access__error", role: "alert" });
    var form = h("form", { class: "access__form" },
      h("div", { class: "access__row" }, input,
        h("button", { type: "submit", class: "access__btn access__btn--primary" }, S.unlock)),
      h("label", { class: "access__check" }, show, " " + S.show_password),
      h("label", { class: "access__check" }, remember, " " + S.remember),
      error);

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      error.textContent = "";
      var key = await pbkdf2(input.value, cfg.saltPw);
      var ok = false;
      var wraps = payloadOf(box).w;
      for (var i = 0; i < wraps.length && !ok; i++) {
        try { await open(key, b64d(wraps[i].w)); ok = true; } catch (e) { /* next */ }
      }
      if (!ok) {
        error.textContent = S.wrong_password;
        return;
      }
      saveKey(key, remember.checked);
      refreshAll();
    });
    return form;
  }

  /* -------------------------------------------------------------------- toc */

  function buildToc(body) {
    var list = document.querySelector('.md-sidebar--secondary [data-md-component="toc"]');
    if (!list) return;
    list.innerHTML = "";
    var items = Array.prototype.filter.call(
      body.querySelectorAll("h1, h2, h3, h4"), function (el) {
        return el.id && el.tagName !== "H1";
      }).map(function (el) {
        var clone = el.cloneNode(true);
        var perm = clone.querySelector(".headerlink");
        if (perm) perm.remove();
        return { level: +el.tagName[1], id: el.id, text: clone.textContent.trim(), children: [] };
      });

    var root = { children: [] };
    var stack = [{ level: 1, node: root }];
    items.forEach(function (item) {
      while (stack[stack.length - 1].level >= item.level) stack.pop();
      stack[stack.length - 1].node.children.push(item);
      stack.push({ level: item.level, node: item });
    });

    function render(item) {
      var li = h("li", { class: "md-nav__item" },
        h("a", { href: "#" + item.id, class: "md-nav__link" },
          h("span", { class: "md-ellipsis" }, item.text)));
      if (item.children.length) {
        var ul = h("ul", { class: "md-nav__list" });
        item.children.forEach(function (c) { ul.appendChild(render(c)); });
        li.appendChild(h("nav", { class: "md-nav", "aria-label": item.text }, ul));
      }
      return li;
    }
    root.children.forEach(function (item) { list.appendChild(render(item)); });
  }

  /* ----------------------------------------------------------- header + UI */

  /* The buttons are rendered by partials/access-header.html so that Material
   * mounts its tooltips on them; here we only toggle and wire them. */
  async function mountHeader() {
    var wrap = document.querySelector(".access-header");
    if (!wrap) return;
    var login = wrap.querySelector(".access-header__login");
    var logoutBtn = wrap.querySelector(".access-header__logout");
    if (!login.dataset.accessWired) {
      login.dataset.accessWired = "1";
      login.addEventListener("click", openDialog);
      logoutBtn.addEventListener("click", logout);
    }

    await ensureSession();
    var loggedIn = !!session || stored().keys.length > 0;
    login.hidden = loggedIn;
    logoutBtn.hidden = !loggedIn;
    logoutBtn.querySelector(".access-header__user").textContent = session ? session.name : "";
  }

  var dialog = null;

  function openDialog() {
    if (!dialog || !dialog.isConnected) dialog = buildDialog();
    dialog.querySelector(".access__error").textContent = "";
    dialog.showModal();
    dialog.querySelector("input").focus();
  }

  function buildDialog() {
    var user = h("input", {
      type: "text", class: "access__input", autocomplete: "username",
      placeholder: S.username, "aria-label": S.username, required: "",
    });
    var pass = h("input", {
      type: "password", class: "access__input", autocomplete: "current-password",
      placeholder: S.password, "aria-label": S.password, required: "",
    });
    var show = h("input", { type: "checkbox" });
    show.addEventListener("change", function () { pass.type = show.checked ? "text" : "password"; });
    var remember = h("input", { type: "checkbox" });
    var error = h("p", { class: "access__error", role: "alert" });
    var cancel = h("button", { type: "button", class: "access__btn" }, S.cancel);
    var form = h("form", { method: "dialog", class: "access__form" },
      h("h2", null, S.dialog_title), user, pass,
      h("label", { class: "access__check" }, show, " " + S.show_password),
      h("label", { class: "access__check" }, remember, " " + S.remember),
      error,
      h("div", { class: "access__row access__row--end" }, cancel,
        h("button", { type: "submit", class: "access__btn access__btn--primary" }, S.submit)));
    var dlg = h("dialog", { class: "access-dialog" }, form);
    cancel.addEventListener("click", function () { dlg.close(); });

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      error.textContent = "";
      try {
        await login(user.value, pass.value, remember.checked);
        pass.value = "";
        dlg.close();
      } catch (e) {
        error.textContent = e.message === "credentials" || e.name === "OperationError"
          ? S.wrong_credentials : S.network_error;
      }
    });
    document.body.appendChild(dlg);
    return dlg;
  }

  /* ------------------------------------------------------- dev preview bar */

  function setPreview(mode) {
    preview = mode;
    try { sessionStorage.setItem(PREVIEW, mode); } catch (e) { /* ignore */ }
  }

  /* Loads the dev data and the preview mode (every page: they drive the session). */
  async function loadDev() {
    if (!cfg.dev) return;
    if (!dev) {
      try {
        var resp = await fetch(new URL("access/dev.json", baseUrl()));
        dev = await resp.json();
      } catch (e) { dev = { users: {} }; }
    }
    if (!preview) {
      var saved = null;
      try { saved = sessionStorage.getItem(PREVIEW); } catch (e) { /* ignore */ }
      preview = saved || (cfg.reveal ? "reveal" : "real");
    }
  }

  /* The preview bar only makes sense on pages that have protected content. */
  function mountDevBar() {
    var existing = document.querySelector(".access-dev");
    if (!cfg.dev || !boxes().length) {
      if (existing) existing.remove();
      return;
    }
    if (existing) return;

    var select = h("select", { class: "access-dev__select" },
      cfg.reveal ? h("option", { value: "reveal" }, S.dev_reveal) : null,
      h("option", { value: "real" }, S.dev_anonymous),
      Object.keys(dev.users).sort().map(function (name) {
        return h("option", { value: "user:" + name }, name);
      }));
    select.value = preview;
    select.addEventListener("change", async function () {
      clearAll();  // every preview starts without stored credentials
      setPreview(select.value);
      await resetSession();
      await mountHeader();
      refreshAll(true);
    });
    document.body.appendChild(h("div", { class: "access-dev" },
      h("strong", null, S.dev_banner), h("label", null, S.dev_as + " ", select)));
  }

  /* ------------------------------------------------------------------- init */

  function boxes() {
    return Array.prototype.slice.call(document.querySelectorAll(".access[data-access-page]"));
  }

  function refreshAll(force) {
    boxes().forEach(function (box) {
      if (force && box.dataset.accessState === "unlocked") {
        // Relock first so the UI is rebuilt from scratch.
        box.dataset.accessState = "";
        box.querySelector(".access__content").innerHTML = "";
      }
      evaluate(box);
    });
    mountHeader();
  }

  function importShared() {
    var m = location.hash.match(/^#!access=(.+)$/);
    if (!m) return;
    try { saveKey(b64d(decodeURIComponent(m[1])), false); } catch (e) { return; }
    history.replaceState(null, "", location.pathname + location.search);
  }

  async function init() {
    importShared();
    await loadDev();
    mountDevBar();
    await ensureSession();
    boxes().forEach(function (box) {
      if (box.dataset.accessState) return;  // already handled
      box.dataset.accessState = "locked";
      evaluate(box);
    });
    mountHeader();
  }

  if (window.document$) window.document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
