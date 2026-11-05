/* Draw.io diagrams with instant navigation.
 *
 * Temporary: remove once mkdocs-drawio supports instant navigation.
 *
 * The drawio plugin adds the viewer at the end of the body, only on pages with
 * diagrams, and the viewer renders once when it loads. This script loads it
 * when a page needs it and renders the diagrams that are new to the document.
 */
(function () {
  "use strict";

  // Relative URLs are relative to the page this script was first loaded on.
  var viewer = new URL(document.currentScript.dataset.viewer, document.baseURI).href;
  var loading = false;

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
