/* Per-page extra_javascript with instant navigation.
 *
 * Adds the scripts listed in partials/page-scripts.html that this document
 * hasn't loaded yet, in order. Each script is loaded only once, so scripts that
 * set up page content must subscribe to document$, like site-wide ones.
 */
(function () {
  "use strict";

  var queue = Promise.resolve();

  function isLoaded(src) {
    return Array.prototype.some.call(document.scripts, function (script) {
      return script.src === src;
    });
  }

  function load(source) {
    return new Promise(function (resolve) {
      var script = document.createElement("script");
      source.getAttributeNames().forEach(function (name) {
        script.setAttribute(name, source.getAttribute(name));
      });
      // Dynamic scripts are async by default, which would break the order.
      if (!script.hasAttribute("async")) script.async = false;
      script.onload = script.onerror = resolve;
      document.body.appendChild(script);
    });
  }

  document$.subscribe(function () {
    var list = document.getElementById("__page_scripts");
    if (!list) return;
    list.content.querySelectorAll("script").forEach(function (source) {
      queue = queue.then(function () {
        if (!isLoaded(new URL(source.getAttribute("src"), location.href).href)) {
          return load(source);
        }
      });
    });
  });
})();
