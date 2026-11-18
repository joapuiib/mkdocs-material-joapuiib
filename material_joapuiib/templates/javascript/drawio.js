/* Draw.io diagrams with instant navigation.
 *
 * Temporary: remove once mkdocs-drawio supports instant navigation.
 *
 * The drawio plugin adds the viewer at the end of the body, only on pages with
 * diagrams, and the viewer renders once when it loads. This script loads it
 * when a page needs it and renders the diagrams that are new to the document.
 *
 * It also converts the `![](x.drawio)` images that the plugin could not see: the access plugin
 * encrypts the content before the drawio plugin runs, so in protected pages they stay as plain
 * images until the page is unlocked.
 */
(function () {
  "use strict";

  // Relative URLs are relative to the page this script was first loaded on.
  var viewer = new URL(document.currentScript.dataset.viewer, document.baseURI).href;
  var config = JSON.parse(document.currentScript.dataset.config || "{}");
  var loading = false;

  // Replaces the images left by the plugin with the same element it would have created, but the
  // viewer fetches the file itself (`url`) instead of receiving its XML.
  function convert() {
    document.querySelectorAll('img[src$=".drawio" i]').forEach(function (img) {
      if (img.closest(".mxgraph")) return;
      var div = document.createElement("div");
      div.className = "mxgraph";
      div.style.cssText = "max-width:100%;border:1px solid transparent;" + (img.getAttribute("style") || "");
      div.dataset.mxgraph = JSON.stringify(Object.assign({}, config, { url: img.src }));
      // The lightbox plugin wraps the image in a link, which makes no sense around the diagram.
      var link = img.parentElement;
      (link && link.matches("a.glightbox") ? link : img).replaceWith(div);
    });
  }

  function render() {
    document.querySelectorAll(".mxgraph[data-mxgraph]:not([data-drawio-rendered])").forEach(function (el) {
      el.dataset.drawioRendered = "true";
      try {
        el.innerText = "";
        GraphViewer.createViewerForElement(el);
      } catch (error) {
        el.innerText = error.message;
        console.error(error);
      }
    });
  }

  // Called by the viewer when it loads, instead of rendering every diagram.
  window.onDrawioViewerLoad = render;

  document$.subscribe(function () {
    convert();
    if (window.GraphViewer) {
      render();
    } else if (!loading && document.querySelector(".mxgraph[data-mxgraph]")) {
      loading = true;
      var script = document.createElement("script");
      script.src = viewer;
      document.body.appendChild(script);
    }
  });
})();
